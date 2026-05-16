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
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    Renders the main dashboard.
    Note: Real implementation should verify JWT here or in the frontend.
    """
    return templates.TemplateResponse(request=request, name="dashboard.html")

@router.get("/cfdis", response_class=HTMLResponse)
async def cfdis_page(request: Request):
    """
    Renders the CFDI listing with advanced filters.
    """
    return templates.TemplateResponse(request=request, name="cfdis.html")

@router.get("/configuracion")
async def config_view(request: Request):
    return templates.TemplateResponse(request=request, name="configuracion.html")

@router.get("/selector", response_class=HTMLResponse)
async def selector_page(request: Request):
    return templates.TemplateResponse(request=request, name="selector.html")

@router.get("/recovery", response_class=HTMLResponse)
async def recovery_page(request: Request):
    return templates.TemplateResponse(request=request, name="recovery.html")

@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_view(request: Request):
    return templates.TemplateResponse(request=request, name="reset_password.html")
