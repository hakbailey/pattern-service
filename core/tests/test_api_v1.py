import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from core import api_examples
from core import models


@pytest.fixture(autouse=True)
def frozen_time():
    with freeze_time("2025-06-25 01:02:03"):
        yield


@pytest.fixture()
def client():
    client = APIClient()
    return client


@pytest.fixture()
def automation(db, pattern_instance) -> models.Automation:
    automation = models.Automation.objects.create(
        automation_type=api_examples.automation_response.value["automation_type"],
        automation_id=api_examples.automation_response.value["automation_id"],
        pattern_instance=pattern_instance,
        primary=api_examples.automation_response.value["primary"],
    )
    return automation


@pytest.fixture()
def controller_label(db) -> models.ControllerLabel:
    controller_label = models.ControllerLabel.objects.create(
        label_id=api_examples.controller_label_response.value["label_id"]
    )
    return controller_label


@pytest.fixture()
def pattern(db) -> models.Pattern:
    pattern = models.Pattern.objects.create(
        collection_name=api_examples.pattern_post.value["collection_name"],
        collection_version=api_examples.pattern_post.value["collection_version"],
        pattern_name=api_examples.pattern_post.value["pattern_name"],
    )
    return pattern


@pytest.fixture()
def pattern_instance(db, pattern) -> models.PatternInstance:
    pattern_instance = models.PatternInstance.objects.create(
        credentials=api_examples.pattern_instance_post.value["credentials"],
        executors=api_examples.pattern_instance_post.value["executors"],
        organization_id=1,
        pattern=pattern,
    )
    return pattern_instance


@pytest.fixture()
def task(db) -> models.Task:
    task = models.Task.objects.create(
        status=api_examples.task_response.value["status"],
        details=api_examples.task_response.value["details"],
    )
    return task


def test_retrieve_automation_success(client, automation):
    url = f"/api/pattern-service/v1/automations/{automation.pk}/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == api_examples.automation_response.value


def test_list_automations_success(client, automation):
    url = "/api/pattern-service/v1/automations/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [api_examples.automation_response.value]


def test_retrieve_controller_label_success(client, controller_label):
    url = f"/api/pattern-service/v1/controller_labels/{controller_label.pk}/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == api_examples.controller_label_response.value


def test_list_controller_labels_success(client, controller_label):
    url = "/api/pattern-service/v1/controller_labels/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [api_examples.controller_label_response.value]


def test_create_pattern_success(client, db):
    url = "/api/pattern-service/v1/patterns/"
    data = api_examples.pattern_post.value
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == api_examples.pattern_post_response.value


def test_retrieve_pattern_success(client, pattern):
    url = f"/api/pattern-service/v1/patterns/{pattern.pk}/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == api_examples.pattern_response.value


def test_list_patterns_success(client, pattern):
    url = "/api/pattern-service/v1/patterns/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [api_examples.pattern_response.value]


def test_create_pattern_instance_success(client, pattern):
    url = "/api/pattern-service/v1/pattern_instances/"
    data = api_examples.pattern_instance_post.value
    data["pattern"] = pattern.pk
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == api_examples.pattern_instance_post_response.value


def test_retrieve_pattern_instance_success(client, controller_label, pattern_instance):
    pattern_instance.controller_labels.add(controller_label)
    url = f"/api/pattern-service/v1/pattern_instances/{pattern_instance.pk}/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == api_examples.pattern_instance_response.value


def test_list_pattern_instances_success(client, controller_label, pattern_instance):
    pattern_instance.controller_labels.add(controller_label)
    url = "/api/pattern-service/v1/pattern_instances/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [api_examples.pattern_instance_response.value]


def test_retrieve_task_success(client, task):
    url = f"/api/pattern-service/v1/tasks/{task.pk}/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == api_examples.task_response.value


def test_list_tasks_success(client, task):
    url = "/api/pattern-service/v1/tasks/"
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [api_examples.task_response.value]
