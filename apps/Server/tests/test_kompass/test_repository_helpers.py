"""Unit tests for repository helper methods: get_by_name_and_parent, get_by_name."""

from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.repository.kompass_repository import CategoryRepository, SupplierRepository


# =============================================================================
# CATEGORY REPOSITORY: get_by_name_and_parent
# =============================================================================


class TestCategoryGetByNameAndParent:
    """Tests for CategoryRepository.get_by_name_and_parent()."""

    def setup_method(self):
        self.repo = CategoryRepository()
        self.now = datetime.now()

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_find_root_category(self, mock_get_conn, mock_close_conn):
        """Test finding an existing root category (parent_id=None)."""
        category_id = uuid4()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            category_id,
            "BAÑOS",
            None,
            None,
            0,
            True,
            self.now,
            self.now,
        )
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name_and_parent("BAÑOS", None)

        assert result is not None
        assert result["id"] == category_id
        assert result["name"] == "BAÑOS"
        assert result["parent_id"] is None
        mock_cursor.execute.assert_called_once()
        sql = mock_cursor.execute.call_args[0][0]
        assert "LOWER(name) = LOWER(%s)" in sql
        assert "IS NOT DISTINCT FROM" in sql
        params = mock_cursor.execute.call_args[0][1]
        assert params == ("BAÑOS", None)

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_find_child_category(self, mock_get_conn, mock_close_conn):
        """Test finding an existing child category (parent_id=UUID)."""
        parent_id = uuid4()
        child_id = uuid4()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            child_id,
            "Griferías",
            None,
            parent_id,
            0,
            True,
            self.now,
            self.now,
        )
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name_and_parent("Griferías", parent_id)

        assert result is not None
        assert result["id"] == child_id
        assert result["name"] == "Griferías"
        assert result["parent_id"] == parent_id
        params = mock_cursor.execute.call_args[0][1]
        assert params == ("Griferías", str(parent_id))

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_not_found_returns_none(self, mock_get_conn, mock_close_conn):
        """Test returning None when category not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name_and_parent("Nonexistent", None)

        assert result is None

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_case_insensitive_query(self, mock_get_conn, mock_close_conn):
        """Test that the query uses case-insensitive matching."""
        category_id = uuid4()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            category_id,
            "BAÑOS",
            None,
            None,
            0,
            True,
            self.now,
            self.now,
        )
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name_and_parent("baños", None)

        assert result is not None
        sql = mock_cursor.execute.call_args[0][0]
        assert "LOWER(name) = LOWER(%s)" in sql

    @patch("app.repository.kompass_repository.get_database_connection")
    def test_no_connection_returns_none(self, mock_get_conn):
        """Test returning None when database connection fails."""
        mock_get_conn.return_value = None

        result = self.repo.get_by_name_and_parent("BAÑOS", None)

        assert result is None

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_database_error_returns_none(self, mock_get_conn, mock_close_conn):
        """Test returning None on database exception."""
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=Exception("DB error")
        )
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name_and_parent("BAÑOS", None)

        assert result is None


# =============================================================================
# SUPPLIER REPOSITORY: get_by_name
# =============================================================================


class TestSupplierGetByName:
    """Tests for SupplierRepository.get_by_name()."""

    def setup_method(self):
        self.repo = SupplierRepository()
        self.now = datetime.now()

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_find_existing_supplier(self, mock_get_conn, mock_close_conn):
        """Test finding an existing supplier by name."""
        supplier_id = uuid4()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            supplier_id,
            "BWBYONE",
            "BWB001",
            "active",
            "John Doe",
            "john@example.com",
            "123456",
            "123 Street",
            "Guangzhou",
            "China",
            "https://example.com",
            "Test notes",
            self.now,
            self.now,
        )
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name("BWBYONE")

        assert result is not None
        assert result["id"] == supplier_id
        assert result["name"] == "BWBYONE"
        mock_cursor.execute.assert_called_once()
        sql = mock_cursor.execute.call_args[0][0]
        assert "LOWER(name) = LOWER(%s)" in sql
        assert "LIMIT 1" in sql

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_not_found_returns_none(self, mock_get_conn, mock_close_conn):
        """Test returning None when supplier not found."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name("Nonexistent")

        assert result is None

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_case_insensitive_query(self, mock_get_conn, mock_close_conn):
        """Test that the query uses case-insensitive matching."""
        supplier_id = uuid4()
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (
            supplier_id,
            "BWBYONE",
            "BWB001",
            "active",
            None,
            None,
            None,
            None,
            None,
            "China",
            None,
            None,
            self.now,
            self.now,
        )
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name("bwbyone")

        assert result is not None
        sql = mock_cursor.execute.call_args[0][0]
        assert "LOWER(name) = LOWER(%s)" in sql

    @patch("app.repository.kompass_repository.get_database_connection")
    def test_no_connection_returns_none(self, mock_get_conn):
        """Test returning None when database connection fails."""
        mock_get_conn.return_value = None

        result = self.repo.get_by_name("BWBYONE")

        assert result is None

    @patch("app.repository.kompass_repository.close_database_connection")
    @patch("app.repository.kompass_repository.get_database_connection")
    def test_database_error_returns_none(self, mock_get_conn, mock_close_conn):
        """Test returning None on database exception."""
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(
            side_effect=Exception("DB error")
        )
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)
        mock_get_conn.return_value = mock_conn

        result = self.repo.get_by_name("BWBYONE")

        assert result is None
