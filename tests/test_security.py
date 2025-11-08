import pytest
from datetime import datetime
from unittest.mock import patch

from app.core.security import encrypt_age, decrypt_age, get_password_hash, verify_password
from app.models.users import User
from app.models.students import Student
from app.core.config import Settings

def test_password_hashing():
    # Test password hashing and verification
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
    assert not verify_password(password + "extra", hashed)

def test_age_encryption():
    # Test age encryption/decryption
    test_age = 25
    encrypted = encrypt_age(test_age)
    decrypted = decrypt_age(encrypted)
    
    assert isinstance(encrypted, bytes)
    assert test_age == decrypted
    assert decrypt_age(encrypt_age(30)) == 30

def test_student_age_encryption():
    # Test student model age encryption
    student = Student(
        name="Test Student",
        level="Intermediate",
        price_per_class=50.0
    )
    test_age = 25
    student.set_age(test_age)
    
    # Test that age is encrypted in the database
    assert isinstance(student.age_ciphertext, bytes)
    assert student.get_age() == test_age
    
    # Test different age
    student.set_age(30)
    assert student.get_age() == 30

@pytest.mark.asyncio
async def test_user_password():
    # Test User model password methods
    user = User(
        username="testuser",
        email="test@example.com",
        is_active=True
    )
    
    password = "securepass123"
    user.set_password(password)
    
    assert user.password_hash is not None
    assert verify_password(password, user.password_hash)
    assert not verify_password("wrongpass", user.password_hash)

def test_student_validation():
    # Test student model validation
    with pytest.raises(ValueError):
        Student(
            name="",  # Empty name should raise error
            level="Beginner",
            price_per_class=50.0
        )
    
    with pytest.raises(ValueError):
        Student(
            name="Test Student",
            level="Beginner",
            price_per_class=-10  # Negative price should raise error
        )
    
    # Valid student should work
    student = Student(
        name="Test Student",
        level="Beginner",
        price_per_class=50.0
    )
    assert student.name == "Test Student"
    assert student.level == "Beginner"
    assert student.price_per_class == 50.0