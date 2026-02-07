"""
Script to create users from Excel data and add sample data
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'upg_system.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from accounts.models import User
from core.models import Village, SubCounty, Program
from households.models import Household, HouseholdMember, HouseholdProgram
from business_groups.models import BusinessGroup, BusinessGroupMember
from savings_groups.models import BusinessSavingsGroup, BSGMember, SavingsRecord
from training.models import Training, TrainingModule, TrainingAttendance, MentoringVisit, PhoneNudge
from upg_grants.models import SBGrant, PRGrant

# User data from Excel
USERS_DATA = [
    {"name": "Gloria Mutuku", "job_title": "County Liaison Coordinator- VE", "email": "gloriam@villageenterprise.org"},
    {"name": "Michael Asiago", "job_title": "M&E Officer- VE", "email": "michael.asiago@villageenterprise.org"},
    {"name": "Esther Kisavi", "job_title": "Program Manager", "email": "estherk@villageenterprise.org"},
    {"name": "Winfred Musyoka", "job_title": "Program Manager- Makueni", "email": "winfred.musyoka@makueni.go.ke"},
    {"name": "Benjamin Mengo", "job_title": "M&E Officer", "email": "benjamin.mengo@makueni.go.ke"},
    {"name": "Murio Joel", "job_title": "M&E Officer", "email": "joelnguriarita@gmail.com"},
    {"name": "Isaac Ritakou", "job_title": "Director(Executive)", "email": "yeko.isaac@gmail.com"},
    {"name": "Agnes Maza", "job_title": "M&E Officer", "email": "agnes.maza@taitataveta.go.ke"},
    {"name": "Wilfred Shogosho", "job_title": "Mentor Supervisor", "email": "wilfred.shoghosho@taitataveta.go.ke"},
    {"name": "Zipporah Waeni", "job_title": "Mentor Supervisor", "email": "zipporah.waeni@makueni.go.ke"},
    {"name": "Alexander Musembi", "job_title": "ICT Officer", "email": "alexander.musembi@makueni.go.ke"},
    {"name": "Gibran Mwadime", "job_title": "Director ICT", "email": "gibran.mwadime@taitataveta.go.ke"},
    {"name": "Esther Mwanyumba", "job_title": "Program Manager- Taita Taveta", "email": "esthermwangombe@gmail.com"},
    {"name": "Joan Amosong", "job_title": "Mentor Supervisor", "email": "joanamosong@gmail.com"},
    {"name": "Nickson Poghisho", "job_title": "ICT Officer", "email": "poghishonickson@gmail.com"},
    {"name": "Carolyne Cheptoo", "job_title": "Chief communication Officer", "email": "cheptoocarol@gmail.com"},
    {"name": "Clifford Kangero", "job_title": "Chief ICT officer", "email": "ckangero@taitataveta.go.ke"},
    {"name": "Joseph Tonyirwo", "job_title": "Program Manager- West Pokot", "email": "tonyirwow@gmail.com"},
    {"name": "Benjamin Makau", "job_title": "Director ICT", "email": "benjamin.makau@makueni.go.ke"},
    {"name": "Shedrack Mutungi", "job_title": "CECM-Taita Taveta(Executive)", "email": "mutungi.sm@gmail.com"},
    {"name": "Sebastian Kyoni", "job_title": "CECM-Makueni(Executive)", "email": "sebastian.kyoni@gmail.com"},
    {"name": "Lucky Litole", "job_title": "CECM- West Pokot(Executive)", "email": "luckylitole@gmail.com"},
]

# Role mapping
def get_role_from_job_title(job_title):
    job_lower = job_title.lower()
    if 'ict' in job_lower or 'chief ict' in job_lower:
        return 'ict_admin'
    elif 'm&e' in job_lower or 'monitoring' in job_lower:
        return 'me_staff'
    elif 'cecm' in job_lower or 'director' in job_lower and 'executive' in job_lower:
        return 'county_executive'
    elif 'mentor supervisor' in job_lower:
        return 'field_associate'
    elif 'program manager' in job_lower or 'liaison' in job_lower or 'communication' in job_lower:
        return 'field_associate'
    else:
        return 'field_associate'

def create_users():
    """Create users from the Excel data"""
    print("\n=== Creating Users ===")
    default_password = "UPG@2026"
    created_count = 0

    for user_data in USERS_DATA:
        name_parts = user_data['name'].split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        email = user_data['email']
        username = email.split('@')[0].replace('.', '_').lower()
        role = get_role_from_job_title(user_data['job_title'])

        if User.objects.filter(email=email).exists():
            print(f"  User already exists: {email}")
            continue

        user = User.objects.create_user(
            username=username,
            email=email,
            password=default_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True
        )
        print(f"  Created: {user.username} ({user.get_role_display()}) - {email}")
        created_count += 1

    # Update admin user to be ICT admin
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        admin_user.role = 'ict_admin'
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.save()
        print(f"  Updated admin user to ICT Admin role")

    print(f"\nTotal users created: {created_count}")
    print(f"Default password for all users: {default_password}")
    return created_count

def create_sample_data():
    """Create sample data for testing"""
    print("\n=== Creating Sample Data ===")

    # Get or create counties/subcounties
    counties = ['Makueni', 'Taita Taveta', 'West Pokot']
    subcounties_data = {
        'Makueni': ['Makueni', 'Kibwezi East', 'Kibwezi West', 'Kilome'],
        'Taita Taveta': ['Taveta', 'Wundanyi', 'Mwatate', 'Voi'],
        'West Pokot': ['Kapenguria', 'Kacheliba', 'Pokot South', 'Sigor']
    }

    # Create subcounties and villages
    print("\n  Creating locations...")
    villages_created = 0
    for county, subcounty_names in subcounties_data.items():
        for sc_name in subcounty_names:
            subcounty, _ = SubCounty.objects.get_or_create(
                name=sc_name,
                defaults={'county': county}
            )
            # Create villages for each subcounty
            for i in range(3):
                village_name = f"{sc_name} Village {i+1}"
                village, created = Village.objects.get_or_create(
                    name=village_name,
                    defaults={
                        'subcounty_obj': subcounty,
                        'county': county,
                        'is_program_area': True
                    }
                )
                if created:
                    villages_created += 1
    print(f"    Villages created: {villages_created}")

    # Create programs
    print("\n  Creating programs...")
    programs_data = [
        {'name': 'UPG Makueni 2024', 'status': 'active', 'target_households': 500, 'target_villages': 20},
        {'name': 'UPG Taita Taveta 2024', 'status': 'active', 'target_households': 400, 'target_villages': 15},
        {'name': 'UPG West Pokot 2024', 'status': 'active', 'target_households': 300, 'target_villages': 12},
    ]
    programs = []
    for prog_data in programs_data:
        program, created = Program.objects.get_or_create(
            name=prog_data['name'],
            defaults={
                'status': prog_data['status'],
                'target_households': prog_data['target_households'],
                'target_villages': prog_data['target_villages'],
                'start_date': timezone.now().date() - timedelta(days=180),
                'end_date': timezone.now().date() + timedelta(days=365),
            }
        )
        programs.append(program)
        if created:
            print(f"    Created program: {program.name}")

    # Create households
    print("\n  Creating households...")
    villages = list(Village.objects.all())
    households_created = 0
    first_names = ['John', 'Mary', 'Peter', 'Grace', 'James', 'Sarah', 'David', 'Ruth', 'Joseph', 'Esther',
                   'Michael', 'Rebecca', 'Daniel', 'Hannah', 'Samuel', 'Naomi', 'Benjamin', 'Leah', 'Isaac', 'Rachel']
    last_names = ['Mwangi', 'Ochieng', 'Kamau', 'Wanjiku', 'Otieno', 'Njeri', 'Kiprop', 'Chebet', 'Mutua', 'Muthoni',
                  'Kibet', 'Wambui', 'Korir', 'Achieng', 'Kiptoo', 'Njoroge', 'Sang', 'Nyambura', 'Rono', 'Waithera']

    for i in range(100):
        village = random.choice(villages)
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)

        household, created = Household.objects.get_or_create(
            name=f"{first_name} {last_name} Household",
            defaults={
                'head_name': f"{first_name} {last_name}",
                'head_gender': random.choice(['male', 'female']),
                'phone_number': f"07{random.randint(10000000, 99999999)}",
                'village': village,
                'national_id': f"{random.randint(10000000, 99999999)}",
                'status': random.choice(['active', 'active', 'active', 'graduated', 'inactive']),
                'household_size': random.randint(2, 8),
                'poverty_score': random.uniform(0, 100),
            }
        )
        if created:
            households_created += 1
            # Create household members
            for j in range(random.randint(1, 4)):
                HouseholdMember.objects.create(
                    household=household,
                    name=f"{random.choice(first_names)} {last_name}",
                    relationship=random.choice(['spouse', 'child', 'parent', 'sibling']),
                    gender=random.choice(['male', 'female']),
                    age=random.randint(5, 65)
                )

            # Enroll in a program
            program = random.choice(programs)
            HouseholdProgram.objects.get_or_create(
                household=household,
                program=program,
                defaults={
                    'enrollment_date': timezone.now().date() - timedelta(days=random.randint(30, 180)),
                    'status': 'active'
                }
            )

    print(f"    Households created: {households_created}")

    # Create business groups
    print("\n  Creating business groups...")
    business_types = ['Poultry Farming', 'Vegetable Growing', 'Tailoring', 'Boda Boda', 'Retail Shop',
                      'Goat Rearing', 'Bee Keeping', 'Charcoal Business', 'Food Vending', 'Cereal Trading']
    bg_created = 0
    households = list(Household.objects.filter(status='active')[:60])

    for i in range(20):
        village = random.choice(villages)
        business_type = random.choice(business_types)

        bg, created = BusinessGroup.objects.get_or_create(
            name=f"{village.name} {business_type} Group",
            defaults={
                'village': village,
                'business_type': business_type,
                'status': random.choice(['active', 'active', 'active', 'graduated']),
                'formation_date': timezone.now().date() - timedelta(days=random.randint(60, 180)),
                'target_members': random.randint(5, 15),
            }
        )
        if created:
            bg_created += 1
            # Add members
            for household in random.sample(households, min(random.randint(3, 8), len(households))):
                BusinessGroupMember.objects.get_or_create(
                    business_group=bg,
                    household=household,
                    defaults={
                        'role': random.choice(['member', 'member', 'member', 'chairperson', 'treasurer', 'secretary']),
                        'join_date': timezone.now().date() - timedelta(days=random.randint(30, 150))
                    }
                )

    print(f"    Business groups created: {bg_created}")

    # Create savings groups
    print("\n  Creating savings groups...")
    bsgs = list(BusinessGroup.objects.filter(status='active'))
    savings_created = 0

    for bg in bsgs[:15]:
        bsg, created = BusinessSavingsGroup.objects.get_or_create(
            name=f"{bg.name} Savings",
            defaults={
                'status': 'active',
                'savings_frequency': random.choice(['weekly', 'bi_weekly', 'monthly']),
                'contribution_amount': Decimal(random.choice([100, 200, 500, 1000])),
                'formation_date': timezone.now().date() - timedelta(days=random.randint(30, 120)),
            }
        )
        if created:
            savings_created += 1
            bsg.business_groups.add(bg)

            # Add members from business group
            for bgm in bg.members.all()[:8]:
                BSGMember.objects.get_or_create(
                    savings_group=bsg,
                    household=bgm.household,
                    defaults={
                        'role': random.choice(['member', 'member', 'member', 'chairperson', 'treasurer']),
                        'shares': random.randint(1, 5)
                    }
                )

            # Add savings records
            for week in range(8):
                SavingsRecord.objects.create(
                    savings_group=bsg,
                    amount=bsg.contribution_amount * bsg.members.count() * Decimal(random.uniform(0.7, 1.0)),
                    record_date=timezone.now().date() - timedelta(weeks=week),
                    notes=f"Week {8-week} contribution"
                )

    print(f"    Savings groups created: {savings_created}")

    # Create training modules and sessions
    print("\n  Creating training data...")
    modules_data = [
        'Business Skills', 'Financial Literacy', 'Savings Management',
        'Market Linkages', 'Group Dynamics', 'Record Keeping'
    ]

    for mod_name in modules_data:
        TrainingModule.objects.get_or_create(
            name=mod_name,
            defaults={
                'description': f"Training module covering {mod_name.lower()}",
                'duration_hours': random.randint(2, 6)
            }
        )

    modules = list(TrainingModule.objects.all())
    mentors = list(User.objects.filter(role__in=['mentor', 'field_associate']))
    trainings_created = 0

    for i in range(15):
        module = random.choice(modules)
        village = random.choice(villages)
        mentor = random.choice(mentors) if mentors else None

        training, created = Training.objects.get_or_create(
            title=f"{module.name} - {village.name}",
            defaults={
                'module': module,
                'village': village,
                'assigned_mentor': mentor,
                'scheduled_date': timezone.now() - timedelta(days=random.randint(-30, 60)),
                'status': random.choice(['completed', 'completed', 'scheduled', 'in_progress']),
                'duration_hours': random.randint(2, 4),
                'location': f"{village.name} Community Center"
            }
        )
        if created:
            trainings_created += 1
            # Add attendance
            village_households = Household.objects.filter(village=village)[:10]
            for hh in village_households:
                TrainingAttendance.objects.get_or_create(
                    training=training,
                    household=hh,
                    defaults={
                        'attended': random.choice([True, True, True, False]),
                    }
                )

    print(f"    Training sessions created: {trainings_created}")

    # Create mentoring visits
    print("\n  Creating mentoring visits...")
    visits_created = 0
    households = list(Household.objects.filter(status='active')[:40])

    for i in range(30):
        household = random.choice(households)
        mentor = random.choice(mentors) if mentors else None

        visit = MentoringVisit.objects.create(
            household=household,
            mentor=mentor,
            visit_date=timezone.now() - timedelta(days=random.randint(1, 60)),
            visit_type=random.choice(['initial', 'follow_up', 'business_check', 'savings_check']),
            status=random.choice(['completed', 'completed', 'scheduled']),
            notes=f"Regular mentoring visit to {household.name}",
            duration_minutes=random.randint(30, 90),
            completed=random.choice([True, True, False])
        )
        visits_created += 1

    print(f"    Mentoring visits created: {visits_created}")

    # Create phone nudges
    print("\n  Creating phone nudges...")
    nudges_created = 0

    for i in range(25):
        household = random.choice(households)
        mentor = random.choice(mentors) if mentors else None

        PhoneNudge.objects.create(
            household=household,
            mentor=mentor,
            call_date=timezone.now() - timedelta(days=random.randint(1, 45)),
            nudge_type=random.choice(['savings_reminder', 'meeting_reminder', 'training_reminder', 'general_check_in']),
            successful_contact=random.choice([True, True, True, False]),
            duration_minutes=random.randint(2, 15),
            notes=f"Phone nudge to {household.name}"
        )
        nudges_created += 1

    print(f"    Phone nudges created: {nudges_created}")

    # Create grants
    print("\n  Creating grants...")
    grants_created = 0
    business_groups = list(BusinessGroup.objects.filter(status='active'))

    for bg in business_groups[:12]:
        # SB Grant
        SBGrant.objects.get_or_create(
            business_group=bg,
            defaults={
                'status': random.choice(['approved', 'approved', 'disbursed', 'pending']),
                'amount': Decimal(random.choice([15000, 20000, 25000, 30000])),
                'purpose': f"Start-up capital for {bg.business_type}",
                'application_date': timezone.now().date() - timedelta(days=random.randint(30, 90)),
            }
        )
        grants_created += 1

        # PR Grant for some
        if random.choice([True, False]):
            PRGrant.objects.get_or_create(
                business_group=bg,
                defaults={
                    'status': random.choice(['approved', 'pending', 'disbursed']),
                    'amount': Decimal(random.choice([10000, 15000, 20000])),
                    'purpose': f"Poverty reduction support for {bg.name}",
                    'application_date': timezone.now().date() - timedelta(days=random.randint(15, 60)),
                }
            )
            grants_created += 1

    print(f"    Grants created: {grants_created}")

    print("\n=== Sample Data Creation Complete ===")

if __name__ == '__main__':
    print("=" * 60)
    print("UPG System - User Creation and Sample Data Setup")
    print("=" * 60)

    create_users()
    create_sample_data()

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
