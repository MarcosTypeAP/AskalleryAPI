
from datetime import timedelta
from .base import * # NOQA
from .base import env

LOCAL_DEV = False

ALLOWED_HOSTS = [
    APP_URL, # NOQA
]

# Email
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.smtp.EmailBackend'
)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', default=True)

# REST Framework
REST_FRAMEWORK = {
    'PAGE_SIZE': 30,
}

# Application
INSTALLED_APPS += [ # NOQA
    'cloudinary',
    'cloudinary_storage',
    'gunicorn'
]

# Database
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'ATOMIC_REQUESTS': True,
    }
}

# Media
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

CLOUDINARY_STORAGE = {
  'CLOUD_NAME': env('CLOUD_NAME'),
  'API_KEY': env('API_KEY'),
  'API_SECRET': env('API_SECRET')
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Simple JWT
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=5) # NOQA
