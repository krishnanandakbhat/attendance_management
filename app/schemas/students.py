from pydantic import BaseModel, condecimal
from datetime import datetime
from typing import Optional
from decimal import Decimal

class StudentBase(BaseModel):
    name: str
    age: int
    level: str
    price_per_class: condecimal(max_digits=10, decimal_places=2)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    name: Optional[str] = None
    age: Optional[int] = None
    level: Optional[str] = None
    price_per_class: Optional[Decimal] = None

class Student(StudentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True