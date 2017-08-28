import os
import sys

from django.core.exceptions import ImproperlyConfigured

import json
import dj_database_url


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(FILE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))


with open(os.path.join(FILE_DIR, 'secrets.json')) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = 'Set the {0} variable'.format(setting)
        raise ImproperlyConfigured(error_msg)


DEBUG = bool(get_secret('DEBUG'))


SECRET_KEY = get_secret('SECRET_KEY')
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG


ALLOWED_HOSTS = get_secret('ALLOWED_HOSTS').split()


DATABASES = {
    'default': dj_database_url.config(
        default=get_secret('CONNECTION_STRING'),
    ),
}


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    'debug_toolbar',
    'wkhtmltopdf',
    'qrcode',
    'django_celery_results',
    'django_celery_beat',

    'cars.apps.CarsConfig',
    'controller.apps.ControllerConfig',
    'pki.apps.PkiConfig',
    'payment.apps.PaymentConfig',
    'numberplates.apps.NumberPlatesConfig',
    'req_log.apps.ReqLogConfig',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'req_log.middleware.log_middleware'
]


ROOT_URLCONF = 'carbase.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
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


WSGI_APPLICATION = 'carbase.wsgi.application'


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


LANGUAGE_CODE = 'ru-RU'


TIME_ZONE = 'UTC'


USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = get_secret('STATIC_ROOT')


DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]
INTERNAL_IPS = get_secret('INTERNAL_IPS').split()


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


MCI = get_secret('MCI')


PAYBOX = get_secret('PAYBOX')


FIXTURE_DIRS = (
   os.path.join(BASE_DIR, 'fixtures'),
)


VIP1 = get_secret('VIP1').split()
VIP2 = get_secret('VIP2').split()
VIP3 = get_secret('VIP3').split()

VIP1_TAX = get_secret('VIP1_TAX')
VIP2_TAX = get_secret('VIP2_TAX')
VIP3_TAX = get_secret('VIP3_TAX')

VIP1_EXTRA_TAX = get_secret('VIP1_EXTRA_TAX')
VIP2_EXTRA_TAX = get_secret('VIP2_EXTRA_TAX')

SRTS_TAX = get_secret('SRTS_TAX')
GRNZ_TAX = get_secret('GRNZ_TAX')


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@carbase.kz'
EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True


WKHTMLTOPDF_CMD = get_secret('WKHTMLTOPDF_CMD')


CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_URL = 'amqp://guest:guest@localhost//'

MONGO_URL = get_secret('MONGO_URL')
