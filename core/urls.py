from django.urls import path
from . import views
from . import kobo_views

app_name = 'core'

urlpatterns = [
    path('esr-imports/', views.esr_import_list, name='esr_import_list'),
    path('esr-imports/create/', views.esr_import_create, name='esr_import_create'),
    path('esr-imports/<int:pk>/', views.esr_import_detail, name='esr_import_detail'),

    # Mentor-Village Assignment
    path('assign-mentor/', views.assign_mentor_to_village, name='assign_mentor_to_village'),
    path('mentor-villages/', views.mentor_villages_list, name='mentor_villages_list'),
    path('remove-mentor-village/<int:mentor_id>/<int:village_id>/', views.remove_mentor_village, name='remove_mentor_village'),

    # BM Cycle Management
    path('bm-cycles/', views.bm_cycle_list, name='bm_cycle_list'),
    path('bm-cycles/create/', views.bm_cycle_create, name='bm_cycle_create'),
    path('bm-cycles/<int:cycle_id>/edit/', views.bm_cycle_edit, name='bm_cycle_edit'),
    path('bm-cycles/<int:cycle_id>/delete/', views.bm_cycle_delete, name='bm_cycle_delete'),

    # API endpoints
    path('api/bm-cycles/', views.api_bm_cycles, name='api_bm_cycles'),
    path('api/mentors/', views.api_mentors, name='api_mentors'),

    # KoBoToolbox CSV Exports
    path('kobo/export/', kobo_views.kobo_export_dashboard, name='kobo_export_dashboard'),
    path('kobo/export/households/', kobo_views.export_households, name='kobo_export_households'),
    path('kobo/export/bm-cycles/', kobo_views.export_bm_cycles, name='kobo_export_bm_cycles'),
    path('kobo/export/villages/', kobo_views.export_villages, name='kobo_export_villages'),
    path('kobo/export/business-groups/', kobo_views.export_business_groups, name='kobo_export_business_groups'),
    path('kobo/export/mentors/', kobo_views.export_mentors, name='kobo_export_mentors'),
    path('kobo/export/all/', kobo_views.export_all_zip, name='kobo_export_all'),

    # KoBoToolbox API Integration
    path('kobo/settings/', kobo_views.kobo_settings, name='kobo_settings'),
    path('kobo/push/', kobo_views.push_to_kobo, name='kobo_push'),
]