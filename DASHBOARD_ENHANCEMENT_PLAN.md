# UPG Kenya Dashboard Enhancement Plan
## Borrowing Features from UPG Kaduna MIS

**Date:** February 2, 2026
**Project:** UPG System (Kenya)
**Reference:** UPG MIS Kaduna

---

## Executive Summary

This plan outlines enhancements to the UPG Kenya dashboard by borrowing proven features from the UPG Kaduna MIS. The focus is on adding visualizations, alerts, progress tracking, and data quality indicators while maintaining the existing Django/Bootstrap architecture.

**Note:** Asset Transfer features are excluded as they are Kaduna-specific.

---

## Current State vs Target State

### UPG Kenya Dashboard (Current)
| Feature | Status |
|---------|--------|
| Role-based dashboards | ✅ 6 types (Admin, Mentor, Executive, M&E, Field Associate, General) |
| Basic statistics | ✅ Count-based cards |
| Charts/Visualizations | ❌ None |
| Trend Analysis | ❌ None |
| Alert System | ❌ None |
| Target vs Actual KPIs | ❌ None |
| Data Quality Indicators | ❌ None |
| Progress Bars | ❌ None |
| Geographic Breakdown | ⚠️ Basic counts only |

### Features to Borrow from Kaduna
1. **Chart.js Visualizations** - Bar, Line, Doughnut charts
2. **KPI Cards with Targets** - Actual vs Target with status indicators
3. **Alert Banners** - Actionable alerts for pending items
4. **Progress Indicators** - Visual progress bars with color coding
5. **Data Quality Score** - Automated profile completeness checks
6. **Geographic Distribution** - Breakdown by Village/SubCounty
7. **Recent Activity Timeline** - Enhanced activity feed
8. **Trend Analysis** - Historical data comparison

---

## Implementation Plan

### Phase 1: Chart.js Integration (HIGH PRIORITY)
**Estimated Effort:** 2-3 hours

#### 1.1 Add Chart.js to Base Template
**File:** `templates/base.html`

```html
<!-- Add before closing </body> -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1"></script>
```

#### 1.2 Create Chart Include Templates
**New Files:**
- `templates/includes/charts/bar_chart.html`
- `templates/includes/charts/line_chart.html`
- `templates/includes/charts/doughnut_chart.html`

**Example Bar Chart Template:**
```html
<!-- templates/includes/charts/bar_chart.html -->
<canvas id="{{ chart_id }}" height="{{ height|default:300 }}"></canvas>
<script>
new Chart(document.getElementById('{{ chart_id }}'), {
  type: 'bar',
  data: {
    labels: {{ labels|safe }},
    datasets: [{
      label: '{{ dataset_label }}',
      data: {{ values|safe }},
      backgroundColor: '{{ bg_color|default:"rgba(54, 162, 235, 0.8)" }}'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: 'top' } },
    scales: { y: { beginAtZero: true } }
  }
});
</script>
```

#### 1.3 Update Dashboard Views
**File:** `dashboard/views.py`

Add data for charts:
```python
def get_enrollment_trend():
    """Get enrollment data for last 6 months"""
    from django.db.models.functions import TruncMonth

    six_months_ago = timezone.now() - timedelta(days=180)
    trend = Household.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')

    return {
        'labels': [item['month'].strftime('%b %Y') for item in trend],
        'values': [item['count'] for item in trend]
    }

def get_status_distribution():
    """Get households by participation status"""
    distribution = HouseholdProgram.objects.values(
        'participation_status'
    ).annotate(count=Count('id'))

    return {
        'labels': [item['participation_status'].title() for item in distribution],
        'values': [item['count'] for item in distribution]
    }
```

---

### Phase 2: KPI Cards with Targets (HIGH PRIORITY)
**Estimated Effort:** 2 hours

#### 2.1 Create KPI Card Component
**New File:** `templates/includes/kpi_card.html`

```html
<div class="card border-0 shadow-sm h-100">
  <div class="card-body">
    <div class="d-flex justify-content-between align-items-start">
      <div>
        <p class="text-muted mb-1">{{ title }}</p>
        <h3 class="mb-2">{{ value }}</h3>
        {% if target %}
        <div class="progress mb-2" style="height: 6px;">
          <div class="progress-bar bg-{% if percentage >= 80 %}success{% elif percentage >= 50 %}warning{% else %}danger{% endif %}"
               style="width: {{ percentage }}%"></div>
        </div>
        <small class="text-muted">{{ value }} / {{ target }} ({{ percentage }}%)</small>
        {% endif %}
      </div>
      <div class="bg-{{ icon_bg|default:'light' }} rounded-3 p-3">
        <i class="fas {{ icon }} text-{{ icon_color|default:'primary' }} fs-4"></i>
      </div>
    </div>
    {% if trend %}
    <div class="mt-2">
      <small class="text-{% if trend == 'up' %}success{% elif trend == 'down' %}danger{% else %}secondary{% endif %}">
        <i class="fas fa-arrow-{{ trend }}"></i> {{ trend_text }}
      </small>
    </div>
    {% endif %}
  </div>
</div>
```

