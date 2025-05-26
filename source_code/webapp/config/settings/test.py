from .base import *

# 테스트 환경 설정
DEBUG = False

# 테스트용 데이터베이스 설정
DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": env("TEST_POSTGRES_DB"),
        "USER": env("TEST_POSTGRES_USER"),
        "PASSWORD": env("TEST_POSTGRES_PASSWORD"),
        "HOST": env("TEST_POSTGRES_HOST"),
        "PORT": env("TEST_POSTGRES_PORT"),
    }
}

# PostgreSQL 확장 설정
POSTGRES_EXTRA_AUTO_EXTENSION = True  # 자동으로 필요한 확장 설치
POSTGRES_EXTRA_EXTENSIONS = ["pg_trgm", "btree_gin"]  # 필요한 확장 추가

# 테스트 시 이메일 발송 방지
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# 테스트 시 캐시 사용 방지
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# 테스트 시 정적 파일 처리
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# 테스트 시 미디어 파일 처리
MEDIA_ROOT = os.path.join(BASE_DIR, "test_media")

# 테스트 시 비밀번호 해싱 속도 향상
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# 테스트 시 로깅 설정
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}
