"""
Beneficiary Lookup Service for MIS Integration

This service validates Kobo form submissions against existing MIS data
and handles different form purposes (registration, enrollment, surveys, updates).
"""

from django.db.models import Q
from households.models import Household, HouseholdMember
from core.models import Village


# Common form field names that map to MIS fields
COMMON_FIELD_MAPPINGS = {
    # ID Number variations
    'id_number': ['id_number', 'national_id', 'id_no', 'ID_Number', 'national_id_number',
                  'head_id_number', 'identification_number', 'idno'],
    # Phone variations
    'phone_number': ['phone_number', 'phone', 'phone_no', 'telephone', 'mobile',
                     'head_phone_number', 'contact_phone', 'mobile_number', 'phonenumber'],
    # Village variations
    'village': ['village', 'village_name', 'Village', 'village_id'],
    # Name variations
    'first_name': ['first_name', 'firstname', 'First_Name', 'given_name'],
    'last_name': ['last_name', 'lastname', 'Last_Name', 'surname', 'family_name'],
    'middle_name': ['middle_name', 'middlename', 'Middle_Name', 'other_names'],
}


def extract_identifier_from_form_data(form_data, field_mapping, identifier_type):
    """
    Extract a specific identifier value from form_data using field_mapping or common patterns.

    Args:
        form_data: dict - The submitted form data
        field_mapping: dict - Custom field mapping from FormTemplate
        identifier_type: str - Type of identifier (id_number, phone_number, village, etc.)

    Returns:
        str or None - The extracted value
    """
    # First check custom field mapping
    if field_mapping and identifier_type in field_mapping:
        mapped_field = field_mapping[identifier_type]
        if mapped_field in form_data:
            return str(form_data[mapped_field]).strip() if form_data[mapped_field] else None

    # Fall back to common field names
    common_names = COMMON_FIELD_MAPPINGS.get(identifier_type, [])
    for field_name in common_names:
        if field_name in form_data and form_data[field_name]:
            return str(form_data[field_name]).strip()

    return None


def find_household_by_identifiers(id_number=None, phone_number=None, village_name=None):
    """
    Search for an existing household by various identifiers.

    Args:
        id_number: str - National ID or head's ID number
        phone_number: str - Phone number
        village_name: str - Village name

    Returns:
        tuple: (household or None, match_type: str, confidence: str)
    """
    if not any([id_number, phone_number]):
        return None, 'no_identifiers', 'none'

    households = Household.objects.all()

    # Priority 1: Match by ID number (highest confidence)
    if id_number:
        # Clean the ID number
        clean_id = id_number.replace(' ', '').replace('-', '')

        # Try exact match first on head_id_number
        hh = households.filter(
            Q(head_id_number__iexact=clean_id) |
            Q(national_id__iexact=clean_id)
        ).first()

        if hh:
            return hh, 'id_number', 'high'

        # Try partial match (contains)
        hh = households.filter(
            Q(head_id_number__icontains=clean_id) |
            Q(national_id__icontains=clean_id)
        ).first()

        if hh:
            return hh, 'id_number_partial', 'medium'

    # Priority 2: Match by phone number
    if phone_number:
        # Clean the phone number (remove spaces, dashes, country code prefix)
        clean_phone = phone_number.replace(' ', '').replace('-', '').replace('+', '')
        if clean_phone.startswith('254'):
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('0'):
            clean_phone = clean_phone[1:]

        # Try matching various phone formats
        hh = households.filter(
            Q(head_phone_number__icontains=clean_phone) |
            Q(phone_number__icontains=clean_phone)
        ).first()

        if hh:
            # If we have village, verify it matches for higher confidence
            if village_name:
                try:
                    if hh.village and hh.village.name.lower() == village_name.lower():
                        return hh, 'phone_and_village', 'high'
                except:
                    pass
            return hh, 'phone_number', 'medium'

    # Priority 3: If we have village, search by village (low confidence alone)
    if village_name:
        try:
            village = Village.objects.filter(name__iexact=village_name).first()
            if village:
                # Return the village match info but not a specific household
                return None, 'village_only', 'low'
        except:
            pass

    return None, 'not_found', 'none'


