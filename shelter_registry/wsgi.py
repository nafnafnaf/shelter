"""
WSGI config for shelter_registry project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelter_registry.settings')

application = get_wsgi_application()
