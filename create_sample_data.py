"""
Create comprehensive sample data for UPG System
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')
django.setup()

from django.utils import timezone
from datetime import date, timedelta
import random

from core.models import County, SubCounty, Village, Program
from households.models import Household, HouseholdProgram, HouseholdMember, UPGMilestone
from business_groups.models import BusinessGroup
from training.models import Training, MentoringVisit, PhoneNudge
from savings_groups.models import BusinessSavingsGroup
from accounts.models import User

print('=== Creating Comprehensive Sample Data ===')
print()

# 1. Create more villages
print('1. Creating more Villages...')
villages_by_subcounty = {
    'Makueni': ['Kathonzweni', 'Nziu', 'Mavindini', 'Mbooni', 'Kalawa', 'Nguu', 'Kilungu'],
    'Kibwezi West': ['Emali', 'Mikuyuni', 'Kiundwani', 'Utithi', 'Mukaoni'],
    'Kibwezi East': ['Masue', 'Kasikeu', 'Kiio', 'Muthingiini'],
    'Taveta': ['Chala', 'Jipe', 'Lumi', 'Grogan', 'Mata'],
    'Wundanyi': ['Werugha', 'Mwanda Wundanyi', 'Mbale', 'Ngerenyi', 'Chawia'],
    'Mwatate': ['Mghambonyi', 'Choke', 'Wusi', 'Kishushe', 'Lushangonyi'],
}

villages_created = 0
for sc_name, village_names in villages_by_subcounty.items():
    try:
        sc = SubCounty.objects.get(name=sc_name)
        for v_name in village_names:
            village, created = Village.objects.get_or_create(
                name=v_name,
                defaults={
                    'subcounty_obj': sc,
                    'is_program_area': True,
                    'saturation': random.randint(20, 80)
                }
            )
            if created:
                villages_created += 1
    except SubCounty.DoesNotExist:
        pass
print(f'  Created {villages_created} new villages. Total: {Village.objects.count()}')

# 2. Create more households
print('2. Creating more Households...')
first_names_m = ['James', 'John', 'Peter', 'David', 'Samuel', 'Joseph', 'Daniel', 'Moses', 'Paul', 'Stephen', 'Michael', 'Patrick', 'George', 'Francis', 'Charles']
first_names_f = ['Mary', 'Susan', 'Grace', 'Faith', 'Hope', 'Rose', 'Joyce', 'Sarah', 'Elizabeth', 'Martha', 'Agnes', 'Catherine', 'Jane', 'Eunice', 'Beatrice']
last_names = ['Mwangi', 'Kamau', 'Ochieng', 'Wanjiku', 'Njoroge', 'Achieng', 'Mutua', 'Muthoni', 'Kiprono', 'Chebet', 'Koech', 'Wambui', 'Kiplagat', 'Jepkosgei', 'Rotich', 'Kipchoge', 'Nderitu', 'Kariuki', 'Otieno', 'Wekesa']

villages = list(Village.objects.all())
households_created = 0
for village in villages:
    existing = Household.objects.filter(village=village).count()
    needed = max(0, 5 - existing)
    for i in range(needed):
        gender = random.choice(['M', 'F'])
        first = random.choice(first_names_m if gender == 'M' else first_names_f)
        last = random.choice(last_names)
        try:
            hh, created = Household.objects.get_or_create(
                head_first_name=first,
                head_last_name=last,
                village=village,
                defaults={
                    'phone_number': f'07{random.randint(10000000, 99999999)}',
                    'national_id': f'{random.randint(10000000, 99999999)}',
                    'head_gender': gender,
                    'consent_given': True,
                    'monthly_income': random.randint(1000, 10000),
                }
            )
            if created:
                households_created += 1
        except:
            pass
print(f'  Created {households_created} new households. Total: {Household.objects.count()}')

# 3. Create household members
print('3. Creating Household Members...')
relationships = ['spouse', 'child', 'parent', 'sibling', 'grandchild', 'other']
members_created = 0
for hh in Household.objects.all()[:100]:
    existing = HouseholdMember.objects.filter(household=hh).count()
    if existing < 2:
        for i in range(random.randint(2, 5)):
            gender = random.choice(['M', 'F'])
            first = random.choice(first_names_m if gender == 'M' else first_names_f)
            try:
                member, created = HouseholdMember.objects.get_or_create(
                    household=hh,
                    first_name=first,
                    defaults={
                        'last_name': hh.head_last_name,
                        'relationship': random.choice(relationships),
                        'gender': gender,
                        'age': random.randint(5, 70),
                    }
                )
                if created:
                    members_created += 1
            except:
                pass
print(f'  Created {members_created} household members. Total: {HouseholdMember.objects.count()}')

# 4. Create Business Groups
print('4. Creating Business Groups...')
program = Program.objects.first()
bg_prefixes = ['Sunrise', 'Unity', 'Hope', 'Progress', 'Victory', 'Future', 'Success', 'Prosperity', 'Harmony', 'Growth', 'Vision', 'Faith', 'New Dawn', 'Joyful', 'Blessed']
bg_types = [('poultry', 'Poultry'), ('crop_farming', 'Farming'), ('retail', 'Retail'), ('tailoring', 'Tailoring'), ('food_processing', 'Food'), ('livestock', 'Livestock')]

bg_created = 0
for village in villages[:30]:
    for i in range(2):
        bg_type, bg_type_name = random.choice(bg_types)
        name = f'{random.choice(bg_prefixes)} {bg_type_name} - {village.name}'
        try:
            bg, created = BusinessGroup.objects.get_or_create(
                name=name[:100],
                defaults={
                    'program': program,
                    'group_size': random.randint(5, 15),
                    'business_type': bg_type,
                    'participation_status': random.choice(['active', 'active', 'active', 'inactive']),
                    'current_business_health': random.choice(['thriving', 'stable', 'struggling']),
                    'formation_date': date(2025, 1, 1) + timedelta(days=random.randint(0, 365)),
                }
            )
            if created:
                bg_created += 1
        except:
            pass
print(f'  Created {bg_created} business groups. Total: {BusinessGroup.objects.count()}')

# 5. Create Trainings
print('5. Creating Trainings...')
training_modules = [
    ('Business Basics', 'Introduction to business fundamentals'),
    ('Financial Literacy', 'Money management and savings'),
    ('Entrepreneurship', 'Starting and growing your business'),
    ('Marketing Skills', 'How to market your products'),
    ('Record Keeping', 'Tracking income and expenses'),
    ('Group Dynamics', 'Working together effectively'),
    ('Customer Service', 'Serving customers well'),
    ('Product Quality', 'Ensuring quality products'),
    ('Leadership Skills', 'Leading your group'),
    ('Conflict Resolution', 'Managing disagreements'),
]

mentors = list(User.objects.filter(role='mentor'))
if not mentors:
    mentors = list(User.objects.filter(role='field_associate'))

trainings_created = 0
for module_name, desc in training_modules:
    for cycle in ['2025-Q1', '2025-Q2', '2025-Q3', '2025-Q4', '2026-Q1']:
        name = f'{module_name} - {cycle}'
        start = date(2025, 1, 1) + timedelta(days=random.randint(0, 400))
        try:
            training, created = Training.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'status': random.choice(['completed', 'completed', 'active', 'planned']),
                    'start_date': start,
                    'end_date': start + timedelta(days=random.randint(1, 7)),
                    'duration_hours': random.randint(2, 8),
                    'location': random.choice(['Community Hall', 'Village Center', 'School', 'Church']),
                    'assigned_mentor': random.choice(mentors) if mentors else None,
                }
            )
            if created:
                trainings_created += 1
        except:
            pass
print(f'  Created {trainings_created} trainings. Total: {Training.objects.count()}')

# 6. Create Mentoring Visits
print('6. Creating Mentoring Visits...')
visits_created = 0
households = list(Household.objects.all()[:100])
for household in households:
    for i in range(random.randint(1, 3)):
        visit_date = timezone.now() - timedelta(days=random.randint(1, 60))
        try:
            visit, created = MentoringVisit.objects.get_or_create(
                household=household,
                visit_date=visit_date,
                defaults={
                    'mentor': random.choice(mentors) if mentors else None,
                    'visit_type': random.choice(['regular', 'follow_up', 'assessment']),
                    'duration_minutes': random.randint(30, 120),
                    'notes': f'Visit to {household.name}. Discussed progress and challenges.',
                    'completed': random.choice([True, True, True, False]),
                }
            )
            if created:
                visits_created += 1
        except:
            pass
print(f'  Created {visits_created} mentoring visits. Total: {MentoringVisit.objects.count()}')

# 7. Create Phone Nudges
print('7. Creating Phone Nudges...')
nudges_created = 0
for household in households[:50]:
    for i in range(random.randint(1, 2)):
        call_date = timezone.now() - timedelta(days=random.randint(1, 45))
        try:
            nudge, created = PhoneNudge.objects.get_or_create(
                household=household,
                call_date=call_date,
                defaults={
                    'mentor': random.choice(mentors) if mentors else None,
                    'purpose': random.choice(['reminder', 'follow_up', 'support', 'check_in']),
                    'duration_minutes': random.randint(5, 30),
                    'notes': f'Phone call with {household.name}.',
                    'outcome': random.choice(['successful', 'no_answer', 'callback_requested']),
                }
            )
            if created:
                nudges_created += 1
        except:
            pass
print(f'  Created {nudges_created} phone nudges. Total: {PhoneNudge.objects.count()}')

# 8. Create Savings Groups
print('8. Creating Savings Groups...')
business_groups = list(BusinessGroup.objects.filter(participation_status='active')[:30])
sg_created = 0
for bg in business_groups:
    try:
        sg, created = BusinessSavingsGroup.objects.get_or_create(
            name=f'{bg.name} Savings'[:100],
            defaults={
                'target_amount': random.randint(50000, 200000),
                'current_amount': random.randint(10000, 100000),
                'savings_frequency': random.choice(['weekly', 'biweekly', 'monthly']),
                'is_active': True,
            }
        )
        if created:
            sg.business_groups.add(bg)
            sg_created += 1
    except:
        pass
print(f'  Created {sg_created} savings groups. Total: {BusinessSavingsGroup.objects.count()}')

# 9. Create Household Program enrollments
print('9. Creating Program Enrollments...')
enrollments_created = 0
for household in Household.objects.all()[:100]:
    try:
        hp, created = HouseholdProgram.objects.get_or_create(
            household=household,
            program=program,
            defaults={
                'enrollment_date': date(2025, 1, 1) + timedelta(days=random.randint(0, 200)),
                'participation_status': random.choice(['active', 'active', 'active', 'graduated', 'dropout']),
            }
        )
        if created:
            enrollments_created += 1
    except:
        pass
print(f'  Created {enrollments_created} program enrollments. Total: {HouseholdProgram.objects.count()}')

# 10. Create UPG Milestones
print('10. Creating UPG Milestones...')
milestones_created = 0
for hp in HouseholdProgram.objects.all()[:50]:
    for month in range(1, 13):
        milestone_key = f'month_{month}'
        status = 'completed' if month <= random.randint(3, 10) else random.choice(['in_progress', 'not_started'])
        try:
            ms, created = UPGMilestone.objects.get_or_create(
                household_program=hp,
                milestone=milestone_key,
                defaults={
                    'status': status,
                    'target_date': hp.enrollment_date + timedelta(days=30*month) if hp.enrollment_date else None,
                    'completion_date': hp.enrollment_date + timedelta(days=30*month - random.randint(1, 10)) if status == 'completed' and hp.enrollment_date else None,
                }
            )
            if created:
                milestones_created += 1
        except:
            pass
print(f'  Created {milestones_created} milestones. Total: {UPGMilestone.objects.count()}')

# Summary
print()
print('=== Sample Data Summary ===')
print(f'Counties: {County.objects.count()}')
print(f'SubCounties: {SubCounty.objects.count()}')
print(f'Villages: {Village.objects.count()}')
print(f'Households: {Household.objects.count()}')
print(f'Household Members: {HouseholdMember.objects.count()}')
print(f'Business Groups: {BusinessGroup.objects.count()}')
print(f'Savings Groups: {BusinessSavingsGroup.objects.count()}')
print(f'Trainings: {Training.objects.count()}')
print(f'Mentoring Visits: {MentoringVisit.objects.count()}')
print(f'Phone Nudges: {PhoneNudge.objects.count()}')
print(f'Program Enrollments: {HouseholdProgram.objects.count()}')
print(f'UPG Milestones: {UPGMilestone.objects.count()}')
print()
print('Sample data creation complete!')
