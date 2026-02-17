from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates"))


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/loading")
def loading_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@router.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/upload")
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@router.get("/browse")
def browse_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/resource/{resource_id}")
def resource_detail_page(request: Request, resource_id: str):
    return templates.TemplateResponse("resource_detail.html", {"request": request, "resource_id": resource_id})
