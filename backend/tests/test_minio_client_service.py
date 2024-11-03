
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


os.environ['ENV_STATE'] = 'dev'
os.environ['DEV_MINIO_ACCESS_KEY'] = 'test_access_key'
os.environ['DEV_MINIO_SECRET_KEY'] = 'test_secret_key'
os.environ['DEV_MINIO_BUCKET_NAME'] = 'test_bucket'
os.environ['DEV_MINIO_ENDPOINT'] = 'localhost:9000'

from unittest.mock import patch, MagicMock, mock_open
import pytest
from backend.services.minioClientService import list_files, upload_file
from backend.minioConfig import MinioConfig
from minio.error import S3Error
from fastapi import HTTPException
import requests



@patch('backend.services.minioClientService.MinioConfig')
def test_list_files_success(mock_minio_config):
    """
    This test control list files behaviour under successful conditions.
    Args:
        mock_minio_config:

    Returns: Success/Fail statement

    """

    mock_config_instance = MagicMock()
    mock_config_instance.get_client.return_value = MagicMock()
    mock_config_instance.minio_bucket_name = 'test_bucket'
    mock_minio_config.return_value = mock_config_instance

    mock_minio_client = mock_config_instance.get_client.return_value

    mock_object1 = MagicMock()
    mock_object1.object_name = 'file1.pdf'
    mock_object2 = MagicMock()
    mock_object2.object_name = 'file2.pdf'
    mock_minio_client.list_objects.return_value = [mock_object1, mock_object2]

    result = list_files()

    mock_minio_client.list_objects.assert_called_with('test_bucket')
    assert result == {'files': ['file1.pdf', 'file2.pdf']}



@patch('backend.services.minioClientService.MinioConfig')
def test_list_files_exception(mock_minio_config):
    """
    This test control list files behaviour under exception conditions.
    Args:
        mock_minio_config:

    Returns: Success/Fail statement

    """

    mock_config_instance = MagicMock()
    mock_config_instance.get_client.return_value = MagicMock()
    mock_config_instance.minio_bucket_name = 'test_bucket'
    mock_minio_config.return_value = mock_config_instance

    mock_minio_client = mock_config_instance.get_client.return_value

    mock_minio_client.list_objects.side_effect = Exception('Mocked exception')

    with pytest.raises(HTTPException) as exc_info:
        list_files()

    assert exc_info.value.status_code == 500
    assert 'Failed to list files' in exc_info.value.detail


@patch('backend.services.minioClientService.requests.get')
def test_upload_file_download_error(mock_requests_get):
    """
    This test control upload files behaviour under exception conditions (false url).
    Args:
        mock_requests_get:

    Returns:

    """
    URL = 'http://example.com/test.pdf'
    minio_file_name = 'test.pdf'

    mock_requests_get.side_effect = requests.exceptions.RequestException('Mocked download error')

    with pytest.raises(HTTPException) as exc_info:
        upload_file(URL, minio_file_name)

    assert exc_info.value.status_code == 400
    assert 'Error downloading the PDF' in exc_info.value.detail


@patch('backend.services.minioClientService.requests.get')
@patch('backend.services.minioClientService.Minio')
@patch('backend.services.minioClientService.MinioConfig')
def test_upload_file_success(mock_minio_config, mock_minio, mock_requests_get):
    """
    This test control upload files behaviour under successful conditions.
    Args:
        mock_minio_config:
        mock_minio:
        mock_requests_get:

    Returns: Success/Fail statement

    """
    URL = 'https://economy-finance.ec.europa.eu/document/download/29fe907c-6cf9-4c2c-9f5f-8c62f3513e23_en?filename=ip220_en.pdf'
    minio_file_name = 'test.pdf'
    pdf_content = b'%PDF-1.4 test pdf content'

    mock_response = MagicMock()
    mock_response.content = pdf_content
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    mock_config_instance = MagicMock()
    mock_config_instance.minio_endpoint = 'localhost:9000'
    mock_config_instance.minio_access_key = 'test_access_key'
    mock_config_instance.minio_secret_key = 'test_secret_key'
    mock_config_instance.minio_bucket_name = 'test_bucket'
    mock_minio_config.return_value = mock_config_instance

    mock_minio_client = mock_minio.return_value

    mock_minio_client.bucket_exists.return_value = True

    mock_minio_client.fput_object.return_value = None

    with patch('builtins.open', mock_open()) as mocked_file:
        upload_file(URL, minio_file_name)

    mock_requests_get.assert_called_with(URL)
    mock_minio_client.bucket_exists.assert_called_with('test_bucket')
    mock_minio_client.fput_object.assert_called_with(
        bucket_name='test_bucket',
        object_name=minio_file_name,
        file_path='/tmp/temp_pdf.pdf',
        content_type='application/pdf'
    )
    mocked_file().write.assert_called_with(pdf_content)


