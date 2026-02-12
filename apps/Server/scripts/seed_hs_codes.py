#!/usr/bin/env python3
"""Seed script for HS codes with Colombian duty rates."""

import sys
import os
from decimal import Decimal

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.repository.kompass_repository import hs_code_repository

# Hardcoded HS codes with Colombian duty rates mapped to categories
HS_CODES = [
    {
        "code": "6910.10",
        "description": "Ceramic sanitaryware",
        "duty_rate": Decimal("15.00"),
        "notes": "Sanitarios y Muebles de Baño",
    },
    {
        "code": "7324.90",
        "description": "Sanitary ware, faucets",
        "duty_rate": Decimal("15.00"),
        "notes": "Griferías",
    },
    {
        "code": "9403.60",
        "description": "Wooden furniture",
        "duty_rate": Decimal("15.00"),
        "notes": "Mobiliario, Camas, Mesas de Noche",
    },
    {
        "code": "9403.20",
        "description": "Metal furniture",
        "duty_rate": Decimal("15.00"),
        "notes": "Mobiliario Restaurante",
    },
    {
        "code": "6907.21",
        "description": "Ceramic tiles/flags",
        "duty_rate": Decimal("10.00"),
        "notes": "REVESTIMIENTOS",
    },
    {
        "code": "9405.10",
        "description": "Chandeliers, lighting",
        "duty_rate": Decimal("15.00"),
        "notes": "ILUMINACIÓN",
    },
    {
        "code": "7013.49",
        "description": "Glassware, mirrors",
        "duty_rate": Decimal("15.00"),
        "notes": "ESPEJOS",
    },
    {
        "code": "3921.90",
        "description": "Plastic plates/sheets (SPC flooring)",
        "duty_rate": Decimal("10.00"),
        "notes": "SPC Floor, PISOS - GUARDAESCOBAS",
    },
    {
        "code": "7323.93",
        "description": "Stainless steel kitchenware",
        "duty_rate": Decimal("15.00"),
        "notes": "DOTACIÓN DE COCINA",
    },
    {
        "code": "3917.40",
        "description": "Plastic fittings (baseboards)",
        "duty_rate": Decimal("10.00"),
        "notes": "Guardaescobas",
    },
    {
        "code": "4411.14",
        "description": "MDF/fibreboard (decking)",
        "duty_rate": Decimal("5.00"),
        "notes": "DECK - FACHADAS",
    },
    {
        "code": "7324.10",
        "description": "Stainless steel sinks",
        "duty_rate": Decimal("15.00"),
        "notes": "Lavamanos",
    },
    {
        "code": "8481.80",
        "description": "Taps, valves, dispensers",
        "duty_rate": Decimal("10.00"),
        "notes": "DISPENSADORES",
    },
    {
        "code": "9401.61",
        "description": "Upholstered seating",
        "duty_rate": Decimal("15.00"),
        "notes": "Mobiliario a Medida",
    },
    {
        "code": "7610.90",
        "description": "Aluminum structures (stages)",
        "duty_rate": Decimal("10.00"),
        "notes": "TARIMAS & EVENTOS",
    },
]


def seed_hs_codes() -> dict:
    """Seed HS codes with Colombian duty rates.

    Returns:
        Dict with 'mappings' ({hs_code: uuid_string}),
        'created' count, and 'skipped' count.
    """
    mappings = {}
    created = 0
    skipped = 0

    for entry in HS_CODES:
        existing = hs_code_repository.get_by_code(entry["code"])
        if existing:
            mappings[entry["code"]] = str(existing["id"])
            print(
                f"  SKIP [HSCode]: '{entry['code']}' already exists ({existing['id']})"
            )
            skipped += 1
        else:
            result = hs_code_repository.create(
                code=entry["code"],
                description=entry["description"],
                duty_rate=entry["duty_rate"],
                notes=entry["notes"],
            )
            if result:
                mappings[entry["code"]] = str(result["id"])
                print(f"  CREATE [HSCode]: '{entry['code']}' ({result['id']})")
                created += 1
            else:
                print(f"  ERROR [HSCode]: Failed to create '{entry['code']}'")

    return {"mappings": mappings, "created": created, "skipped": skipped}


if __name__ == "__main__":
    print("INFO [SeedHSCodes]: Starting HS code seeding...")
    result = seed_hs_codes()
    print(
        f"\nINFO [SeedHSCodes]: Done. "
        f"Created: {result['created']}, Skipped: {result['skipped']}"
    )
