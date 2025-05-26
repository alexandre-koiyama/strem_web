# app/routes/auth_routes.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app import auth, models, schemas
from ..database import SessionLocal, engine
from fastapi.templating import Jinja2Templates
from app.auth import authenticate_user


models.Base.metadata.create_all(bind=engine)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        # failed login
        return templates.TemplateResponse("login.html", {
            "request": request,
            "msg": "Invalid credentials"
        })
    # 🟢 Here is where we store the user ID in session
    request.session["user_id"] = user.id
   
    return RedirectResponse(url="/dashboard", status_code=302)



@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "User already exists"})
    user_create = schemas.UserCreate(email=email, password=password)
    auth.create_user(db, user_create)
    return RedirectResponse(url="/", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    cameras = db.query(models.Camera).filter(models.Camera.user_id == user_id).all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "cameras": cameras
    })


@router.post("/add_camera")
async def add_camera(
    request: Request,
    name: str = Form(...),
    stream_url: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    camera = models.Camera(name=name, stream_url=stream_url, user_id=user_id)
    db.add(camera)
    db.commit()
    return RedirectResponse("/dashboard", status_code=302)