@patch('backend.services.minioClientService.requests.get')
@patch('backend.services.minioClientService.Minio')
@patch('backend.services.minioClientService.MinioConfig')
def test_upload_file_bucket_error(mock_minio_config, mock_minio, mock_requests_get):
    """
    This test control Minio Bucket's  behaviour under exception conditions (false url).
    Args:
        mock_minio_config:
        mock_minio:
        mock_requests_get:

    Returns: Success/Fail statement

    """
    URL = 'http://example.com/test.pdf'
    minio_file_name = 'test.pdf'
    pdf_content = b'%PDF-1.4 test pdf content'

    mock_response = MagicMock()
    mock_response.content = pdf_content
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    mock_config_instance = MagicMock()
    mock_config_instance.minio_endpoint = 'localhost:9000'
    mock_config_instance.minio_access_key = 'test_access_key'
    mock_config_instance.minio_secret_key = 'test_secret_key'
    mock_config_instance.minio_bucket_name = 'test_bucket'
    mock_minio_config.return_value = mock_config_instance

    mock_minio_client = mock_minio.return_value

    mock_minio_client.bucket_exists.side_effect = S3Error(
        code='MockedCode',
        message='Mocked error message',
        resource='Mocked resource',
        request_id='Mocked request ID',
        host_id='Mocked host ID',
        response=None
    )

    with patch('builtins.open', mock_open()):
        with pytest.raises(HTTPException) as exc_info:
            upload_file(URL, minio_file_name)

    assert exc_info.value.status_code == 500
    assert 'Error creating bucket' in exc_info.value.detail




@patch('backend.services.minioClientService.requests.get')
@patch('backend.services.minioClientService.Minio')
@patch('backend.services.minioClientService.MinioConfig')
def test_upload_file_upload_error(mock_minio_config, mock_minio, mock_requests_get):
    """
    This test control upload files behaviour under exception conditions (false url).
    Args:
        mock_minio_config:
        mock_minio:
        mock_requests_get:

    Returns:

    """
    URL = 'http://example.com/test.pdf'
    minio_file_name = 'test.pdf'
    pdf_content = b'%PDF-1.4 test pdf content'

    mock_response = MagicMock()
    mock_response.content = pdf_content
    mock_response.raise_for_status.return_value = None
    mock_requests_get.return_value = mock_response

    mock_config_instance = MagicMock()
    mock_config_instance.minio_endpoint = 'localhost:9000'
    mock_config_instance.minio_access_key = 'test_access_key'
    mock_config_instance.minio_secret_key = 'test_secret_key'
    mock_config_instance.minio_bucket_name = 'test_bucket'
    mock_minio_config.return_value = mock_config_instance

    mock_minio_client = mock_minio.return_value

    mock_minio_client.bucket_exists.return_value = True

    mock_minio_client.fput_object.side_effect = S3Error(
        code='MockedCode',
        message='Mocked error message',
        resource='Mocked resource',
        request_id='Mocked request ID',
        host_id='Mocked host ID',
        response=None
    )

    with patch('builtins.open', mock_open()):
        with pytest.raises(HTTPException) as exc_info:
            upload_file(URL, minio_file_name)

    assert exc_info.value.status_code == 500
    assert 'Error uploading the PDF to MinIO' in exc_info.value.detail





