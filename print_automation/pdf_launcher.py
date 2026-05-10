"""
PDF print launcher for PangaPrint Assistant.
Handles launching PDFs with the print dialog.
"""

import os
import logging
import subprocess
import win32api
import win32con
from django.conf import settings
from print_automation.printer_manager import get_default_printer, is_printer_available

logger = logging.getLogger(__name__)


def launch_pdf_print(pdf_path, printer_name=None):
    """
    Launch a PDF file with the print dialog or send it directly to a printer.

    Args:
        pdf_path (str): Path to the PDF file
        printer_name (str): Name of the printer to use (optional)

    Returns:
        bool: True if successful
    """
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        printer_name = printer_name or get_default_printer()
        if printer_name and is_printer_available(printer_name):
            try:
                result = win32api.ShellExecute(
                    0,
                    "printto",
                    pdf_path,
                    f'"{printer_name}"',
                    None,
                    win32con.SW_HIDE
                )
                if result > 32:
                    logger.info(f"Sent PDF to printer '{printer_name}' using printto: {pdf_path}")
                    return True
                logger.warning(f"ShellExecute printto returned {result} for {pdf_path}")
            except Exception as e:
                logger.warning(f"printto failed for {pdf_path} on printer {printer_name}: {e}")

        # Fallback to default print verb if printer-specific printto is unavailable
        result = win32api.ShellExecute(
            0,
            "print",
            pdf_path,
            None,
            None,
            win32con.SW_HIDE
        )

        if result > 32:
            logger.info(f"Print dialog launched for: {pdf_path}")
            return True

        logger.error(f"ShellExecute print returned {result} for {pdf_path}")
        return False

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
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        printer_name = printer_name or get_default_printer()
        if not printer_name or not is_printer_available(printer_name):
            logger.error(f"Printer unavailable for silent print: {printer_name}")
            return False

        result = win32api.ShellExecute(
            0,
            "printto",
            pdf_path,
            f'"{printer_name}"',
            None,
            win32con.SW_HIDE
        )

        if result > 32:
            logger.info(f"PDF printed silently: {pdf_path} to {printer_name}")
            return True

        logger.error(f"Silent print ShellExecute returned {result} for {pdf_path}")
        return False

    except Exception as e:
        logger.error(f"Failed to print PDF silently {pdf_path}: {str(e)}")
        return False