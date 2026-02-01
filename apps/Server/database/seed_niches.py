"""Seed script for default niches."""

from app.config.database import close_database_connection, get_database_connection


# Default niches for the Kompass Portfolio & Quotation System
DEFAULT_NICHES = [
    {
        "name": "Constructoras",
        "description": "Construction companies and general contractors",
    },
    {
        "name": "Estudios de Arquitectura",
        "description": "Architectural firms and design studios",
    },
    {
        "name": "Desarrolladores",
        "description": "Real estate developers and property development companies",
    },
    {
        "name": "Hoteles",
        "description": "Hotels, resorts, and hospitality establishments",
    },
    {
        "name": "Operadores Rentas Cortas",
        "description": "Short-term rental operators and vacation property managers",
    },
    {
        "name": "Retailers",
        "description": "Retail businesses and commercial stores",
    },
]


def seed_default_niches() -> bool:
    """Seed the database with default niches.

    This function is idempotent - it uses INSERT ... ON CONFLICT DO NOTHING
    to avoid duplicate entries.

    Returns:
        True if successful, False otherwise
    """
    conn = get_database_connection()
    if not conn:
        print("WARN [SeedNiches]: No database connection available")
        return False

    try:
        with conn.cursor() as cur:
            for niche in DEFAULT_NICHES:
                cur.execute(
                    """
                    INSERT INTO niches (name, description, is_active)
                    VALUES (%s, %s, TRUE)
                    ON CONFLICT (name) DO NOTHING
                    """,
                    (niche["name"], niche["description"]),
                )

        conn.commit()
        print(f"INFO [SeedNiches]: Seeded {len(DEFAULT_NICHES)} default niches")
        return True

    except Exception as e:
        print(f"ERROR [SeedNiches]: Failed to seed niches: {e}")
        conn.rollback()
        return False

    finally:
        close_database_connection(conn)


def list_niches() -> None:
    """List all niches in the database."""
    conn = get_database_connection()
    if not conn:
        print("WARN [SeedNiches]: No database connection available")
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, is_active
                FROM niches
                ORDER BY name
                """
            )
            rows = cur.fetchall()

            print(f"\nFound {len(rows)} niches:")
            print("-" * 80)
            for row in rows:
                status = "active" if row[3] else "inactive"
                print(f"  [{status}] {row[1]}: {row[2] or 'No description'}")
            print("-" * 80)

    except Exception as e:
        print(f"ERROR [SeedNiches]: Failed to list niches: {e}")

    finally:
        close_database_connection(conn)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_niches()
    else:
        success = seed_default_niches()
        if success:
            print("Niches seeded successfully")
            list_niches()
        else:
            print("Failed to seed niches")
            exit(1)
