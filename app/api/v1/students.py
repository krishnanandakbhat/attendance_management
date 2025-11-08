from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.students import Student
from app.schemas.students import StudentCreate, StudentUpdate, Student as StudentSchema
from app.api.dependencies import get_current_user
from sqlalchemy import select

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=StudentSchema)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new student."""
    db_student = Student(
        name=student.name,
        level=student.level,
        price_per_class=student.price_per_class
    )
    db_student.set_age(student.age)
    
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    
    return db_student

@router.get("/", response_model=List[StudentSchema])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all students."""
    stmt = select(Student).order_by(Student.name).offset(skip).limit(limit)
    students = await db.scalars(stmt)
    return students.all()

@router.get("/{student_id}", response_model=StudentSchema)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific student by ID."""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    return student

@router.put("/{student_id}", response_model=StudentSchema)
async def update_student(
    student_id: int,
    student: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a student's information."""
    stmt = select(Student).where(Student.id == student_id)
    result = await db.execute(stmt)
    db_student = result.scalar_one_or_none()
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields if provided
    if student.name is not None:
        db_student.name = student.name
    if student.age is not None:
        db_student.set_age(student.age)
    if student.level is not None:
        db_student.level = student.level
    if student.price_per_class is not None:
        db_student.price_per_class = student.price_per_class
    
    await db.commit()
    await db.refresh(db_student)
    
    return db_student

@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a student."""
    result = await db.execute(
        Student.__table__.delete()
        .where(Student.id == student_id)
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    await db.commit()
    
    return {"message": "Student deleted successfully"}