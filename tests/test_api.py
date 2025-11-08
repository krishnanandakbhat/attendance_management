import pytest
from datetime import date
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.users import User
from app.models.students import Student

@pytest.mark.asyncio
async def test_auth_flow(client: AsyncClient, db: AsyncSession):
    """Test the authentication flow."""
    # Create test user
    test_user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
        is_active=True
    )
    db.add(test_user)
    await db.commit()
    
    # Test login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpass123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Test login with wrong password
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "wrongpass"}
    )
    assert response.status_code == 401
    
    # Test logout
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_student_crud(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """Test student CRUD operations."""
    # Create student
    response = await client.post(
        "/api/v1/students/",
        json={
            "name": "Test Student",
            "age": 25,
            "level": "Intermediate",
            "price_per_class": 50.00
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    student_id = response.json()["id"]
    
    # Get student
    response = await client.get(
        f"/api/v1/students/{student_id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Student"
    assert response.json()["level"] == "Intermediate"
    
    # Update student
    response = await client.put(
        f"/api/v1/students/{student_id}",
        json={"name": "Updated Name", "level": "Advanced"},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    assert response.json()["level"] == "Advanced"
    
    # Delete student
    response = await client.delete(
        f"/api/v1/students/{student_id}",
        headers=auth_headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_attendance(client: AsyncClient, db: AsyncSession, auth_headers: dict):
    """Test attendance marking and retrieval."""
    # Create a test student
    student = Student(
        name="Test Student",
        level="Beginner",
        price_per_class=50.0
    )
    student.set_age(25)
    db.add(student)
    await db.commit()
    
    # Mark attendance
    response = await client.post(
        "/api/v1/attendance/",
        json={
            "student_id": student.id,
            "date": str(date.today())
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    
    # Try to mark duplicate attendance
    response = await client.post(
        "/api/v1/attendance/",
        json={
            "student_id": student.id,
            "date": str(date.today())
        },
        headers=auth_headers
    )
    assert response.status_code == 400  # Should fail with duplicate error
    
    # Get attendance records
    response = await client.get(
        "/api/v1/attendance/",
        params={"student_id": student.id},
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1