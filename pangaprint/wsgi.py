"""
WSGI config for pangaprint project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pangaprint.settings')

# Run migrations on startup to ensure database is ready
call_command('migrate', verbosity=0, interactive=False)

application = get_wsgi_application()
