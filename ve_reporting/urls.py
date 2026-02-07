"""
VE Reporting URL Configuration
Silent API routes for Village Enterprise reporting.
"""
from django.urls import path
from . import views

app_name = 've_reporting'

urlpatterns = [
    # Public API endpoints (VE API Key required)
    path('health/', views.HealthView.as_view(), name='health'),
    path('metadata/', views.MetadataView.as_view(), name='metadata'),
    path('summary/', views.SummaryView.as_view(), name='summary'),
    path('enrollment/', views.EnrollmentView.as_view(), name='enrollment'),
    path('beneficiaries/', views.BeneficiariesView.as_view(), name='beneficiaries'),
    path('graduation/', views.GraduationView.as_view(), name='graduation'),
    path('savings/', views.SavingsView.as_view(), name='savings'),
    path('training/', views.TrainingView.as_view(), name='training'),
    path('disbursements/', views.DisbursementsView.as_view(), name='disbursements'),
    path('milestones/', views.MilestonesView.as_view(), name='milestones'),
    path('timeseries/', views.TimeSeriesView.as_view(), name='timeseries'),

    # Admin API endpoints (MIS admin authentication required)
    path('admin/keys/', views.list_api_keys, name='list_keys'),
    path('admin/keys/create/', views.create_api_key, name='create_key'),
    path('admin/keys/<uuid:key_id>/revoke/', views.revoke_api_key, name='revoke_key'),

    # Web views for settings page (admin access)
    path('settings/keys/', views.ve_api_keys_list, name='ve_api_keys'),
    path('settings/keys/create/', views.ve_api_key_create_view, name='ve_api_key_create'),
    path('settings/keys/<uuid:key_id>/revoke/', views.ve_api_key_revoke_view, name='ve_api_key_revoke'),
]
