"""
Django settings for UPG System project.

Generated for Village Enterprise Ultra-Poor Graduation Management System.
For local development and testing.
"""

from pathlib import Path
import os
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Security settings - Use environment variables in production
SECRET_KEY = config('SECRET_KEY', default='django-insecure-upg-system-dev-key-change-in-production-123456789')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# CSRF Trusted Origins - Required for Django 4+ for cross-origin requests
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost,http://127.0.0.1,http://54.87.33.103,https://54.87.33.103',
    cast=Csv()
)


# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
]

LOCAL_APPS = [
    'accounts',
    'core',
    'households',
    'business_groups',
    'savings_groups',
    'training',
    'surveys',
    'reports',
    'programs',
    'dashboard',
    'grants',
    'upg_grants',  # UPG-specific grant management
    'forms',  # Dynamic forms system
    'enrollment',  # Enrollment and targeting system
    'settings_module',
    've_reporting',  # Silent VE Data Hub API (no UI)
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.AuditLogMiddleware',
]

ROOT_URLCONF = 'upg_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.user_permissions',
                'core.context_processors.system_alerts',
            ],
        },
    },
]

WSGI_APPLICATION = 'upg_system.wsgi.application'


# Database Configuration

# MySQL Configuration (Active) - Use environment variables for credentials
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='upg_management_system'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        },
    }
}

# SQLite Configuration (Backup - data migrated to MySQL)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Email Configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# SMS Configuration
# Africa's Talking API (Primary SMS provider for Kenya)
AFRICAS_TALKING_API_KEY = ''  # Set in production
AFRICAS_TALKING_USERNAME = 'sandbox'  # Change to production username
SMS_SENDER_ID = 'UPG_SYS'

# Twilio API (Fallback SMS provider)
TWILIO_ACCOUNT_SID = ''  # Set in production
TWILIO_AUTH_TOKEN = ''   # Set in production
TWILIO_PHONE_NUMBER = '' # Set in production

# SMS Settings
SMS_ENABLED = True
SMS_BACKEND = 'core.sms.SMSService'  # Can be changed for testing

# SSL Configuration - Set ENABLE_SSL=True in .env when SSL certificate is configured
ENABLE_SSL = config('ENABLE_SSL', default=False, cast=bool)

# Session Configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SECURE = ENABLE_SSL  # Only True when SSL is configured
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# CSRF Configuration
CSRF_COOKIE_SECURE = ENABLE_SSL  # Only True when SSL is configured
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript to read CSRF token for AJAX requests
CSRF_COOKIE_SAMESITE = 'Lax'

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking

# Production security settings (enabled when DEBUG=False and ENABLE_SSL=True)
if not DEBUG and ENABLE_SSL:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# UPG System Specific Settings
UPG_SYSTEM_VERSION = '1.0.0'
UPG_DEFAULT_COUNTRY = 'Kenya'
UPG_DEFAULT_CURRENCY = 'KES'

# Database compatibility settings
import sys
if 'migrate' in sys.argv or 'makemigrations' in sys.argv:
    # Only apply MySQL/MariaDB settings if using MySQL backend
    if DATABASES['default']['ENGINE'] in ['django.db.backends.mysql', 'django.db.backends.mariadb']:
        if 'OPTIONS' not in DATABASES['default']:
            DATABASES['default']['OPTIONS'] = {}
        DATABASES['default']['OPTIONS']['init_command'] = (
            "SET sql_mode='STRICT_TRANS_TABLES'; "
            "SET SESSION innodb_strict_mode=1; "
        )

# Pagination
ITEMS_PER_PAGE = 25

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# ==================== KoboToolbox Integration ====================

# API Configuration - Set KOBO_API_TOKEN in .env file
KOBO_API_URL = config('KOBO_API_URL', default='https://kf.kobotoolbox.org/api/v2')
KOBO_API_TOKEN = config('KOBO_API_TOKEN', default='')  # REQUIRED: Set in .env file
KOBO_BASE_URL = config('KOBO_BASE_URL', default='https://kf.kobotoolbox.org')

# Webhook Configuration
KOBO_WEBHOOK_SECRET = config('KOBO_WEBHOOK_SECRET', default='')  # Optional for signature validation
KOBO_WEBHOOK_ENABLED = True

# Sync Settings
KOBO_AUTO_SYNC_ON_ACTIVATION = True  # Auto-sync when form becomes Active
KOBO_AUTO_SYNC_ON_ASSIGNMENT = True  # Auto-sync when form assigned
KOBO_SYNC_TIMEOUT = 30  # seconds

# Reference Data Settings
KOBO_PUSH_REFERENCE_DATA = True  # Push households, villages, etc. for pulldata()
KOBO_REFERENCE_DATA_UPDATE_INTERVAL = 86400  # seconds (24 hours)

# Validation Settings
KOBO_ALLOW_NEW_HOUSEHOLDS = True  # Allow creating new HH from Kobo submissions
KOBO_VALIDATE_PHONE_NUMBERS = True  # Validate phone number format
KOBO_VALIDATE_ID_NUMBERS = True  # Validate ID number format

# Error Handling
KOBO_RETRY_FAILED_SYNCS = True
KOBO_MAX_RETRY_ATTEMPTS = 3
KOBO_RETRY_DELAY = 300  # seconds (5 minutes)

# Notifications
KOBO_NOTIFY_ON_SYNC_FAILURE = True
KOBO_NOTIFY_EMAILS = []  # Add M&E staff emails for sync failure notifications

# ==================== End KoboToolbox Config ====================

# ==================== VE Data Hub Reporting Configuration ====================
# Silent API configuration for Village Enterprise reporting access
# These settings are used by the ve_reporting app
#
# IMPORTANT: Each county deployment MUST set these in their .env file:
#
# For Taita Taveta County:
#   VE_INSTANCE_ID=kenya-taita-taveta
#   VE_INSTANCE_NAME=Taita Taveta County UPG MIS
#   VE_REGION=Taita Taveta
#
# For Makueni County:
#   VE_INSTANCE_ID=kenya-makueni
#   VE_INSTANCE_NAME=Makueni County UPG MIS
#   VE_REGION=Makueni
#
# For West Pokot County:
#   VE_INSTANCE_ID=kenya-west-pokot
#   VE_INSTANCE_NAME=West Pokot County UPG MIS
#   VE_REGION=West Pokot

VE_INSTANCE_ID = config('VE_INSTANCE_ID', default='kenya-county')
VE_INSTANCE_NAME = config('VE_INSTANCE_NAME', default='Kenya County UPG MIS')
VE_COUNTRY = config('VE_COUNTRY', default='Kenya')
VE_REGION = config('VE_REGION', default='County')
VE_CURRENCY = config('VE_CURRENCY', default='KES')
VE_TIMEZONE = config('VE_TIMEZONE', default='Africa/Nairobi')

# ==================== End VE Data Hub Config ====================