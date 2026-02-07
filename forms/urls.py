from django.urls import path
from . import views, kobo_webhook

app_name = 'forms'

urlpatterns = [
    path('', views.forms_dashboard, name='dashboard'),

    # Form Templates
    path('templates/', views.form_template_list, name='template_list'),
    path('templates/create/', views.form_template_create, name='template_create'),
    path('templates/import/', views.import_form_template, name='import_template'),
    path('templates/import-from-kobo/', views.import_from_kobo, name='import_from_kobo'),
    path('templates/<int:pk>/builder/', views.form_template_builder, name='template_builder'),
    path('templates/<int:pk>/copy/', views.copy_form_template, name='copy_template'),
    path('api/save-template/', views.save_form_template, name='api_save_template'),

    # Form Assignments
    path('assignments/create/', views.form_assignment_create, name='assignment_create'),
    path('assignments/<int:pk>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_pk>/assign-mentor/', views.assign_to_mentor, name='assign_to_mentor'),
    path('assignments/<int:assignment_pk>/fill/', views.fill_form, name='fill_form'),

    # Submissions
    path('submissions/<int:pk>/', views.submission_detail, name='submission_detail'),
    path('templates/<int:form_template_id>/submissions/', views.form_submissions_list, name='form_submissions'),
    path('templates/<int:form_template_id>/fetch-submissions/', views.fetch_submissions_from_kobo, name='fetch_submissions'),

    # User-specific views
    path('my-assignments/', views.my_assignments, name='my_assignments'),
    path('my-fa-assignments/', views.form_fa_assignments_list, name='fa_assignments_list'),
    path('templates/<int:form_template_id>/assign-mentors/', views.form_assign_mentors, name='form_assign_mentors'),

    # KoboToolbox Integration
    path('kobo/preview/<int:form_template_id>/', views.preview_kobo_form, name='kobo_preview'),
    path('kobo/sync/<int:form_template_id>/', views.manual_sync_to_kobo, name='kobo_manual_sync'),
    path('kobo/sync-history/<int:form_template_id>/', views.kobo_sync_history, name='kobo_sync_history'),
    path('kobo/webhook-logs/', views.kobo_webhook_logs, name='kobo_webhook_logs'),

    # Webhook endpoint (no auth - validated by signature)
    path('kobo/webhook/', kobo_webhook.kobo_webhook_receiver, name='kobo_webhook'),

    # API endpoints
    path('api/stats/', views.forms_stats_api, name='forms_stats_api'),
    path('api/check-beneficiary-lookup/<int:form_template_id>/', views.check_beneficiary_lookup_api, name='check_beneficiary_lookup'),
]