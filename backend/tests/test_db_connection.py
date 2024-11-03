from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app

client = TestClient(app)

@patch("backend.database.db_connection.connect_to_db")
def test_get_db_connection_success(mock_connect_to_db):
    """
    This test creates a mock database and test connection
    Args:
        mock_connect_to_db:

    Returns: Success/Fail statement

    """
    mock_session = MagicMock()
    mock_connect_to_db.return_value = mock_session

    response = client.get("/db_connection")

    assert response.status_code == 200
    assert response.json() == {"db_connection": "Database connection is active"}


