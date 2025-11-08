from datetime import date, datetime
from pydantic import BaseModel

class AttendanceBase(BaseModel):
    student_id: int
    date: date

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    marked_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True