"""
Print spooler monitor for PangaPrint Assistant.
Monitors print jobs and their status.
"""

import logging
import win32print

logger = logging.getLogger(__name__)


def get_print_jobs(printer_name=None):
    """
    Get current print jobs for a printer.

    Args:
        printer_name (str): Name of the printer (optional, uses default if not specified)

    Returns:
        list: List of print jobs
    """
    try:
        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()

        handle = win32print.OpenPrinter(printer_name)
        jobs = win32print.EnumJobs(handle, 0, -1, 1)
        win32print.ClosePrinter(handle)

        return jobs
    except Exception as e:
        logger.error(f"Failed to get print jobs for {printer_name}: {str(e)}")
        return []


def monitor_print_job(job_id, printer_name=None):
    """
    Monitor a specific print job until completion.

    Args:
        job_id (int): Print job ID
        printer_name (str): Name of the printer

    Returns:
        dict: Job status information
    """
    try:
        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()

        handle = win32print.OpenPrinter(printer_name)
        job_info = win32print.GetJob(handle, job_id, 1)
        win32print.ClosePrinter(handle)

        return {
            'job_id': job_info['JobId'],
            'status': job_info['Status'],
            'pages': job_info.get('TotalPages', 0),
            'submitted': job_info.get('Submitted', None),
        }
    except Exception as e:
        logger.error(f"Failed to monitor print job {job_id}: {str(e)}")
        return None