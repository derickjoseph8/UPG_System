"""
Custom template filters for UPG System
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a variable key.
    Usage: {{ my_dict|get_item:key_variable }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def get_attr(obj, attr):
    """
    Get an attribute from an object using a variable attribute name.
    Usage: {{ object|get_attr:'attribute_name' }}
    """
    if obj is None:
        return None
    return getattr(obj, attr, None)


@register.filter
def in_list(value, the_list):
    """
    Check if a value is in a list.
    Usage: {{ value|in_list:my_list }}
    """
    return value in the_list


@register.filter
def percentage(value, total):
    """
    Calculate percentage.
    Usage: {{ value|percentage:total }}
    """
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0


@register.filter
def has_permission(user, permission_string):
    """
    Check if user has a specific permission.
    Usage: {{ user|has_permission:'module:permission_type' }}
    Example: {{ user|has_permission:'households:full' }}
    """
    if not hasattr(user, 'has_module_permission'):
        return False

    parts = permission_string.split(':')
    if len(parts) != 2:
        return False

    module_name, permission_type = parts
    return user.has_module_permission(module_name, permission_type)


@register.simple_tag
def get_permission_level(role, module_key):
    """
    Get permission level for a specific module from a CustomRole.
    Usage: {% get_permission_level role 'households' as level %}
    """
    if role and hasattr(role, 'permissions') and role.permissions:
        return role.permissions.get(module_key, 'none')
    return 'none'
