from django.urls import path
from . import views

app_name = 'programs'

urlpatterns = [
    path('', views.program_list, name='program_list'),
    path('create/', views.program_create, name='program_create'),
    path('<int:pk>/', views.program_detail, name='program_detail'),
    path('<int:pk>/edit/', views.program_edit, name='program_edit'),
    path('<int:pk>/delete/', views.program_delete, name='program_delete'),
    path('<int:pk>/toggle-status/', views.program_toggle_status, name='program_toggle_status'),
    path('<int:pk>/applications/', views.program_applications, name='program_applications'),
    path('<int:pk>/apply/', views.program_apply, name='program_apply'),
    path('<int:pk>/team/', views.program_team, name='program_team'),
    path('<int:pk>/assign-mentors/', views.assign_mentors, name='assign_mentors'),
    path('<int:pk>/add-fa/', views.add_fa_to_program, name='add_fa_to_program'),
    path('applications/', views.my_applications, name='my_applications'),
    path('applications/<int:application_id>/approve/', views.approve_application, name='approve_application'),
    path('applications/<int:application_id>/reject/', views.reject_application, name='reject_application'),
    path('mentor-assignment/<int:assignment_id>/remove/', views.remove_mentor_assignment, name='remove_mentor_assignment'),
    path('notifications/', views.my_notifications, name='my_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/count/', views.get_unread_notification_count, name='notification_count'),
    path('<int:pk>/enroll-households/', views.enroll_households, name='enroll_households'),
    path('<int:pk>/beneficiaries/', views.program_beneficiaries, name='program_beneficiaries'),
    path('beneficiary/<int:beneficiary_id>/remove/', views.remove_beneficiary, name='remove_beneficiary'),
]