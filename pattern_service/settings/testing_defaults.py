from pathlib import Path

ALLOWED_HOSTS = ["localhost", "pattern-service", "127.0.0.1"]
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = (
    "django-insecure-_f^+pc=x%dd&p8ht4qv7rqr8&a%@j#lda6v!x9353m+)fm8&gk"  # notsecret
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
