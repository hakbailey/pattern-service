import logging

from dispatcherd.config import setup as dispatcher_setup
from django.apps import AppConfig
from django.conf import settings

from core.utils import validate_url

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        # Validate AAP_URL
        try:
            settings.AAP_URL = validate_url(settings.AAP_URL)
        except ValueError as e:
            logger.error(f"AAP_URL validation failed: {e}")
            raise

        # Configure dispatcher
        dispatcher_setup(config=settings.DISPATCHER_CONFIG)
