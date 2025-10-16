from typing import Dict

from fastapi import Request, Depends, status
from fastapi.responses import Response, RedirectResponse

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.common.processors import RequestProcessor, ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.sso import SSO_TEMPLATES
from src.domains.sso.core.dto import RegisterResponse
from src.domains.sso.dependencies.auth import AuthDependenciesRepository


async def register_page(
        request: Request,
        user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_user)  # noqa
):
    response: Response = SSO_TEMPLATES.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "display_name": RequestProcessor.get_payload_info(key="display_name", request=request),
            "email": RequestProcessor.get_payload_info(key="email", request=request),
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
    )
    CookieProcessor.delete_temp_cookies(request=request, response=response)

    return response


async def process_register(
        result: RegisterResponse = Depends(AuthDependenciesRepository.process_register)
):
    if result.error is not None:
        response: Response = RedirectResponse(url="/sso/register", status_code=status.HTTP_303_SEE_OTHER)
        response_context: Dict[str, str] = {
            ERROR_OPERATION_KEY: result.error,
            "display_name": result.display_name,  # type: ignore
            "email": result.email  # type: ignore
        }
        ResponseProcessor.set_bulk_operation_response(response=response, context=response_context)

    else:
        response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)  # type: ignore
        ResponseProcessor.set_operation_response(response=response, key=SUCCESS_OPERATION_KEY, value="2100")

    return response
