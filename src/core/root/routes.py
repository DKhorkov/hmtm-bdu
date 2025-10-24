from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

from src.core.common.constants import SUCCESS_OPERATION_KEY, ERROR_OPERATION_KEY
from src.core.cookies.processors import CookieProcessor
from src.core.common.dto import GetMeResponse
from src.core.common.dependencies import CommonAuthBaseRepository
from src.core.common.processors import RequestProcessor

router = APIRouter(tags=["Main"])
templates = Jinja2Templates(directory="templates")


@router.get(path="/", response_class=HTMLResponse, name="home_page")
async def home(
        request: Request,
        current_user: GetMeResponse = Depends(CommonAuthBaseRepository.get_me)
):
    response: Response = templates.TemplateResponse(
        request=request,
        name="homepage.html",
        context={
            "user": current_user.user,
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
    )
    CookieProcessor.delete_temp_cookies(request=request, response=response)

    for cookie in current_user.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response
