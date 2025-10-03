from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from src.core.common.cookies import set_cookie
from src.domains.sso.dependencies import (
    process_register as process_register_dependency,
    process_login as process_login_dependency,
    verify_email as verify_email_dependency,
    send_verify_email_message as send_verify_email_message_dependency,
    send_forget_password_message as send_forget_password_message_dependency,
    change_forget_password as change_forget_password_dependency,
    get_user_info as get_user_info_dependency,
)
from src.core.common.dependencies import get_me as get_me_dependency
from src.domains.sso.dto import (
    LoginResponse,
    RegisterResponse,
    VerifyEmailResponse,
    SendVerifyEmailMessageResponse,
    SendForgetPasswordMessageResponse,
    GetFullUserInfoResponse, ChangeForgetPasswordResponse,
)
from src.core.common.dto import GetMeResponse
from src.domains.sso.constants import FORGET_PASSWORD_TOKEN_NAME
from src.core.common.extractors import UrlExtractors
from src.core.common.encryptor import Cryptography
from src.core.state import GlobalAppState

router = APIRouter(prefix="/sso", tags=["SSO"])
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Регистрация пользователя - Форма """
    if current_user.user is not None:
        encrypted_error_key = encryptor.encrypt("Вы уже зарегистрированы!")

        return RedirectResponse(url=f"/?error={encrypted_error_key}", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register", response_class=HTMLResponse, name="register")
async def process_register(
        request: Request,
        display_name: str = Form(...),
        email: str = Form(...),
        result: RegisterResponse = Depends(process_register_dependency)
):
    """ Регистрация пользователя - Процесс """
    if result.error is not None:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": result.error,
                "display_name": display_name,
                "email": email,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "message": "На ваш email отправлено письмо для подтверждения регистрации, пожалуйста проверьте"
        }
    )


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Аутентификация пользователя - Форма """
    if current_user.user is not None:
        encrypted_error = encryptor.encrypt("У вас активная сессия!")

        return RedirectResponse(url=f"/?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "success_message": UrlExtractors.success_message_from_url(request=request, cryptography=encryptor),
            "error_message": UrlExtractors.error_from_url(request=request, cryptography=encryptor),
        }
    )


@router.post("/login", response_class=HTMLResponse, name="login")
async def process_login(
        request: Request,
        email: str = Form(...),
        result: LoginResponse = Depends(process_login_dependency)
):
    """ Аутентификация пользователя - Процесс """
    if result.error is not None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": result.error,
                "email": email,
            }
        )

    response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in result.cookies:
        set_cookie(response, cookie)

    return response


@router.get("/verify-email/{verify_email_token}", response_class=HTMLResponse, name="verify_email")
async def verify_email(
        request: Request,
        result: VerifyEmailResponse = Depends(verify_email_dependency)
):
    """ Обработчик подтверждения почты пользователя """
    if result.error is not None:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": result.error})

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": "Ваша почта успешно подтверждена"}
    )


@router.get("/logout", response_class=RedirectResponse, name="logout")
async def logout(request: Request):
    """ Завершение сессии """
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in request.cookies:
        response.delete_cookie(key=cookie)

    return response


@router.get("/verify-email-letter-form", response_class=RedirectResponse, name="verify-email-letter")
async def verify_email_letter_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Повторная отправка письма подтверждения почты - Форма """
    if current_user.user is not None:
        encrypted_error = encryptor.encrypt("Ваша почта уже подтверждена!")

        return RedirectResponse(url=f"/?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="verify-email-letter-form.html")


@router.post("/verify-email-letter-form", response_class=HTMLResponse, name="verify-email-letter")
async def process_verify_email_letter(
        request: Request,
        email: str = Form(...),
        result: SendVerifyEmailMessageResponse = Depends(send_verify_email_message_dependency)
):
    """ Повторная отправка письма подтверждения почты - Процесс """
    if result.error is not None:
        return templates.TemplateResponse(
            request=request,
            name="verify-email-letter-form.html",
            context={
                "error": result.error,
                "email": email,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": "Повторное письмо для подтверждения почты было отправлено"}
    )


@router.get("/forget-password-form", response_class=RedirectResponse, name="forget-password-form")
async def forget_password_form_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Восстановление пароля для не аутентифицированного пользователя - Форма """
    if current_user.user is not None:
        encrypted_error = encryptor.encrypt("Для смены забытого пароля вам необходима форма в профиле")

        return RedirectResponse(
            url=f"/sso/profile?error={encrypted_error}&tab=security",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        request=request,
        name="forget-password-form.html",
        context={
            "error_message": UrlExtractors.error_from_url(request=request, cryptography=encryptor)
        }
    )


