"""
Unit tests for the Flask web application (`app.py`).

This module contains test cases for the functions in the `app.py` file,
focusing on database connection logic. It uses mocking to isolate functions
from external dependencies like the database and environment variables.
"""
import unittest
from unittest.mock import patch, MagicMock
import os
import pyodbc
from app import get_db_connection


class TestApp(unittest.TestCase):
    """Test suite for the core application logic."""

    @patch("os.environ.get")
    @patch("pyodbc.connect")
    def test_get_db_connection_uses_env_vars(self, mock_connect, mock_os_get):
        """
        Tests if get_db_connection correctly uses environment variables.

        This test mocks `os.environ.get` to provide a custom set of database
        credentials and mocks `pyodbc.connect` to prevent an actual database
        connection. It then asserts that `pyodbc.connect` was called with a
        connection string built from the mocked environment variables.

        Args:
            mock_connect (MagicMock): A mock for the `pyodbc.connect` function.
            mock_os_get (MagicMock): A mock for the `os.environ.get` function.
        """
        # Arrange
        mock_os_get.side_effect = lambda key, default: {
            "DB_SERVER": "test-server",
            "DB_NAME": "test-db",
            "DB_USER": "test-user",
            "DB_PASSWORD": "test-password",
        }.get(key, default)

        mock_connect.return_value = MagicMock()

        # Act
        conn = get_db_connection()

        # Assert
        self.assertIsNotNone(conn)

        expected_conn_str = (
            "Driver={ODBC Driver 18 for SQL Server};"
            "Server=test-server;"
            "Database=test-db;"
            "Uid=test-user;"
            "Pwd=test-password;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
        )

        mock_connect.assert_called_once_with(expected_conn_str)


if __name__ == "__main__":
    unittest.main()
