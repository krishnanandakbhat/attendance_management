"""Initialize the database and create an admin user."""
import asyncio
import os
from getpass import getpass

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.models.users import User
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import command
from alembic.config import Config

async def init_db():
    settings = get_settings()
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    
    # Create admin user
    admin_username = input("Enter admin username (default: admin): ") or "admin"
    admin_email = input("Enter admin email (default: admin@example.com): ") or "admin@example.com"
    admin_password = getpass("Enter admin password (default: admin): ") or "admin"

    # Create admin user in database
    engine = create_async_engine(settings.SQLITE_URL)
    async with engine.begin() as conn:
        # Check if admin user exists
        result = await conn.execute(
            "SELECT id FROM users WHERE username = :username",
            {"username": admin_username}
        )
        if result.scalar_one_or_none() is None:
            # Create admin user
            await conn.execute(
                """
                INSERT INTO users (username, email, password_hash, is_active)
                VALUES (:username, :email, :password_hash, true)
                """,
                {
                    "username": admin_username,
                    "email": admin_email,
                    "password_hash": get_password_hash(admin_password)
                }
            )
            print(f"\nAdmin user '{admin_username}' created successfully!")
        else:
            print(f"\nAdmin user '{admin_username}' already exists.")

if __name__ == "__main__":
    asyncio.run(init_db())