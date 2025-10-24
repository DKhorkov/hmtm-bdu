from fastapi import Request, status, Depends
from fastapi.responses import RedirectResponse, Response

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.processors import RequestProcessor, ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.profile import PROFILE_TEMPLATES
from src.domains.profile.core.schemas import GetUserWithMasterResponse
from src.domains.profile.dependencies.users import UserProfileDependenciesRepository


async def profile_page(
        request: Request,
        result: GetUserWithMasterResponse = Depends(UserProfileDependenciesRepository.user_with_master),
):
    if not result.user:
        response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value="4017", response=response)

    else:
        response: Response = PROFILE_TEMPLATES.TemplateResponse(  # type: ignore
            request=request,
            name="profile.html",
            context={
                "tab": request.query_params.get("tab", "main"),
                "user": result.user,
                "master": result.master or None,
                "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
                "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
            }
        )
        CookieProcessor.delete_temp_cookies(request=request, response=response)

        for cookie in result.cookies:
            CookieProcessor.set_cookie(response, cookie)

    return response
