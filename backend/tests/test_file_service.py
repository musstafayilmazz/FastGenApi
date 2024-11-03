import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
import pytest
from backend.services.fileService import delete_pdf_and_records
from backend.config import config
from backend.database.db_models import PdfEmbedding
from fastapi import HTTPException
from minio.error import S3Error



@patch('backend.services.fileService.create_db_and_table')
@patch('backend.services.fileService.Minio')
def test_delete_pdf_and_records_success(mock_minio, mock_create_db_and_table):
    """
    This test controls delete service's behaviour under successful conditions
    Args:
        mock_minio:
        mock_create_db_and_table:

    Returns: Success/Fail statement

    """

    filename = 'testfile.pdf'

    mock_minio_client = MagicMock()
    mock_minio.return_value = mock_minio_client

    mock_minio_client.remove_object.return_value = None

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session

    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.delete.return_value = 1

    result = delete_pdf_and_records(filename)

    mock_minio_client.remove_object.assert_called_with(config.MINIO_BUCKET_NAME, filename)
    mock_session.query.assert_called_with(PdfEmbedding)
    mock_query.filter.assert_called()
    mock_filter.delete.assert_called()
    mock_session.commit.assert_called()

    assert result == {"status": "success", "message": f"Deleted {filename} from MinIO and PostgreSQL"}


@patch('backend.services.fileService.create_db_and_table')
@patch('backend.services.fileService.Minio')


def test_delete_pdf_and_records_minio_error(mock_minio, mock_create_db_and_table):
    """
    This test controls delete service's behaviour under failure conditions'
    Args:
        mock_minio:
        mock_create_db_and_table:

    Returns: Success/Fail statement

    """

    filename = 'testfile.pdf'

    mock_minio_client = MagicMock()
    mock_minio.return_value = mock_minio_client

    mock_minio_client.remove_object.side_effect = S3Error(
        code="MockedCode",
        message="Mocked error message",
        resource="Mocked resource",
        request_id="Mocked request ID",
        host_id="Mocked host ID",
        response=None
    )

    result = delete_pdf_and_records(filename)

    mock_minio_client.remove_object.assert_called_with(config.MINIO_BUCKET_NAME, filename)
    assert result == {"status": "error", "message": f"Failed to delete {filename} from MinIO"}


@patch('backend.services.fileService.create_db_and_table')
@patch('backend.services.fileService.Minio')
def test_delete_pdf_and_records_no_db_records(mock_minio, mock_create_db_and_table):
    """
    This test controls delete service's behaviour under failure conditions (No Record)
    Args:
        mock_minio:
        mock_create_db_and_table:

    Returns: Success/Fail statement

    """

    filename = 'testfile.pdf'

    mock_minio_client = MagicMock()
    mock_minio.return_value = mock_minio_client
    mock_minio_client.remove_object.return_value = None

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session

    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.delete.return_value = 0

    with pytest.raises(HTTPException) as exc_info:
        delete_pdf_and_records(filename)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == f"No records found for filename {filename}"


@patch('backend.services.fileService.create_db_and_table')
@patch('backend.services.fileService.Minio')
def test_delete_pdf_and_records_db_exception(mock_minio, mock_create_db_and_table):
    """
    This test controls delete service's behaviour under failure conditions (Exception)
    Args:
        mock_minio:
        mock_create_db_and_table:

    Returns:

    """

    filename = 'testfile.pdf'

    mock_minio_client = MagicMock()
    mock_minio.return_value = mock_minio_client
    mock_minio_client.remove_object.return_value = None

    mock_session = MagicMock()
    mock_create_db_and_table.return_value = mock_session

    mock_query = mock_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_filter.delete.side_effect = Exception("Database error")

    result = delete_pdf_and_records(filename)

    mock_session.rollback.assert_called()
    assert result == {"status": "error", "message": f"Failed to delete records for {filename} from PostgreSQL"}




