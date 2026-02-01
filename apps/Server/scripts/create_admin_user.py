#!/usr/bin/env python3
"""Script to create an admin user."""

import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from app.repository.user_repository import user_repository

# Password hashing context (same as used in auth_service)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user(email: str, password: str, first_name: str = None, last_name: str = None):
    """Create an admin user with the given credentials."""

    # Check if user already exists
    existing_user = user_repository.get_user_by_email(email)
    if existing_user:
        print(f"User {email} already exists with role: {existing_user['role']}")
        return existing_user

    # Hash the password
    password_hash = pwd_context.hash(password)

    # Create the user
    user = user_repository.create_user(
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        role="admin"
    )

    if user:
        print(f"Successfully created admin user: {user['email']}")
        print(f"  ID: {user['id']}")
        print(f"  Role: {user['role']}")
        return user
    else:
        print("Failed to create user")
        return None


if __name__ == "__main__":
    create_admin_user(
        email="danke@huevos.ai",
        password="Tremarel2026",
        first_name="Danke",
        last_name="Admin"
    )
