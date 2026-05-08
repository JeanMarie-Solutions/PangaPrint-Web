"""
PDF print launcher for PrintFix Assistant.
Handles launching PDFs with the print dialog.
"""

import os
import logging
import subprocess
import win32api
import win32con
from django.conf import settings

logger = logging.getLogger(__name__)


def launch_pdf_print(pdf_path, printer_name=None):
    """
    Launch a PDF file with the print dialog.

    Args:
        pdf_path (str): Path to the PDF file
        printer_name (str): Name of the printer to use (optional)

    Returns:
        bool: True if successful
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Use Windows ShellExecute to open PDF with default viewer and print
        if printer_name:
            # If specific printer is requested, we might need different approach
            # For now, just open with default
            pass

        # Open PDF with default application
        win32api.ShellExecute(
            0,      # hwnd
            "print",  # operation
            pdf_path,  # file
            None,   # parameters
            None,   # directory
            win32con.SW_HIDE  # show command
        )

        logger.info(f"Print dialog launched for: {pdf_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to launch PDF print for {pdf_path}: {str(e)}")
        return False


def print_pdf_silently(pdf_path, printer_name=None):
    """
    Print a PDF silently without showing dialog.

    Args:
        pdf_path (str): Path to the PDF file
        printer_name (str): Name of the printer to use

    Returns:
        bool: True if successful
    """
    try:
        if not printer_name:
            printer_name = settings.DEFAULT_PRINTER

        # Use Windows print command
        # This is a simplified approach - in production, might need more sophisticated PDF printing
        cmd = f'print /d:"{printer_name}" "{pdf_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"PDF printed silently: {pdf_path} to {printer_name}")
            return True
        else:
            logger.error(f"Silent print failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Failed to print PDF silently {pdf_path}: {str(e)}")
        return False