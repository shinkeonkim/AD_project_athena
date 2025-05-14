import os
from pathlib import Path

import environ

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = ["*"]


# Application definition

PACKAGE_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "django.contrib.postgres",
    "psqlextra",
    "django_extensions",
    "nplusone.ext.django",
    "silk",
    "rest_framework",
    "drf_spectacular",
    "django_filters",
    "django_guid",
    "drf_api_logger",
    "markdownx",
    "django_celery_beat",
    "django_celery_results",
]

INSTALLED_APPS = PACKAGE_APPS + [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# Custom apps

INSTALLED_APPS += [
    "user",
    "article",
    "problem",
    "agent",
    "main",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# TODO: koa - Use Cache (Redis)


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "static/"
STATIC_DIR = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    STATIC_DIR,
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "media/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Custom user model
AUTH_USER_MODEL = "user.User"

SITE_ID = 1


REDIS_HOST = env("REDIS_HOST", default="redis")
REDIS_PORT = env("REDIS_PORT", default="6379")
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Celery Beat 설정
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"


GEMINI_API_KEY = env("GEMINI_API_KEY")
