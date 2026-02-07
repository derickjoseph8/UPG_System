"""
Dashboard URL Configuration
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
    path('activity-logs/export/', views.export_activity_logs, name='export_activity_logs'),
]