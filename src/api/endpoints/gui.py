from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

# Configuración de plantillas
TEMPLATES_DIR = Path(__file__).parent.parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["GUI"])

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Renders the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Renders the main dashboard.
    Note: Real implementation should verify JWT here or in the frontend.
    """
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/cfdis", response_class=HTMLResponse)
async def cfdis_page(request: Request):
    """
    Renders the CFDI listing with advanced filters.
    """
    return templates.TemplateResponse("cfdis.html", {"request": request})

@router.get("/configuracion")
async def config_view(request: Request):
    return templates.TemplateResponse("configuracion.html", {"request": request})