#### 2.2 Usage in Dashboard
```html
{% include 'includes/kpi_card.html' with
    title='Enrollment Progress'
    value=stats.active_households
    target=1000
    percentage=85
    icon='fa-users'
    icon_color='primary'
    icon_bg='primary-subtle'
    trend='up'
    trend_text='12% from last month'
%}
```

---

### Phase 3: Alert System (MEDIUM PRIORITY)
**Estimated Effort:** 1.5 hours

#### 3.1 Create Alert Banner Component
**New File:** `templates/includes/alert_banner.html`

```html
{% if count > 0 %}
<div class="alert alert-{{ severity|default:'warning' }} d-flex align-items-center gap-3 mb-3">
  <i class="fas {{ icon }} fs-4"></i>
  <div class="flex-grow-1">
    <strong>{{ count }} {{ title }}</strong>
    <p class="mb-0 small text-muted">{{ description }}</p>
  </div>
  <a href="{{ action_url }}" class="btn btn-sm btn-{{ severity|default:'warning' }}">
    {{ action_text|default:'View' }}
  </a>
</div>
{% endif %}
```

#### 3.2 Add Alert Data to Dashboard Views
**File:** `dashboard/views.py`

```python
def get_dashboard_alerts(user):
    """Generate alerts based on system state"""
    alerts = []

    # Overdue mentoring visits (for M&E and Admin)
    if user.role in ['me_staff', 'ict_admin'] or user.is_superuser:
        overdue_visits = MentoringVisit.objects.filter(
            visit_date__lt=timezone.now().date() - timedelta(days=30),
            completed=False
        ).count()
        if overdue_visits > 0:
            alerts.append({
                'count': overdue_visits,
                'title': 'Overdue Mentoring Visits',
                'description': 'Visits scheduled but not completed',
                'severity': 'danger',
                'icon': 'fa-exclamation-triangle',
                'action_url': '/training/mentoring-visits/?status=overdue'
            })

    # Pending grant applications
    pending_grants = HouseholdGrantApplication.objects.filter(
        status='submitted'
    ).count()
    if pending_grants > 0:
        alerts.append({
            'count': pending_grants,
            'title': 'Pending Grant Applications',
            'description': 'Awaiting review and approval',
            'severity': 'warning',
            'icon': 'fa-clock',
            'action_url': '/grants/applications/?status=pending'
        })

    # At-risk households
    at_risk = HouseholdProgram.objects.filter(
        participation_status='at_risk'
    ).count()
    if at_risk > 0:
        alerts.append({
            'count': at_risk,
            'title': 'At-Risk Households',
            'description': 'Require immediate attention',
            'severity': 'danger',
            'icon': 'fa-user-times',
            'action_url': '/households/?status=at_risk'
        })

    return alerts
```

---

### Phase 4: Data Quality Indicators (MEDIUM PRIORITY)
**Estimated Effort:** 2 hours

#### 4.1 Create Data Quality Service
**New File:** `core/services/data_quality.py`

