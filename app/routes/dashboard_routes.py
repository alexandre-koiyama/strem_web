from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dashboard Page
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # In a real app, filter cameras by logged-in user
    cameras = db.query(models.Camera).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "cameras": cameras
    })


# Add new camera
@router.post("/add_camera")
async def add_camera(
    request: Request,
    name: str = Form(...),
    stream_url: str = Form(...),
    db: Session = Depends(get_db)
):
    # TODO: Replace with real user_id from session/token
    dummy_user_id = 1
    camera = models.Camera(name=name, stream_url=stream_url, user_id=dummy_user_id)
    db.add(camera)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=302)
