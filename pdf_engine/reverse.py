"""
PDF page reversal engine for PrintFix Assistant.
Handles reversing page order to correct printer stacking issues.
"""

import os
import logging
from pypdf import PdfReader, PdfWriter
from django.conf import settings

logger = logging.getLogger(__name__)


def reverse_pdf_pages(input_path, profile=None):
    """
    Reverse the pages of a PDF file.

    Args:
        input_path (str): Path to the input PDF file
        profile (PrinterProfile): Printer profile to use for processing

    Returns:
        str: Path to the processed PDF file

    Raises:
        Exception: If processing fails
    """
    try:
        # Determine if reversal is needed
        should_reverse = True
        if profile:
            should_reverse = profile.reverse_pages

        if not should_reverse:
            # If no reversal needed, return original path
            return input_path

        # Read the PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Reverse the pages
        for page_num in reversed(range(len(reader.pages))):
            writer.add_page(reader.pages[page_num])

        # Generate output path
        base_name = os.path.basename(input_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_filename = f"{name_without_ext}_reversed.pdf"
        output_path = os.path.join(settings.OUTPUT_FOLDER, output_filename)

        # Ensure output directory exists
        os.makedirs(settings.OUTPUT_FOLDER, exist_ok=True)

        # Write the reversed PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        logger.info(f"PDF reversed: {input_path} -> {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to reverse PDF {input_path}: {str(e)}")
        raise Exception(f"PDF reversal failed: {str(e)}")


def get_pdf_info(pdf_path):
    """
    Get information about a PDF file.

    Args:
        pdf_path (str): Path to the PDF file

    Returns:
        dict: PDF information (page_count, file_size, etc.)
    """
    try:
        reader = PdfReader(pdf_path)
        return {
            'page_count': len(reader.pages),
            'file_size': os.path.getsize(pdf_path),
            'metadata': reader.metadata,
        }
    except Exception as e:
        logger.error(f"Failed to get PDF info for {pdf_path}: {str(e)}")
        return None