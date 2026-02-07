"""
KoBoToolbox CSV Export Module for UPG MIS
Generates CSV files for use with KoBoToolbox pulldata() function

Usage:
- Export CSV files from UPG MIS database
- Upload to KoBoToolbox as media files
- Use pulldata() in XLSForm for offline validation
"""

import csv
import io
from datetime import date
from django.http import HttpResponse
from django.db.models import Q


def export_households_csv(request=None, bm_cycle=None, village=None, status=None):
    """
    Export households for KoBoToolbox validation

    CSV columns match KoBoToolbox pulldata() requirements:
    - hh_id: Unique household identifier (for lookup)
    - hh_name: Household head name
    - head_gender: Gender of household head
    - head_dob: Date of birth
    - head_phone: Phone number
    - national_id: National ID number
    - village_name: Village name
    - subcounty: Sub-county name
    - county: County name
    - bm_cycle: Business Mentor Cycle
    - status: Participation status
    - ppi_score: Latest PPI score
    - is_eligible: Whether eligible for UPG (1/0)
    """
    from households.models import Household, HouseholdProgram

    # Build queryset with filters
    queryset = Household.objects.select_related(
        'village',
        'village__subcounty_obj',
        'village__subcounty_obj__county'
    ).prefetch_related(
        'ppi_scores',
        'program_participations'
    )

    if village:
        queryset = queryset.filter(village_id=village)

    if status:
        queryset = queryset.filter(
            program_participations__participation_status=status
        )

    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'hh_id',
        'hh_name',
        'head_gender',
        'head_dob',
        'head_phone',
        'national_id',
        'village_name',
        'subcounty',
        'county',
        'bm_cycle',
        'status',
        'ppi_score',
        'is_eligible'
    ])

    # Data rows
    for hh in queryset:
        # Get latest PPI score
        latest_ppi = hh.ppi_scores.order_by('-assessment_date').first()
        ppi_score = latest_ppi.eligibility_score if latest_ppi else ''

        # Get participation status
        participation = hh.program_participations.first()
        part_status = participation.participation_status if participation else 'not_enrolled'

        # Get BM Cycle name
        bm_cycle_name = ''
        if participation and hasattr(participation, 'mentor') and participation.mentor:
            bm_cycles = participation.mentor.businessmentorcycle_set.first()
            if bm_cycles:
                bm_cycle_name = bm_cycles.bm_cycle_name

        # Get geographic info
        village_name = hh.village.name if hh.village else ''
        subcounty = ''
        county = ''
        if hh.village and hh.village.subcounty_obj:
            subcounty = hh.village.subcounty_obj.name
            if hh.village.subcounty_obj.county:
                county = hh.village.subcounty_obj.county.name

        # Check eligibility (PPI score < 50 is typically eligible)
        is_eligible = 1 if ppi_score and int(ppi_score) < 50 else 0

        writer.writerow([
            hh.id,
            hh.head_full_name or hh.name,
            hh.head_gender or '',
            hh.head_date_of_birth.isoformat() if hh.head_date_of_birth else '',
            hh.head_phone_number or hh.phone_number or '',
            hh.head_id_number or hh.national_id or '',
            village_name,
            subcounty,
            county,
            bm_cycle_name,
            part_status,
            ppi_score,
            is_eligible
        ])

    # Return as response or string
    if request:
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="households_{date.today().isoformat()}.csv"'
        return response

    return output.getvalue()


def export_bm_cycles_csv(request=None):
    """
    Export Business Mentor Cycles for KoBoToolbox dropdown/validation

    CSV columns:
    - bm_cycle_name: Unique cycle identifier (for lookup)
    - mentor_name: Business mentor name
    - field_associate: Field associate name
    - cycle: Cycle code (e.g., FY25C1)
    - project: Project name
    - office: Office location
    """
    from core.models import BusinessMentorCycle

    queryset = BusinessMentorCycle.objects.select_related('business_mentor').all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'bm_cycle_name',
        'mentor_name',
        'field_associate',
        'cycle',
        'project',
        'office'
    ])

    for bmc in queryset:
        mentor_name = ''
        if bmc.business_mentor:
            mentor_name = f"{bmc.business_mentor.first_name} {bmc.business_mentor.last_name}"

        writer.writerow([
            bmc.bm_cycle_name,
            mentor_name,
            bmc.field_associate,
            bmc.cycle,
            bmc.project,
            bmc.office
        ])

    if request:
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bm_cycles_{date.today().isoformat()}.csv"'
        return response

    return output.getvalue()


