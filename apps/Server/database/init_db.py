"""Database initialization module."""

import os
from app.config.database import get_database_connection, close_database_connection


def init_database() -> bool:
    """Initialize database by running schema.sql.

    This function is idempotent - it can be run multiple times safely.

    Returns:
        True if successful, False otherwise
    """
    conn = get_database_connection()
    if not conn:
        print("WARN [InitDB]: No database connection available")
        return False

    try:
        # Get the schema file path
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

        if not os.path.exists(schema_path):
            print(f"ERROR [InitDB]: Schema file not found: {schema_path}")
            return False

        # Read schema
        with open(schema_path, "r") as f:
            schema = f.read()

        # Execute schema
        with conn.cursor() as cur:
            cur.execute(schema)

        conn.commit()
        print("INFO [InitDB]: Database schema initialized successfully")
        return True

    except Exception as e:
        print(f"ERROR [InitDB]: Failed to initialize database: {e}")
        conn.rollback()
        return False

    finally:
        close_database_connection(conn)


def check_tables_exist() -> bool:
    """Check if core tables exist in the database.

    Returns:
        True if users table exists, False otherwise
    """
    conn = get_database_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'users'
                )
                """
            )
            result = cur.fetchone()
            return result[0] if result else False

    except Exception as e:
        print(f"ERROR [InitDB]: Failed to check tables: {e}")
        return False

    finally:
        close_database_connection(conn)


if __name__ == "__main__":
    # Allow running this file directly for initialization
    success = init_database()
    if success:
        print("Database initialized successfully")
    else:
        print("Database initialization failed")
        exit(1)
