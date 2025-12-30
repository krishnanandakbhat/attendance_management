# Minimal main.py for initial testing
from fastapi import FastAPI, Depends, HTTPException, Request, Response, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import engine, Base, get_db
from app.api.dependencies import get_optional_current_user
from typing import Optional
from app.models.users import User
from sqlalchemy import select
from app.core.security import verify_password, create_access_token

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static"
)
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

@app.get("/")
async def root(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the homepage."""
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "title": settings.PROJECT_NAME, "user": user, "messages": []}
    )


@app.get("/students")
async def students_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the students list page (frontend)."""
    return templates.TemplateResponse(
        "students/list.html",
        {"request": request, "title": "Students", "user": user, "messages": []}
    )


@app.get("/students/create")
async def create_student_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the create student page."""
    return templates.TemplateResponse(
        "students/create.html",
        {"request": request, "title": "Add Student", "user": user, "messages": []}
    )


@app.get("/students/{student_id}")
async def view_student_page(student_id: int, request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the view student page."""
    return templates.TemplateResponse(
        "students/view.html",
        {"request": request, "title": "Student Details", "user": user, "messages": []}
    )



# GET: Render login page
@app.get("/auth/login")
async def login_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request, "title": "Login", "user": user, "messages": []}
    )

# POST: Handle login form, set cookie, redirect
@app.post("/auth/login")
async def login_form(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db)
):
    from app.models.sessions import Session
    
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        # Show error on login page
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "title": "Login", "user": None, "messages": [{"type": "danger", "text": "Invalid credentials"}]},
            status_code=401
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    # Create session record in database
    session = Session(
        user_id=user.id,
        device_name=request.headers.get("User-Agent", "Unknown Device"),
        session_token=access_token,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("User-Agent")
    )
    db.add(session)
    await db.commit()
    
    # Redirect and set cookie
    redirect = RedirectResponse(url="/students", status_code=303)
    redirect.set_cookie(
        key="session",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    return redirect


@app.post("/auth/logout")
async def logout_form(
    request: Request,
    response: Response,
    db=Depends(get_db)
):
    """Handle logout from browser form, delete session cookie and redirect."""
    from app.models.sessions import Session
    session_token = request.cookies.get("session")
    if session_token:
        await db.execute(
            Session.__table__.delete().where(Session.session_token == session_token)
        )
        await db.commit()
    
    redirect = RedirectResponse(url="/auth/login", status_code=303)
    redirect.delete_cookie(key="session")
    return redirect


@app.get("/attendance")
async def attendance_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the attendance list page."""
    return templates.TemplateResponse(
        "attendance/list.html",
        {"request": request, "title": "Attendance", "user": user, "messages": []}
    )


@app.get("/attendance/mark")
async def mark_attendance_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the mark attendance page."""
    return templates.TemplateResponse(
        "attendance/mark.html",
        {"request": request, "title": "Mark Attendance", "user": user, "messages": []}
    )


@app.get("/reports")
async def reports_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render the reports page."""
    return templates.TemplateResponse(
        "reports/index.html",
        {"request": request, "title": "Reports", "user": user, "messages": []}
    )


@app.get("/sessions")
async def sessions_page(request: Request, user: Optional[User] = Depends(get_optional_current_user)):
    """Render a simple sessions (devices) page placeholder."""
    return templates.TemplateResponse(
        "base.html",
        {"request": request, "title": "Devices", "user": user, "messages": []}
    )

# Import and include routers
from app.api.v1 import auth, students, attendance, sessions

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(students.router, prefix=settings.API_V1_STR)
app.include_router(attendance.router, prefix=settings.API_V1_STR)
app.include_router(sessions.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )