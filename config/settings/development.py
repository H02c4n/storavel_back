from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.onrender.com',]

INSTALLED_APPS += ['django_extensions']

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}

# # SQLite kullan - PostgreSQL'i tamamen ez
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

CORS_ALLOW_ALL_ORIGINS = True

# Cloudinary'yi development ortamında devre dışı bırak (isteğe bağlı)
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'