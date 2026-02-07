from django.urls import path
from . import views

app_name = 'upg_grants'

urlpatterns = [
    # Grant Programs (PM creates, assigns to FA)
    path('programs/', views.grant_program_list, name='grant_program_list'),
    path('programs/create/', views.grant_program_create, name='grant_program_create'),
    path('programs/<int:grant_program_id>/', views.grant_program_detail, name='grant_program_detail'),
    path('programs/<int:grant_program_id>/assign-mentors/', views.grant_assign_mentors, name='grant_assign_mentors'),

    # FA Assignment Management
    path('my-fa-assignments/', views.grant_fa_assignments_list, name='grant_fa_assignments_list'),

    # Grant application list and management
    path('applications/', views.grant_application_list, name='application_list'),
    path('applications/create/', views.grant_application_create, name='application_create_universal'),
    path('applications/create/<int:household_id>/', views.grant_application_create, name='application_create'),
    path('applications/<int:application_id>/', views.grant_application_detail, name='application_detail'),
    path('applications/<int:application_id>/review/', views.grant_application_review, name='application_review'),

    # Review dashboard
    path('reviews/pending/', views.pending_reviews, name='pending_reviews'),

    # Available grants for application
    path('available/', views.available_grants_list, name='available_grants'),
]
