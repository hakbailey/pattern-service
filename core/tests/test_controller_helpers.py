import pytest
from unittest.mock import patch, MagicMock
import os

from core.utils.controller import build_collection_uri, download_collection


# @pytest.fixture
# def mock_settings():
#     """A fixture to mock the Django settings for the AAP_URL."""
#     with patch('your_module_name.settings.AAP_URL', 'https://example-hub.com'):
#         yield

@pytest.fixture
def mock_tar_data():
    """A fixture to provide mock tarball data."""
    return b"This is some mock tarball content"


@pytest.mark.parametrize("collection_name, version, expected_uri", [
    ("my_namespace.my_collection", "1.2.3", "https://example-hub.com/api/galaxy/v3/plugin/ansible/content/published/collections/artifacts/my_namespace-my_collection-1.2.3.tar.gz"),
    ("another.collection", "2.0.0", "https://example-hub.com/api/galaxy/v3/plugin/ansible/content/published/collections/artifacts/another-collection-2.0.0.tar.gz"),
    ("edge.case", "0.1.0-beta", "https://example-hub.com/api/galaxy/v3/plugin/ansible/content/published/collections/artifacts/edge-case-0.1.0-beta.tar.gz")
])
def test_build_collection_uri(collection_name, version, expected_uri):
    """
    Tests that various collection names and versions build the correct URI.
    """
    assert build_collection_uri(collection_name, version) == expected_uri

@pytest.fixture
def mock_download_success(mock_tar_data):
    """
    Corrected fixture to mock a successful download scenario.
    """
    # The patch targets should be where the modules are used.
    # If the functions are in `core.utils.controller.py`, this is the correct path.
    with patch('core.utils.controller.helpers.get') as mock_get, \
         patch('core.utils.controller.helpers.tarfile') as mock_tarfile, \
         patch('core.utils.controller.helpers.shutil') as mock_shutil, \
         patch('core.utils.controller.helpers.tempfile') as mock_tempfile:

        # Mock the tarfile context manager
        mock_tar_open = mock_tarfile.open
        mock_tar_open.return_value.__enter__.return_value = MagicMock()

        # Mock the response from the 'get' function
        mock_response = MagicMock()
        mock_response.raw = mock_tar_data
        mock_get.return_value = mock_response

        # Correctly mock the temp directory and path joins
        mock_tempfile.mkdtemp.return_value = '/mock/temp/dir'
        
        yield mock_get, mock_tar_open, mock_shutil


# def test_download_collection_success(mock_download_success):
#     """
#     Tests the successful download and extraction of a collection.
#     """
#     mock_get, mock_tar_open, mock_mkdtemp = mock_download_success

#     collection_name = 'my_namespace.my_collection'
#     version = '1.0.0'
#     expected_path = os.path.join('/mock/temp/dir', 'my_namespace-my_collection-1.0.0')

#     with download_collection(collection_name, version) as path:
#         assert path == expected_path
#         mock_get.assert_called_once()
#         mock_tar_open.assert_called_once()
#         mock_tar_open.return_value.__enter__.return_value.extractall.assert_called_once_with(
#             path=expected_path,
#             filter="data"
#         )
#         mock_mkdtemp.assert_called_once()
    

# def test_download_collection_failure_cleans_up():
#     """
#     Tests that an exception during download correctly cleans up the temp directory.
#     """
#     with patch('core.utils.controller.helpers.get', side_effect=Exception('Network error')), \
#          patch('core.utils.controller.helpers.shutil.rmtree') as mock_rmtree, \
#          patch('core.utils.controller.helpers.tempfile.mkdtemp', return_value='/mock/temp/dir') as mock_mkdtemp:

#         collection_name = 'my_namespace.my_collection'
#         version = '1.0.0'
        
#         with pytest.raises(Exception, match='Network error'):
#             with download_collection(collection_name, version):
#                 pass
        
#         mock_mkdtemp.assert_called_once()
#         mock_rmtree.assert_called_once_with('/mock/temp/dir')
