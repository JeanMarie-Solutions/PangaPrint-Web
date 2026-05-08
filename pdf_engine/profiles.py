"""
Printer profile management for PDF processing.
"""

from dashboard.models import PrinterProfile


def get_default_profile():
    """
    Get the default printer profile.

    Returns:
        PrinterProfile: The default profile or None
    """
    try:
        return PrinterProfile.objects.get(is_default=True)
    except PrinterProfile.DoesNotExist:
        # Return first profile if no default set
        return PrinterProfile.objects.first()


def get_profile_by_name(name):
    """
    Get a printer profile by name.

    Args:
        name (str): Profile name

    Returns:
        PrinterProfile: The profile or None
    """
    try:
        return PrinterProfile.objects.get(name=name)
    except PrinterProfile.DoesNotExist:
        return None