def find_member_by_identifiers(id_number=None, phone_number=None):
    """
    Search for an existing household member by identifiers.

    Args:
        id_number: str - ID number
        phone_number: str - Phone number

    Returns:
        HouseholdMember or None
    """
    if not any([id_number, phone_number]):
        return None

    members = HouseholdMember.objects.all()

    if id_number:
        clean_id = id_number.replace(' ', '').replace('-', '')
        member = members.filter(id_number__iexact=clean_id).first()
        if member:
            return member

    if phone_number:
        clean_phone = phone_number.replace(' ', '').replace('-', '').replace('+', '')
        if clean_phone.startswith('254'):
            clean_phone = clean_phone[3:]
        elif clean_phone.startswith('0'):
            clean_phone = clean_phone[1:]

        member = members.filter(phone_number__icontains=clean_phone).first()
        if member:
            return member

    return None


def get_beneficiary_data_for_form(household, field_mapping=None):
    """
    Get household data formatted for form pre-fill or validation display.

    Args:
        household: Household instance
        field_mapping: dict - Optional custom field mapping

    Returns:
        dict with beneficiary data
    """
    if not household:
        return {}

    data = {
        'household_id': household.id,
        'household_name': household.name,
        'head_full_name': household.head_full_name,
        'head_first_name': household.head_first_name,
        'head_middle_name': household.head_middle_name,
        'head_last_name': household.head_last_name,
        'head_id_number': household.head_id_number or household.national_id,
        'head_phone_number': household.head_phone_number or household.phone_number,
        'head_gender': household.head_gender,
        'head_date_of_birth': str(household.head_date_of_birth) if household.head_date_of_birth else '',
        'village_id': household.village_id,
        'village_name': household.village.name if household.village else '',
        'subcounty': household.subcounty.name if household.subcounty else '',
        'county': household.village.subcounty_obj.county.name if household.village and hasattr(household.village, 'subcounty_obj') and household.village.subcounty_obj and household.village.subcounty_obj.county else '',
        'gps_latitude': str(household.gps_latitude) if household.gps_latitude else '',
        'gps_longitude': str(household.gps_longitude) if household.gps_longitude else '',
        'total_members': household.members.count() if hasattr(household, 'members') else 0,
    }

    return data


def validate_submission_for_purpose(form_template, form_data):
    """
    Main validation function that checks submission against MIS based on form purpose.

    Args:
        form_template: FormTemplate instance
        form_data: dict - The submitted form data

    Returns:
        dict: {
            'status': str - validation status code
            'message': str - human readable message
            'household': Household or None - matched household
            'match_type': str - how the match was made
            'confidence': str - confidence level
            'beneficiary_data': dict - matched beneficiary data
            'should_update': bool - whether to update existing record
        }
    """
    form_purpose = form_template.form_purpose
    field_mapping = form_template.field_mapping or {}

    # Extract identifiers from form data
    id_number = extract_identifier_from_form_data(form_data, field_mapping, 'id_number')
    phone_number = extract_identifier_from_form_data(form_data, field_mapping, 'phone_number')
    village_name = extract_identifier_from_form_data(form_data, field_mapping, 'village')

    # Find matching household
    household, match_type, confidence = find_household_by_identifiers(
        id_number=id_number,
        phone_number=phone_number,
        village_name=village_name
    )

    # Default result
    result = {
        'status': 'not_validated',
        'message': '',
        'household': None,
        'match_type': match_type,
        'confidence': confidence,
        'beneficiary_data': {},
        'should_update': False,
    }

    # Handle based on form purpose
    if form_purpose == 'general':
        # No validation needed
        result['status'] = 'not_validated'
        result['message'] = 'Form does not require MIS validation'
        return result

    elif form_purpose == 'new_registration':
        # For new registration, existing beneficiary is a problem (duplicate)
        if household:
            result['status'] = 'duplicate_detected'
            result['message'] = f'Beneficiary already exists in MIS: {household.head_full_name} (ID: {household.id}). Match confidence: {confidence}'
            result['household'] = household
            result['beneficiary_data'] = get_beneficiary_data_for_form(household)
        else:
            result['status'] = 'beneficiary_not_found'
            result['message'] = 'No existing beneficiary found - ready for new registration'
        return result

    elif form_purpose == 'program_enrollment':
        # For enrollment, we need to find the existing beneficiary
        if household:
            result['status'] = 'beneficiary_found'
            result['message'] = f'Beneficiary found: {household.head_full_name} (ID: {household.id}). Ready for program enrollment.'
            result['household'] = household
            result['beneficiary_data'] = get_beneficiary_data_for_form(household)
        else:
            result['status'] = 'beneficiary_not_found'
            result['message'] = 'No matching beneficiary found in MIS. Beneficiary needs to be registered first.'
        return result

    elif form_purpose == 'survey':
        # For surveys, we should ideally link to existing beneficiary
        if household:
            result['status'] = 'beneficiary_found'
            result['message'] = f'Survey linked to: {household.head_full_name} (ID: {household.id})'
            result['household'] = household
            result['beneficiary_data'] = get_beneficiary_data_for_form(household)
        else:
            result['status'] = 'beneficiary_not_found'
            result['message'] = 'Could not link survey to existing beneficiary'
        return result

    elif form_purpose == 'update_details':
        # For updates, we must find existing beneficiary
        if household:
            result['status'] = 'beneficiary_found'
            result['message'] = f'Beneficiary found: {household.head_full_name}. Data will be updated.'
            result['household'] = household
            result['beneficiary_data'] = get_beneficiary_data_for_form(household)
            result['should_update'] = True
        else:
            result['status'] = 'beneficiary_not_found'
            result['message'] = 'Cannot update - no matching beneficiary found in MIS'
        return result

    return result


