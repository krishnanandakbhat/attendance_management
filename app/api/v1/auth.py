from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.models.users import User
from app.models.sessions import Session
from app.schemas.users import UserLogin, User as UserSchema

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and create a new session."""
     # Find user
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Check active sessions count
    stmt = select(func.count()).select_from(Session).where(
        Session.user_id == user.id,
        Session.last_seen > datetime.utcnow() - timedelta(minutes=settings.SESSION_CLEANUP_MINUTES),
    )
    active_sessions = await db.scalar(stmt)

    if active_sessions >= settings.MAX_DEVICES_PER_USER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of devices reached. Please logout from another device."
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username}
    )

    # Create session
    session = Session(
        user_id=user.id,
        device_name=request.headers.get("User-Agent", "Unknown Device"),
        session_token=access_token,
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(session)
    await db.commit()

    # Set cookie (mark secure only when running over HTTPS)
    secure_cookie = (request.url.scheme == "https")
    response.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Invalidate the current session."""
    session_token = request.cookies.get("session")
    if session_token:
        await db.execute(
            Session.__table__.delete().where(Session.session_token == session_token)
        )
        await db.commit()
        response.delete_cookie(key="session")
    
    return {"message": "Successfully logged out"}