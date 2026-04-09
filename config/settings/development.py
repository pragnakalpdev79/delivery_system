# config/settings/development.py
from .base import *
from decouple import config

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

DATABASES = {
    'default':
     {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD' : config('DB_PASSWORD'),
        'HOST' : config('DB_HOST'),
        'PORT' : config('DB_PORT'),
    }
}
# Development-specific apps
INSTALLED_APPS += [
    'drf_spectacular',
    'debug_toolbar',
    'silk',
]

MIDDLEWARE += [
    'silk.middleware.SilkyMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

# Email - Console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all in development
CORS_ALLOW_ALL_ORIGINS = True