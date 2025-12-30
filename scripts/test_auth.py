"""
Test authentication flow for FastAPI app.
Run with: python scripts/test_auth.py
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_auth_flow():
    login_data = {
        "username": "admin",  # replace with your username
        "password": "admin"  # replace with your password
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    print(f"Login Response Status: {response.status_code}")
    print(f"Login Response Body: {response.text}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        students_response = client.get("/api/v1/students/", headers=headers)
        print(f"\nStudents Response Status: {students_response.status_code}")
        print(f"Students Response Body: {students_response.text}")

if __name__ == "__main__":
    test_auth_flow()
