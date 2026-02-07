"""
System-wide constants for UPG System.
Centralizes hardcoded values for maintainability.
"""

# Pagination Settings
DEFAULT_PAGE_SIZE = 10
LARGE_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
DASHBOARD_RECENT_ITEMS = 50

# Date/Time Ranges
ACTIVITY_LOOKBACK_DAYS = 30
RECENT_ACTIVITY_DAYS = 7
LOG_RETENTION_DAYS = 90

# SMS Settings
SMS_CHARACTER_LIMIT = 160
SMS_TRUNCATION_LENGTH = 157

# File Upload Limits
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Kenya-specific Validation
KENYA_PHONE_REGEX = r'^(07|01)[0-9]{8}$'
KENYA_PHONE_INTERNATIONAL_PREFIX = '254'
KENYA_ID_MIN_LENGTH = 7
KENYA_ID_MAX_LENGTH = 8

# Grant Calculation Defaults
DEFAULT_GRANT_BASE_AMOUNT = 50000  # KES
MIN_GROUP_SIZE = 15
MAX_GROUP_SIZE = 25
DEFAULT_SAVINGS_TARGET = 50000  # KES

# Training Settings
MAX_HOUSEHOLDS_PER_TRAINING = 25
DEFAULT_TRAINING_DURATION_HOURS = 2

# Form Settings
MAX_FIELDS_PER_PAGE = 6
FORM_PAGINATION_THRESHOLD = 10

# KoboToolbox Settings
KOBO_SYNC_TIMEOUT_SECONDS = 30
KOBO_MAX_RETRY_ATTEMPTS = 3
KOBO_RETRY_DELAY_SECONDS = 300
KOBO_REFERENCE_DATA_UPDATE_HOURS = 24

# User Roles
ADMIN_ROLES = ['me_staff', 'ict_admin']
FIELD_ROLES = ['mentor', 'field_associate']
ALL_STAFF_ROLES = ADMIN_ROLES + FIELD_ROLES + ['program_manager', 'data_clerk']

# Status Values
ACTIVE_STATUSES = ['active', 'enrolled', 'in_progress']
COMPLETED_STATUSES = ['completed', 'graduated']
INACTIVE_STATUSES = ['dropped_out', 'cancelled', 'inactive']
