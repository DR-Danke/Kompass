"""Database connection utilities."""

from typing import Optional
import psycopg2
from psycopg2.extensions import connection
from .settings import get_settings


def get_database_connection() -> Optional[connection]:
    """Create a new database connection.

    Returns:
        Database connection if successful, None otherwise
    """
    settings = get_settings()

    if not settings.DATABASE_URL:
        print("WARN [Database]: DATABASE_URL not set")
        return None

    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        return conn
    except Exception as e:
        print(f"ERROR [Database]: Failed to connect: {e}")
        return None


def close_database_connection(conn: Optional[connection]) -> None:
    """Close a database connection safely.

    Args:
        conn: Database connection to close
    """
    if conn:
        try:
            conn.close()
        except Exception as e:
            print(f"ERROR [Database]: Failed to close connection: {e}")
