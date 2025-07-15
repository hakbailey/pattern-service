import logging
import os

from dispatcherd.config import setup as dispatcher_setup
from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        dispatcher_feature = os.environ.get(
            "PATTERN_SERVICE_FEATURE_DISPATCHERD", "false"
        )
        if dispatcher_feature.lower() in ("true", "1", "yes"):
            # Setup dispatcher configuration
            dispatcher_setup(config=settings.DISPATCHER_CONFIG)
