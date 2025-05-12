from .base import *

DATABASES = {
    "default": {
        "ENGINE": "psqlextra.backend",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
        "TEST": {
            "NAME": env("TEST_POSTGRES_DB"),
            "HOST": env("TEST_POSTGRES_HOST"),
            "PORT": env("TEST_POSTGRES_PORT"),
            "USER": env("TEST_POSTGRES_USER"),
            "PASSWORD": env("TEST_POSTGRES_PASSWORD"),
        },
    }
}
