from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.sso.dependencies import (
    process_register as process_register_dependency,
    process_login as process_login_dependency,
    verify_email as verify_email_dependency
)

router = APIRouter(prefix="/sso", tags=["SSO"])
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register", response_class=HTMLResponse, name="register")
async def process_register(
        request: Request,
        error: Optional[str] = Depends(process_register_dependency)
):
    if error is None:
        return templates.TemplateResponse(request=request, name="login.html")

    return templates.TemplateResponse(request=request, name="register.html", context={"error": error})


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login", response_class=HTMLResponse, name="login")
async def process_login(
        request: Request,
        error: Optional[str] = Depends(process_login_dependency)
):
    if error is None:
        return templates.TemplateResponse(request=request, name="index.html")

    return templates.TemplateResponse(request=request, name="login.html", context={"error": error})


@router.get("/verify-email/{verify_email_token}", response_class=HTMLResponse, name="verify_email")
async def verify_email(
        request: Request,
        error: Optional[str] = Depends(verify_email_dependency)
):
    if error is None:
        return templates.TemplateResponse(request=request, name="login.html")

    return templates.TemplateResponse(request=request, name="login.html", context={"error": error})
