from typing import Dict

from fastapi import Request, Depends, status
from fastapi.responses import Response
from starlette.responses import RedirectResponse

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.common.processors import RequestProcessor, ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.sso import SSO_TEMPLATES
from src.domains.sso.core.dto import LoginResponse
from src.domains.sso.dependencies.auth import AuthDependenciesRepository


async def login_page(
        request: Request,
        user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_user)  # noqa
):
    response: Response = SSO_TEMPLATES.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "email": RequestProcessor.get_payload_info(key="email", request=request),
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
    )
    CookieProcessor.delete_temp_cookies(request=request, response=response)

    return response


async def process_login(
        result: LoginResponse = Depends(AuthDependenciesRepository.process_login)
):
    if result.error is not None:
        response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)
        context: Dict[str, str] = {
            ERROR_OPERATION_KEY: result.error,
            "email": result.email  # type: ignore
        }
        ResponseProcessor.set_bulk_operation_response(response=response, context=context)

    else:
        response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)  # type: ignore

    for cookie in result.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response
