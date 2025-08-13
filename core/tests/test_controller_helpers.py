import os
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from core.utils.controller import build_collection_uri
from core.utils.controller import download_collection


@pytest.fixture
def mock_tar_data():
    """A fixture to provide mock tarball data."""
    return b"This is some mock tarball content"


@pytest.fixture
def mock_download_success(mock_tar_data):
    """
    Corrected fixture to mock a successful download scenario,
    including mocking os.makedirs and ensuring cleanup.
    """
    with (
        patch("core.utils.controller.helpers.get") as mock_get,
        patch("core.utils.controller.helpers.tarfile.open") as mock_tar_open,
        patch("core.utils.controller.helpers.os.makedirs") as mock_makedirs,
        patch("core.utils.controller.helpers.shutil.rmtree") as mock_rmtree,
        patch(
            "core.utils.controller.helpers.tempfile.mkdtemp",
            return_value="/mock/temp/dir",
        ) as mock_mkdtemp,
    ):

        mock_response = MagicMock()
        mock_response.raw = mock_tar_data
        mock_get.return_value = mock_response

        mock_tar_open.return_value.__enter__.return_value = MagicMock()

        yield mock_get, mock_tar_open, mock_makedirs, mock_mkdtemp, mock_rmtree


@pytest.fixture
def mock_download_failure():
    """
    Fixture to mock a download failure scenario by raising an exception
    and mocking the cleanup functions.
    """
    with (
        patch(
            "core.utils.controller.helpers.get", side_effect=Exception("Network error")
        ) as mock_get,
        patch("core.utils.controller.helpers.shutil.rmtree") as mock_rmtree,
        patch("core.utils.controller.helpers.os.makedirs"),
        patch(
            "core.utils.controller.helpers.tempfile.mkdtemp",
            return_value="/mock/temp/dir",
        ) as mock_mkdtemp,
    ):

        yield mock_get, mock_rmtree, mock_mkdtemp


@pytest.mark.parametrize(
    "collection_name, version, expected_uri",
    [
        (
            "another.collection",
            "2.0.0",
            (
                "http://localhost:44926/api/galaxy/v3/plugin/ansible/content/published/"
                "collections/artifacts/another-collection-2.0.0.tar.gz"
            ),
        ),
        (
            "edge.case",
            "0.1.0-beta",
            (
                "http://localhost:44926/api/galaxy/v3/plugin/ansible/content/published/"
                "collections/artifacts/edge-case-0.1.0-beta.tar.gz"
            ),
        ),
    ],
)
def test_build_collection_uri(collection_name, version, expected_uri):
    """
    Tests that various collection names and versions build the correct URI.
    """
    assert build_collection_uri(collection_name, version) == expected_uri


def test_download_collection_success(mock_download_success):
    """
    Tests the successful download and extraction of a collection.
    """
    mock_get, mock_tar_open, mock_makedirs, mock_mkdtemp, mock_rmtree = (
        mock_download_success
    )

    collection_name = "my_namespace.my_collection"
    version = "1.0.0"
    expected_path = os.path.join("/mock/temp/dir", "my_namespace.my_collection-1.0.0")

    with download_collection(collection_name, version) as path:
        # Assert that the correct path was yielded
        assert path == expected_path

        mock_mkdtemp.assert_called_once()
        mock_makedirs.assert_called_once_with(expected_path, exist_ok=True)
        mock_get.assert_called_once()
        mock_tar_open.assert_called_once()

    mock_rmtree.assert_called_once_with("/mock/temp/dir")


def test_download_collection_failure(mock_download_failure):
    """
    Tests that an exception during download.
    """
    mock_get, mock_rmtree, mock_mkdtemp = mock_download_failure

    collection_name = "my_namespace.my_collection"
    version = "1.0.0"

    with pytest.raises(Exception, match="Network error"):
        with download_collection(collection_name, version):
            pass

    mock_mkdtemp.assert_called_once()
    mock_rmtree.assert_called_once_with("/mock/temp/dir")
