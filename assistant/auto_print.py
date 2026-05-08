"""
Automatic printing module for PrintFix Assistant.
Handles automated PDF printing workflows.
"""

import logging
from print_automation.pdf_launcher import launch_pdf_print, print_pdf_silently

logger = logging.getLogger(__name__)


def auto_print_pdf(pdf_path, profile=None):
    """
    Automatically print a PDF based on profile settings.

    Args:
        pdf_path (str): Path to the PDF file
        profile (PrinterProfile): Printer profile to use

    Returns:
        bool: True if successful
    """
    try:
        if profile and profile.auto_print:
            if profile.reverse_pages:
                # PDF should already be reversed by pdf_engine
                pass

            # Launch print dialog or print silently
            if profile.duplex_mode:
                # Handle duplex printing
                pass

            # For now, always show print dialog
            return launch_pdf_print(pdf_path)
        else:
            logger.info(f"Auto-print disabled for profile: {profile}")
            return False

    except Exception as e:
        logger.error(f"Auto-print failed for {pdf_path}: {str(e)}")
        return False