@router.post("/forget-password-form", response_class=HTMLResponse, name="forget-password-form")
async def process_send_forget_password_message(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: SendForgetPasswordMessageResponse = Depends(send_forget_password_message_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Восстановление пароля в профиле через форму - Процесс"""
    encrypted_success_message = encryptor.encrypt(
        "Письмо о смене пароля отправлено на почту, указанную при регистрации!"
    )
    if current_user.user is not None:
        if result.error is not None:
            encrypted_error = encryptor.encrypt("Необходима почта, указанная при регистрации")
            return RedirectResponse(
                url=f"/profile/me?error={encrypted_error}&tab=security",
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url=f"/profile/me?message={encrypted_success_message}&tab=security",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if result.error is not None:
        encrypted_error = encryptor.encrypt(result.error)
        return RedirectResponse(
            url=f"/sso/forget-password-form?error={encrypted_error}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=f"/sso/login?message={encrypted_success_message}",
        status_code=status.HTTP_303_SEE_OTHER
    )


@router.get("/forget-password/{forget_password_token}", response_class=HTMLResponse, name="change-forget-password")
async def forget_password_page(
        request: Request,
        forget_password_token: str
):
    """ Обработчик установки нового пароля после отправки письма восстановления - Форма """
    if forget_password_token is not None:
        response: Response = templates.TemplateResponse(request=request, name="change-forget-password.html")
        response.set_cookie(key=FORGET_PASSWORD_TOKEN_NAME, value=forget_password_token)

        return response

    return templates.TemplateResponse(
        request=request,
        name="change-forget-password.html",
        context={"error": "Ошибка обработки токена"}
    )


@router.post("/forget-password", response_class=HTMLResponse, name="change-forget-password")
async def process_change_forget_password(
        request: Request,
        result: ChangeForgetPasswordResponse = Depends(change_forget_password_dependency),
):
    """ Обработчик установки нового пароля после отправки письма восстановления - Процесс """
    if result.error is not None:
        return templates.TemplateResponse(
            request=request,
            name="change-forget-password.html",
            context={"error": result.error}
        )

    response: Response = templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": "Пароль успешно обновлен"}
    )
    response.delete_cookie(key=FORGET_PASSWORD_TOKEN_NAME)
    response.delete_cookie(key="accessToken")
    response.delete_cookie(key="refreshToken")

    return response


@router.get("/find-users", response_class=HTMLResponse, name="find_users")
async def find_users_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    return templates.TemplateResponse(
        request=request,
        name="find-users-form.html",
        context={
            "user": current_user.user if current_user.user else None,
            "error_message": UrlExtractors.error_from_url(request=request, cryptography=encryptor),
        }
    )


@router.post("/users/{query_params}", response_class=HTMLResponse, name="get_user_info")
async def get_user_info(
        request: Request,
        result: GetFullUserInfoResponse = Depends(get_user_info_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    if result.user is None:
        encrypted_error: str = encryptor.encrypt("user_not_found")

        return RedirectResponse(
            url=f"/sso/find-users?error={encrypted_error}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    context = {
        "user": result.user if result.user else None,
        "master": result.master if result.master else None,
    }

    return templates.TemplateResponse(request=request, name="user-info.html", context=context)