def update_household_from_submission(household, form_data, field_mapping=None):
    """
    Update household details from form submission data.

    Args:
        household: Household instance to update
        form_data: dict - The submitted form data
        field_mapping: dict - Field mapping from FormTemplate

    Returns:
        tuple: (success: bool, updated_fields: list, message: str)
    """
    if not household:
        return False, [], 'No household to update'

    field_mapping = field_mapping or {}
    updated_fields = []

    # Define updateable fields and their form equivalents
    update_map = {
        'head_first_name': ['first_name', 'firstname', 'head_first_name'],
        'head_middle_name': ['middle_name', 'middlename', 'head_middle_name'],
        'head_last_name': ['last_name', 'lastname', 'surname', 'head_last_name'],
        'head_phone_number': ['phone_number', 'phone', 'mobile', 'head_phone_number'],
        'head_id_number': ['id_number', 'national_id', 'head_id_number'],
        'head_gender': ['gender', 'sex', 'head_gender'],
    }

    try:
        for hh_field, form_fields in update_map.items():
            # Check custom mapping first
            if hh_field in field_mapping:
                form_field = field_mapping[hh_field]
                if form_field in form_data and form_data[form_field]:
                    new_value = str(form_data[form_field]).strip()
                    old_value = getattr(household, hh_field, '')
                    if new_value and new_value != old_value:
                        setattr(household, hh_field, new_value)
                        updated_fields.append(hh_field)
                    continue

            # Try common field names
            for form_field in form_fields:
                if form_field in form_data and form_data[form_field]:
                    new_value = str(form_data[form_field]).strip()
                    old_value = getattr(household, hh_field, '')
                    if new_value and new_value != old_value:
                        setattr(household, hh_field, new_value)
                        updated_fields.append(hh_field)
                    break

        if updated_fields:
            household.save()
            return True, updated_fields, f'Updated fields: {", ".join(updated_fields)}'
        else:
            return True, [], 'No fields needed updating'

    except Exception as e:
        return False, [], f'Error updating household: {str(e)}'


