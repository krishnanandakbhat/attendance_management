from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.sessions import Session
from app.schemas.sessions import Session as SessionSchema
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.get("/", response_model=List[SessionSchema])
async def list_sessions(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all active sessions for the current user."""
    sessions = await db.scalars(
        Session.__table__.select()
        .where(Session.user_id == current_user.id)
        .order_by(Session.last_seen.desc())
    )
    return sessions.all()

@router.delete("/{session_id}")
async def revoke_session(
    session_id: int,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Revoke a specific session."""
    session = await db.scalar(
        Session.__table__.select()
        .where(Session.id == session_id)
        .where(Session.user_id == current_user.id)
    )
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    await db.execute(Session.__table__.delete().where(Session.id == session_id))
    await db.commit()
    
    return {"message": "Session revoked successfully"}