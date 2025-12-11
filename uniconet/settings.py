"""
Django settings for UnicoNet project.
Red Social Universitaria - UPEC
"""

import os
from pathlib import Path
from decouple import config, Csv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']


# ==============================================================================
# APPS
# ==============================================================================

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_filters',
]

# Solo agregar en desarrollo
if DEBUG:
    THIRD_PARTY_APPS += [
        'debug_toolbar',
        'django_extensions',
    ]

LOCAL_APPS = [
    'apps.authentication',
    'apps.users',
    'apps.profiles',
    'apps.posts',
    'apps.comments',
    'apps.likes',
    'apps.friends',
    'apps.groups',
    'apps.notifications',
    'apps.messaging',
    'apps.feed',
    'apps.events',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ==============================================================================
# MIDDLEWARE
# ==============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS debe ir temprano
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Debug toolbar en desarrollo
if DEBUG:
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']


# ==============================================================================
# URLS & WSGI
# ==============================================================================

ROOT_URLCONF = 'uniconet.urls'
WSGI_APPLICATION = 'uniconet.wsgi.application'


# ==============================================================================
# TEMPLATES
# ==============================================================================

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
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.friends.context_processors.friends_context',
            ],
        },
    },
]


# ==============================================================================
# DATABASE
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='uniconet_db'),
        'USER': config('DB_USER', default='uniconet_user'),
        'PASSWORD': config('DB_PASSWORD', default='uniconet_password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'ATOMIC_REQUESTS': True,
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}


# ==============================================================================
# CACHE (Redis)
# ==============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default='6379')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'uniconet',
        'TIMEOUT': 300,
    }
}

# Usar Redis para sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


# ==============================================================================
# AUTHENTICATION
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'authentication.User'

# Login/Logout URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/feed/'
LOGOUT_REDIRECT_URL = '/'


# ==============================================================================
# REST FRAMEWORK
# ==============================================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M:%S',
    'DATE_FORMAT': '%Y-%m-%d',
}


# ==============================================================================
# CORS (Cross-Origin Resource Sharing)
# ==============================================================================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://0.0.0.0:8000',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]


# ==============================================================================
# CSRF & SECURITY (Cross-Site Request Forgery)
# ==============================================================================

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost',
    'http://127.0.0.1',
]

# Configuración CSRF para desarrollo
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = False

# Configuración de sesiones para desarrollo
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 semanas
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_NAME = 'uniconet_sessionid'


# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================

LANGUAGE_CODE = 'es-ec'
TIME_ZONE = 'America/Guayaquil'
USE_I18N = True
USE_TZ = True


# ==============================================================================
# STATIC FILES (CSS, JavaScript, Images)
# ==============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


# ==============================================================================
# MEDIA FILES (User Uploaded Files)
# ==============================================================================

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================================================
# EMAIL CONFIGURATION
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

if not DEBUG:
    EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@uniconet.com')


# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'uniconet.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)


# ==============================================================================
# SECURITY SETTINGS
# ==============================================================================

if not DEBUG:
    # HTTPS/SSL en producción
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Desarrollo
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False


# ==============================================================================
# FILE UPLOAD SETTINGS
# ==============================================================================

# Tamaño máximo de archivo (10MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Tipos de archivos permitidos para uploads
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/mpeg', 'video/quicktime']
ALLOWED_DOCUMENT_TYPES = ['application/pdf', 'application/msword']


# ==============================================================================
# DEBUG TOOLBAR (Solo en desarrollo)
# ==============================================================================

if DEBUG:
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
    
    # Para Docker
    import socket
    try:
        hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
        INTERNAL_IPS += ['.'.join(ip.split('.')[:-1] + ['1']) for ip in ips]
    except:
        pass


# ==============================================================================
# DEFAULT PRIMARY KEY FIELD TYPE
# ==============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# CONFIGURACIONES PERSONALIZADAS DE UNICONET
# ==============================================================================

# Configuraciones de la red social
UNICONET_CONFIG = {
    'MAX_POST_LENGTH': 5000,
    'MAX_COMMENT_LENGTH': 1000,
    'MAX_MESSAGE_LENGTH': 2000,
    'POSTS_PER_PAGE': 20,
    'FRIENDS_LIMIT': 5000,
    'MAX_GROUP_MEMBERS': 10000,
    'NOTIFICATION_RETENTION_DAYS': 30,
    'MAX_FILE_SIZE_MB': 10,
    'ALLOWED_IMAGE_FORMATS': ['JPEG', 'PNG', 'GIF', 'WEBP'],
    'THUMBNAIL_SIZE': (300, 300),
    'PROFILE_IMAGE_SIZE': (500, 500),
}

# Configuraciones de notificaciones
NOTIFICATION_SETTINGS = {
    'SEND_EMAIL_NOTIFICATIONS': False,  # En desarrollo
    'SEND_PUSH_NOTIFICATIONS': False,
    'NOTIFICATION_TYPES': [
        'friend_request',
        'friend_accept',
        'post_like',
        'post_comment',
        'comment_reply',
        'group_invitation',
        'event_invitation',
        'mention',
    ]
}

# Tiempo de cache para diferentes tipos de datos
CACHE_TIMEOUT = {
    'feed': 60 * 5,        # 5 minutos
    'profile': 60 * 15,    # 15 minutos
    'posts': 60 * 10,      # 10 minutos
    'notifications': 60,    # 1 minuto
    'friends': 60 * 30,    # 30 minutos
}
# URL para acceder a los archivos media desde el navegador
MEDIA_URL = '/media/'

# Directorio físico donde se guardarán los archivos subidos
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Opcional: Limitar tamaño de archivos subidos
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB en bytes
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB en bytes