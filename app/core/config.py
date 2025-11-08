from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Attendance Management System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    AGE_ENCRYPTION_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    BCRYPT_ROUNDS: int = 12
    
    # Database
    DATABASE_URL: str = "sqlite:///./attendance.db"
    
    # Network Security
    ALLOWED_HOSTS: List[str] = ["127.0.0.1", "localhost"]
    ALLOWED_ORIGINS: List[str] = ["http://127.0.0.1:8000", "http://localhost:8000"]
    
    # Session Management
    MAX_DEVICES_PER_USER: int = 2
    SESSION_CLEANUP_MINUTES: int = 60 * 24  # 24 hours
    
    class Config:
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    import os
    env_file = ".env.test" if os.getenv("TESTING") else ".env"
    return Settings(_env_file=env_file)