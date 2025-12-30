"""Create a user in the application's database.

Run this from the project root with the venv active:

    source .venv/bin/activate
    python scripts/create_user.py

The script will prompt for username, email and password.
"""
import asyncio
from getpass import getpass
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import get_settings
from app.core.security import get_password_hash


async def main():
    settings = get_settings()

    username = input("Username (default: admin): ") or "admin"
    email = input("Email (default: admin@example.com): ") or "admin@example.com"
    password = getpass("Password (will be hidden): ")
    if not password:
        print("No password entered, aborting.")
        return

    password_hash = get_password_hash(password)

    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Check if user exists
        res = await conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": username})
        if res.scalar_one_or_none() is not None:
            print(f"User '{username}' already exists.")
            return

        await conn.execute(
            text(
                """
                INSERT INTO users (username, email, password_hash, is_active)
                VALUES (:username, :email, :password_hash, 1)
                """
            ),
            {"username": username, "email": email, "password_hash": password_hash}
        )
        print(f"User '{username}' created successfully.")

if __name__ == "__main__":
    asyncio.run(main())
