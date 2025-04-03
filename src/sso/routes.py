from typing import Optional

from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from src.cookies import set_cookie
from src.sso.dependencies import (
    process_register as process_register_dependency,
    process_login as process_login_dependency,
    verify_email as verify_email_dependency,
    get_me as get_me_dependency,
)
from src.sso.dto import LoginResponse, GetMeResponse

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
        return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="register.html", context={"error": error})


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login", response_class=HTMLResponse, name="login")
async def process_login(
        request: Request,
        result: LoginResponse = Depends(process_login_dependency)
):
    if result.error is not None:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": result.error})

    response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.get("/verify-email/{verify_email_token}", response_class=HTMLResponse, name="verify_email")
async def verify_email(
        request: Request,
        error: Optional[str] = Depends(verify_email_dependency)
):
    if error is None:
        return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="login.html", context={"error": error})


@router.get("/profile", response_class=HTMLResponse, name="profile")
async def profile_page(request: Request, current_user: GetMeResponse = Depends(get_me_dependency)):
    if current_user.user is not None:
        response: Response = templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"user": current_user.user}
        )

        for cookie in current_user.cookies:
            response = set_cookie(response, cookie)

        return response

    return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout", response_class=RedirectResponse, name="logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in request.cookies:
        response.delete_cookie(key=cookie)

    return response
