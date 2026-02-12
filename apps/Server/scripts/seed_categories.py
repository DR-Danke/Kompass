#!/usr/bin/env python3
"""Seed script for categories from supplier catalog folder structure."""

import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repository.kompass_repository import category_repository

# Category tree matching the supplier catalog folder structure.
# Keys are root categories, values are lists of subcategories.
CATEGORY_TREE = {
    "BAÑOS": ["Griferías", "Lavamanos", "Sanitarios y Muebles de Baño"],
    "DECK - FACHADAS": [],
    "DISPENSADORES": [],
    "DOTACIÓN DE COCINA": [],
    "ESPEJOS": [],
    "ILUMINACIÓN": [],
    "MOBILIARIO": [
        "Camas",
        "Mesas de Noche",
        "Mobiliario Restaurante",
        "Mobiliario a Medida",
    ],
    "ONE STOP SHOP": [],
    "PISOS - GUARDAESCOBAS": ["SPC Floor", "Guardaescobas"],
    "REVESTIMIENTOS": ["Panel Exterior", "Panel Interior"],
    "TARIMAS & EVENTOS": [],
}


def seed_categories() -> dict:
    """Seed categories from the hardcoded tree.

    Returns:
        Dict with 'mappings' ({category_path: uuid_string}),
        'created' count, and 'skipped' count.
    """
    mappings = {}
    created = 0
    skipped = 0

    for root_name, children in CATEGORY_TREE.items():
        # Check if root category already exists
        existing = category_repository.get_by_name_and_parent(root_name, None)
        if existing:
            root_id = existing["id"]
            print(f"  SKIP [Category]: Root '{root_name}' already exists ({root_id})")
            skipped += 1
        else:
            result = category_repository.create(name=root_name)
            if result:
                root_id = result["id"]
                print(f"  CREATE [Category]: Root '{root_name}' ({root_id})")
                created += 1
            else:
                print(f"  ERROR [Category]: Failed to create root '{root_name}'")
                continue

        mappings[root_name] = str(root_id)

        # Seed children
        for child_name in children:
            existing_child = category_repository.get_by_name_and_parent(
                child_name, root_id
            )
            if existing_child:
                child_id = existing_child["id"]
                print(
                    f"  SKIP [Category]: Child '{root_name}/{child_name}' "
                    f"already exists ({child_id})"
                )
                skipped += 1
            else:
                child_result = category_repository.create(
                    name=child_name, parent_id=root_id
                )
                if child_result:
                    child_id = child_result["id"]
                    print(
                        f"  CREATE [Category]: Child '{root_name}/{child_name}' "
                        f"({child_id})"
                    )
                    created += 1
                else:
                    print(
                        f"  ERROR [Category]: Failed to create "
                        f"child '{root_name}/{child_name}'"
                    )
                    continue

            mappings[f"{root_name}/{child_name}"] = str(child_id)

    return {"mappings": mappings, "created": created, "skipped": skipped}


if __name__ == "__main__":
    print("INFO [SeedCategories]: Starting category seeding...")
    result = seed_categories()
    print(
        f"\nINFO [SeedCategories]: Done. "
        f"Created: {result['created']}, Skipped: {result['skipped']}"
    )
