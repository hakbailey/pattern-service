from pathlib import Path

ALLOWED_HOSTS = ["localhost", "pattern-service", "127.0.0.1"]
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "insecure"
