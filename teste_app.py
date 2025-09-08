import unittest
from unittest.mock import patch, MagicMock
import os
import pyodbc
from app import get_db_connection

class TestApp(unittest.TestCase):

    @patch('os.environ.get')
    @patch('pyodbc.connect')
    def test_get_db_connection_uses_env_vars(self, mock_connect, mock_os_get):
        # Arrange
        mock_os_get.side_effect = lambda key, default: {
            'DB_SERVER': 'test-server',
            'DB_NAME': 'test-db',
            'DB_USER': 'test-user',
            'DB_PASSWORD': 'test-password'
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

if __name__ == '__main__':
    unittest.main()
