"""
Management command to create UserProfile for all users who don't have one.
Run this after deploying the UserProfile signal to fix existing users.
"""

from django.core.management.base import BaseCommand
from accounts.models import User, UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile for all users who do not have one'

    def handle(self, *args, **options):
        users_without_profile = []

        for user in User.objects.all():
            try:
                # Try to access profile
                profile = user.profile
            except UserProfile.DoesNotExist:
                users_without_profile.append(user)

        if not users_without_profile:
            self.stdout.write(self.style.SUCCESS('All users already have profiles.'))
            return

        self.stdout.write(f'Found {len(users_without_profile)} users without profiles.')

        created_count = 0
        for user in users_without_profile:
            UserProfile.objects.create(user=user)
            created_count += 1
            self.stdout.write(f'  Created profile for: {user.username} ({user.role})')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} user profiles.'))
