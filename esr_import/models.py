"""
ESR (Economic Strengthening Record) Import Models
Extended location hierarchy and household data for ESR imports
"""
from django.db import models
from django.contrib.auth import get_user_model
from core.models import County, Village

User = get_user_model()


class BMCycle(models.Model):
    """BM (Business Mentoring) Cycle model for tracking fiscal year cycles"""
    name = models.CharField(max_length=50, unique=True, db_index=True)  # e.g., "FY2025/26C1"
    fiscal_year = models.CharField(max_length=20)  # e.g., "2025/26"
    cycle_number = models.IntegerField()  # e.g., 1, 2, 3
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'esr_bm_cycles'
        ordering = ['-name']


class Constituency(models.Model):
    """Constituency model within County"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='esr_constituencies')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.county.name}"

    class Meta:
        db_table = 'esr_constituencies'
        unique_together = ['name', 'county']
        verbose_name_plural = 'Constituencies'


class District(models.Model):
    """District model within Constituency"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='districts')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.constituency.name}"

    class Meta:
        db_table = 'esr_districts'
        unique_together = ['name', 'constituency']


class Division(models.Model):
    """Division model within District"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='divisions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.district.name}"

    class Meta:
        db_table = 'esr_divisions'
        unique_together = ['name', 'district']


class ESRWard(models.Model):
    """ESR Ward model within Division"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='wards')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.division.name}"

    class Meta:
        db_table = 'esr_wards'
        unique_together = ['name', 'division']


class Location(models.Model):
    """Location model within Ward"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    ward = models.ForeignKey(ESRWard, on_delete=models.CASCADE, related_name='locations')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.ward.name}"

    class Meta:
        db_table = 'esr_locations'
        unique_together = ['name', 'ward']


class SubLocation(models.Model):
    """SubLocation model within Location"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='sub_locations')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.location.name}"

    class Meta:
        db_table = 'esr_sub_locations'
        unique_together = ['name', 'location']


class ESRVillage(models.Model):
    """Extended Village model for ESR with additional fields"""
    name = models.CharField(max_length=100, db_index=True)
    code = models.CharField(max_length=20, blank=True)
    sub_location = models.ForeignKey(SubLocation, on_delete=models.CASCADE, related_name='villages')
    landmark = models.TextField(blank=True)
    community_leader_name = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Link to core Village if exists
    core_village = models.ForeignKey(Village, on_delete=models.SET_NULL, null=True, blank=True, related_name='esr_villages')

    def __str__(self):
        return f"{self.name} - {self.sub_location.name}"

    class Meta:
        db_table = 'esr_villages'
        unique_together = ['name', 'sub_location']


class MentorSupervisor(models.Model):
    """Mentor Supervisor tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')
    employee_id = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Supervisor"

    class Meta:
        db_table = 'esr_mentor_supervisors'


class MentorProfile(models.Model):
    """Extended mentor profile for ESR"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='esr_mentor_profile')
    supervisor = models.ForeignKey(MentorSupervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentors')
    employee_id = models.CharField(max_length=50, blank=True)
    phone_secondary = models.CharField(max_length=20, blank=True)
    profile_completed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Mentor"

    class Meta:
        db_table = 'esr_mentor_profiles'


class MentorAssignment(models.Model):
    """Mentor assignment to villages within BM cycles"""
    mentor = models.ForeignKey(MentorProfile, on_delete=models.CASCADE, related_name='village_assignments')
    village = models.ForeignKey(ESRVillage, on_delete=models.CASCADE, related_name='mentor_assignments')
    bm_cycle = models.ForeignKey(BMCycle, on_delete=models.CASCADE, related_name='mentor_assignments')
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.mentor} - {self.village} - {self.bm_cycle}"

    class Meta:
        db_table = 'esr_mentor_assignments'
        unique_together = ['mentor', 'village', 'bm_cycle']


