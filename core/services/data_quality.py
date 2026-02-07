"""
Data Quality Service for UPG System
Provides automated data quality checks and scoring
Borrowed from UPG Kaduna MIS patterns
"""

from django.db.models import Q, Count
from households.models import Household, HouseholdMember


class DataQualityService:
    """
    Service for calculating data quality metrics.

    Quality scoring uses weighted severity:
    - HIGH severity issues: 3 points per record
    - MEDIUM severity issues: 2 points per record
    - LOW severity issues: 1 point per record

    Final score = 100 - (weighted_issue_score / total_records * 100)
    """

    SEVERITY_WEIGHTS = {
        'high': 3,
        'medium': 2,
        'low': 1
    }

    @classmethod
    def get_quality_report(cls, village_ids=None):
        """
        Generate comprehensive data quality report.

        Args:
            village_ids: Optional list of village IDs to filter by (for mentor view)

        Returns:
            dict: Quality report with score, issues, and recommendations
        """
        # Build base queryset
        queryset = Household.objects.all()
        if village_ids:
            queryset = queryset.filter(village_id__in=village_ids)

        total = queryset.count()
        if total == 0:
            return {
                'quality_score': 100,
                'total_records': 0,
                'issues_count': 0,
                'issues': [],
                'summary': {
                    'high_severity': 0,
                    'medium_severity': 0,
                    'low_severity': 0
                }
            }

        issues = []

        # Check 1: Missing National ID (HIGH severity)
        missing_id = queryset.filter(
            Q(national_id__isnull=True) | Q(national_id='')
        ).count()
        if missing_id > 0:
            issues.append({
                'field': 'National ID',
                'issue_type': 'missing_value',
                'count': missing_id,
                'severity': 'high',
                'percentage': round(missing_id / total * 100, 1),
                'recommendation': 'Update household records with valid ID numbers during mentoring visits'
            })

        # Check 2: Missing Phone Number (MEDIUM severity)
        missing_phone = queryset.filter(
            Q(phone_number__isnull=True) | Q(phone_number='')
        ).count()
        if missing_phone > 0:
            issues.append({
                'field': 'Phone Number',
                'issue_type': 'missing_value',
                'count': missing_phone,
                'severity': 'medium',
                'percentage': round(missing_phone / total * 100, 1),
                'recommendation': 'Collect phone numbers to enable SMS communication'
            })

        # Check 3: Households without members (HIGH severity)
        no_members = queryset.annotate(
            member_count=Count('members')
        ).filter(member_count=0).count()
        if no_members > 0:
            issues.append({
                'field': 'Household Members',
                'issue_type': 'missing_data',
                'count': no_members,
                'severity': 'high',
                'percentage': round(no_members / total * 100, 1),
                'recommendation': 'Add household member information for complete profiles'
            })

        # Check 4: Missing Village assignment (MEDIUM severity)
        no_village = queryset.filter(
            Q(village__isnull=True)
        ).count()
        if no_village > 0:
            issues.append({
                'field': 'Village',
                'issue_type': 'missing_value',
                'count': no_village,
                'severity': 'medium',
                'percentage': round(no_village / total * 100, 1),
                'recommendation': 'Assign households to their respective villages'
            })

        # Check 5: Missing head name (MEDIUM severity)
        missing_head_name = queryset.filter(
            Q(head_first_name__isnull=True) | Q(head_first_name='') |
            Q(head_last_name__isnull=True) | Q(head_last_name='')
        ).count()
        if missing_head_name > 0:
            issues.append({
                'field': 'Head Name',
                'issue_type': 'missing_value',
                'count': missing_head_name,
                'severity': 'medium',
                'percentage': round(missing_head_name / total * 100, 1),
                'recommendation': 'Complete household head name information'
            })

        # Check 6: Missing GPS coordinates (LOW severity) - if the field exists
        try:
            if hasattr(Household, 'latitude') and hasattr(Household, 'longitude'):
                no_gps = queryset.filter(
                    Q(latitude__isnull=True) | Q(longitude__isnull=True)
                ).count()
                if no_gps > 0:
                    issues.append({
                        'field': 'GPS Coordinates',
                        'issue_type': 'missing_value',
                        'count': no_gps,
                        'severity': 'low',
                        'percentage': round(no_gps / total * 100, 1),
                        'recommendation': 'Collect GPS coordinates during field visits'
                    })
        except Exception:
            pass  # GPS fields may not exist

        # Calculate weighted quality score
        issue_score = sum(
            issue['count'] * cls.SEVERITY_WEIGHTS[issue['severity']]
            for issue in issues
        )

        # Normalize score (cap at 100%)
        normalized_score = min(100, issue_score / total * 100) if total > 0 else 0
        quality_score = max(0, round(100 - normalized_score, 1))

        # Sort issues by severity (high first)
        issues = sorted(
            issues,
            key=lambda x: cls.SEVERITY_WEIGHTS[x['severity']],
            reverse=True
        )

        return {
            'quality_score': quality_score,
            'total_records': total,
            'issues_count': len(issues),
            'issues': issues,
            'summary': {
                'high_severity': len([i for i in issues if i['severity'] == 'high']),
                'medium_severity': len([i for i in issues if i['severity'] == 'medium']),
                'low_severity': len([i for i in issues if i['severity'] == 'low'])
            }
        }

    @classmethod
    def get_quality_score_only(cls, village_ids=None):
        """
        Get just the quality score (faster for dashboard cards).

        Returns:
            float: Quality score from 0-100
        """
        report = cls.get_quality_report(village_ids)
        return report['quality_score']

    @classmethod
    def get_status_from_score(cls, score):
        """
        Get status label from quality score.

        Args:
            score: Quality score (0-100)

        Returns:
            str: Status label ('excellent', 'good', 'needs_attention', 'critical')
        """
        if score >= 90:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 50:
            return 'needs_attention'
        else:
            return 'critical'
