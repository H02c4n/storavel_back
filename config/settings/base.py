from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change')

DEBUG = False

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',

#Third party
'rest_framework',
'rest_framework_simplejwt',
'corsheaders',
'django_filters',
'drf_spectacular',
'cloudinary',
'cloudinary_storage',

#Local apps
'apps.accounts',
'apps.languages',
'apps.stories',
'apps.vocabulary',
'apps.notebook',
'apps.quizzes',
'apps.progress.apps.ProgressConfig',
]


MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'corsheaders.middleware.CorsMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
'default': {
'ENGINE': 'django.db.backends.postgresql',
'NAME': os.getenv('DB_NAME', 'storavel'),
'USER': os.getenv('DB_USER', 'postgres'),
'PASSWORD': os.getenv('DB_PASSWORD', ''),
'HOST': os.getenv('DB_HOST', 'localhost'),
'PORT': os.getenv('DB_PORT', '5432'),
}
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'



CLOUDINARY_STORAGE = {
'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


REST_FRAMEWORK = {
'DEFAULT_AUTHENTICATION_CLASSES': (
'rest_framework_simplejwt.authentication.JWTAuthentication',
),
'DEFAULT_PERMISSION_CLASSES': (
'rest_framework.permissions.IsAuthenticatedOrReadOnly',
),
'DEFAULT_FILTER_BACKENDS': (
'django_filters.rest_framework.DjangoFilterBackend',
'rest_framework.filters.SearchFilter',
'rest_framework.filters.OrderingFilter',
),
'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPagination',
'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
'DEFAULT_THROTTLE_CLASSES': [
#'rest_framework.throttling.AnonRateThrottle',
#'rest_framework.throttling.UserRateThrottle',
],
'DEFAULT_THROTTLE_RATES': {
#'anon': '60/hour',
#'user': '1000/hour',
#'review': '2000/hour',
}
}


SIMPLE_JWT = {
'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
'ROTATE_REFRESH_TOKENS': False,
'BLACKLIST_AFTER_ROTATION': True,
'UPDATE_LAST_LOGIN': True,
'ALGORITHM': 'HS256',
'SIGNING_KEY': SECRET_KEY,
'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOWED_ORIGINS = [
os.getenv('FRONTEND_URL', 'http://localhost:3000'),
]

CORS_ALLOW_CREDENTIALS = True

SPECTACULAR_SETTINGS = {
'TITLE': 'Storavel API',
'DESCRIPTION': 'Language learning platform backend',
'VERSION': '1.0.0',
}