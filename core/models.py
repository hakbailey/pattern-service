from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional

from ansible_base.lib.abstract_models import CommonModel
from django.db import models
from django.utils.functional import cached_property


class Pattern(CommonModel):
    class Meta:
        app_label = "core"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["collection_name", "collection_version", "pattern_name"],
                name="unique_pattern_collection_version",
            )
        ]

    collection_name: models.CharField = models.CharField(max_length=200)
    collection_version: models.CharField = models.CharField(max_length=50)
    collection_version_uri: models.CharField = models.CharField(
        max_length=200, blank=True, null=True
    )
    pattern_name: models.CharField = models.CharField(max_length=200)
    pattern_definition: models.JSONField = models.JSONField(blank=True, null=True)


class ControllerLabel(CommonModel):
    class Meta:
        app_label = "core"
        ordering = ["id"]

    label_id: models.PositiveBigIntegerField = models.PositiveBigIntegerField(
        unique=True
    )


class PatternInstance(CommonModel):
    class Meta:
        app_label = "core"
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization_id", "pattern"],
                name="unique_pattern_instance_organization",
            )
        ]

    organization_id: models.PositiveBigIntegerField = models.PositiveBigIntegerField()
    controller_project_id: models.PositiveBigIntegerField = (
        models.PositiveBigIntegerField(blank=True, null=True)
    )
    controller_ee_id: models.PositiveBigIntegerField = models.PositiveBigIntegerField(
        null=True, blank=True
    )
    credentials: models.JSONField = models.JSONField()
    executors: models.JSONField = models.JSONField(null=True, blank=True)

    pattern: models.ForeignKey = models.ForeignKey(
        Pattern, on_delete=models.CASCADE, related_name="pattern_instances"
    )
    controller_labels: models.ManyToManyField = models.ManyToManyField(
        ControllerLabel, related_name="pattern_instances", blank=True
    )


class Automation(CommonModel):
    class Meta:
        app_label = "core"
        ordering = ["id"]

    automation_type_choices = (("job_template", "Job template"),)
    automation_type: models.CharField = models.CharField(
        max_length=200, choices=automation_type_choices
    )
    automation_id: models.PositiveBigIntegerField = models.PositiveBigIntegerField()
    primary: models.BooleanField = models.BooleanField(default=False)

    pattern_instance: models.ForeignKey = models.ForeignKey(
        PatternInstance, on_delete=models.CASCADE, related_name="automations"
    )


class Task(CommonModel):
    class Meta:
        app_label = "core"
        ordering = ["id"]

    class Status(models.TextChoices):
        INITIATED = "Initiated"
        RUNNING = "Running"
        COMPLETED = "Completed"
        FAILED = "Failed"

    status: models.CharField = models.CharField(max_length=20, choices=Status.choices)
    details: models.JSONField = models.JSONField(null=True, blank=True)

    def set_status(
        self,
        new_status: str,
        details: Optional[Dict[str, Any]] = None,
        save_immediately: bool = True,
    ) -> None:
        """
        Safely update the task's status and optional details.

        Args:
            new_status (str): The new status (must be one of Status.choices).
            details (dict, optional): Additional info about this status update.
            save_immediately (bool): If True, saves the instance to the database
                immediately.

        Raises:
            ValueError: If the provided status is invalid.
        """
        if new_status not in self.Status.values:
            raise ValueError(
                f"Invalid status '{new_status}'. Allowed values: {self.Status.values}"
            )

        self.status = new_status
        self.details = details or {}
        if save_immediately:
            self.save(update_fields=["status", "details"])

    def mark_initiated(self, details: Optional[Dict[str, Any]] = None) -> None:
        self.set_status(self.Status.INITIATED, details)

    def mark_running(self, details: Optional[Dict[str, Any]] = None) -> None:
        self.set_status(self.Status.RUNNING, details)

    def mark_completed(self, details: Optional[Dict[str, Any]] = None) -> None:
        self.set_status(self.Status.COMPLETED, details)

    def mark_failed(self, details: Optional[Dict[str, Any]] = None) -> None:
        self.set_status(self.Status.FAILED, details)

    def __str__(self) -> str:
        return f"Task #{self.pk} - {self.status}"


class TokenUser:
    """
    A dummy user class modeled after django.contrib.auth.models.AnonymousUser.
    Used in conjunction with the `JWTStatelessUserAuthentication` backend to
    implement single sign-on functionality across services which share the same
    secret key. `JWTStatelessUserAuthentication` will return an instance of this
    class instead of a `User` model instance. Instances of this class act as
    stateless user objects which are backed by validated tokens.
    """

    is_active = True

    def __init__(self, token: dict) -> None:
        self.token = token

    def __str__(self) -> str:
        return f"TokenUser {self.id}"

    @cached_property
    def id(self) -> str:
        return self.token["sub"]

    @cached_property
    def pk(self) -> str:
        return self.id

    @cached_property
    def username(self) -> str:
        return self.token.get("user_data", {}).get("username", "")

    @cached_property
    def first_name(self) -> str:
        return self.token.get("user_data", {}).get("first_name", "")

    @cached_property
    def last_name(self) -> str:
        return self.token.get("user_data", {}).get("last_name", "")

    @cached_property
    def email(self) -> str:
        return self.token.get("user_data", {}).get("email", "")

    @cached_property
    def is_superuser(self) -> bool:
        return self.token.get("user_data", {}).get("is_superuser", False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TokenUser):
            return NotImplemented
        return self.id == other.id

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return hash(self.id)

    def save(self) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def delete(self) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def set_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token users have no DB representation")

    def check_password(self, raw_password: str) -> None:
        raise NotImplementedError("Token users have no DB representation")

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_authenticated(self) -> bool:
        return True

    def get_username(self) -> str:
        return self.username
