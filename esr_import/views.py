"""
ESR Data Import Views
Imports ESR data into the main Household model
"""
import re
import uuid
import secrets
import string
from datetime import datetime
from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator

from core.decorators import role_required
from core.models import County, Village, SubCounty, Mentor, BusinessMentorCycle, AuditLog
from households.models import Household, HouseholdMember
from accounts.models import User

from .models import ESRImportLog


def generate_temp_password(length=12):
    """Generate a secure temporary password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    password = (
        secrets.choice(string.ascii_uppercase) +
        secrets.choice(string.ascii_lowercase) +
        secrets.choice(string.digits) +
        secrets.choice("!@#$%") +
        password[4:]
    )
    return password


def parse_bm_cycle_from_mentor(mentor_value):
    """
    Parse BM cycle prefix from mentor name
    Example: "FY2025/26C1 Jane Doe" -> ("FY2025/26C1", "Jane Doe")
    """
    if not mentor_value:
        return None, None

    mentor_value = str(mentor_value).strip()
    pattern = r'^(FY\d{4}[/-]\d{2}C\d+)\s+(.+)$'
    match = re.match(pattern, mentor_value, re.IGNORECASE)

    if match:
        bm_cycle = match.group(1).upper()
        mentor_name = match.group(2).strip()
        return bm_cycle, mentor_name

    return None, mentor_value


def normalize_enum_value(value, choices):
    """Normalize and validate enum value against choices"""
    if not value:
        return ''

    value = str(value).lower().strip().replace(' ', '_').replace('-', '_')
    valid_values = [choice[0] for choice in choices]

    if value in valid_values:
        return value

    for valid_value in valid_values:
        if value in valid_value or valid_value in value:
            return valid_value

    return ''


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def esr_import_page(request):
    """ESR Import main page"""
    import_logs = ESRImportLog.objects.all().order_by('-created_at')[:10]
    context = {
        'import_logs': import_logs,
        'page_title': 'ESR Data Import',
    }
    return render(request, 'esr_import/import.html', context)


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def download_template(request):
    """Download ESR import Excel template"""
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        messages.error(request, "openpyxl is required for Excel operations")
        return redirect('core:esr_import_list')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ESR Data"

    columns = [
        ("ID_Number", "National ID - REQUIRED for deduplication", "12345678"),
        ("Beneficiary_Name", "Name of the beneficiary - REQUIRED", "Mary Wanjiku"),
        ("Village", "Village name - REQUIRED", "Wote Village"),
        ("Mentor_Supervisor", "Name of the mentor supervisor", "John Smith"),
        ("Mentor", "Mentor name (may include BM cycle prefix)", "FY2025/26C1 Jane Doe"),
        ("CountyName", "County name", "Makueni"),
        ("SubCounty", "Sub-County name", "Makueni"),
        ("Landmark", "Landmark near the household", "Near primary school"),
        ("Phone_Number", "Phone number", "0712345678"),
        ("NumberOfMembers", "Total household members", "5"),
        ("NoOfHabitableRooms", "Number of habitable rooms", "3"),
        ("DwellingTenure", "Ownership status (owned/rented/family/squatter/other)", "owned"),
        ("Roof", "Roof material (iron_sheets/tiles/concrete/thatch/mud/other)", "iron_sheets"),
        ("Wall", "Wall material (brick/stone/mud/wood/iron_sheets/other)", "brick"),
        ("Floor", "Floor material (cement/tiles/mud/wood/other)", "cement"),
        ("DwellingRisk", "Risk level (low/medium/high/critical)", "low"),
        ("LightingFuel", "Lighting source (electricity/solar/kerosene/candle/firewood/none/other)", "solar"),
        ("WaterSource", "Water source (piped/borehole/well/spring/river/rain/vendor/other)", "borehole"),
        ("WasteDisposal", "Disposal method (flush_toilet/pit_latrine/vip_latrine/bush/shared/none/other)", "pit_latrine"),
        ("CookingFuel", "Cooking fuel (electricity/gas/kerosene/charcoal/firewood/other)", "firewood"),
        ("Disability", "Has disability (yes/no)", "no"),
        ("Notes", "Additional notes", ""),
    ]

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    required_fill = PatternFill(start_color="FF6B6B", end_color="FF6B6B", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin')
    )

    for col_num, (col_name, description, example) in enumerate(columns, 1):
        cell = ws.cell(row=1, column=col_num, value=col_name)
        cell.font = header_font
        cell.fill = required_fill if col_name in ['ID_Number', 'Beneficiary_Name', 'Village'] else header_fill
        cell.alignment = Alignment(horizontal="center")
        cell.border = thin_border
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = max(15, len(col_name) + 2)

    example_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    for col_num, (col_name, description, example) in enumerate(columns, 1):
        cell = ws.cell(row=2, column=col_num, value=example)
        cell.fill = example_fill
        cell.border = thin_border

    ws_instructions = wb.create_sheet("Instructions")
    ws_instructions.column_dimensions["A"].width = 80

    instructions = [
        "ESR Data Import Template Instructions",
        "",
        "REQUIRED FIELDS (highlighted in red):",
        "- ID_Number: National ID for deduplication",
        "- Beneficiary_Name: Name of the household head/beneficiary",
        "- Village: Village name (will be matched or created)",
        "",
        "OPTIONAL FIELDS:",
        "- All other fields are optional and will be imported if provided",
        "- Mentor column can include BM cycle prefix: 'FY2025/26C1 Jane Doe'",
        "- Mentors and supervisors will be created as users if they don't exist",
        "",
        "VALID VALUES FOR CHOICE FIELDS:",
        "DwellingTenure: owned, rented, family, squatter, other",
        "Roof: iron_sheets, tiles, concrete, thatch, mud, other",
        "Wall: brick, stone, mud, wood, iron_sheets, other",
        "Floor: cement, tiles, mud, wood, other",
        "DwellingRisk: low, medium, high, critical",
        "LightingFuel: electricity, solar, kerosene, candle, firewood, none, other",
        "WaterSource: piped, borehole, well, spring, river, rain, vendor, other",
        "WasteDisposal: flush_toilet, pit_latrine, vip_latrine, bush, shared, none, other",
        "CookingFuel: electricity, gas, kerosene, charcoal, firewood, other",
    ]

    for row_idx, instruction in enumerate(instructions, 1):
        ws_instructions.cell(row=row_idx, column=1, value=instruction)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=ESR_Import_Template_{datetime.now().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def process_import(request):
    """Process ESR import from Excel file into main Household model"""
    if request.method != 'POST':
        return redirect('core:esr_import_list')

    if 'file' not in request.FILES:
        messages.error(request, "Please select a file to import")
        return redirect('core:esr_import_list')

    uploaded_file = request.FILES['file']
    skip_duplicates = request.POST.get('skip_duplicates', 'true') == 'true'

    if not uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
        messages.error(request, "File must be Excel format (.xlsx or .xls)")
        return redirect('core:esr_import_list')

    try:
        import openpyxl
        workbook = openpyxl.load_workbook(BytesIO(uploaded_file.read()))
        sheet = workbook.active
    except ImportError:
        messages.error(request, "openpyxl library is required")
        return redirect('core:esr_import_list')
    except Exception as e:
        messages.error(request, f"Failed to parse Excel file: {str(e)}")
        return redirect('core:esr_import_list')

    # Get headers
    headers = []
    for cell in sheet[1]:
        if cell.value:
            header = str(cell.value).strip().replace(' ', '').replace('_', '').lower()
            headers.append(header)
        else:
            headers.append(f'col_{len(headers)}')

    header_map = {header: idx for idx, header in enumerate(headers)}

    batch_id = f"ESR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8]}"
    stats = {
        'total_records': 0, 'successful': 0, 'failed': 0, 'duplicates': 0,
        'villages_created': 0, 'mentors_created': 0, 'supervisors_created': 0,
        'households_created': 0, 'bm_cycles_created': 0,
    }
    errors = []
    mentor_credentials = []
    supervisor_credentials = []

    # Caches
    village_cache = {}
    subcounty_cache = {}
    county_cache = {}
    bm_cycle_cache = {}
    mentor_cache = {}
    supervisor_cache = {}

    def get_value(row, col_name):
        """Get value from row by column name"""
        normalized = col_name.replace('_', '').replace(' ', '').lower()
        variations = [normalized, col_name.lower(), col_name.lower().replace('_', '')]
        for var in variations:
            if var in header_map:
                idx = header_map[var]
                if idx < len(row):
                    val = row[idx]
                    if val is not None:
                        return str(val).strip() if not isinstance(val, (int, float)) else val
        return None

    with transaction.atomic():
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            if all(cell is None for cell in row):
                continue

            stats['total_records'] += 1

            try:
                # REQUIRED: ID Number
                id_number = get_value(row, 'ID_Number') or get_value(row, 'idnumber') or get_value(row, 'nationalid')
                if not id_number:
                    errors.append({"row": row_idx, "error": "Missing required ID_Number"})
                    stats['failed'] += 1
                    continue

                id_number = str(id_number).strip()

                # Check for duplicate
                if skip_duplicates and Household.objects.filter(national_id=id_number).exists():
                    stats['duplicates'] += 1
                    continue

                # REQUIRED: Beneficiary Name
                beneficiary_name = (get_value(row, 'Beneficiary_Name') or get_value(row, 'beneficiaryname') or
                                   get_value(row, 'name') or get_value(row, 'maincaregiver') or
                                   get_value(row, 'MainCaregiver'))
                if not beneficiary_name:
                    errors.append({"row": row_idx, "error": "Missing required Beneficiary_Name"})
                    stats['failed'] += 1
                    continue

                # REQUIRED: Village
                village_name = get_value(row, 'Village') or get_value(row, 'villagename')
                if not village_name:
                    errors.append({"row": row_idx, "error": "Missing required Village"})
                    stats['failed'] += 1
                    continue

                # Get or create village
                village_key = village_name.lower()
                if village_key not in village_cache:
                    # Try to find existing village
                    village = Village.objects.filter(name__iexact=village_name).first()
                    if not village:
                        # Get or create subcounty
                        subcounty_name = get_value(row, 'SubCounty') or get_value(row, 'subcountyname')
                        county_name = get_value(row, 'CountyName') or get_value(row, 'county')

                        subcounty = None
                        if subcounty_name:
                            subcounty_key = subcounty_name.lower()
                            if subcounty_key not in subcounty_cache:
                                # Get or create county first
                                if county_name:
                                    county_key = county_name.lower()
                                    if county_key not in county_cache:
                                        county, _ = County.objects.get_or_create(
                                            name__iexact=county_name,
                                            defaults={'name': county_name}
                                        )
                                        county_cache[county_key] = county
                                    county = county_cache[county_key]
                                else:
                                    county = County.objects.first()

                                subcounty, _ = SubCounty.objects.get_or_create(
                                    name__iexact=subcounty_name,
                                    defaults={'name': subcounty_name, 'county': county}
                                )
                                subcounty_cache[subcounty_key] = subcounty
                            subcounty = subcounty_cache.get(subcounty_key)

                        village, created = Village.objects.get_or_create(
                            name__iexact=village_name,
                            defaults={
                                'name': village_name,
                                'subcounty_obj': subcounty
                            }
                        )
                        if created:
                            stats['villages_created'] += 1

                    village_cache[village_key] = village
                village = village_cache[village_key]

                # Parse mentor and BM cycle
                mentor_value = get_value(row, 'Mentor')
                bm_cycle_name, mentor_name = parse_bm_cycle_from_mentor(mentor_value)

                # Get or create BM Cycle
                bm_cycle = None
                if bm_cycle_name:
                    bm_cycle_key = bm_cycle_name.upper()
                    if bm_cycle_key not in bm_cycle_cache:
                        bm_cycle, created = BusinessMentorCycle.objects.get_or_create(
                            bm_cycle_name__iexact=bm_cycle_key,
                            defaults={'bm_cycle_name': bm_cycle_key}
                        )
                        if created:
                            stats['bm_cycles_created'] += 1
                        bm_cycle_cache[bm_cycle_key] = bm_cycle
                    bm_cycle = bm_cycle_cache[bm_cycle_key]

                # Get or create Supervisor
                supervisor_name = get_value(row, 'Mentor_Supervisor') or get_value(row, 'mentorsupervisor')
                supervisor_user = None
                if supervisor_name:
                    supervisor_key = supervisor_name.lower()
                    if supervisor_key not in supervisor_cache:
                        try:
                            supervisor_user = User.objects.get(
                                Q(first_name__iexact=supervisor_name.split()[0]) |
                                Q(username__iexact=supervisor_name.replace(' ', '_').lower())
                            )
                        except User.DoesNotExist:
                            name_parts = supervisor_name.split(' ', 1)
                            username = f"supervisor_{supervisor_key.replace(' ', '_').replace('.', '_')}"
                            email = f"{username}@esr.local"

                            if not User.objects.filter(Q(email=email) | Q(username=username)).exists():
                                temp_password = generate_temp_password()
                                supervisor_user = User.objects.create_user(
                                    username=username,
                                    email=email,
                                    password=temp_password,
                                    first_name=name_parts[0],
                                    last_name=name_parts[1] if len(name_parts) > 1 else '',
                                    role='field_associate',
                                    is_active=True
                                )
                                stats['supervisors_created'] += 1
                                supervisor_credentials.append({
                                    'name': supervisor_name,
                                    'username': username,
                                    'email': email,
                                    'temp_password': temp_password
                                })
                        except User.MultipleObjectsReturned:
                            supervisor_user = User.objects.filter(
                                Q(first_name__iexact=supervisor_name.split()[0])
                            ).first()

                        if supervisor_user:
                            supervisor_cache[supervisor_key] = supervisor_user
                    supervisor_user = supervisor_cache.get(supervisor_key)

                # Get or create Mentor
                mentor = None
                if mentor_name:
                    mentor_key = mentor_name.lower()
                    if mentor_key not in mentor_cache:
                        try:
                            mentor = Mentor.objects.get(
                                Q(first_name__iexact=mentor_name.split()[0]) |
                                Q(user__username__iexact=mentor_name.replace(' ', '_').lower())
                            )
                        except Mentor.DoesNotExist:
                            name_parts = mentor_name.split(' ', 1)
                            username = f"mentor_{mentor_key.replace(' ', '_').replace('.', '_')}"
                            email = f"{username}@esr.local"

                            if not User.objects.filter(Q(email=email) | Q(username=username)).exists():
                                temp_password = generate_temp_password()
                                mentor_user = User.objects.create_user(
                                    username=username,
                                    email=email,
                                    password=temp_password,
                                    first_name=name_parts[0],
                                    last_name=name_parts[1] if len(name_parts) > 1 else '',
                                    role='mentor',
                                    is_active=True
                                )

                                mentor = Mentor.objects.create(
                                    user=mentor_user,
                                    first_name=name_parts[0],
                                    last_name=name_parts[1] if len(name_parts) > 1 else '',
                                    is_active=True
                                )
                                stats['mentors_created'] += 1
                                mentor_credentials.append({
                                    'name': mentor_name,
                                    'username': username,
                                    'email': email,
                                    'temp_password': temp_password
                                })
                        except Mentor.MultipleObjectsReturned:
                            mentor = Mentor.objects.filter(
                                Q(first_name__iexact=mentor_name.split()[0])
                            ).first()

                        if mentor:
                            mentor_cache[mentor_key] = mentor
                    mentor = mentor_cache.get(mentor_key)

                # Parse optional fields
                num_members_val = get_value(row, 'NumberOfMembers') or get_value(row, 'numberofhouseholdmembers')
                habitable_rooms_val = get_value(row, 'NoOfHabitableRooms') or get_value(row, 'noofhabitablerooms')

                disability_val = get_value(row, 'Disability')
                has_disability = disability_val and str(disability_val).lower() in ['yes', 'true', '1', 'y']

                # Create household
                household = Household.objects.create(
                    name=str(beneficiary_name),
                    national_id=id_number,
                    village=village,
                    subcounty=village.subcounty_obj,
                    phone_number=str(get_value(row, 'Phone_Number') or get_value(row, 'phonenumber') or ''),
                    main_caregiver=str(beneficiary_name),
                    landmark=str(get_value(row, 'Landmark') or ''),
                    disability=has_disability,

                    # Staff assignment
                    assigned_mentor=mentor,
                    mentor_supervisor=supervisor_user,
                    bm_cycle=bm_cycle,

                    # Dwelling characteristics
                    no_of_habitable_rooms=int(float(str(habitable_rooms_val))) if habitable_rooms_val else None,
                    dwelling_tenure=normalize_enum_value(get_value(row, 'DwellingTenure'), Household.DWELLING_TENURE_CHOICES),
                    dwelling_risk=normalize_enum_value(get_value(row, 'DwellingRisk') or get_value(row, 'dwelinunitrisk'), Household.DWELLING_RISK_CHOICES),
                    roof_type=normalize_enum_value(get_value(row, 'Roof'), Household.ROOF_TYPE_CHOICES),
                    wall_type=normalize_enum_value(get_value(row, 'Wall'), Household.WALL_TYPE_CHOICES),
                    floor_type=normalize_enum_value(get_value(row, 'Floor'), Household.FLOOR_TYPE_CHOICES),

                    # Utilities
                    lighting_fuel=normalize_enum_value(get_value(row, 'LightingFuel'), Household.LIGHTING_FUEL_CHOICES),
                    water_source=normalize_enum_value(get_value(row, 'WaterSource'), Household.WATER_SOURCE_CHOICES),
                    waste_disposal=normalize_enum_value(get_value(row, 'WasteDisposal') or get_value(row, 'humanwastedisposal'), Household.WASTE_DISPOSAL_CHOICES),
                    cooking_fuel=normalize_enum_value(get_value(row, 'CookingFuel'), Household.COOKING_FUEL_CHOICES),

                    # Import tracking
                    notes=str(get_value(row, 'Notes') or ''),
                    import_batch_id=batch_id,
                    imported_at=timezone.now(),
                    imported_by=request.user
                )

                stats['households_created'] += 1
                stats['successful'] += 1

            except Exception as e:
                errors.append({"row": row_idx, "error": str(e)})
                stats['failed'] += 1

        # Create import log
        import_log = ESRImportLog.objects.create(
            batch_id=batch_id,
            file_name=uploaded_file.name,
            total_records=stats['total_records'],
            successful=stats['successful'],
            failed=stats['failed'],
            duplicates=stats['duplicates'],
            villages_created=stats['villages_created'],
            mentors_created=stats['mentors_created'],
            supervisors_created=stats['supervisors_created'],
            households_created=stats['households_created'],
            bm_cycles_created=stats['bm_cycles_created'],
            status='completed' if stats['failed'] == 0 else 'completed_with_errors',
            error_summary={'errors': errors[:100]} if errors else {},
            mentor_credentials=mentor_credentials,
            supervisor_credentials=supervisor_credentials,
            imported_by=request.user,
            completed_at=timezone.now()
        )

        AuditLog.objects.create(
            user=request.user,
            action='create',
            model_name='ESRImport',
            object_id=str(import_log.id),
            description=f"Imported {stats['successful']} households from {uploaded_file.name}",
            ip_address=request.META.get('REMOTE_ADDR')
        )

    messages.success(
        request,
        f"Import completed! Created: {stats['households_created']} households, "
        f"{stats['villages_created']} villages, {stats['mentors_created']} mentors, "
        f"{stats['supervisors_created']} supervisors. "
        f"Duplicates skipped: {stats['duplicates']}. Errors: {stats['failed']}"
    )

    return redirect('core:esr_import_result', batch_id=batch_id)


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def import_result(request, batch_id):
    """View import result details"""
    import_log = get_object_or_404(ESRImportLog, batch_id=batch_id)
    context = {
        'import_log': import_log,
        'page_title': f'Import Result - {batch_id}',
    }
    return render(request, 'esr_import/result.html', context)


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def import_history(request):
    """View import history"""
    import_logs = ESRImportLog.objects.all().order_by('-created_at')
    paginator = Paginator(import_logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'import_logs': page_obj,
        'page_obj': page_obj,
        'page_title': 'Import History',
    }
    return render(request, 'esr_import/history.html', context)


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def household_list(request):
    """List imported households (redirect to main households list with import filter)"""
    # Redirect to main households list
    return redirect('households:household_list')


@login_required
@role_required(['ict_admin', 'program_manager', 'me_staff'])
def household_detail(request, household_id):
    """View/Edit household (redirect to main household detail)"""
    return redirect('households:household_detail', pk=household_id)
