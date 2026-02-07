"""
Management command to import forms from Salesforce/TaroWorks JSON exports
"""
import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from forms.models import FormTemplate, FormField

User = get_user_model()


class Command(BaseCommand):
    help = 'Import form templates from JSON files (Salesforce/TaroWorks export format)'

    # Map Salesforce field types to UPG field types
    TYPE_MAP = {
        'text-short': 'text',
        'text-long': 'textarea',
        'number-integer': 'number',
        'number-decimal': 'decimal',
        'date-date': 'date',
        'date-datetime': 'datetime',
        'radio': 'radio',
        'checkbox': 'checkbox',
        'dropdown': 'select',
        'gps-location': 'geopoint',
        'signature': 'signature',
        'photo': 'image',
        'section': 'section',
        'note': 'note',
        'barcode': 'barcode',
    }

    def add_arguments(self, parser):
        parser.add_argument(
            'path',
            type=str,
            help='Path to JSON file or directory containing JSON files'
        )
        parser.add_argument(
            '--user',
            type=str,
            default='admin',
            help='Username to set as form creator (default: admin)'
        )
        parser.add_argument(
            '--activate',
            action='store_true',
            help='Set imported forms to active status'
        )

    def handle(self, *args, **options):
        path = options['path']
        username = options['user']
        activate = options['activate']

        # Get or create user
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stderr.write(self.style.ERROR(f'User "{username}" not found and no superuser exists'))
                return

        # Collect JSON files
        json_files = []
        if os.path.isfile(path):
            json_files = [path]
        elif os.path.isdir(path):
            for filename in os.listdir(path):
                if filename.endswith('.json'):
                    json_files.append(os.path.join(path, filename))

        if not json_files:
            self.stderr.write(self.style.ERROR(f'No JSON files found at: {path}'))
            return

        self.stdout.write(f'Found {len(json_files)} JSON file(s) to import')

        for json_path in json_files:
            self.import_json_file(json_path, user, activate)

    def import_json_file(self, json_path, user, activate):
        """Import a single JSON file"""
        self.stdout.write(f'\nImporting: {os.path.basename(json_path)}')

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stderr.write(self.style.ERROR(f'  Invalid JSON: {e}'))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'  Error reading file: {e}'))
            return

        # Extract form metadata
        forms = data.get('Forms', [])
        if not forms:
            self.stderr.write(self.style.WARNING('  No forms found in file'))
            return

        form_data = forms[0]
        form_name = form_data.get('Name', 'Imported Form')
        form_description = form_data.get('gfsurveys__Description__c', '')

        # Check if form already exists
        if FormTemplate.objects.filter(name=form_name).exists():
            self.stdout.write(self.style.WARNING(f'  Form "{form_name}" already exists, skipping'))
            return

        # Create form template
        form_template = FormTemplate.objects.create(
            name=form_name,
            description=form_description,
            form_type='custom_form',
            status='active' if activate else 'draft',
            sync_to_kobo=True,
            require_gps_location=form_data.get('gfsurveys__Gps_Location_Enabled__c', False),
            created_by=user
        )

        self.stdout.write(self.style.SUCCESS(f'  Created form: {form_name}'))

        # Import questions/fields
        questions = data.get('Questions', [])
        # Try both 'Options' (Salesforce) and 'Answers' (legacy) for choices
        options = data.get('Options', []) or data.get('Answers', [])

        # Build options/choices lookup by question ID
        answers_by_question = {}
        for option in options:
            q_id = option.get('gfsurveys__Question__c')
            if q_id not in answers_by_question:
                answers_by_question[q_id] = []

            # Get the value - prefer 'Name' but sometimes it's a Salesforce ID
            value = option.get('Name', '')
            label = option.get('gfsurveys__Caption__c', value)

            # If Name looks like a Salesforce ID (starts with a0), use caption as value too
            if value and value.startswith('a0') and len(value) > 10:
                # Create a slug from the label
                value = label.lower().replace(' ', '_').replace('-', '_')[:50]

            answers_by_question[q_id].append({
                'value': value,
                'label': label,
                'position': option.get('gfsurveys__Position__c', 0)
            })

        # Sort questions by position
        questions.sort(key=lambda q: q.get('gfsurveys__Position__c', 0))

        field_count = 0
        for idx, question in enumerate(questions):
            field = self.create_field_from_question(
                form_template, question, answers_by_question, idx
            )
            if field:
                field_count += 1

        self.stdout.write(f'  Imported {field_count} fields')

    def create_field_from_question(self, form_template, question, answers_by_question, order):
        """Create a FormField from a question object"""
        q_type = question.get('gfsurveys__Type__c', 'text-short')
        q_name = question.get('Name', f'field_{order}')
        q_label = question.get('gfsurveys__Caption__c', q_name)
        q_required = question.get('gfsurveys__Required__c', False)
        q_hint = question.get('gfsurveys__Hint__c', '')
        q_id = question.get('Id')

        # Map field type
        field_type = self.TYPE_MAP.get(q_type, 'text')

        # Get choices if applicable
        choices = []
        if q_id in answers_by_question:
            raw_choices = answers_by_question[q_id]
            raw_choices.sort(key=lambda c: c.get('position', 0))
            choices = [{'value': c['value'], 'label': c['label']} for c in raw_choices]

        # Get validation constraints
        min_value = question.get('gfsurveys__Minimum__c')
        max_value = question.get('gfsurveys__Maximum__c')
        min_length = question.get('gfsurveys__MinLength__c')
        max_length = question.get('gfsurveys__MaxLength__c')

        try:
            field = FormField.objects.create(
                form_template=form_template,
                field_name=q_name,
                field_label=q_label,
                field_type=field_type,
                required=q_required,
                help_text=q_hint,
                choices=choices if choices else [],
                min_value=min_value,
                max_value=max_value,
                min_length=min_length,
                max_length=max_length,
                order=order
            )
            return field
        except Exception as e:
            self.stderr.write(f'    Error creating field {q_name}: {e}')
            return None
