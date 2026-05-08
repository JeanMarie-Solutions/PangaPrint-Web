#!/usr/bin/env python
"""
PrintFix Assistant - Main entry point for the desktop assistant.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'printfix.settings')

import django
django.setup()

from assistant.tray_app import PrintFixTrayApp

def main():
    """Main entry point."""
    app = PrintFixTrayApp()
    app.run()

if __name__ == '__main__':
    main()