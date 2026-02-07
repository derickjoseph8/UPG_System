"""
Create sample mentors with village assignments and FA-Mentor relationships
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')
django.setup()

from django.db import transaction
from accounts.models import User, UserProfile
from core.models import Village
import random

print('=== Creating Sample Mentors ===')
print()

# Check existing users
print('Existing Users:')
for u in User.objects.all():
    print(f'  {u.username} - {u.role}')

print()
print(f'Total Villages: {Village.objects.count()}')

# Get or create Field Associates first
fa_data = [
    ('fa_makueni', 'James', 'Mutua', 'james.mutua@upg.go.ke'),
    ('fa_kibwezi', 'Grace', 'Wanjiku', 'grace.wanjiku@upg.go.ke'),
    ('fa_taita', 'Peter', 'Ochieng', 'peter.ochieng@upg.go.ke'),
]

print()
print('Creating Field Associates...')
field_associates = []
for username, first, last, email in fa_data:
    fa, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first,
            'last_name': last,
            'email': email,
            'role': 'field_associate',
            'is_active': True,
        }
    )
    if created:
        fa.set_password('upg2025')
        fa.save()
        print(f'  Created FA: {fa.get_full_name()}')
    else:
        # Ensure role is field_associate
        if fa.role != 'field_associate':
            fa.role = 'field_associate'
            fa.save()
        print(f'  FA exists: {fa.get_full_name()}')
    field_associates.append(fa)

# Create UserProfile for FAs if not exists
for fa in field_associates:
    profile, created = UserProfile.objects.get_or_create(user=fa)
    if created:
        print(f'  Created profile for {fa.username}')

# Mentor data
mentor_data = [
    ('mentor_mary', 'Mary', 'Wambui'),
    ('mentor_john', 'John', 'Kamau'),
    ('mentor_faith', 'Faith', 'Achieng'),
    ('mentor_david', 'David', 'Kipchoge'),
    ('mentor_susan', 'Susan', 'Chebet'),
    ('mentor_joseph', 'Joseph', 'Nderitu'),
    ('mentor_rose', 'Rose', 'Muthoni'),
    ('mentor_samuel', 'Samuel', 'Koech'),
    ('mentor_grace', 'Grace', 'Jepkosgei'),
    ('mentor_michael', 'Michael', 'Rotich'),
    ('mentor_jane', 'Jane', 'Kariuki'),
    ('mentor_paul', 'Paul', 'Otieno'),
    ('mentor_beatrice', 'Beatrice', 'Wekesa'),
    ('mentor_daniel', 'Daniel', 'Kiplagat'),
    ('mentor_agnes', 'Agnes', 'Wanjiru'),
]

print()
print('Creating Mentors...')
mentors = []
for username, first, last in mentor_data:
    email = f'{username}@upg.go.ke'
    mentor, created = User.objects.get_or_create(
        username=username,
        defaults={
            'first_name': first,
            'last_name': last,
            'email': email,
            'role': 'mentor',
            'is_active': True,
        }
    )
    if created:
        mentor.set_password('upg2025')
        mentor.save()
        print(f'  Created Mentor: {mentor.get_full_name()}')
    else:
        print(f'  Mentor exists: {mentor.get_full_name()}')
    mentors.append(mentor)

# Assign villages and supervisors
villages = list(Village.objects.all())
print()
print(f'Assigning {len(villages)} villages to mentors...')

if villages:
    # Distribute villages among mentors (3-5 villages per mentor)
    random.shuffle(villages)
    village_idx = 0

    for i, mentor in enumerate(mentors):
        # Get or create profile
        profile, _ = UserProfile.objects.get_or_create(user=mentor)

        # Assign supervisor (Field Associate)
        # Rotate through FAs
        supervisor = field_associates[i % len(field_associates)]
        profile.supervisor = supervisor
        profile.save()

        # Assign 3-5 villages
        num_villages = min(random.randint(3, 5), len(villages) - village_idx)
        if num_villages > 0:
            assigned_villages = villages[village_idx:village_idx + num_villages]
            profile.assigned_villages.set(assigned_villages)
            village_idx += num_villages
            print(f'  {mentor.get_full_name()}: {num_villages} villages, Supervisor: {supervisor.get_full_name()}')

        # Wrap around if we run out of villages
        if village_idx >= len(villages):
            village_idx = 0
            random.shuffle(villages)

# Summary
print()
print('=== Summary ===')
print(f'Field Associates: {User.objects.filter(role="field_associate").count()}')
print(f'Mentors: {User.objects.filter(role="mentor").count()}')

print()
print('FA -> Mentor Relationships:')
for fa in field_associates:
    try:
        supervised = User.objects.filter(role='mentor', profile__supervisor=fa)
        print(f'  {fa.get_full_name()} supervises {supervised.count()} mentors:')
        for m in supervised:
            village_count = m.profile.assigned_villages.count() if hasattr(m, 'profile') else 0
            print(f'    - {m.get_full_name()} ({village_count} villages)')
    except Exception as e:
        print(f'  Error for {fa.username}: {e}')

print()
print('Done!')
