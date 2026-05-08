"""
File watcher for PrintFix Assistant.
Monitors watch folders for new PDF files.
"""

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
from pdf_engine.validator import validate_pdf
from pdf_engine.reverse import reverse_pdf_pages
from print_automation.pdf_launcher import launch_pdf_print

logger = logging.getLogger(__name__)


class PDFHandler(FileSystemEventHandler):
    """Handler for PDF file events."""

    def __init__(self, watch_folder):
        self.watch_folder = watch_folder
        self.processing_files = set()  # Track files being processed

    def on_created(self, event):
        """Handle file creation event."""
        if event.is_directory:
            return

        filepath = event.src_path
        filename = os.path.basename(filepath)

        # Only process PDF files
        if not filename.lower().endswith('.pdf'):
            return

        logger.info(f"New PDF detected: {filepath}")

        # Wait for file to be fully written
        if not self._wait_for_file_completion(filepath):
            logger.warning(f"File write timeout: {filepath}")
            return

        # Validate the PDF
        validation = validate_pdf(filepath)
        if not validation['valid']:
            logger.error(f"Invalid PDF {filepath}: {', '.join(validation['errors'])}")
            return

        # Process the PDF
        try:
            processed_path = reverse_pdf_pages(filepath)
            launch_pdf_print(processed_path)
            logger.info(f"Successfully processed: {filepath}")
        except Exception as e:
            logger.error(f"Processing failed for {filepath}: {str(e)}")

    def _wait_for_file_completion(self, filepath, timeout=30):
        """
        Wait for file to be fully written by checking if size stabilizes.

        Args:
            filepath (str): Path to the file
            timeout (int): Maximum time to wait in seconds

        Returns:
            bool: True if file is ready
        """
        if not os.path.exists(filepath):
            return False

        initial_size = os.path.getsize(filepath)
        start_time = time.time()

        while time.time() - start_time < timeout:
            time.sleep(0.5)
            if os.path.getsize(filepath) == initial_size:
                time.sleep(1)  # Wait a bit more to be sure
                if os.path.getsize(filepath) == initial_size:
                    return True

        return False


class PDFWatcher:
    """PDF file watcher."""

    def __init__(self, watch_folder=None):
        self.watch_folder = watch_folder or settings.WATCH_FOLDER
        self.observer = None
        self.handler = None

    def start(self):
        """Start watching the folder."""
        try:
            os.makedirs(self.watch_folder, exist_ok=True)

            self.handler = PDFHandler(self.watch_folder)
            self.observer = Observer()
            self.observer.schedule(self.handler, self.watch_folder, recursive=False)
            self.observer.start()

            logger.info(f"Started watching folder: {self.watch_folder}")

        except Exception as e:
            logger.error(f"Failed to start watcher: {str(e)}")
            raise

    def stop(self):
        """Stop watching the folder."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Stopped watching folder")

    def is_running(self):
        """Check if watcher is running."""
        return self.observer and self.observer.is_alive()