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

### Free Deployment Options

PrintFix Assistant can be deployed for free using cloud platforms. Here are the recommended free options:

#### Option 1: Railway (Recommended)

Railway offers a generous free tier with PostgreSQL database included.

1. **Sign up** at [Railway.app](https://railway.app)
2. **Connect GitHub** and deploy from your repository
3. **Database**: PostgreSQL is automatically provisioned
4. **Environment Variables**:
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://... (auto-provided)
   ALLOWED_HOSTS=your-app.railway.app
   ```
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `python manage.py migrate && gunicorn printfix.wsgi:application --bind 0.0.0.0:$PORT`

#### Option 2: Render

Render provides free web services with PostgreSQL.

1. **Sign up** at [Render.com](https://render.com)
2. **Create Web Service** from your GitHub repo
3. **Add PostgreSQL** database (free tier available)
4. **Environment Variables**:
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://... (from Render dashboard)
   ALLOWED_HOSTS=your-app.onrender.com
   ```
5. **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
6. **Start Command**: `gunicorn printfix.wsgi:application`

#### Option 3: Fly.io

Fly.io offers free tier with global deployment.

1. **Install Fly CLI** and sign up at [Fly.io](https://fly.io)
2. **Initialize app**: `fly launch`
3. **Configure database**: Add PostgreSQL with `fly postgres create`
4. **Environment Variables** in `fly.toml`:
   ```toml
   [env]
   DEBUG = "False"
   SECRET_KEY = "your-secret-key-here"
   ALLOWED_HOSTS = "your-app.fly.dev"
   ```
5. **Deploy**: `fly deploy`

#### Option 4: Heroku (Alternative)

Heroku has a free tier (with limitations).

1. **Sign up** at [Heroku.com](https://heroku.com)
2. **Install Heroku CLI**
3. **Create app**: `heroku create your-app-name`
4. **Add PostgreSQL**: `heroku addons:create heroku-postgresql:hobby-dev`
5. **Environment Variables**:
   ```
   heroku config:set DEBUG=False
   heroku config:set SECRET_KEY=your-secret-key-here
   heroku config:set ALLOWED_HOSTS=your-app.herokuapp.com
   ```
6. **Deploy**: Push to Heroku git remote

### Production Configuration

For any deployment, ensure these settings:

```python
# settings.py for production
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database (PostgreSQL recommended)
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### File Storage Considerations

For free tiers, be mindful of storage limits:
- Uploaded PDFs are stored temporarily
- Processed files are cleaned up automatically
- Consider using cloud storage (AWS S3, Cloudinary) for larger deployments

### Deployment Files Included

The repository includes ready-to-use deployment configurations:

- **`railway.toml`**: Railway deployment configuration
- **`render.yaml`**: Render deployment configuration  
- **`Procfile`**: Heroku deployment configuration
- **`.env.example`**: Environment variables template

### Quick Deploy Steps

1. **Railway**: Connect your GitHub repo, Railway auto-deploys
2. **Render**: Use the render.yaml file for one-click deployment
3. **Heroku**: Push to Heroku git remote with Procfile
4. **Fly.io**: Run `fly launch` and follow prompts

All configurations include automatic database setup and static file serving.

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