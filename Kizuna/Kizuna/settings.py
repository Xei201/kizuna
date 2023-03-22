"""
Django settings for Kizuna project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.

BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-iwo8l+c7jq*#07(oq(59ds@un1y&evt5jx)y&64@bd__9$r*_!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'API.apps.APIConfig',
    'general.apps.GeneralConfig',
    'rest_framework',
    'debug_toolbar',
    'crispy_forms',
    'crispy_bootstrap4',
]

MIDDLEWARE = [
    "API.middleware.RequestTimeControl",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'Kizuna.urls'

INTERNAL_IPS = [
    '127.0.0.1',
]

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
            ],
        },
    },
]

WSGI_APPLICATION = 'Kizuna.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

DIRECTORY_FROM_FILE_IMPORT = 'load_file_import/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = '/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Url API service bizon for export
URL_BIZON_API = 'https://online.bizon365.ru/api/v1'
URL_BIZON_WEBINAR = 'webinars/reports'

# Url API service getcourse for import
URL_GETCOURSE_API = '.getcourse.ru/pl/api'
URL_GETCOURSE_API_USERS = 'users'

# Min rate success import viewers to Getcourse
IMPORT_SUCCESS_RATE = 0.8

# Test data API for TestCases
GETCOURSE_TEST_API = 'test_api_config_from_gk'
BIZON_TEST_API = 'test_api_config_from_bizon'

# Crispy forms version, using bootstrap

CRISPY_TEMPLATE_PACK = 'bootstrap4'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(name)-12s %(levelname)-8s %(message)s'
        },
        'file': {
            'format': '%(name)s %(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'file-info': {
            'format': '%(name)s %(levelname)s %(asctime)s %(funcName)s %(module)s %(message)s'
        },
        'file-request-time': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'core-file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'formatter': 'file',
            'filename': 'core-warning.log'
        },
        'info-core': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'file-info',
            'filename': 'info-core.log'
        },
        'info-request': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'file-request-time',
            'filename': 'info-time-request.log'
        }
    },
    'loggers': {
        'API': {
            'level': 'DEBUG',
            'handlers': ['console', 'core-file', 'info-core']
        },
        'time_request_control': {
            'level': 'INFO',
            'handlers': ['info-request']
        }
    }
}