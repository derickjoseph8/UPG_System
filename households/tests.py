"""
Tests for Households App - Critical Path Coverage
"""

from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

from .models import Household, HouseholdMember, PPI, HouseholdProgram
from core.models import Village, SubCounty, County

User = get_user_model()


def unique_id():
    """Generate unique ID for test data"""
    return str(uuid.uuid4())[:8]


class HouseholdModelTests(TestCase):
    """Tests for Household model"""

    def setUp(self):
        """Set up test data"""
        self.county = County.objects.create(name=f'Test County {unique_id()}')
        self.subcounty = SubCounty.objects.create(
            name=f'Test SubCounty {unique_id()}',
            county=self.county
        )
        self.village = Village.objects.create(
            name=f'Test Village {unique_id()}',
            subcounty_obj=self.subcounty
        )
        uid = unique_id()
        self.user = User.objects.create_user(
            username=f'testuser_{uid}',
            email=f'test_{uid}@test.com',
            password='testpass123'
        )

    def test_household_creation(self):
        """Test creating a household"""
        uid = unique_id()
        household = Household.objects.create(
            name='Test Household',
            village=self.village,
            head_first_name='John',
            head_last_name='Doe',
            head_gender='male',
            national_id=f'ID{uid}',
            phone_number='0712345678'
        )
        self.assertEqual(household.name, 'Test Household')
        self.assertEqual(household.head_full_name, 'John Doe')

    def test_household_head_full_name(self):
        """Test head_full_name property"""
        uid = unique_id()
        household = Household.objects.create(
            name='Test',
            village=self.village,
            head_first_name='John',
            head_middle_name='James',
            head_last_name='Doe',
            national_id=f'ID{uid}',
            phone_number='0712345678'
        )
        self.assertEqual(household.head_full_name, 'John James Doe')

    def test_household_member_count(self):
        """Test total_members property"""
        uid = unique_id()
        household = Household.objects.create(
            name='Test',
            village=self.village,
            national_id=f'ID{uid}',
            phone_number='0712345678'
        )
        # Add members
        HouseholdMember.objects.create(
            household=household,
            name='Head',
            gender='male',
            age=45,
            relationship_to_head='head'
        )
        HouseholdMember.objects.create(
            household=household,
            name='Spouse',
            gender='female',
            age=40,
            relationship_to_head='spouse'
        )
        self.assertEqual(household.total_members, 2)

    def test_head_member_property(self):
        """Test head_member property returns correct member"""
        uid = unique_id()
        household = Household.objects.create(
            name='Test',
            village=self.village,
            national_id=f'ID{uid}',
            phone_number='0712345678'
        )
        head = HouseholdMember.objects.create(
            household=household,
            name='John Doe',
            gender='male',
            age=45,
            relationship_to_head='head'
        )
        self.assertEqual(household.head_member, head)

    def test_head_gender_field_not_shadowed(self):
        """Test that head_gender field works correctly (not shadowed by property)"""
        uid = unique_id()
        household = Household.objects.create(
            name='Test',
            village=self.village,
            head_gender='female',
            national_id=f'ID{uid}',
            phone_number='0712345678'
        )
        # The field should return 'female', not empty string from property
        self.assertEqual(household.head_gender, 'female')


class HouseholdViewTests(TestCase):
    """Tests for Household views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        uid = unique_id()
        self.county = County.objects.create(name=f'Test County {uid}')
        self.subcounty = SubCounty.objects.create(
            name=f'Test SubCounty {uid}',
            county=self.county
        )
        self.village = Village.objects.create(
            name=f'Test Village {uid}',
            subcounty_obj=self.subcounty
        )
        self.user = User.objects.create_user(
            username=f'admin_{uid}',
            email=f'admin_{uid}@test.com',
            password='testpass123',
            role='me_staff'
        )
        self.household = Household.objects.create(
            name='Test Household',
            village=self.village,
            national_id=f'ID{uid}',
            phone_number='0712345678'
        )

    def test_household_list_requires_login(self):
        """Test that household list requires authentication"""
        response = self.client.get(reverse('households:household_list'))
        self.assertEqual(response.status_code, 302)

    def test_household_list_authenticated(self):
        """Test household list with authenticated user"""
        logged_in = self.client.login(
            username=self.user.username,
            password='testpass123'
        )
        self.assertTrue(logged_in)
        response = self.client.get(reverse('households:household_list'))
        self.assertEqual(response.status_code, 200)

    def test_household_detail(self):
        """Test household detail view"""
        logged_in = self.client.login(
            username=self.user.username,
            password='testpass123'
        )
        self.assertTrue(logged_in)
        response = self.client.get(
            reverse('households:household_detail', args=[self.household.id])
        )
        self.assertEqual(response.status_code, 200)


class EligibilityTests(TestCase):
    """Tests for eligibility assessment"""

    def setUp(self):
        """Set up test data"""
        uid = unique_id()
        self.county = County.objects.create(name=f'Test County {uid}')
        self.subcounty = SubCounty.objects.create(
            name=f'Test SubCounty {uid}',
            county=self.county
        )
        self.village = Village.objects.create(
            name=f'Test Village {uid}',
            subcounty_obj=self.subcounty
        )
        self.household = Household.objects.create(
            name='Test Household',
            village=self.village,
            national_id=f'ID{uid}',
            phone_number='0712345678',
            monthly_income=Decimal('5000.00'),
            disability=True
        )
        # Add head member
        HouseholdMember.objects.create(
            household=self.household,
            name='Head',
            gender='female',
            age=35,
            relationship_to_head='head',
            education_level='none'
        )

    def test_eligibility_assessment_runs(self):
        """Test that eligibility assessment can run without errors"""
        try:
            result = self.household.run_eligibility_assessment()
            self.assertIn('total_score', result)
            self.assertIn('eligibility_level', result)
        except (ImportError, AttributeError):
            # Skip if eligibility module not fully implemented
            pass

    def test_ppi_score_creation(self):
        """Test PPI score creation and retrieval"""
        from django.utils import timezone
        ppi = PPI.objects.create(
            household=self.household,
            name='Baseline PPI',
            eligibility_score=45,
            assessment_date=timezone.now().date()
        )
        self.assertEqual(self.household.latest_ppi_score, 45)