def create_household_from_submission(form_data, field_mapping=None, gps_latitude=None, gps_longitude=None, created_by=None):
    """
    Create a new household from Kobo form submission data.

    Args:
        form_data: dict - The submitted form data
        field_mapping: dict - Field mapping from FormTemplate
        gps_latitude: float - GPS latitude if available
        gps_longitude: float - GPS longitude if available
        created_by: User - User who created the submission

    Returns:
        tuple: (household: Household or None, success: bool, message: str)
    """
    field_mapping = field_mapping or {}

    # Extract required fields
    first_name = extract_identifier_from_form_data(form_data, field_mapping, 'first_name')
    last_name = extract_identifier_from_form_data(form_data, field_mapping, 'last_name')
    middle_name = extract_identifier_from_form_data(form_data, field_mapping, 'middle_name')
    id_number = extract_identifier_from_form_data(form_data, field_mapping, 'id_number')
    phone_number = extract_identifier_from_form_data(form_data, field_mapping, 'phone_number')
    village_name = extract_identifier_from_form_data(form_data, field_mapping, 'village')

    # Validate minimum required data
    if not first_name and not last_name:
        # Try to extract from combined name field
        full_name = form_data.get('full_name') or form_data.get('name') or form_data.get('head_name') or ''
        if full_name:
            name_parts = full_name.strip().split()
            if len(name_parts) >= 1:
                first_name = name_parts[0]
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
            if len(name_parts) >= 3:
                middle_name = ' '.join(name_parts[1:-1])

    if not first_name:
        return None, False, 'Cannot create household: First name is required'

    try:
        # Find or create village
        village = None
        if village_name:
            village = Village.objects.filter(name__iexact=village_name).first()
            if not village:
                # Try partial match
                village = Village.objects.filter(name__icontains=village_name).first()

        # Generate household name
        household_name = f"{first_name} {last_name}".strip() if last_name else first_name
        if village:
            household_name = f"{household_name} - {village.name}"

        # Extract gender
        gender = None
        gender_value = form_data.get('gender') or form_data.get('sex') or form_data.get('head_gender')
        if gender_value:
            gender_lower = str(gender_value).lower()
            if gender_lower in ['male', 'm', 'man']:
                gender = 'male'
            elif gender_lower in ['female', 'f', 'woman']:
                gender = 'female'

        # Extract date of birth
        dob = None
        dob_value = form_data.get('date_of_birth') or form_data.get('dob') or form_data.get('head_dob')
        if dob_value:
            try:
                from datetime import datetime
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
                    try:
                        dob = datetime.strptime(str(dob_value), fmt).date()
                        break
                    except ValueError:
                        continue
            except:
                pass

        # Village is required - if no village found, cannot create household
        if not village:
            return None, False, 'Cannot create household: Village is required but could not be matched'

        # Create the household
        household = Household.objects.create(
            name=household_name,
            head_first_name=first_name or '',
            head_middle_name=middle_name or '',
            head_last_name=last_name or '',
            head_id_number=id_number or '',
            head_phone_number=phone_number or '',
            national_id=id_number or '',  # Also set legacy field
            phone_number=phone_number or '',  # Also set legacy field
            village=village,
            gps_latitude=gps_latitude,
            gps_longitude=gps_longitude,
        )

        # Set gender if provided (handled by property in some models)
        if gender and hasattr(household, 'head_gender') and not callable(getattr(household, 'head_gender', None)):
            try:
                household.head_gender = gender
                household.save()
            except:
                pass

        # Set date of birth if provided
        if dob:
            try:
                household.head_date_of_birth = dob
                household.save()
            except:
                pass

        return household, True, f'New household created: {household.name} (ID: {household.id})'

    except Exception as e:
        return None, False, f'Error creating household: {str(e)}'


def process_new_registration(form_template, form_data, gps_latitude=None, gps_longitude=None, created_by=None):
    """
    Process a new registration form submission.
    Creates a new household if no duplicate is found and settings allow it.

    Args:
        form_template: FormTemplate instance
        form_data: dict - The submitted form data
        gps_latitude: float - GPS latitude if available
        gps_longitude: float - GPS longitude if available
        created_by: User - User who created the submission

    Returns:
        dict: {
            'status': str - 'created', 'duplicate', 'error'
            'household': Household or None
            'message': str
        }
    """
    # First validate to check for duplicates
    validation = validate_submission_for_purpose(form_template, form_data)

    if validation['status'] == 'duplicate_detected':
        return {
            'status': 'duplicate',
            'household': validation['household'],
            'message': validation['message']
        }

    # Check if new household creation is allowed
    try:
        from settings_module.models import SystemConfiguration
        allow_new = SystemConfiguration.objects.filter(
            key='kobo_allow_new_households'
        ).first()
        allow_creation = allow_new.value == 'true' if allow_new else True
    except:
        allow_creation = True

    if not allow_creation:
        return {
            'status': 'not_allowed',
            'household': None,
            'message': 'New household creation is disabled in system settings'
        }

    # Create the new household
    household, success, message = create_household_from_submission(
        form_data=form_data,
        field_mapping=form_template.field_mapping,
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude,
        created_by=created_by
    )

    if success:
        return {
            'status': 'created',
            'household': household,
            'message': message
        }
    else:
        return {
            'status': 'error',
            'household': None,
            'message': message
        }
