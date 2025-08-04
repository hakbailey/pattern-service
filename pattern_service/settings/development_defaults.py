import os
from pathlib import Path

ALLOWED_HOSTS = ["localhost", "pattern-service", "127.0.0.1"]
BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = True
SECRET_KEY = "insecure"

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "{levelname} {name} {lineno} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": DEBUG,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "loggers": {
        "ansible_base": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "core": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "dispatcherd": {"handlers": ["console"], "level": "INFO"},
    },
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Default DB path
default_path = BASE_DIR / "db.sqlite3"

# Use environment variable if set, else default
env_path = os.getenv("SQLITE_PATH")
db_path = Path(env_path) if env_path else default_path

# Ensure DB directory exists
db_path.parent.mkdir(parents=True, exist_ok=True)

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(db_path),
    }
}

# Base URL of your AAP service
AAP_URL = "http://localhost:44926"  # or your default URL

# Whether to verify SSL certificates (True or False)
AAP_VALIDATE_CERTS = False

# Default username and password for authentication
AAP_USERNAME = "admin"
AAP_PASSWORD = "password"
