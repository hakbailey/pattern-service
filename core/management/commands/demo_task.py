# Copyright (c) 2015 Ansible, Inc.
# All Rights Reserved.
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from dispatcherd.publish import submit_task

from core.tasks import print_hello

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Submit a demo task to the dispatcher service"

    def handle(self, *arg, **options):
        submit_task(print_hello)