```python
from django.db.models import Q, Count
from households.models import Household, HouseholdMember

class DataQualityService:
    """Service for calculating data quality metrics"""

    SEVERITY_WEIGHTS = {'high': 3, 'medium': 2, 'low': 1}

    @classmethod
    def get_quality_report(cls):
        """Generate comprehensive data quality report"""
        total = Household.objects.count()
        if total == 0:
            return {'quality_score': 100, 'issues': [], 'total_records': 0}

        issues = []

        # Missing National ID (HIGH severity)
        missing_id = Household.objects.filter(
            Q(national_id__isnull=True) | Q(national_id='')
        ).count()
        if missing_id > 0:
            issues.append({
                'field': 'National ID',
                'issue_type': 'missing_value',
                'count': missing_id,
                'severity': 'high',
                'percentage': round(missing_id / total * 100, 1),
                'recommendation': 'Update household records with valid ID numbers'
            })

        # Missing Phone Number (MEDIUM severity)
        missing_phone = Household.objects.filter(
            Q(phone_number__isnull=True) | Q(phone_number='')
        ).count()
        if missing_phone > 0:
            issues.append({
                'field': 'Phone Number',
                'issue_type': 'missing_value',
                'count': missing_phone,
                'severity': 'medium',
                'percentage': round(missing_phone / total * 100, 1),
                'recommendation': 'Collect phone numbers during next mentoring visit'
            })

        # Households without members (HIGH severity)
        no_members = Household.objects.annotate(
            member_count=Count('members')
        ).filter(member_count=0).count()
        if no_members > 0:
            issues.append({
                'field': 'Household Members',
                'issue_type': 'missing_data',
                'count': no_members,
                'severity': 'high',
                'percentage': round(no_members / total * 100, 1),
                'recommendation': 'Add household member information'
            })

        # Missing Village assignment (MEDIUM severity)
        no_village = Household.objects.filter(
            Q(village__isnull=True)
        ).count()
        if no_village > 0:
            issues.append({
                'field': 'Village',
                'issue_type': 'missing_value',
                'count': no_village,
                'severity': 'medium',
                'percentage': round(no_village / total * 100, 1),
                'recommendation': 'Assign households to their villages'
            })

        # Calculate weighted quality score
        issue_score = sum(
            issue['count'] * cls.SEVERITY_WEIGHTS[issue['severity']]
            for issue in issues
        ) / total * 100 if total > 0 else 0

        quality_score = max(0, round(100 - issue_score, 1))

        return {
            'quality_score': quality_score,
            'total_records': total,
            'issues_count': len(issues),
            'issues': sorted(issues, key=lambda x: cls.SEVERITY_WEIGHTS[x['severity']], reverse=True),
            'summary': {
                'high_severity': len([i for i in issues if i['severity'] == 'high']),
                'medium_severity': len([i for i in issues if i['severity'] == 'medium']),
                'low_severity': len([i for i in issues if i['severity'] == 'low'])
            }
        }
```

#### 4.2 Data Quality Widget Template
**New File:** `templates/includes/data_quality_widget.html`

```html
<div class="card">
  <div class="card-header d-flex justify-content-between align-items-center">
    <h5 class="mb-0"><i class="fas fa-clipboard-check me-2"></i>Data Quality</h5>
    <span class="badge fs-6 bg-{% if quality.quality_score >= 80 %}success{% elif quality.quality_score >= 60 %}warning{% else %}danger{% endif %}">
      {{ quality.quality_score }}%
    </span>
  </div>
  <div class="card-body">
    <div class="progress mb-3" style="height: 10px;">
      <div class="progress-bar bg-{% if quality.quality_score >= 80 %}success{% elif quality.quality_score >= 60 %}warning{% else %}danger{% endif %}"
           style="width: {{ quality.quality_score }}%"></div>
    </div>

    {% if quality.issues %}
    <h6 class="mb-2">Issues Found ({{ quality.issues_count }})</h6>
    <ul class="list-group list-group-flush">
      {% for issue in quality.issues %}
      <li class="list-group-item d-flex justify-content-between align-items-center px-0">
        <div>
          <span class="badge me-2 bg-{% if issue.severity == 'high' %}danger{% elif issue.severity == 'medium' %}warning{% else %}secondary{% endif %}">
            {{ issue.severity|upper }}
          </span>
          <strong>{{ issue.field }}:</strong> {{ issue.count }} records
        </div>
        <span class="text-muted">{{ issue.percentage }}%</span>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <div class="text-center text-success py-3">
      <i class="fas fa-check-circle fa-2x mb-2"></i>
      <p class="mb-0">All records are complete!</p>
    </div>
    {% endif %}
  </div>
</div>
```

---

### Phase 5: Geographic Distribution (MEDIUM PRIORITY)
**Estimated Effort:** 1.5 hours

#### 5.1 Add Geographic Breakdown Functions
**File:** `dashboard/views.py`

```python
def get_geographic_distribution():
    """Get household distribution by geography"""
    from django.db.models import Count

    # By SubCounty
    by_subcounty = list(Household.objects.values(
        name=F('village__subcounty_obj__name')
    ).annotate(
        count=Count('id')
    ).order_by('-count'))

    # By Village (top 10)
    by_village = list(Household.objects.values(
        name=F('village__name')
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10])

    return {
        'by_subcounty': by_subcounty,
        'by_village': by_village,
        'subcounty_labels': [item['name'] or 'Unknown' for item in by_subcounty],
        'subcounty_values': [item['count'] for item in by_subcounty],
        'village_labels': [item['name'] or 'Unknown' for item in by_village],
        'village_values': [item['count'] for item in by_village]
    }
```

