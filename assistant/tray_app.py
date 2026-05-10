"""
System tray application for PangaPrint Assistant.
Provides GUI controls for the background assistant.
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
import requests
from django.conf import settings
from .watcher import PDFWatcher
from .hotkeys import HotkeyManager

logger = logging.getLogger(__name__)


class PangaPrintTrayApp:
    """System tray application for PangaPrint Assistant."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.tray_icon = None
        self.watcher = None
        self.hotkey_manager = None
        self.is_watching = False

        self.setup_tray_icon()
        self.setup_watcher()
        self.setup_hotkeys()

    def setup_tray_icon(self):
        """Setup the system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon()
        # For now, use default icon - in production, would load custom icon
        self.tray_icon.setToolTip("PangaPrint Assistant")

        # Create menu
        menu = QMenu()

        # Status action
        self.status_action = QAction("Status: Stopped")
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)

        menu.addSeparator()

        # Start/Stop monitoring
        self.toggle_action = QAction("Start Monitoring")
        self.toggle_action.triggered.connect(self.toggle_monitoring)
        menu.addAction(self.toggle_action)

        # Open Dashboard
        dashboard_action = QAction("Open Dashboard")
        dashboard_action.triggered.connect(self.open_dashboard)
        menu.addAction(dashboard_action)

        menu.addSeparator()

        # Exit
        exit_action = QAction("Exit")
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def setup_watcher(self):
        """Setup the PDF watcher."""
        self.watcher = PDFWatcher()

    def setup_hotkeys(self):
        """Setup global hotkeys."""
        self.hotkey_manager = HotkeyManager()
        self.hotkey_manager.register_hotkey(settings.HOTKEY, self.open_dashboard)

    def toggle_monitoring(self):
        """Toggle PDF monitoring on/off."""
        if self.is_watching:
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        """Start PDF monitoring."""
        try:
            self.watcher.start()
            self.is_watching = True
            self.status_action.setText("Status: Running")
            self.toggle_action.setText("Stop Monitoring")
            self.tray_icon.showMessage(
                "PangaPrint Assistant",
                "PDF monitoring started",
                QSystemTrayIcon.MessageIcon.Information
            )
            logger.info("Monitoring started")
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            self.tray_icon.showMessage(
                "PangaPrint Assistant",
                f"Failed to start monitoring: {str(e)}",
                QSystemTrayIcon.MessageIcon.Critical
            )

    def stop_monitoring(self):
        """Stop PDF monitoring."""
        try:
            self.watcher.stop()
            self.is_watching = False
            self.status_action.setText("Status: Stopped")
            self.toggle_action.setText("Start Monitoring")
            self.tray_icon.showMessage(
                "PangaPrint Assistant",
                "PDF monitoring stopped",
                QSystemTrayIcon.MessageIcon.Information
            )
            logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")

    def open_dashboard(self):
        """Open the web dashboard."""
        try:
            import webbrowser
            dashboard_url = "http://localhost:8000"  # Assuming Django runs on 8000
            webbrowser.open(dashboard_url)
        except Exception as e:
            logger.error(f"Failed to open dashboard: {str(e)}")

    def check_dashboard_status(self):
        """Check if Django dashboard is running."""
        try:
            response = requests.get("http://localhost:8000/api/status/", timeout=5)
            if response.status_code == 200:
                self.tray_icon.setToolTip("PangaPrint Assistant - Dashboard Online")
            else:
                self.tray_icon.setToolTip("PangaPrint Assistant - Dashboard Offline")
        except:
            self.tray_icon.setToolTip("PangaPrint Assistant - Dashboard Offline")

    def run(self):
        """Run the tray application."""
        # Check dashboard status periodically
        timer = QTimer()
        timer.timeout.connect(self.check_dashboard_status)
        timer.start(30000)  # Check every 30 seconds

        # Initial status check
        self.check_dashboard_status()

        # Start the application
        sys.exit(self.app.exec())

    def exit_app(self):
        """Exit the application."""
        if self.is_watching:
            self.stop_monitoring()
        self.app.quit()