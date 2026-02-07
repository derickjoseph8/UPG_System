"""
System Maintenance Views - Backup, Restore, Cache Clear, Log Cleanup
Supports system-wide backups including database, media files, and configurations
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings as django_settings
from .models import SystemBackup, SystemAuditLog, SystemConfiguration
import subprocess
import os
import shutil
import zipfile
import json
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)


def find_mysqldump():
    """Find mysqldump executable across different platforms"""
    mysqldump_in_path = shutil.which('mysqldump')
    if mysqldump_in_path:
        return mysqldump_in_path

    possible_paths = [
        '/usr/bin/mysqldump',
        '/usr/local/bin/mysqldump',
        '/usr/local/mysql/bin/mysqldump',
        'C:\\xampp\\mysql\\bin\\mysqldump.exe',
        'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe',
        'C:\\Program Files\\MySQL\\MySQL Server 5.7\\bin\\mysqldump.exe',
        '/usr/bin/mariadb-dump',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def find_mysql():
    """Find mysql client executable for restore operations"""
    mysql_in_path = shutil.which('mysql')
    if mysql_in_path:
        return mysql_in_path

    possible_paths = [
        '/usr/bin/mysql',
        '/usr/local/bin/mysql',
        '/usr/local/mysql/bin/mysql',
        'C:\\xampp\\mysql\\bin\\mysql.exe',
        'C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysql.exe',
        'C:\\Program Files\\MySQL\\MySQL Server 5.7\\bin\\mysql.exe',
        '/usr/bin/mariadb',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def get_backup_dir():
    """Get or create the backup directory"""
    backup_dir = os.path.join(django_settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# =============================================================================
# Backup Management Dashboard
# =============================================================================

@login_required
def backup_dashboard(request):
    """Main backup and restore dashboard"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'You do not have permission to access backup management.')
        return redirect('settings:settings_dashboard')

    # Get all backups
    backups = SystemBackup.objects.all().order_by('-started_at')[:50]

    # Get backup configuration
    auto_backup_enabled = False
    backup_frequency = 'daily'
    backup_retention_days = 90  # Default: 90 days recommended for most organizations

    try:
        config = SystemConfiguration.objects.get(key='auto_backup_enabled')
        auto_backup_enabled = config.get_typed_value()
    except SystemConfiguration.DoesNotExist:
        pass

    try:
        config = SystemConfiguration.objects.get(key='backup_frequency')
        backup_frequency = config.value
    except SystemConfiguration.DoesNotExist:
        pass

    try:
        config = SystemConfiguration.objects.get(key='backup_retention_days')
        backup_retention_days = config.get_typed_value()
    except SystemConfiguration.DoesNotExist:
        pass

    # Calculate storage usage
    backup_dir = get_backup_dir()
    total_size = 0
    backup_count = 0
    for filename in os.listdir(backup_dir):
        filepath = os.path.join(backup_dir, filename)
        if os.path.isfile(filepath):
            total_size += os.path.getsize(filepath)
            backup_count += 1

    context = {
        'page_title': 'Backup & Restore',
        'backups': backups,
        'auto_backup_enabled': auto_backup_enabled,
        'backup_frequency': backup_frequency,
        'backup_retention_days': backup_retention_days,
        'total_storage_used': format_file_size(total_size),
        'backup_file_count': backup_count,
    }
    return render(request, 'settings_module/backup_dashboard.html', context)


# =============================================================================
# Create Backups
# =============================================================================

