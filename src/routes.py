from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from src.cookies import set_cookie
from src.sso.dto import GetMeResponse
from src.sso import get_me as get_me_dependency
from src.request_utils import extract_url_error_message

main_router = APIRouter(tags=["Main"])
templates = Jinja2Templates(directory="templates")


@main_router.get("/", response_class=HTMLResponse, name="home_page")
async def home_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    error_message: Optional[str] = extract_url_error_message(request=request)

    response: Response = templates.TemplateResponse(
        request=request,
        name="homepage.html",
        context={
            "user": current_user.user,
            "error_message": error_message,
        }
    )

    for cookie in current_user.cookies:
        response = set_cookie(response, cookie)

    return response
