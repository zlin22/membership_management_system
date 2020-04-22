"""
Django settings for hotshot_web project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import django_heroku

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# environment variables set here
STRIPE_API_KEY = os.environ['STRIPE_API_KEY']
STRIPE_ENDPOINT_SECRET = os.environ['STRIPE_ENDPOINT_SECRET']
STRIPE_REDIRECT_URL_BASE = os.environ['STRIPE_REDIRECT_URL_BASE']
STRIPE_PUBLIC_KEY = os.environ['STRIPE_PUBLIC_KEY']
ALLOWED_HOST1 = os.environ['ALLOWED_HOST1']
ALLOWED_HOST2 = os.environ['ALLOWED_HOST2']
COMPANY_NAME = os.environ['COMPANY_NAME']

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.environ['ENVIRONMENT'] == 'test')

ALLOWED_HOSTS = [ALLOWED_HOST1, ALLOWED_HOST2, '127.0.0.1', 'localhost']

CSRF_COOKIE_SECURE = (os.environ['ENVIRONMENT'] != 'test')
SESSION_COOKIE_SECURE = (os.environ['ENVIRONMENT'] != 'test')

USE_EMAIL = 'gmail'

# Mailgun email config
if USE_EMAIL == 'postmark':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.postmarkapp.com'
    EMAIL_HOST_USER = os.environ['POSTMARK_PASSWORD']
    EMAIL_HOST_PASSWORD = os.environ['POSTMARK_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'Membership Management <no_reply@zlin22.me>'

elif USE_EMAIL == 'gmail':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = os.environ['GMAIL_USER']
    EMAIL_HOST_PASSWORD = os.environ['GMAIL_PASSWORD']
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    DEFAULT_FROM_EMAIL = 'zlin@zlin22.me'

else:
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = os.path.join(BASE_DIR, "sent_emails")

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
AWS_DEFAULT_ACL = None
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
# change to your region to get v4 signature authentication for private storage
AWS_S3_REGION_NAME = 'us-east-2'

# s3 static settings
STATIC_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
STATICFILES_STORAGE = 'hotshot_web.storage_backends.StaticStorage'
# s3 public media settings
PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
# s3 private media settings
PRIVATE_MEDIA_LOCATION = 'private'
PRIVATE_FILE_STORAGE = 'hotshot_web.storage_backends.PrivateMediaStorage'
DEFAULT_FILE_STORAGE = 'hotshot_web.storage_backends.PublicMediaStorage'  # <-- here is where we reference it

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'membership_management/static'),
]

# Application definition
INSTALLED_APPS = [
    'membership_management.apps.MembershipManagementConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'storages',
    'import_export',
]

AUTH_USER_MODEL = 'membership_management.Member'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hotshot_web.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'hotshot_web.context_processors.export_vars',
            ],
        },
    },
]

WSGI_APPLICATION = 'hotshot_web.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

if os.environ['ENVIRONMENT'] == 'test':
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ['POSTGRES_DB_NAME'],
            "USER": os.environ['POSTGRES_USER'],
            "PASSWORD": os.environ['POSTGRES_PASSWORD'],
            "HOST": "localhost",
            "PORT": "",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'US/Eastern'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

LOGIN_REDIRECT_URL = 'admin'
LOGOUT_REDIRECT_URL = '/admin'

django_heroku.settings(locals(), staticfiles=False)