@login_required
@require_POST
def create_backup(request):
    """Create a database-only backup"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        backup_dir = get_backup_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        db_settings = django_settings.DATABASES['default']
        db_engine = db_settings['ENGINE']

        # Create backup based on database type
        if 'sqlite3' in db_engine:
            return _backup_sqlite(request.user, backup_dir, timestamp)
        elif 'mysql' in db_engine:
            return _backup_mysql(request.user, backup_dir, timestamp, db_settings)
        elif 'postgresql' in db_engine:
            return _backup_postgresql(request.user, backup_dir, timestamp, db_settings)
        else:
            return JsonResponse({'success': False, 'error': f'Unsupported database: {db_engine}'}, status=500)

    except Exception as e:
        logger.error(f"Backup error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def create_full_backup(request):
    """Create a full system backup including database, media, and static files"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        backup_dir = get_backup_dir()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f'upg_full_backup_{timestamp}'
        temp_dir = os.path.join(backup_dir, f'temp_{timestamp}')
        os.makedirs(temp_dir, exist_ok=True)

        backup_record = SystemBackup.objects.create(
            name=f'{backup_name}.zip',
            backup_type='full',
            file_path=os.path.join(backup_dir, f'{backup_name}.zip'),
            started_by=request.user,
            status='running',
            notes='Full system backup: Database + Media + Configuration'
        )

        try:
            # 1. Backup Database
            db_settings = django_settings.DATABASES['default']
            db_engine = db_settings['ENGINE']
            db_backup_file = os.path.join(temp_dir, 'database.sql')

            if 'sqlite3' in db_engine:
                shutil.copy2(db_settings['NAME'], os.path.join(temp_dir, 'database.sqlite3'))
            elif 'mysql' in db_engine:
                _dump_mysql_to_file(db_backup_file, db_settings)
            elif 'postgresql' in db_engine:
                _dump_postgresql_to_file(db_backup_file, db_settings)

            # 2. Backup Media Files
            media_root = getattr(django_settings, 'MEDIA_ROOT', None)
            if media_root and os.path.exists(media_root):
                media_backup_dir = os.path.join(temp_dir, 'media')
                shutil.copytree(media_root, media_backup_dir, dirs_exist_ok=True)

            # 3. Backup Configuration (env file if exists)
            env_file = os.path.join(django_settings.BASE_DIR, '.env')
            if os.path.exists(env_file):
                shutil.copy2(env_file, os.path.join(temp_dir, 'env_backup'))

            # 4. Create backup manifest
            manifest = {
                'created_at': timestamp,
                'created_by': request.user.username,
                'backup_type': 'full',
                'database_engine': db_engine,
                'django_version': django_settings.INSTALLED_APPS,
                'includes': {
                    'database': True,
                    'media': media_root is not None and os.path.exists(media_root),
                    'env_config': os.path.exists(env_file),
                }
            }
            with open(os.path.join(temp_dir, 'manifest.json'), 'w') as f:
                json.dump(manifest, f, indent=2, default=str)

            # 5. Create ZIP archive
            zip_path = os.path.join(backup_dir, f'{backup_name}.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

            # Update backup record
            backup_record.status = 'completed'
            backup_record.file_size = os.path.getsize(zip_path)
            backup_record.completed_at = timezone.now()
            backup_record.save()

            SystemAuditLog.objects.create(
                user=request.user,
                action='create',
                model_name='SystemBackup',
                object_repr=f'Full system backup: {backup_name}.zip',
                success=True
            )

            return JsonResponse({
                'success': True,
                'message': f'Full backup created: {backup_name}.zip',
                'backup_size': format_file_size(backup_record.file_size),
                'backup_id': backup_record.id
            })

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            backup_record.status = 'failed'
            backup_record.error_message = str(e)
            backup_record.save()
            raise

    except Exception as e:
        logger.error(f"Full backup error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _backup_sqlite(user, backup_dir, timestamp):
    """Backup SQLite database"""
    db_name = django_settings.DATABASES['default']['NAME']
    backup_filename = f'upg_db_backup_{timestamp}.sqlite3'
    backup_path = os.path.join(backup_dir, backup_filename)

    backup_record = SystemBackup.objects.create(
        name=backup_filename, backup_type='database', file_path=backup_path,
        started_by=user, status='running'
    )

    try:
        shutil.copy2(db_name, backup_path)
        backup_record.status = 'completed'
        backup_record.file_size = os.path.getsize(backup_path)
        backup_record.completed_at = timezone.now()
        backup_record.save()

        return JsonResponse({
            'success': True,
            'message': f'Database backup created: {backup_filename}',
            'backup_size': format_file_size(backup_record.file_size)
        })
    except Exception as e:
        backup_record.status = 'failed'
        backup_record.error_message = str(e)
        backup_record.save()
        raise


def _backup_mysql(user, backup_dir, timestamp, db_settings):
    """Backup MySQL database"""
    backup_filename = f'upg_db_backup_{timestamp}.sql'
    backup_path = os.path.join(backup_dir, backup_filename)

    backup_record = SystemBackup.objects.create(
        name=backup_filename, backup_type='database', file_path=backup_path,
        started_by=user, status='running'
    )

    try:
        _dump_mysql_to_file(backup_path, db_settings)

        backup_record.status = 'completed'
        backup_record.file_size = os.path.getsize(backup_path)
        backup_record.completed_at = timezone.now()
        backup_record.save()

        return JsonResponse({
            'success': True,
            'message': f'Database backup created: {backup_filename}',
            'backup_size': format_file_size(backup_record.file_size)
        })
    except Exception as e:
        backup_record.status = 'failed'
        backup_record.error_message = str(e)
        backup_record.save()
        raise


def _dump_mysql_to_file(backup_path, db_settings):
    """Dump MySQL database to a file"""
    mysqldump_path = find_mysqldump()
    if not mysqldump_path:
        raise Exception('mysqldump not found. Install mysql-client: sudo apt-get install mysql-client')

    cmd = [
        mysqldump_path,
        '-h', db_settings.get('HOST', 'localhost'),
        '-P', str(db_settings.get('PORT', '3306')),
        '-u', db_settings.get('USER', 'root'),
    ]
    if db_settings.get('PASSWORD'):
        cmd.append(f'--password={db_settings["PASSWORD"]}')
    cmd.extend(['--single-transaction', '--routines', '--triggers', db_settings['NAME']])

    with open(backup_path, 'w', encoding='utf-8') as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise Exception(f'mysqldump failed: {result.stderr}')


def _backup_postgresql(user, backup_dir, timestamp, db_settings):
    """Backup PostgreSQL database"""
    backup_filename = f'upg_db_backup_{timestamp}.sql'
    backup_path = os.path.join(backup_dir, backup_filename)

    backup_record = SystemBackup.objects.create(
        name=backup_filename, backup_type='database', file_path=backup_path,
        started_by=user, status='running'
    )

    try:
        _dump_postgresql_to_file(backup_path, db_settings)

        backup_record.status = 'completed'
        backup_record.file_size = os.path.getsize(backup_path)
        backup_record.completed_at = timezone.now()
        backup_record.save()

        return JsonResponse({
            'success': True,
            'message': f'Database backup created: {backup_filename}',
            'backup_size': format_file_size(backup_record.file_size)
        })
    except Exception as e:
        backup_record.status = 'failed'
        backup_record.error_message = str(e)
        backup_record.save()
        raise


def _dump_postgresql_to_file(backup_path, db_settings):
    """Dump PostgreSQL database to a file"""
    pg_dump_path = shutil.which('pg_dump') or '/usr/bin/pg_dump'

    env = os.environ.copy()
    if db_settings.get('PASSWORD'):
        env['PGPASSWORD'] = db_settings['PASSWORD']

    cmd = [
        pg_dump_path,
        '-h', db_settings.get('HOST', 'localhost'),
        '-p', str(db_settings.get('PORT', '5432')),
        '-U', db_settings.get('USER', 'postgres'),
        '-F', 'p',
        db_settings['NAME']
    ]

    with open(backup_path, 'w', encoding='utf-8') as f:
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, env=env)

    if result.returncode != 0:
        raise Exception(f'pg_dump failed: {result.stderr}')


# =============================================================================
# Restore Backups
# =============================================================================

@login_required
@require_POST
def restore_backup(request, backup_id):
    """Restore from a backup"""
    if not request.user.is_superuser:
        return JsonResponse({'success': False, 'error': 'Only superusers can restore backups'}, status=403)

    try:
        backup = SystemBackup.objects.get(id=backup_id)

        if not os.path.exists(backup.file_path):
            return JsonResponse({'success': False, 'error': 'Backup file not found'}, status=404)

        db_settings = django_settings.DATABASES['default']
        db_engine = db_settings['ENGINE']

        # Handle full backup (ZIP)
        if backup.backup_type == 'full' and backup.file_path.endswith('.zip'):
            return _restore_full_backup(request.user, backup, db_settings, db_engine)

        # Handle database-only backup
        if 'sqlite3' in db_engine:
            return _restore_sqlite(request.user, backup, db_settings)
        elif 'mysql' in db_engine:
            return _restore_mysql(request.user, backup, db_settings)
        elif 'postgresql' in db_engine:
            return _restore_postgresql(request.user, backup, db_settings)
        else:
            return JsonResponse({'success': False, 'error': f'Unsupported database: {db_engine}'}, status=500)

    except SystemBackup.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Backup not found'}, status=404)
    except Exception as e:
        logger.error(f"Restore error: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def _restore_full_backup(user, backup, db_settings, db_engine):
    """Restore a full system backup from ZIP"""
    backup_dir = get_backup_dir()
    temp_dir = os.path.join(backup_dir, f'restore_temp_{datetime.now().strftime("%Y%m%d_%H%M%S")}')

    try:
        # Extract ZIP
        with zipfile.ZipFile(backup.file_path, 'r') as zipf:
            zipf.extractall(temp_dir)

        # Read manifest
        manifest_path = os.path.join(temp_dir, 'manifest.json')
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        else:
            manifest = {}

        # Restore database
        if 'sqlite3' in db_engine:
            sqlite_backup = os.path.join(temp_dir, 'database.sqlite3')
            if os.path.exists(sqlite_backup):
                shutil.copy2(sqlite_backup, db_settings['NAME'])
        elif 'mysql' in db_engine:
            sql_backup = os.path.join(temp_dir, 'database.sql')
            if os.path.exists(sql_backup):
                _restore_mysql_from_file(sql_backup, db_settings)
        elif 'postgresql' in db_engine:
            sql_backup = os.path.join(temp_dir, 'database.sql')
            if os.path.exists(sql_backup):
                _restore_postgresql_from_file(sql_backup, db_settings)

        # Restore media files
        media_backup = os.path.join(temp_dir, 'media')
        media_root = getattr(django_settings, 'MEDIA_ROOT', None)
        if os.path.exists(media_backup) and media_root:
            # Backup current media first
            if os.path.exists(media_root):
                media_backup_old = f"{media_root}_old_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.move(media_root, media_backup_old)
            shutil.copytree(media_backup, media_root)

        # Clean up
        shutil.rmtree(temp_dir, ignore_errors=True)

        SystemAuditLog.objects.create(
            user=user,
            action='update',
            model_name='SystemBackup',
            object_repr=f'Restored full backup: {backup.name}',
            success=True
        )

        return JsonResponse({
            'success': True,
            'message': f'Full system restored from: {backup.name}',
            'note': 'Please restart the application to apply all changes.'
        })

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def _restore_sqlite(user, backup, db_settings):
    """Restore SQLite database"""
    # Create a backup of current DB first
    current_db = db_settings['NAME']
    backup_current = f"{current_db}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(current_db, backup_current)

    try:
        shutil.copy2(backup.file_path, current_db)

        SystemAuditLog.objects.create(
            user=user, action='update', model_name='SystemBackup',
            object_repr=f'Restored database from: {backup.name}', success=True
        )

        return JsonResponse({
            'success': True,
            'message': f'Database restored from: {backup.name}',
            'note': 'Previous database saved as: ' + os.path.basename(backup_current)
        })
    except Exception as e:
        # Rollback
        shutil.copy2(backup_current, current_db)
        raise


def _restore_mysql(user, backup, db_settings):
    """Restore MySQL database"""
    _restore_mysql_from_file(backup.file_path, db_settings)

    SystemAuditLog.objects.create(
        user=user, action='update', model_name='SystemBackup',
        object_repr=f'Restored database from: {backup.name}', success=True
    )

    return JsonResponse({
        'success': True,
        'message': f'Database restored from: {backup.name}'
    })


def _restore_mysql_from_file(backup_path, db_settings):
    """Restore MySQL database from SQL file"""
    mysql_path = find_mysql()
    if not mysql_path:
        raise Exception('mysql client not found. Install mysql-client.')

    cmd = [
        mysql_path,
        '-h', db_settings.get('HOST', 'localhost'),
        '-P', str(db_settings.get('PORT', '3306')),
        '-u', db_settings.get('USER', 'root'),
    ]
    if db_settings.get('PASSWORD'):
        cmd.append(f'--password={db_settings["PASSWORD"]}')
    cmd.append(db_settings['NAME'])

    with open(backup_path, 'r', encoding='utf-8') as f:
        result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise Exception(f'MySQL restore failed: {result.stderr}')


def _restore_postgresql(user, backup, db_settings):
    """Restore PostgreSQL database"""
    _restore_postgresql_from_file(backup.file_path, db_settings)

    SystemAuditLog.objects.create(
        user=user, action='update', model_name='SystemBackup',
        object_repr=f'Restored database from: {backup.name}', success=True
    )

    return JsonResponse({
        'success': True,
        'message': f'Database restored from: {backup.name}'
    })


def _restore_postgresql_from_file(backup_path, db_settings):
    """Restore PostgreSQL database from SQL file"""
    psql_path = shutil.which('psql') or '/usr/bin/psql'

    env = os.environ.copy()
    if db_settings.get('PASSWORD'):
        env['PGPASSWORD'] = db_settings['PASSWORD']

    cmd = [
        psql_path,
        '-h', db_settings.get('HOST', 'localhost'),
        '-p', str(db_settings.get('PORT', '5432')),
        '-U', db_settings.get('USER', 'postgres'),
        '-d', db_settings['NAME'],
        '-f', backup_path
    ]

    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, env=env)
    if result.returncode != 0:
        raise Exception(f'PostgreSQL restore failed: {result.stderr}')


# =============================================================================
# Backup Management
# =============================================================================

@login_required
def download_backup(request, backup_id):
    """Download a backup file"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        messages.error(request, 'Permission denied')
        return redirect('settings:backup_dashboard')

    try:
        backup = SystemBackup.objects.get(id=backup_id)

        if not os.path.exists(backup.file_path):
            messages.error(request, 'Backup file not found on disk')
            return redirect('settings:backup_dashboard')

        response = FileResponse(
            open(backup.file_path, 'rb'),
            as_attachment=True,
            filename=backup.name
        )
        return response

    except SystemBackup.DoesNotExist:
        messages.error(request, 'Backup not found')
        return redirect('settings:backup_dashboard')


@login_required
@require_POST
def delete_backup(request, backup_id):
    """Delete a backup"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        backup = SystemBackup.objects.get(id=backup_id)
        backup_name = backup.name

        # Delete file if exists
        if os.path.exists(backup.file_path):
            os.remove(backup.file_path)

        backup.delete()

        SystemAuditLog.objects.create(
            user=request.user, action='delete', model_name='SystemBackup',
            object_repr=f'Deleted backup: {backup_name}', success=True
        )

        return JsonResponse({'success': True, 'message': f'Backup deleted: {backup_name}'})

    except SystemBackup.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Backup not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Automated Backup Configuration
# =============================================================================

@login_required
@require_POST
def save_backup_settings(request):
    """Save automated backup configuration"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        auto_enabled = request.POST.get('auto_backup_enabled') == 'on'
        frequency = request.POST.get('backup_frequency', 'daily')
        retention_days = min(int(request.POST.get('backup_retention_days', 90)), 90)  # Max 90 days

        # Save configurations
        configs = [
            ('auto_backup_enabled', str(auto_enabled).lower(), 'boolean', 'Enable automatic backups'),
            ('backup_frequency', frequency, 'string', 'Backup frequency: daily, weekly, monthly'),
            ('backup_retention_days', str(retention_days), 'integer', 'Days to keep backups'),
        ]

        for key, value, setting_type, description in configs:
            config, created = SystemConfiguration.objects.update_or_create(
                key=key,
                defaults={
                    'value': value,
                    'setting_type': setting_type,
                    'description': description,
                    'category': 'backup',
                    'modified_by': request.user,
                }
            )
            if created:
                config.created_by = request.user
                config.save()

        # Generate cron schedule hint
        cron_hint = ""
        if auto_enabled:
            if frequency == 'daily':
                cron_hint = "0 2 * * * cd /var/www/upg_system && /var/www/upg_system/venv/bin/python manage.py create_backup"
            elif frequency == 'weekly':
                cron_hint = "0 2 * * 0 cd /var/www/upg_system && /var/www/upg_system/venv/bin/python manage.py create_backup"
            elif frequency == 'monthly':
                cron_hint = "0 2 1 * * cd /var/www/upg_system && /var/www/upg_system/venv/bin/python manage.py create_backup"

        SystemAuditLog.objects.create(
            user=request.user, action='update', model_name='SystemConfiguration',
            object_repr='Updated backup settings', success=True
        )

        return JsonResponse({
            'success': True,
            'message': 'Backup settings saved successfully!',
            'cron_hint': cron_hint
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def cleanup_old_backups(request):
    """Clean up backups older than retention period"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        # Get retention period (default 90 days, max 90 days)
        retention_days = 90
        try:
            config = SystemConfiguration.objects.get(key='backup_retention_days')
            retention_days = min(config.get_typed_value(), 90)  # Enforce max 90 days
        except SystemConfiguration.DoesNotExist:
            pass

        cutoff_date = timezone.now() - timedelta(days=retention_days)

        # Find old backups
        old_backups = SystemBackup.objects.filter(
            started_at__lt=cutoff_date,
            status='completed'
        )

        deleted_count = 0
        deleted_size = 0

        for backup in old_backups:
            if os.path.exists(backup.file_path):
                deleted_size += os.path.getsize(backup.file_path)
                os.remove(backup.file_path)
            backup.delete()
            deleted_count += 1

        SystemAuditLog.objects.create(
            user=request.user, action='delete', model_name='SystemBackup',
            object_repr=f'Cleaned up {deleted_count} old backups ({format_file_size(deleted_size)})',
            success=True
        )

        return JsonResponse({
            'success': True,
            'message': f'Deleted {deleted_count} backups older than {retention_days} days',
            'space_freed': format_file_size(deleted_size)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# =============================================================================
# Cache and Log Management
# =============================================================================

@login_required
@require_POST
def clear_cache(request):
    """Clear Django cache"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        from django.core.cache import cache
        cache.clear()

        SystemAuditLog.objects.create(
            user=request.user, action='delete', model_name='Cache',
            object_repr='System cache cleared', success=True
        )

        return JsonResponse({'success': True, 'message': 'Cache cleared successfully!'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_POST
def cleanup_logs(request):
    """Clean up old audit logs"""
    if not (request.user.is_superuser or request.user.role == 'ict_admin'):
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)

    try:
        days_to_keep = int(request.POST.get('days', 90))
        cutoff_date = timezone.now() - timedelta(days=days_to_keep)

        logs_to_delete = SystemAuditLog.objects.filter(timestamp__lt=cutoff_date)
        count = logs_to_delete.count()
        logs_to_delete.delete()

        SystemAuditLog.objects.create(
            user=request.user, action='delete', model_name='SystemAuditLog',
            object_repr=f'Cleaned up {count} audit logs older than {days_to_keep} days',
            success=True
        )

        return JsonResponse({
            'success': True,
            'message': f'Deleted {count} log entries older than {days_to_keep} days'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