class ESRHousehold(models.Model):
    """ESR Household with comprehensive dwelling and economic data"""

    # Dwelling tenure choices
    DWELLING_TENURE_CHOICES = [
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('family', 'Family'),
        ('squatter', 'Squatter'),
        ('other', 'Other'),
    ]

    # Roof type choices
    ROOF_TYPE_CHOICES = [
        ('iron_sheets', 'Iron Sheets'),
        ('tiles', 'Tiles'),
        ('concrete', 'Concrete'),
        ('thatch', 'Thatch'),
        ('mud', 'Mud'),
        ('other', 'Other'),
    ]

    # Wall type choices
    WALL_TYPE_CHOICES = [
        ('brick', 'Brick'),
        ('stone', 'Stone'),
        ('mud', 'Mud'),
        ('wood', 'Wood'),
        ('iron_sheets', 'Iron Sheets'),
        ('other', 'Other'),
    ]

    # Floor type choices
    FLOOR_TYPE_CHOICES = [
        ('cement', 'Cement'),
        ('tiles', 'Tiles'),
        ('mud', 'Mud'),
        ('wood', 'Wood'),
        ('other', 'Other'),
    ]

    # Dwelling risk choices
    DWELLING_RISK_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    # Lighting fuel choices
    LIGHTING_FUEL_CHOICES = [
        ('electricity', 'Electricity'),
        ('solar', 'Solar'),
        ('kerosene', 'Kerosene'),
        ('candle', 'Candle'),
        ('firewood', 'Firewood'),
        ('none', 'None'),
        ('other', 'Other'),
    ]

    # Water source choices
    WATER_SOURCE_CHOICES = [
        ('piped', 'Piped'),
        ('borehole', 'Borehole'),
        ('well', 'Well'),
        ('spring', 'Spring'),
        ('river', 'River'),
        ('rain', 'Rain'),
        ('vendor', 'Vendor'),
        ('other', 'Other'),
    ]

    # Waste disposal choices
    WASTE_DISPOSAL_CHOICES = [
        ('flush_toilet', 'Flush Toilet'),
        ('pit_latrine', 'Pit Latrine'),
        ('vip_latrine', 'VIP Latrine'),
        ('bush', 'Bush'),
        ('shared', 'Shared'),
        ('none', 'None'),
        ('other', 'Other'),
    ]

    # Cooking fuel choices
    COOKING_FUEL_CHOICES = [
        ('electricity', 'Electricity'),
        ('gas', 'Gas'),
        ('kerosene', 'Kerosene'),
        ('charcoal', 'Charcoal'),
        ('firewood', 'Firewood'),
        ('other', 'Other'),
    ]

    # Identification
    household_code = models.CharField(max_length=50, unique=True, db_index=True)
    id_number = models.CharField(max_length=50, unique=True, db_index=True)  # National ID for deduplication - Required

    # Location hierarchy
    village = models.ForeignKey(ESRVillage, on_delete=models.CASCADE, related_name='households')
    landmark = models.TextField(blank=True)

    # BM Cycle
    bm_cycle = models.ForeignKey(BMCycle, on_delete=models.SET_NULL, null=True, blank=True, related_name='households')

    # Household composition
    main_caregiver = models.CharField(max_length=200, blank=True)
    number_of_members = models.IntegerField(default=1)

    # Dwelling characteristics
    no_of_habitable_rooms = models.IntegerField(null=True, blank=True)
    dwelling_tenure = models.CharField(max_length=20, choices=DWELLING_TENURE_CHOICES, blank=True)
    roof_type = models.CharField(max_length=20, choices=ROOF_TYPE_CHOICES, blank=True)
    wall_type = models.CharField(max_length=20, choices=WALL_TYPE_CHOICES, blank=True)
    floor_type = models.CharField(max_length=20, choices=FLOOR_TYPE_CHOICES, blank=True)
    dwelling_risk = models.CharField(max_length=20, choices=DWELLING_RISK_CHOICES, blank=True)

    # Utilities
    lighting_fuel = models.CharField(max_length=20, choices=LIGHTING_FUEL_CHOICES, blank=True)
    water_source = models.CharField(max_length=20, choices=WATER_SOURCE_CHOICES, blank=True)
    waste_disposal = models.CharField(max_length=20, choices=WASTE_DISPOSAL_CHOICES, blank=True)
    cooking_fuel = models.CharField(max_length=20, choices=COOKING_FUEL_CHOICES, blank=True)

    # Mentor assignment
    mentor = models.ForeignKey(MentorProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='households')
    mentor_supervisor = models.ForeignKey(MentorSupervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='households')

    # Additional data
    extra_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)

    # Import tracking
    import_batch_id = models.CharField(max_length=50, blank=True, db_index=True)
    imported_at = models.DateTimeField(null=True, blank=True)
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='esr_imports')

    # Link to core Household if exists
    core_household = models.ForeignKey('households.Household', on_delete=models.SET_NULL, null=True, blank=True, related_name='esr_households')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.household_code} - {self.main_caregiver or 'N/A'}"

    class Meta:
        db_table = 'esr_households'
        ordering = ['-created_at']


class ESRHouseholdMember(models.Model):
    """Individual members of ESR households"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    RELATIONSHIP_CHOICES = [
        ('head', 'Head'),
        ('spouse', 'Spouse'),
        ('child', 'Child'),
        ('parent', 'Parent'),
        ('sibling', 'Sibling'),
        ('relative', 'Relative'),
        ('other', 'Other'),
    ]

    household = models.ForeignKey(ESRHousehold, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=200)
    relationship_to_head = models.CharField(max_length=20, choices=RELATIONSHIP_CHOICES, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    age = models.IntegerField(null=True, blank=True)
    is_head = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.household.household_code})"

    class Meta:
        db_table = 'esr_household_members'


class ESRImportLog(models.Model):
    """Log of ESR import operations"""
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('completed_with_errors', 'Completed with Errors'),
        ('failed', 'Failed'),
    ]

    batch_id = models.CharField(max_length=50, unique=True, db_index=True)
    file_name = models.CharField(max_length=255)
    total_records = models.IntegerField(default=0)
    successful = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    duplicates = models.IntegerField(default=0)

    # New entities created
    villages_created = models.IntegerField(default=0)
    mentors_created = models.IntegerField(default=0)
    supervisors_created = models.IntegerField(default=0)
    households_created = models.IntegerField(default=0)
    bm_cycles_created = models.IntegerField(default=0)

    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='processing')
    error_summary = models.JSONField(default=dict, blank=True)

    # Credentials for created users
    mentor_credentials = models.JSONField(default=list, blank=True)
    supervisor_credentials = models.JSONField(default=list, blank=True)

    # Tracking
    imported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='esr_import_logs')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"ESR Import {self.batch_id} - {self.status}"

    class Meta:
        db_table = 'esr_import_logs'
        ordering = ['-created_at']
