from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from src.core.common.cookies import set_cookie
from src.core.common.dto import GetMeResponse
from src.core.common.dependencies import get_me as get_me_dependency
from src.core.common.utils import Extract, Cryptography
from src.core.config import config

router = APIRouter(tags=["Main"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse, name="home_page")
async def home_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: Cryptography = Depends(config.get_encryptor),
):
    response: Response = templates.TemplateResponse(
        request=request,
        name="homepage.html",
        context={
            "user": current_user.user,
            "error_message": Extract.error_from_url(request=request, cryptography=encryptor),
        }
    )

    for cookie in current_user.cookies:
        set_cookie(response, cookie)

    return response
