# config/settings/base.py
import os
from pathlib import Path
from decouple import config, Csv
from datetime import timedelta

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY: Get secret key from environment
SECRET_KEY = config('SECRET_KEY')

# Application definition
DJANGO_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework_simplejwt',
    'django_filters',
    'rest_framework_simplejwt.token_blacklist',
]

THIRD_PARTY_APPS = [
    'django.contrib.gis',
    'rest_framework',
    'corsheaders',
    'admin_interface',
    'colorfield',
    'django_extensions',
    "channels",
    'channels_redis',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.restaurants',
    'apps.orders',
    'common',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Auth
AUTH_USER_MODEL = 'users.CustomUser'

# Middleware
MIDDLEWARE = [
    'common.middleware.conditional.ConditionalMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

X_FRAME_OPTIONS = "SAMEORIGIN" 



ROOT_URLCONF = 'config.urls'

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES' : [
        'common.renderers.OrjsonRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES' : [
        'rest_framework_simplejwt.authentication.JWTAuthentication'],
    'DEFAULT_PERMISSION_CLASSES' : [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_FILTER_BACKENDS' : [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS' : 'drf_spectacular.openapi.AutoSchema',
    #'EXCEPTION_HANDLER' : 'common.exceptions.custom_exception_handler',
        'DEFAULT_THROTTLE_CLASSES' : [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon' : '100/hour',
        'user' : '1000/hour',
        'order_create': '20/hour',
        'review_create': '10/hour',
        'location_update': '500/hour',
    },
    'DEFAULT_VERSIONING_CLASS' : 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS' : ['v1','v2'],
    'DEFAULT_PAGINATION_CLASS' : 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 2,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME' : timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS' : True,
    'BLACKLIST_AFTER_ROTATION' : True,
    'UPDATE_LAST_LOGIN' : True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY' : SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD' : 'id',
    'USER_ID_CLAIM': 'user_id',
}

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

ASGI_APPLICATION = 'config.asgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
#--------------------------------------------------
STATIC_ROOT = os.path.join(BASE_DIR, 'root')
#-----------------------------------------------------
STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static/'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB - files larger than this go to temp The maximum size (in bytes) that an upload will be before it gets streamed to the file system
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB - max request body size
FILE_UPLOAD_PERMISSIONS = 0o644  # File permissions for uploaded files
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755  # Directory permissions
'''
The maximum size in bytes that a request body may be before a SuspiciousOperation (RequestDataTooBig) is raised.
 The check is done when accessing request.body or request.POST and is calculated against the total request size excluding any file upload data (request.FILES). 
 You can set this to None to disable the check. Applications that are expected to receive unusually large form posts should tune this setting.
'''

# Allowed upload handlers (default)
FILE_UPLOAD_HANDLERS = [
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'django.core.files.uploadhandler.TemporaryFileUploadHandler',
]
'''
Together MemoryFileUploadHandler and TemporaryFileUploadHandler provide Django’s 
default file upload behavior of reading small files into memory and large ones onto disk.
By default, if an uploaded file is smaller than 2.5 megabytes, Django will hold the entire contents of the upload in memory. 
This means that saving the file involves only a read from memory and a write to disk and thus is very fast.
However, if an uploaded file is too large, Django will write the uploaded file to a temporary file stored in your system’s temporary directory.
'''



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.json.JsonFormatter',
            'format' : '{message} {module} {asctime}',
            'style' : '{' ,
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'user.log',
            'formatter': 'json',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'main': {
            'handlers': ['file',],
            'level': 'INFO',
        },
    },
}

CHANNEL_LAYERS = {
    'default':{
        'BACKEND' : 'channels_redis.core.RedisChannelLayer',
        'CONFIG' :
        {
            'hosts' : [('127.0.0.1',6379)],
            'capacity': 1500,
        }

    }
}



CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'food_delivery',
    }
}
