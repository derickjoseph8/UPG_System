"""
ESR Import URL Configuration
"""
from django.urls import path
from . import views

app_name = 'esr_import'

urlpatterns = [
    # Import pages
    path('', views.esr_import_page, name='import_page'),
    path('template/', views.download_template, name='download_template'),
    path('process/', views.process_import, name='process_import'),
    path('result/<str:batch_id>/', views.import_result, name='import_result'),
    path('history/', views.import_history, name='import_history'),

    # Household management
    path('households/', views.household_list, name='household_list'),
    path('households/<int:household_id>/', views.household_detail, name='household_detail'),
]
