from django.urls import path
from . import views
from . import maintenance_views

app_name = 'settings'

urlpatterns = [
    path('', views.settings_dashboard, name='settings_dashboard'),

    # User Management
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),

    # System Configuration
    path('config/', views.system_config, name='system_config'),
    path('config/<int:config_id>/edit/', views.config_edit, name='config_edit'),

    # User Settings
    path('user-settings/', views.user_settings, name='user_settings'),
    path('user-settings/<int:user_id>/', views.user_settings, name='user_settings_view'),

    # Audit Logs
    path('audit/', views.audit_logs, name='audit_logs'),

    # System Alerts
    path('alerts/', views.system_alerts, name='system_alerts'),
    path('alerts/create/', views.create_alert, name='create_alert'),
    path('alerts/<int:alert_id>/toggle/', views.toggle_alert, name='toggle_alert'),
    path('alerts/<int:alert_id>/delete/', views.delete_alert, name='delete_alert'),

    # Backup & Restore Management
    path('backup/', maintenance_views.backup_dashboard, name='backup_dashboard'),
    path('backup/create/', maintenance_views.create_backup, name='create_backup'),
    path('backup/create-full/', maintenance_views.create_full_backup, name='create_full_backup'),
    path('backup/<int:backup_id>/restore/', maintenance_views.restore_backup, name='restore_backup'),
    path('backup/<int:backup_id>/download/', maintenance_views.download_backup, name='download_backup'),
    path('backup/<int:backup_id>/delete/', maintenance_views.delete_backup, name='delete_backup'),
    path('backup/settings/', maintenance_views.save_backup_settings, name='save_backup_settings'),
    path('backup/cleanup/', maintenance_views.cleanup_old_backups, name='cleanup_old_backups'),

    # System Maintenance
    path('maintenance/clear-cache/', maintenance_views.clear_cache, name='clear_cache'),
    path('maintenance/cleanup-logs/', maintenance_views.cleanup_logs, name='cleanup_logs'),

    # KoboToolbox Settings
    path('kobo/', views.kobo_settings, name='kobo_settings'),
    path('kobo/test-connection/', views.kobo_test_connection, name='kobo_test_connection'),

    # Custom Role Management
    path('roles/', views.custom_role_list, name='custom_role_list'),
    path('roles/create/', views.custom_role_create, name='custom_role_create'),
    path('roles/<int:role_id>/edit/', views.custom_role_edit, name='custom_role_edit'),
    path('roles/<int:role_id>/delete/', views.custom_role_delete, name='custom_role_delete'),
    path('roles/<int:role_id>/detail/', views.custom_role_detail, name='custom_role_detail'),
]