#### 5.2 Geographic Chart in Dashboard
```html
<div class="card">
  <div class="card-header">
    <h5><i class="fas fa-map-marked-alt me-2"></i>Households by SubCounty</h5>
  </div>
  <div class="card-body">
    <canvas id="geographicChart" height="300"></canvas>
  </div>
</div>

<script>
new Chart(document.getElementById('geographicChart'), {
  type: 'bar',
  data: {
    labels: {{ geographic.subcounty_labels|safe }},
    datasets: [{
      label: 'Households',
      data: {{ geographic.subcounty_values|safe }},
      backgroundColor: [
        'rgba(54, 162, 235, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)'
      ]
    }]
  },
  options: {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } }
  }
});
</script>
```

---

### Phase 6: Progress Indicators (LOW PRIORITY)
**Estimated Effort:** 1 hour

#### 6.1 Progress Bar Component
**New File:** `templates/includes/progress_indicator.html`

```html
<div class="mb-3">
  <div class="d-flex justify-content-between mb-1">
    <span class="fw-medium">{{ label }}</span>
    <span class="text-{% if percentage >= 80 %}success{% elif percentage >= 50 %}warning{% else %}danger{% endif %}">
      {{ current }} / {{ target }} ({{ percentage|floatformat:0 }}%)
    </span>
  </div>
  <div class="progress" style="height: {{ height|default:'8' }}px;">
    <div class="progress-bar bg-{% if percentage >= 80 %}success{% elif percentage >= 50 %}warning{% else %}danger{% endif %}"
         role="progressbar"
         style="width: {{ percentage|default:0 }}%"
         aria-valuenow="{{ percentage }}"
         aria-valuemin="0"
         aria-valuemax="100">
    </div>
  </div>
  {% if description %}
  <small class="text-muted">{{ description }}</small>
  {% endif %}
</div>
```

---

## Files Summary

### New Files to Create
| File | Purpose |
|------|---------|
| `templates/includes/charts/bar_chart.html` | Reusable bar chart |
| `templates/includes/charts/line_chart.html` | Reusable line chart |
| `templates/includes/charts/doughnut_chart.html` | Reusable pie chart |
| `templates/includes/kpi_card.html` | KPI card with targets |
| `templates/includes/alert_banner.html` | Alert banner |
| `templates/includes/data_quality_widget.html` | Data quality display |
| `templates/includes/progress_indicator.html` | Progress bar |
| `core/services/data_quality.py` | Data quality service |

### Files to Modify
| File | Changes |
|------|---------|
| `templates/base.html` | Add Chart.js CDN |
| `dashboard/views.py` | Add chart data, alerts, KPIs, quality |
| `templates/dashboard/admin_dashboard.html` | Add all new components |
| `templates/dashboard/mentor_dashboard.html` | Add progress indicators |
| `templates/dashboard/me_dashboard.html` | Add data quality widget |
| `templates/dashboard/executive_dashboard.html` | Add trend charts |

---

## Implementation Priority

| Phase | Feature | Priority | Effort | Impact |
|-------|---------|----------|--------|--------|
| 1 | Chart.js Integration | HIGH | 2-3 hrs | HIGH |
| 2 | KPI Cards with Targets | HIGH | 2 hrs | HIGH |
| 3 | Alert System | MEDIUM | 1.5 hrs | MEDIUM |
| 4 | Data Quality Indicators | MEDIUM | 2 hrs | MEDIUM |
| 5 | Geographic Distribution | MEDIUM | 1.5 hrs | MEDIUM |
| 6 | Progress Indicators | LOW | 1 hr | LOW |

**Total Estimated Effort:** 10-12 hours

---

## Verification Checklist

### Testing
- [ ] Charts render correctly with real data
- [ ] Charts are responsive on mobile devices
- [ ] KPI cards show accurate calculations
- [ ] Progress bars reflect actual vs target
- [ ] Alert banners appear/disappear correctly
- [ ] Data quality score calculates properly
- [ ] Geographic breakdown matches database

### Role-Based Testing
- [ ] Admin sees full dashboard with all features
- [ ] Mentor sees relevant progress indicators
- [ ] M&E sees data quality widget
- [ ] Executive sees high-level trend charts

### Browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Mobile responsive

---

## Excluded Features

The following Kaduna features are **NOT** included:
- **Asset Transfer** - Kaduna-specific program
- **GIS/Mapping with Leaflet** - Requires GPS coordinates not collected in Kenya
- **Payment Gateway Integration** - Different payment systems in Kenya
- **External Integrations** (NIMC, KADSMIS) - Nigeria-specific systems

---

## Notes

- All enhancements maintain existing Django/Bootstrap architecture
- Backward compatible - no existing features removed
- Incremental approach - can implement phases independently
- Uses existing model relationships where possible

---

*Plan Created: February 2, 2026*
*Reference: UPG MIS Kaduna Dashboard Implementation*
