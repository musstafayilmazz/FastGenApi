
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from backend.routers.file_route import router

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@patch("backend.routers.file_route.delete_pdf_and_records")
def test_delete_pdf_and_records_route(mock_delete_pdf_and_records):
    """
    This test, controls pdf and records delete route's (/file/delete) behaviour under successful conditions.
    Args:
        mock_delete_pdf_and_records:

    Returns: Success/Fail statement

    """
    filename = "testfile.pdf"
    request_data = {"filename": filename}

    mock_delete_pdf_and_records.return_value = {"status": "success", "message": "File deleted successfully"}


    response = client.request("DELETE", "/file/delete", json=request_data)


    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "File deleted successfully"}
    mock_delete_pdf_and_records.assert_called_once_with(filename)


@patch("backend.routers.file_route.delete_pdf_and_records")
def test_delete_pdf_and_records_route_failure(mock_delete_pdf_and_records):
    """
    This test, controls pdf and records delete route's /file/delete behaviour under failure conditions.
    Args:
        mock_delete_pdf_and_records:

    Returns: Success/Fail statement

    """
    filename = "nonexistentfile.pdf"
    request_data = {"filename": filename}

    mock_delete_pdf_and_records.return_value = {"status": "error", "message": "File not found"}

    response = client.request("DELETE", "/file/delete", json=request_data)

    assert response.status_code == 500
    assert response.json() == {"detail": "File not found"}
    mock_delete_pdf_and_records.assert_called_once_with(filename)

@patch("backend.routers.file_route.minio_list_files")
def test_list_files_route(mock_minio_list_files):
    """
    This test, controls minio list files (/file/list) behaviour under successful conditions.
    Args:
        mock_minio_list_files:

    Returns: Success/Fail statement

    """

    mock_file_list = {"files": ["file1.pdf", "file2.pdf", "file3.pdf"]}
    mock_minio_list_files.return_value = mock_file_list


    response = client.get("/file/list")


    assert response.status_code == 200
    assert response.json() == mock_file_list
    mock_minio_list_files.assert_called_once()
