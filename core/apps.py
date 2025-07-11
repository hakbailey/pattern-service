from django.apps import AppConfig
from django.conf import settings

from dispatcherd.config import setup as dispatcher_setup


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        dispatcher_setup(settings.DISPATCHERD_CONFIG)
