# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved.
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from dispatcherd import run_service
from dispatcherd.config import setup as dispatcher_setup

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Launch the dispatcherd service'

    def handle(self, *arg, **options):
        logger.info(settings.DISPATCHERD_CONFIG)
        dispatcher_setup(settings.DISPATCHERD_CONFIG)
        run_service()
