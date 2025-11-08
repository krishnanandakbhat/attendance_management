from cryptography.fernet import Fernet
from typing import Optional
from datetime import datetime, timedelta
import bcrypt
import jwt
from .config import get_settings

settings = get_settings()

# Age encryption
fernet = Fernet(settings.AGE_ENCRYPTION_KEY.encode())

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8')[:72],
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def encrypt_age(age: int) -> bytes:
    return fernet.encrypt(str(age).encode())

def decrypt_age(encrypted_age: bytes) -> int:
    return int(fernet.decrypt(encrypted_age).decode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt