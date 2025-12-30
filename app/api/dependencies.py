from typing import Optional
from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_db
from app.models.users import User
from app.models.sessions import Session

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user. Accepts token from header or cookie."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # If no Authorization header, try to get token from cookie
    if not token:
        token = request.cookies.get("session") or request.cookies.get("access_token")
    
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    # Verify session
    stmt = select(Session).where(
        Session.session_token == token,
        Session.user_id == user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise credentials_exception

    # Update last seen
    await db.execute(
        Session.__table__.update()
        .where(Session.id == session.id)
        .values(last_seen=datetime.utcnow())
    )
    await db.commit()

    return user


async def get_optional_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Attempt to return the current user or None if unauthenticated.

    This helper reads the Authorization header (Bearer token) but does not
    raise on missing/invalid credentials — it returns None instead which is
    convenient for template rendering.
    """
    auth: Optional[str] = request.headers.get("authorization")
    if not auth:
        # Also check for cookies (session or access_token)
        cookie = request.cookies.get("session") or request.cookies.get("access_token")
        if cookie:
            # support raw token cookies or 'Bearer <token>' formatted cookies
            if cookie.startswith("Bearer "):
                auth = cookie
            else:
                auth = f"Bearer {cookie}"
    if not auth or not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None:
        return None

    # Verify session exists for this token
    stmt = select(Session).where(
        Session.session_token == token,
        Session.user_id == user.id,
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        return None

    return user