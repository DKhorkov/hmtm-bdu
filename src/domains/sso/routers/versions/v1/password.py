from fastapi import Request, Depends, status
from fastapi.responses import RedirectResponse, Response

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dependencies import CommonAuthRedirectRepository, CommonAuthBaseRepository
from src.core.common.dto import GetMeResponse
from src.core.common.processors import ResponseProcessor, RequestProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.sso import SSO_TEMPLATES
from src.domains.sso.dependencies.password import PasswordDependenciesRepository
from src.domains.sso.core.constants import FORGET_PASSWORD_TOKEN_NAME
from src.domains.sso.core.dto import SendForgetPasswordMessageResponse, ChangeForgetPasswordResponse


async def forget_password_form_page(
        request: Request,
        user: GetMeResponse = Depends(CommonAuthRedirectRepository.get_me_with_redirect_if_user)  # noqa
):
    """ Восстановление пароля для не аутентифицированного пользователя - Форма """
    response: Response = SSO_TEMPLATES.TemplateResponse(
        request=request,
        name="forget-password-form.html",
        context={
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
    )
    CookieProcessor.delete_temp_cookies(request=request, response=response)

    return response


async def process_send_forget_password_message(
        current_user: GetMeResponse = Depends(CommonAuthBaseRepository.get_me),
        result: SendForgetPasswordMessageResponse = Depends(PasswordDependenciesRepository.send_forget_password_message)
):
    """ Восстановление пароля в профиле через форму - Процесс"""
    # Обработка случая с авторизованным пользователем:
    if current_user.user is not None:
        response: Response = RedirectResponse(url="/profile/me", status_code=status.HTTP_303_SEE_OTHER)

        if result.error is not None:
            ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)
        else:
            ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2200", response=response)

        return response

    # Обработка случая с неавторизованным пользователем
    if result.error is not None:
        response: Response = RedirectResponse(  # type: ignore
            url="/sso/forget-password-form", status_code=status.HTTP_303_SEE_OTHER
        )
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)

    else:
        response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)  # type: ignore
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2200", response=response)

    return response


async def forget_password_page(
        request: Request,
        forget_password_token: str
):
    response: Response = SSO_TEMPLATES.TemplateResponse(
        request=request,
        name="change-forget-password.html",
        context={
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
    )
    CookieProcessor.delete_temp_cookies(request=request, response=response)

    if forget_password_token is not None:
        response.set_cookie(key=FORGET_PASSWORD_TOKEN_NAME, value=forget_password_token)

    return response


async def process_change_forget_password(
        result: ChangeForgetPasswordResponse = Depends(PasswordDependenciesRepository.change_forget_password)
):
    """Обработчик установки нового пароля после отправки письма восстановления"""
    if result.error is not None:
        response: Response = RedirectResponse(url="/sso/forget-password", status_code=status.HTTP_303_SEE_OTHER)
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)

    else:
        response: Response = RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)  # type: ignore
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2201", response=response)

        response.delete_cookie(key=FORGET_PASSWORD_TOKEN_NAME)
        response.delete_cookie(key="accessToken")
        response.delete_cookie(key="refreshToken")

    return response
