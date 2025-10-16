from typing import Dict

from fastapi import Request, Depends, Response, status
from starlette.responses import RedirectResponse

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dependencies import CommonAuthRedirectRepository
from src.core.common.dto import GetMeResponse
from src.core.common.processors import RequestProcessor, ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.sso import SSO_TEMPLATES
from src.domains.sso.core.dto import VerifyEmailResponse, SendVerifyEmailMessageResponse
from src.domains.sso.dependencies.email import EmailDependenciesRepository


async def verify_email(
        result: VerifyEmailResponse = Depends(EmailDependenciesRepository.verify_email)
):
    """Роут подтверждения почты пользователя"""
    response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)
    else:
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2101", response=response)

    return response


async def verify_email_letter_page(
        request: Request,
        user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_user),  # noqa
):
    response: Response = SSO_TEMPLATES.TemplateResponse(
        request=request,
        name="verify-email-letter-form.html",
        context={
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
    )
    CookieProcessor.delete_temp_cookies(request=request, response=response)

    return response


async def process_verify_email_letter(
        result: SendVerifyEmailMessageResponse = Depends(EmailDependenciesRepository.send_verify_email_message)
):
    """Повторная отправка письма подтверждения почты"""
    if result.error is not None:
        response: Response = RedirectResponse(
            url="/sso/verify-email-letter-form", status_code=status.HTTP_303_SEE_OTHER
        )
        context: Dict[str, str] = {ERROR_OPERATION_KEY: result.error, "email": result.email}  # type: ignore
        ResponseProcessor.set_bulk_operation_response(response=response, context=context)

    else:
        response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)  # type: ignore
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2100", response=response)

    return response
