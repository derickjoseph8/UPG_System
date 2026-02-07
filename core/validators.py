"""
Custom validators for UPG System
Kenya-specific validation for phone numbers, national IDs, and geographic coordinates.
"""

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import re


# =============================================================================
# Phone Number Validators (Kenya)
# =============================================================================

# Kenya phone number formats:
# - +254XXXXXXXXX (international)
# - 07XXXXXXXX or 01XXXXXXXX (local)
kenya_phone_validator = RegexValidator(
    regex=r'^(\+254|0)[17]\d{8}$',
    message='Enter a valid Kenya phone number (e.g., 0712345678 or +254712345678)',
    code='invalid_phone'
)


def validate_kenya_phone(value):
    """
    Validate and normalize Kenya phone numbers.
    Accepts: +254XXXXXXXXX, 0XXXXXXXXX
    """
    if not value:
        return value

    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', value)

    # Check format
    pattern = r'^(\+254|254|0)?([17]\d{8})$'
    match = re.match(pattern, cleaned)

    if not match:
        raise ValidationError(
            'Enter a valid Kenya phone number (e.g., 0712345678 or +254712345678)',
            code='invalid_phone'
        )

    return value


# =============================================================================
# National ID Validators (Kenya)
# =============================================================================

# Kenya National ID: 7-8 digits
kenya_id_validator = RegexValidator(
    regex=r'^\d{7,8}$',
    message='Enter a valid Kenya National ID (7-8 digits)',
    code='invalid_id'
)


def validate_kenya_national_id(value):
    """
    Validate Kenya National ID number.
    Must be 7-8 digits (older IDs are 7 digits, newer are 8).
    """
    if not value:
        return value

    # Remove any spaces or dashes
    cleaned = re.sub(r'[\s\-]', '', str(value))

    if not cleaned.isdigit():
        raise ValidationError(
            'National ID must contain only digits',
            code='invalid_id'
        )

    if len(cleaned) < 7 or len(cleaned) > 8:
        raise ValidationError(
            'National ID must be 7-8 digits',
            code='invalid_id_length'
        )

    return cleaned


# =============================================================================
# GPS Coordinate Validators (Kenya)
# =============================================================================

# Kenya GPS bounds (approximate):
# Latitude: -4.7 to 4.6 (South to North)
# Longitude: 33.9 to 41.9 (West to East)

kenya_latitude_validator = [
    MinValueValidator(-5.0, message='Latitude must be within Kenya bounds (-5.0 to 5.0)'),
    MaxValueValidator(5.0, message='Latitude must be within Kenya bounds (-5.0 to 5.0)')
]

kenya_longitude_validator = [
    MinValueValidator(33.5, message='Longitude must be within Kenya bounds (33.5 to 42.0)'),
    MaxValueValidator(42.0, message='Longitude must be within Kenya bounds (33.5 to 42.0)')
]


def validate_kenya_coordinates(latitude, longitude):
    """
    Validate that coordinates fall within Kenya's boundaries.
    """
    errors = []

    if latitude is not None:
        if latitude < -5.0 or latitude > 5.0:
            errors.append('Latitude must be between -5.0 and 5.0')

    if longitude is not None:
        if longitude < 33.5 or longitude > 42.0:
            errors.append('Longitude must be between 33.5 and 42.0')

    if errors:
        raise ValidationError(errors)

    return True


# =============================================================================
# Financial Validators
# =============================================================================

positive_amount_validator = MinValueValidator(
    0.01,
    message='Amount must be greater than zero'
)

max_grant_amount_validator = MaxValueValidator(
    100000,
    message='Grant amount cannot exceed KES 100,000'
)


def validate_currency_amount(value):
    """
    Validate currency amounts.
    Must be positive and have at most 2 decimal places.
    """
    if value is None:
        return value

    if value < 0:
        raise ValidationError('Amount cannot be negative')

    # Check decimal places
    str_value = str(value)
    if '.' in str_value:
        decimal_places = len(str_value.split('.')[1])
        if decimal_places > 2:
            raise ValidationError('Amount can have at most 2 decimal places')

    return value


