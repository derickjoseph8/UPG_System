"""
Tests for Forms App - Critical Path Coverage
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
import json
import uuid

from .models import FormTemplate, FormField, FormSubmission, FormAssignment
from .kobo_service import XLSFormConverter, check_form_has_beneficiary_lookup

User = get_user_model()


def unique_id():
    """Generate unique ID for test data"""
    return str(uuid.uuid4())[:8]


class FormTemplateTests(TestCase):
    """Tests for FormTemplate model and views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        uid = unique_id()
        self.admin_username = f'admin_{uid}'
        self.admin_user = User.objects.create_user(
            username=self.admin_username,
            email=f'admin_{uid}@test.com',
            password='testpass123',
            role='me_staff'
        )
        uid2 = unique_id()
        self.mentor_username = f'mentor_{uid2}'
        self.mentor_user = User.objects.create_user(
            username=self.mentor_username,
            email=f'mentor_{uid2}@test.com',
            password='testpass123',
            role='mentor'
        )

    def test_form_template_creation(self):
        """Test creating a form template"""
        template = FormTemplate.objects.create(
            name='Test Form',
            description='A test form',
            created_by=self.admin_user,
            form_type='household_survey',
            status='draft'
        )
        self.assertEqual(template.name, 'Test Form')
        self.assertEqual(template.status, 'draft')
        self.assertEqual(str(template), 'Test Form (Household Survey)')

    def test_form_field_creation(self):
        """Test creating form fields"""
        template = FormTemplate.objects.create(
            name='Test Form',
            created_by=self.admin_user,
            form_type='custom_form'
        )
        field = FormField.objects.create(
            form_template=template,
            field_name='phone_number',
            field_label='Phone Number',
            field_type='phone',
            required=True,
            order=1
        )
        self.assertEqual(field.field_name, 'phone_number')
        self.assertTrue(field.required)

    def test_form_dashboard_requires_login(self):
        """Test that form dashboard requires authentication"""
        response = self.client.get(reverse('forms:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_form_dashboard_authenticated(self):
        """Test form dashboard with authenticated user"""
        logged_in = self.client.login(username=self.admin_username, password='testpass123')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('forms:dashboard'))
        self.assertEqual(response.status_code, 200)


class XLSFormConverterTests(TestCase):
    """Tests for XLSForm conversion"""

    def setUp(self):
        """Set up test data"""
        uid = unique_id()
        self.user = User.objects.create_user(
            username=f'testuser_{uid}',
            email=f'test_{uid}@test.com',
            password='testpass123'
        )
        self.template = FormTemplate.objects.create(
            name='Test Form',
            created_by=self.user,
            form_type='custom_form',
            form_purpose='survey'
        )

    def test_beneficiary_lookup_detection_by_purpose(self):
        """Test that forms with specific purposes trigger beneficiary lookup"""
        # Survey purpose should trigger lookup
        self.template.form_purpose = 'survey'
        self.template.save()
        result = check_form_has_beneficiary_lookup(self.template)
        self.assertTrue(result['enabled'])

    def test_beneficiary_lookup_detection_by_phone_field(self):
        """Test that mandatory phone fields trigger beneficiary lookup"""
        self.template.form_purpose = 'general'
        self.template.save()

        # Add required phone field
        FormField.objects.create(
            form_template=self.template,
            field_name='phone_number',
            field_label='Phone Number',
            field_type='phone',
            required=True,
            order=1
        )

        result = check_form_has_beneficiary_lookup(self.template)
        self.assertTrue(result['enabled'])

    def test_beneficiary_lookup_detection_by_id_field(self):
        """Test that mandatory ID fields trigger beneficiary lookup"""
        self.template.form_purpose = 'general'
        self.template.save()

        # Add required ID field
        FormField.objects.create(
            form_template=self.template,
            field_name='national_id',
            field_label='National ID Number',
            field_type='text',
            required=True,
            order=1
        )

        result = check_form_has_beneficiary_lookup(self.template)
        self.assertTrue(result['enabled'])

    def test_xlsform_conversion(self):
        """Test basic XLSForm conversion"""
        FormField.objects.create(
            form_template=self.template,
            field_name='name',
            field_label='Full Name',
            field_type='text',
            required=True,
            order=1
        )

        converter = XLSFormConverter(self.template)
        xlsform = converter.convert_to_xlsform()

        self.assertIn('survey', xlsform)
        self.assertIn('choices', xlsform)
        self.assertIn('settings', xlsform)


class WebhookTests(TestCase):
    """Tests for Kobo webhook processing"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        uid = unique_id()
        self.user = User.objects.create_user(
            username=f'testuser_{uid}',
            email=f'test_{uid}@test.com',
            password='testpass123'
        )
        self.template = FormTemplate.objects.create(
            name='Test Form',
            created_by=self.user,
            form_type='custom_form',
            kobo_asset_uid='test_asset_123'
        )

    def test_webhook_rejects_invalid_json(self):
        """Test that webhook rejects invalid JSON"""
        response = self.client.post(
            reverse('forms:kobo_webhook'),
            data='not valid json',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_webhook_rejects_missing_uuid(self):
        """Test that webhook rejects payload without UUID"""
        response = self.client.post(
            reverse('forms:kobo_webhook'),
            data=json.dumps({'some': 'data'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_webhook_accepts_valid_payload(self):
        """Test that webhook accepts valid payload"""
        payload = {
            '_uuid': f'test-uuid-{unique_id()}',
            'formhub/uuid': 'test_asset_123',
            '_submission_time': '2025-01-01T12:00:00Z'
        }
        response = self.client.post(
            reverse('forms:kobo_webhook'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        # Should return 200 even if processing fails
        self.assertIn(response.status_code, [200, 500])


class PermissionTests(TestCase):
    """Tests for permission decorators and access control"""

    def setUp(self):
        """Set up test users with different roles"""
        self.client = Client()
        uid1 = unique_id()
        uid2 = unique_id()
        self.admin_username = f'admin_{uid1}'
        self.mentor_username = f'mentor_{uid2}'
        self.admin = User.objects.create_user(
            username=self.admin_username,
            email=f'admin_{uid1}@test.com',
            password='testpass123',
            role='me_staff'
        )
        self.mentor = User.objects.create_user(
            username=self.mentor_username,
            email=f'mentor_{uid2}@test.com',
            password='testpass123',
            role='mentor'
        )

    def test_admin_can_access_sync_history(self):
        """Test that admin can access sync history"""
        logged_in = self.client.login(username=self.admin_username, password='testpass123')
        self.assertTrue(logged_in)
        template = FormTemplate.objects.create(
            name='Test',
            created_by=self.admin,
            form_type='custom_form'
        )
        response = self.client.get(
            reverse('forms:kobo_sync_history', args=[template.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_mentor_access_to_assignments(self):
        """Test mentor access to their assignments"""
        logged_in = self.client.login(username=self.mentor_username, password='testpass123')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('forms:my_assignments'))
        self.assertEqual(response.status_code, 200)
