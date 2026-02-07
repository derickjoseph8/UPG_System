"""
Django management command to create a VE API key.
Usage: python manage.py create_ve_api_key --name "VE Data Hub"
"""
from django.core.management.base import BaseCommand
from ve_reporting.models import VEApiKey


class Command(BaseCommand):
    help = 'Create a new VE API key for Village Enterprise Data Hub access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            type=str,
            default='VE Data Hub Access Key',
            help='Name for the API key'
        )
        parser.add_argument(
            '--expires-in-days',
            type=int,
            default=None,
            help='Number of days until the key expires (default: never)'
        )

    def handle(self, *args, **options):
        from datetime import timedelta
        from django.utils import timezone

        name = options['name']
        expires_in_days = options['expires_in_days']

        # Generate the key
        full_key, key_hash, key_prefix = VEApiKey.generate_key()

        # Calculate expiry
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timedelta(days=expires_in_days)

        # Create the key record
        api_key = VEApiKey.objects.create(
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix[:12],
            scopes=["ve-reporting:read"],
            expires_at=expires_at
        )

        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS(f'VE API Key created for Kenya MIS!'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'Key Name: {api_key.name}')
        self.stdout.write(f'Key Prefix: {api_key.key_prefix}')
        if expires_at:
            self.stdout.write(f'Expires: {expires_at}')
        else:
            self.stdout.write('Expires: Never')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('SAVE THIS KEY - It will only be shown once:'))
        self.stdout.write(self.style.SUCCESS(full_key))
        self.stdout.write('=' * 60)