def export_villages_csv(request=None, county=None, subcounty=None):
    """
    Export villages for KoBoToolbox cascading select

    CSV columns:
    - village_id: Unique village ID
    - village_name: Village name (for display)
    - subcounty_name: Sub-county name (for filtering)
    - county_name: County name (for filtering)
    - is_program_area: Whether in program target area (1/0)
    """
    from core.models import Village

    queryset = Village.objects.select_related(
        'subcounty_obj',
        'subcounty_obj__county'
    )

    if county:
        queryset = queryset.filter(subcounty_obj__county__name=county)

    if subcounty:
        queryset = queryset.filter(subcounty_obj__name=subcounty)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'village_id',
        'village_name',
        'subcounty_name',
        'county_name',
        'is_program_area'
    ])

    for v in queryset:
        subcounty_name = v.subcounty_obj.name if v.subcounty_obj else ''
        county_name = ''
        if v.subcounty_obj and v.subcounty_obj.county:
            county_name = v.subcounty_obj.county.name

        writer.writerow([
            v.id,
            v.name,
            subcounty_name,
            county_name,
            1 if v.is_program_area else 0
        ])

    if request:
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="villages_{date.today().isoformat()}.csv"'
        return response

    return output.getvalue()


def export_business_groups_csv(request=None, status=None):
    """
    Export business groups for KoBoToolbox validation

    CSV columns:
    - bg_id: Business group ID
    - bg_name: Business group name
    - business_type: Type of business
    - business_type_detail: Specific business details
    - health_status: Current business health (red/yellow/green)
    - member_count: Number of members
    - has_sb_grant: Whether has SB grant (1/0)
    - has_pr_grant: Whether has PR grant (1/0)
    """
    from business_groups.models import BusinessGroup

    queryset = BusinessGroup.objects.prefetch_related(
        'members', 'sb_grants', 'pr_grants'
    )

    if status:
        queryset = queryset.filter(participation_status=status)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'bg_id',
        'bg_name',
        'business_type',
        'business_type_detail',
        'health_status',
        'member_count',
        'has_sb_grant',
        'has_pr_grant'
    ])

    for bg in queryset:
        has_sb = 1 if bg.sb_grants.filter(funding_status='funded').exists() else 0
        has_pr = 1 if bg.pr_grants.filter(funding_status='funded').exists() else 0

        writer.writerow([
            bg.id,
            bg.name,
            bg.business_type,
            bg.business_type_detail,
            bg.current_business_health,
            bg.members.count(),
            has_sb,
            has_pr
        ])

    if request:
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="business_groups_{date.today().isoformat()}.csv"'
        return response

    return output.getvalue()


def export_mentors_csv(request=None):
    """
    Export mentors for KoBoToolbox assignment

    CSV columns:
    - mentor_id: Mentor ID
    - mentor_name: Full name
    - office: Office location
    - country: Country
    """
    from core.models import Mentor

    queryset = Mentor.objects.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'mentor_id',
        'mentor_name',
        'office',
        'country'
    ])

    for m in queryset:
        writer.writerow([
            m.id,
            f"{m.first_name} {m.last_name}",
            m.office,
            m.country
        ])

    if request:
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="mentors_{date.today().isoformat()}.csv"'
        return response

    return output.getvalue()


def export_all_reference_data(output_dir=None):
    """
    Export all reference data CSVs for KoBoToolbox
    Returns dict of filename -> csv_content
    """
    exports = {
        'households.csv': export_households_csv(),
        'bm_cycles.csv': export_bm_cycles_csv(),
        'villages.csv': export_villages_csv(),
        'business_groups.csv': export_business_groups_csv(),
        'mentors.csv': export_mentors_csv(),
    }

    if output_dir:
        import os
        os.makedirs(output_dir, exist_ok=True)
        for filename, content in exports.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(content)

    return exports
