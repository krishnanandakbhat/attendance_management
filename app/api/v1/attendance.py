from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from app.core.database import get_db
from app.models.attendance import Attendance
from app.models.students import Student
from app.schemas.attendance import AttendanceCreate, Attendance as AttendanceSchema
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.post("/", response_model=AttendanceSchema)
async def mark_attendance(
    attendance: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Mark attendance for a student on a specific date."""
    # Check if student exists
    stmt = select(Student).where(Student.id == attendance.student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check for duplicate attendance
    stmt = select(Attendance).where(
        and_(
            Attendance.student_id == attendance.student_id,
            Attendance.date == attendance.date
        )
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance already marked for this student on this date"
        )
    
    # Create attendance record
    db_attendance = Attendance(
        student_id=attendance.student_id,
        date=attendance.date,
        marked_by_user_id=current_user.id
    )
    db.add(db_attendance)
    await db.commit()
    await db.refresh(db_attendance)
    
    return db_attendance

@router.get("/", response_model=List[AttendanceSchema])
async def list_attendance(
    student_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List attendance records with optional filtering."""
    query = select(Attendance)
    
    if student_id:
        query = query.where(Attendance.student_id == student_id)
    if start_date:
        query = query.where(Attendance.date >= start_date)
    if end_date:
        query = query.where(Attendance.date <= end_date)
    
    query = query.order_by(Attendance.date.desc())
    attendance_records = await db.scalars(query)
    return attendance_records.all()

@router.delete("/{attendance_id}")
async def delete_attendance(
    attendance_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an attendance record."""
    result = await db.execute(
        Attendance.__table__.delete()
        .where(Attendance.id == attendance_id)
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    await db.commit()
    
    return {"message": "Attendance record deleted successfully"}