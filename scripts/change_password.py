"""
Change a user's password in the database using the app's hashing function.
Run with: python scripts/change_password.py
"""
import asyncio
from getpass import getpass
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import get_settings
from app.core.security import get_password_hash

async def main():
    settings = get_settings()
    username = input("Username to change password for: ")
    password = getpass("New password (will be hidden): ")
    if not password:
        print("No password entered, aborting.")
        return
    password_hash = get_password_hash(password)
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": username})
        if res.scalar_one_or_none() is None:
            print(f"User '{username}' not found.")
            return
        await conn.execute(
            text("UPDATE users SET password_hash = :password_hash WHERE username = :username"),
            {"username": username, "password_hash": password_hash}
        )
        print(f"Password for '{username}' updated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
