#!/usr/bin/env python
"""
PangaPrint Assistant - Main entry point for the desktop assistant.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pangaprint.settings')

import django
django.setup()

from assistant.tray_app import PangaPrintTrayApp

def main():
    """Main entry point."""
    app = PangaPrintTrayApp()
    app.run()

if __name__ == '__main__':
    main()