# =============================================================================
# Text Field Validators
# =============================================================================

def validate_no_special_chars(value):
    """
    Validate that text contains no dangerous special characters.
    Allows letters, numbers, spaces, and common punctuation.
    """
    if not value:
        return value

    # Allow letters (including unicode), numbers, spaces, and basic punctuation
    pattern = r'^[\w\s\.\,\-\'\"\(\)\/\&\:]+$'
    if not re.match(pattern, value, re.UNICODE):
        raise ValidationError(
            'Contains invalid characters. Use only letters, numbers, and basic punctuation.',
            code='invalid_chars'
        )

    return value


def validate_name(value):
    """
    Validate person/entity names.
    Must be 2-100 characters, letters and spaces only.
    """
    if not value:
        return value

    value = value.strip()

    if len(value) < 2:
        raise ValidationError('Name must be at least 2 characters')

    if len(value) > 100:
        raise ValidationError('Name cannot exceed 100 characters')

    # Allow letters (including unicode letters), spaces, hyphens, and apostrophes
    pattern = r'^[\w\s\-\'\.]+$'
    if not re.match(pattern, value, re.UNICODE):
        raise ValidationError('Name contains invalid characters')

    return value


# =============================================================================
# Date Validators
# =============================================================================

from django.utils import timezone
from datetime import date, timedelta


def validate_not_future_date(value):
    """
    Validate that a date is not in the future.
    """
    if value and value > timezone.now().date():
        raise ValidationError('Date cannot be in the future')
    return value


def validate_not_too_old(value, max_years=120):
    """
    Validate that a date is not unreasonably old.
    Default: not more than 120 years ago.
    """
    if value:
        min_date = timezone.now().date() - timedelta(days=max_years * 365)
        if value < min_date:
            raise ValidationError(f'Date cannot be more than {max_years} years ago')
    return value


def validate_birth_date(value):
    """
    Validate a birth date.
    Must be in the past, but not more than 120 years ago.
    """
    if not value:
        return value

    validate_not_future_date(value)
    validate_not_too_old(value, max_years=120)

    return value


def validate_program_date(value):
    """
    Validate program-related dates.
    Must not be more than 5 years in the past or future.
    """
    if not value:
        return value

    today = timezone.now().date()
    min_date = today - timedelta(days=5 * 365)
    max_date = today + timedelta(days=5 * 365)

    if value < min_date:
        raise ValidationError('Date cannot be more than 5 years in the past')

    if value > max_date:
        raise ValidationError('Date cannot be more than 5 years in the future')

    return value


# =============================================================================
# File Validators
# =============================================================================

def validate_file_size(value, max_size_mb=5):
    """
    Validate file size.
    Default max: 5 MB.
    """
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'File size cannot exceed {max_size_mb} MB')
    return value


def validate_image_file(value):
    """
    Validate image file type.
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = value.name.lower().split('.')[-1] if '.' in value.name else ''

    if f'.{ext}' not in valid_extensions:
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
        )

    return value


def validate_document_file(value):
    """
    Validate document file type.
    """
    valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv']
    ext = value.name.lower().split('.')[-1] if '.' in value.name else ''

    if f'.{ext}' not in valid_extensions:
        raise ValidationError(
            f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
        )

    return value


# =============================================================================
# Business Logic Validators
# =============================================================================

def validate_percentage(value):
    """
    Validate percentage values (0-100).
    """
    if value is not None:
        if value < 0 or value > 100:
            raise ValidationError('Percentage must be between 0 and 100')
    return value


def validate_interest_rate(value):
    """
    Validate interest rate (0-50%).
    """
    if value is not None:
        if value < 0:
            raise ValidationError('Interest rate cannot be negative')
        if value > 50:
            raise ValidationError('Interest rate cannot exceed 50%')
    return value


def validate_group_size(value, min_size=5, max_size=30):
    """
    Validate group size for business/savings groups.
    """
    if value is not None:
        if value < min_size:
            raise ValidationError(f'Group must have at least {min_size} members')
        if value > max_size:
            raise ValidationError(f'Group cannot exceed {max_size} members')
    return value
