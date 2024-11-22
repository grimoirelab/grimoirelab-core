#
# GrimoireLab core basic settings file.
#
# This file defines the required settings to run GrimoireLab.
# Due to GrimoireLab is a Django based app, these settings are
# based on the configuration file generated by Django by
# default.
#
# Please check the next links for details about the configuration
# in a production environment:
#
# https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/
# https://docs.djangoproject.com/en/4.2/ref/settings/
#

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SILENCED_SYSTEM_CHECKS = [
    'django_mysql.E016'
]

#
# General app parameters
#

#
# You must never enable debug in production.
#
# https://docs.djangoproject.com/en/4.2/ref/settings/#std:setting-DEBUG
#

DEBUG = os.environ.get('GRIMOIRELAB_DEBUG', 'False').lower() in ('true', '1')

#
# ALLOWED_HOST protects the site against CSRF attacks.
# If DEBUG is set to False, you will need to configure this parameter,
# with the host you are using to serve GrimoireLab.
#
# https://docs.djangoproject.com/en/4.2/ref/settings/#allowed-hosts
#

if 'GRIMOIRELAB_ALLOWED_HOST' in os.environ:
    ALLOWED_HOSTS = os.environ['GRIMOIRELAB_ALLOWED_HOST'].split(',')
else:
    ALLOWED_HOSTS = [
        '127.0.0.1',
        'localhost',
    ]

#
# Cross-Origin Resource Sharing (CORS)
#
# You'll HAVE TO configure the origins that are authorized to make
# cross-site HTTP requests. Check the following link to understand
# the possibilities and parameters you can use.
#
# https://github.com/adamchainz/django-cors-headers#configuration
#

if 'GRIMOIRELAB_CORS_ALLOWED_ORIGINS' in os.environ:
    CORS_ALLOWED_ORIGINS = os.environ['GRIMOIRELAB_CORS_ALLOWED_ORIGINS'].split(',')
elif 'GRIMOIRELAB_CORS_ALLOWED_ORIGIN_REGEXES' in os.environ:
    CORS_ALLOWED_ORIGIN_REGEXES = os.environ['GRIMOIRELAB_CORS_ALLOWED_ORIGIN_REGEXES'].split(',')
else:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:5173',
    ]

CORS_ALLOW_CREDENTIALS = True


#
# The secret key must be a large random value and it must be kept secret.
#
# https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key
#

SECRET_KEY = os.environ.get('GRIMOIRELAB_SECRET_KEY', 'fake-key')

#
# Application definition - DO NOT MODIFY
#

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_rq',
    'corsheaders',
    'rest_framework',
    'grimoirelab.core.scheduler',
    'grimoirelab.core.scheduler.tasks',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'grimoirelab.core.app.urls'

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

WSGI_APPLICATION = 'grimoirelab.core.app.wsgi.application'


#
# Grimoirelab core database
#
# You MUST set the database parameters in order to run
# GrimoireLab.
#

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': os.environ.get('GRIMOIRELAB_DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('GRIMOIRELAB_DB_PORT', 3306),
        'USER': os.environ.get('GRIMOIRELAB_DB_USER', 'root'),
        'PASSWORD': os.environ.get('GRIMOIRELAB_DB_PASSWORD', ''),
        'NAME': os.environ.get('GRIMOIRELAB_DB_DATABASE', 'grimoirelab_test'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


#
# Internationalization
#
# https://docs.djangoproject.com/en/4.2/topics/i18n/
#
#

LANGUAGE_CODE = 'en-us'
USE_I18N = True

#
# Time Zone
#

USE_TZ = True
TIME_ZONE = 'UTC'

#
# GrimoireLab Logging
#
# https://docs.djangoproject.com/en/4.2/topics/logging/#configuring-logging
#

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{asctime}] {message}',
            'style': '{',
        },
        'verbose': {
            'format': '[{asctime} - {levelname} - {name}:{lineno}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}


#
# Static files (CSS, JavaScript, Images)
#
# https://docs.djangoproject.com/en/4.2/howto/static-files/
#

STATIC_URL = '/static/'


# UI static files will be copied to the next path when
# 'collectstatic' is run.
# If you are serving these files in a dedicated server, you will
# need to copy them to their final destination.

STATIC_ROOT = os.path.join(BASE_DIR, 'static')


#
# Default primary key field type
#
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
#

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework settings

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

#
# GrimoireLab uses RQ to run background and async jobs.
# You'll HAVE TO set the next parameters in order to run
# them in the background.
#
# You can define the names of the RQ queues using the following
# environment variables.
#
# Take into account RQ uses Redis database. You have more
# info about these parameters on the following link:
#
# https://github.com/rq/django-rq
#

Q_PERCEVAL_JOBS = os.environ.get('GRIMOIRELAB_Q_PERCEVAL_JOBS', 'default')
Q_STORAGE_ITEMS = os.environ.get('GRIMOIRELAB_Q_STORAGE_ITEMS', 'items')
Q_EVENTS = os.environ.get('GRIMOIRELAB_Q_EVENTS', 'events')

_RQ_DATABASE = {
    'HOST': os.environ.get('GRIMOIRELAB_REDIS_HOST', '127.0.0.1'),
    'PORT': os.environ.get('GRIMOIRELAB_REDIS_PORT', 6379),
    'PASSWORD': os.environ.get('GRIMOIRELAB_REDIS_PASSWORD', ''),
    'DB': os.environ.get('GRIMOIRELAB_REDIS_DB', 0),
}

RQ_QUEUES = {
    Q_PERCEVAL_JOBS: _RQ_DATABASE,
    Q_STORAGE_ITEMS: _RQ_DATABASE,
    Q_EVENTS: _RQ_DATABASE,
}

RQ = {
    'JOB_CLASS': 'grimoirelab.core.scheduler.jobs.GrimoireLabJob',
    'WORKER_CLASS': 'grimoirelab.core.scheduler.worker.GrimoireLabWorker',
}

#
# Task default configuration
#

GRIMOIRELAB_JOB_INTERVAL = int(os.environ.get('GRIMOIRELAB_JOB_INTERVAL', 60 * 60 * 2))
GRIMOIRELAB_JOB_MAX_RETRIES = int(os.environ.get('GRIMOIRELAB_JOB_MAX_RETRIES', 5))
GRIMOIRELAB_JOB_RESULT_TTL = int(os.environ.get('GRIMOIRELAB_JOB_RESULT_TTL', 300))
GRIMOIRELAB_JOB_TIMEOUT = int(os.environ.get('GRIMOIRELAB_JOB_TIMEOUT', -1))

GIT_STORAGE_PATH = os.environ.get('GRIMOIRELAB_GIT_PATH', '~/.perceval')
