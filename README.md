# PrintFix Assistant

A smart print workflow correction platform that automatically corrects page stacking/order problems in printers.

## Overview

PrintFix Assistant solves the common issue where printers produce physical pages in reverse stack order. This system automatically detects PDF creation, reorders pages, and launches corrected printing workflows.

## Features

- **Django Web Dashboard**: Responsive Bootstrap 5 interface for management
- **Background Desktop Assistant**: System tray application for automation
- **PDF Processing Engine**: Automatic page reordering and validation
- **Print Automation**: Seamless integration with printing workflows
- **Printer Profiles**: Support for different printer types and configurations
- **Watch-Folder Automation**: Monitors folders for new PDFs
- **Keyboard Shortcuts**: Global hotkeys for quick access
- **REST API**: Local APIs for communication between components

## Tech Stack

- **Backend**: Python, Django, Django REST Framework
- **Frontend**: HTML, CSS, Bootstrap 5, Vanilla JavaScript
- **Desktop**: PyQt6
- **PDF Processing**: pypdf
- **Automation**: watchdog, keyboard, pywin32
- **Database**: SQLite (dev) / PostgreSQL (prod)

## Installation

1. Clone or download the project
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env`
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Usage

### Starting the Dashboard

```bash
python manage.py runserver
```

Access at http://localhost:8000

### Starting the Assistant

```bash
python assistant/tray_app.py
```

### Workflow

1. Configure watch folder in settings
2. Print any document to PDF (Microsoft Print to PDF)
3. Save PDF in the watch folder
4. PrintFix Assistant automatically detects, processes, and launches corrected print

## Configuration

Edit `.env` file for:

- Watch folder path
- Temp/output directories
- Default printer
- Hotkeys

## Development

- Code follows PEP8 standards
- Modular architecture for maintainability
- Comprehensive logging and error handling
- Production-ready with Gunicorn/Whitenoise support

## Deployment

For production deployment:

1. Set DEBUG=False in settings
2. Configure PostgreSQL database
3. Use Gunicorn for serving
4. Enable Whitenoise for static files
5. Set up proper logging

## Testing

1. Start the Django server: `python manage.py runserver`
2. Open http://localhost:8000 in browser
3. Upload a PDF file
4. Check processing history
5. Start the assistant: `python assistant/main.py`
6. Test watch folder functionality

## Project Structure

```
printfix/
├── manage.py                 # Django management script
├── printfix/                 # Django project settings
├── dashboard/                # Web dashboard app
│   ├── models.py            # Database models
│   ├── views.py             # View logic
│   ├── urls.py              # URL routing
│   ├── forms.py             # Django forms
│   └── templates/           # HTML templates
├── assistant/                # Desktop assistant
│   ├── main.py              # Entry point
│   ├── tray_app.py          # System tray app
│   ├── watcher.py           # File watcher
│   ├── hotkeys.py           # Keyboard shortcuts
│   └── config_loader.py     # Configuration management
├── pdf_engine/               # PDF processing
│   ├── reverse.py           # Page reversal
│   ├── duplex.py            # Duplex processing
│   ├── booklet.py           # Booklet processing
│   ├── validator.py         # PDF validation
│   └── profiles.py          # Profile management
├── print_automation/         # Print automation
│   ├── printer_manager.py   # Printer management
│   ├── pdf_launcher.py      # PDF printing
│   ├── spool_monitor.py     # Print job monitoring
│   └── print_executor.py    # Print execution
├── media/                    # User uploaded files
├── temp/                     # Temporary files
├── logs/                     # Application logs
├── config/                   # Configuration files
└── profiles/                 # Printer profiles
```