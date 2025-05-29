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
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    cameras = (
        db.query(models.Camera)
        .filter(models.Camera.user_id == user_id)
        .order_by(models.Camera.group, models.Camera.name)
        .all()
    )
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "cameras": cameras
    })


# Add new camera
@router.post("/dashboard/add_camera")
async def add_camera(
    request: Request,
    name: str = Form(...),
    stream_url: str = Form(...),
    group: str = Form(...),
    db: Session = Depends(get_db)
):
    if not name or not stream_url or not group:
        return RedirectResponse(url="/dashboard", status_code=400)

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    camera = models.Camera(name=name, stream_url=stream_url, group=group, user_id=user_id)
    db.add(camera)
    db.commit()
    return RedirectResponse(url="/dashboard", status_code=302)


# Delete camera
@router.post("/dashboard/delete_camera/{camera_id}")
async def delete_camera(camera_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    camera = db.query(models.Camera).filter(models.Camera.id == camera_id, models.Camera.user_id == user_id).first()
    if camera:
        db.delete(camera)
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=302)


# Billing Page
@router.get("/billing", response_class=HTMLResponse)
async def billing(request: Request):
    username = "User"  # Replace with actual username if available
    return templates.TemplateResponse("billing.html", {"request": request, "username": username})


@router.post("/billing/upgrade")
async def billing_upgrade(request: Request):
    form = await request.form()
    plan = form.get("plan")
    # Here you would handle the plan upgrade logic (demo only)
    username = "User"
    msg = f"Plan upgrade to '{plan}' requested (demo only)."
    return templates.TemplateResponse("billing.html", {"request": request, "username": username, "msg": msg})
