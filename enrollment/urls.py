from django.urls import path
from . import views

app_name = 'enrollment'

urlpatterns = [
    path('', views.enrollment_dashboard, name='dashboard'),
    path('applications/', views.application_list, name='application_list'),
    path('applications/create/', views.application_create, name='application_create'),
    path('applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('applications/<int:application_id>/screen/', views.application_screen, name='application_screen'),
    path('applications/<int:application_id>/approve/', views.application_approve, name='application_approve'),

    # AJAX endpoints
    path('api/validate-id/', views.validate_id_number, name='validate_id'),
    path('api/validate-phone/', views.validate_phone_number, name='validate_phone'),
]
