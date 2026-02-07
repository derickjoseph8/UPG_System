"""
Management command for creating automated backups.
Can be scheduled via cron or Windows Task Scheduler.

Usage:
    python manage.py create_backup                    # Database backup (keeps all backups)
    python manage.py create_backup --full             # Full system backup (keeps all backups)
    python manage.py create_backup --cleanup          # Also cleanup old backups (uses retention settings)
    python manage.py create_backup --cleanup-days=60  # Cleanup backups older than 60 days

IMPORTANT: By default, backups are PRESERVED to maintain multiple restore points.
Cleanup only runs when explicitly requested with --cleanup flag.

Cron examples (daily backups, monthly cleanup):
    Daily at 2 AM (keeps all backups):
        0 2 * * * cd /var/www/upg_system && /var/www/upg_system/venv/bin/python manage.py create_backup --full

    Monthly cleanup (1st of month at 3 AM, keeps 90 days):
        0 3 1 * * cd /var/www/upg_system && /var/www/upg_system/venv/bin/python manage.py create_backup --cleanup-days=90
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import os
import shutil
import subprocess
import zipfile
import json
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create a system backup (database and optionally media files)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Create full system backup including media files',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Also cleanup old backups based on retention settings (default: keep all backups)',
        )
        parser.add_argument(
            '--cleanup-days',
            type=int,
            help='Cleanup backups older than specified days (max 90, implies --cleanup)',
        )
        parser.add_argument(
            '--cleanup-only',
            action='store_true',
            help='Only run cleanup without creating a new backup',
        )

    def handle(self, *args, **options):
        from settings_module.models import SystemBackup, SystemConfiguration

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Determine if cleanup should run (and with what retention)
        cleanup_days = options.get('cleanup_days')
        should_cleanup = options['cleanup'] or cleanup_days is not None

        try:
            # Create backup unless --cleanup-only is specified
            if not options.get('cleanup_only'):
                self.stdout.write('Starting backup process...')

                if options['full']:
                    self.create_full_backup(backup_dir, timestamp)
                else:
                    self.create_db_backup(backup_dir, timestamp)

                self.stdout.write(self.style.SUCCESS('Backup completed successfully!'))

            # Run cleanup if explicitly requested
            if should_cleanup:
                self.cleanup_old_backups(cleanup_days)
            else:
                # Show how many backups are being retained
                backup_count = SystemBackup.objects.filter(status='completed').count()
                self.stdout.write(f'Retaining all {backup_count} existing backups (use --cleanup to remove old ones)')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Backup failed: {str(e)}'))
            logger.error(f'Automated backup failed: {str(e)}')
            raise

    def create_db_backup(self, backup_dir, timestamp):
        """Create database-only backup"""
        from settings_module.models import SystemBackup

        db_settings = settings.DATABASES['default']
        db_engine = db_settings['ENGINE']

        if 'sqlite3' in db_engine:
            backup_filename = f'upg_db_backup_{timestamp}.sqlite3'
            backup_path = os.path.join(backup_dir, backup_filename)
            shutil.copy2(db_settings['NAME'], backup_path)

        elif 'mysql' in db_engine:
            backup_filename = f'upg_db_backup_{timestamp}.sql'
            backup_path = os.path.join(backup_dir, backup_filename)
            self._dump_mysql(backup_path, db_settings)

        elif 'postgresql' in db_engine:
            backup_filename = f'upg_db_backup_{timestamp}.sql'
            backup_path = os.path.join(backup_dir, backup_filename)
            self._dump_postgresql(backup_path, db_settings)

        else:
            raise Exception(f'Unsupported database engine: {db_engine}')

        # Create backup record
        backup_record = SystemBackup.objects.create(
            name=backup_filename,
            backup_type='database',
            file_path=backup_path,
            status='completed',
            file_size=os.path.getsize(backup_path),
            completed_at=timezone.now(),
            notes='Automated backup via management command'
        )

        self.stdout.write(f'Database backup created: {backup_filename} ({self._format_size(backup_record.file_size)})')

    def create_full_backup(self, backup_dir, timestamp):
        """Create full system backup"""
        from settings_module.models import SystemBackup

        backup_name = f'upg_full_backup_{timestamp}'
        temp_dir = os.path.join(backup_dir, f'temp_{timestamp}')
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 1. Backup Database
            db_settings = settings.DATABASES['default']
            db_engine = db_settings['ENGINE']

            if 'sqlite3' in db_engine:
                shutil.copy2(db_settings['NAME'], os.path.join(temp_dir, 'database.sqlite3'))
            elif 'mysql' in db_engine:
                self._dump_mysql(os.path.join(temp_dir, 'database.sql'), db_settings)
            elif 'postgresql' in db_engine:
                self._dump_postgresql(os.path.join(temp_dir, 'database.sql'), db_settings)

            # 2. Backup Media Files
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root and os.path.exists(media_root):
                shutil.copytree(media_root, os.path.join(temp_dir, 'media'), dirs_exist_ok=True)
                self.stdout.write('Media files backed up')

            # 3. Backup Configuration
            env_file = os.path.join(settings.BASE_DIR, '.env')
            if os.path.exists(env_file):
                shutil.copy2(env_file, os.path.join(temp_dir, 'env_backup'))

            # 4. Create manifest
            manifest = {
                'created_at': timestamp,
                'created_by': 'automated_backup',
                'backup_type': 'full',
                'database_engine': db_engine,
            }
            with open(os.path.join(temp_dir, 'manifest.json'), 'w') as f:
                json.dump(manifest, f, indent=2)

            # 5. Create ZIP
            zip_path = os.path.join(backup_dir, f'{backup_name}.zip')
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)

            # Cleanup temp
            shutil.rmtree(temp_dir, ignore_errors=True)

            # Create backup record
            backup_record = SystemBackup.objects.create(
                name=f'{backup_name}.zip',
                backup_type='full',
                file_path=zip_path,
                status='completed',
                file_size=os.path.getsize(zip_path),
                completed_at=timezone.now(),
                notes='Automated full backup via management command'
            )

            self.stdout.write(f'Full backup created: {backup_name}.zip ({self._format_size(backup_record.file_size)})')

        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    def cleanup_old_backups(self, override_days=None):
        """Cleanup backups older than retention period

        Args:
            override_days: If provided, use this instead of system config
        """
        from settings_module.models import SystemBackup, SystemConfiguration

        # Determine retention period (max 90 days)
        MAX_RETENTION = 90
        if override_days is not None:
            retention_days = min(override_days, MAX_RETENTION)
            if override_days > MAX_RETENTION:
                self.stdout.write(self.style.WARNING(f'Retention capped at maximum {MAX_RETENTION} days'))
            self.stdout.write(f'Using specified retention period: {retention_days} days')
        else:
            retention_days = 90  # Default: 90 days
            try:
                config = SystemConfiguration.objects.get(key='backup_retention_days')
                retention_days = min(config.get_typed_value(), MAX_RETENTION)
                self.stdout.write(f'Using configured retention period: {retention_days} days')
            except:
                self.stdout.write(f'Using default retention period: {retention_days} days')

        cutoff_date = timezone.now() - timedelta(days=retention_days)
        self.stdout.write(f'Removing backups older than {cutoff_date.strftime("%Y-%m-%d")}...')

        old_backups = SystemBackup.objects.filter(
            started_at__lt=cutoff_date,
            status='completed'
        )

        deleted_count = 0
        deleted_size = 0

        for backup in old_backups:
            if backup.file_path and os.path.exists(backup.file_path):
                try:
                    deleted_size += os.path.getsize(backup.file_path)
                    os.remove(backup.file_path)
                except OSError as e:
                    self.stdout.write(self.style.WARNING(f'Could not delete file {backup.file_path}: {e}'))
            backup.delete()
            deleted_count += 1

        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Cleaned up {deleted_count} old backups ({self._format_size(deleted_size)})'))
        else:
            self.stdout.write('No old backups to clean up')

        # Show remaining backup count
        remaining = SystemBackup.objects.filter(status='completed').count()
        self.stdout.write(f'Remaining backups: {remaining}')

    def _dump_mysql(self, backup_path, db_settings):
        """Dump MySQL database"""
        mysqldump_path = shutil.which('mysqldump') or '/usr/bin/mysqldump'

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

    def _dump_postgresql(self, backup_path, db_settings):
        """Dump PostgreSQL database"""
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

    def _format_size(self, size_bytes):
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
