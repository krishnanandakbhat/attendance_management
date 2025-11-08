from sqlalchemy import Column, Integer, String, LargeBinary, Numeric, DateTime
from sqlalchemy.sql import func
from ..core.database import Base
from ..core.security import encrypt_age, decrypt_age

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age_ciphertext = Column(LargeBinary)
    level = Column(String)
    price_per_class = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def set_age(self, age: int):
        self.age_ciphertext = encrypt_age(age)

    def __init__(self, name: str, level: str, price_per_class, **kwargs):
        # Basic validation required by tests: non-empty name and positive price
        if not name or not str(name).strip():
            raise ValueError("Student name must not be empty")
        try:
            price_val = float(price_per_class)
        except Exception:
            raise ValueError("price_per_class must be a number")
        if price_val <= 0:
            raise ValueError("price_per_class must be positive")

        # Assign validated fields
        self.name = name
        self.level = level
        self.price_per_class = price_per_class
        # Allow SQLAlchemy to handle other kwargs like id/created_at
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_age(self) -> int:
        return decrypt_age(self.age_ciphertext)

    @property
    def age(self) -> int:
        """Expose decrypted age as a property for Pydantic serialization."""
        return self.get_age()