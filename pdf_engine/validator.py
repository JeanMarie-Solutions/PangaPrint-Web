"""
PDF validation engine for PangaPrint Assistant.
Validates PDF files and checks for processing compatibility.
"""

import os
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)


def validate_pdf(pdf_path):
    """
    Validate a PDF file for processing.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    result = {'valid': True, 'errors': []}

    # Check if file exists
    if not os.path.exists(pdf_path):
        result['valid'] = False
        result['errors'].append("File does not exist")
        return result

    # Check file size (max 100MB)
    file_size = os.path.getsize(pdf_path)
    if file_size > 100 * 1024 * 1024:
        result['valid'] = False
        result['errors'].append("File too large (max 100MB)")
        return result

    # Check if it's actually a PDF
    if not pdf_path.lower().endswith('.pdf'):
        result['valid'] = False
        result['errors'].append("File is not a PDF")
        return result

    # Try to read the PDF
    try:
        reader = PdfReader(pdf_path)
        page_count = len(reader.pages)

        if page_count == 0:
            result['valid'] = False
            result['errors'].append("PDF has no pages")
        elif page_count > 1000:
            result['valid'] = False
            result['errors'].append("PDF has too many pages (max 1000)")

    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Invalid PDF format: {str(e)}")

    return result


def is_pdf_locked(pdf_path):
    """
    Check if a PDF is password-protected or locked.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        bool: True if PDF is locked
    """
    try:
        reader = PdfReader(pdf_path)
        return reader.is_encrypted
    except Exception:
        return True  # Assume locked if we can't read it