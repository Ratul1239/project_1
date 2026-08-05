"""
WSGI config for ecommerce project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

application = get_wsgi_application()

# রেন্ডারে লাইভ হওয়ার সময় স্বয়ংক্রয়ভাবে সুপারইউজার তৈরি করার জন্য
if 'RENDER' in os.environ:
    try:
        User = get_user_model()
        if not User.objects.filter(username='sizan').exists():
            User.objects.create_superuser('sizan', 'sizan@gmail.com', '123456')
    except Exception as e:
        print(f"Superuser creation error: {e}")