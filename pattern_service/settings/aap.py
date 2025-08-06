import os

from dynaconf import Dynaconf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load from dev and PATTERN_SERVICE_* env variables
_settings = Dynaconf(
    settings_files=[
        os.path.join(BASE_DIR, "defaults_development.py"),
        os.path.join(BASE_DIR, "testing_defaults.py"),
    ],
    envvar_prefix="PATTERN_SERVICE",
    envvar_cast=True,
    load_dotenv=True,
)

# Exposed config values
AAP_URL = _settings.AAP_URL
AAP_VALIDATE_CERTS = _settings.AAP_VALIDATE_CERTS
AAP_USERNAME = _settings.AAP_USERNAME
AAP_PASSWORD = _settings.AAP_PASSWORD
