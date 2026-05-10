"""
Printer management for PangaPrint Assistant.
Handles printer detection and configuration.
"""

import logging

try:
    import win32print
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    win32print = None
    win32api = None
    WIN32_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_available_printers():
    """
    Get list of available printers on the system.

    Returns:
        list: List of printer names
    """
    if not WIN32_AVAILABLE:
        logger.warning("Printer enumeration is unavailable on this platform.")
        return []

    try:
        printers = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
            printers.append(printer[2])  # Printer name
        return printers
    except Exception as e:
        logger.error(f"Failed to enumerate printers: {str(e)}")
        return []


def get_default_printer():
    """
    Get the configured default printer or the system default printer.

    Returns:
        str: Default printer name or None
    """
    if not WIN32_AVAILABLE:
        logger.warning("Default printer lookup is unavailable on this platform.")
        return None

    try:
        try:
            from dashboard.settings_manager import SettingsManager
            system_printer = SettingsManager.get('default_printer')
        except Exception:
            system_printer = None

        if system_printer:
            if is_printer_available(system_printer):
                return system_printer
            logger.warning(f"Configured default printer unavailable: {system_printer}")

        return win32print.GetDefaultPrinter()
    except Exception as e:
        logger.error(f"Failed to get default printer: {str(e)}")
        return None


def set_default_printer(printer_name):
    """
    Set the system's default printer.

    Args:
        printer_name (str): Name of the printer to set as default

    Returns:
        bool: True if successful
    """
    if not WIN32_AVAILABLE:
        logger.warning("Cannot set default printer on this platform.")
        return False

    try:
        win32print.SetDefaultPrinter(printer_name)
        return True
    except Exception as e:
        logger.error(f"Failed to set default printer to {printer_name}: {str(e)}")
        return False


def is_printer_available(printer_name):
    """
    Check if a printer is available.

    Args:
        printer_name (str): Name of the printer

    Returns:
        bool: True if printer is available
    """
    if not WIN32_AVAILABLE:
        return False

    try:
        handle = win32print.OpenPrinter(printer_name)
        win32print.ClosePrinter(handle)
        return True
    except Exception:
        return False