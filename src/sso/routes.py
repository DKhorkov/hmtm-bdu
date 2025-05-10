from typing import Optional

from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from src.cookies import set_cookie
from src.sso.dependencies import (
    process_register as process_register_dependency,
    process_login as process_login_dependency,
    verify_email as verify_email_dependency,
    get_me as get_me_dependency,
    send_verify_email_message as send_verify_email_message_dependency,
    send_forget_password_message as send_forget_password_message_dependency,
    change_forget_password as change_forget_password_dependency,
    change_password as change_password_dependency,
    update_user_profile as update_user_profile_dependency,
    master_by_user as master_by_user_dependency,
    update_master as update_master_info_dependency,
    register_master as register_master_dependency,
    get_user_info as get_user_info_dependency,
)
from src.sso.dto import (
    LoginResponse,
    GetMeResponse,
    RegisterResponse,
    VerifyEmailResponse,
    SendVerifyEmailMessageResponse,
    SendForgetPasswordMessageResponse,
    ChangeForgetPasswordResponse,
    ChangePasswordResponse,
    UpdateUserProfileResponse,
    GetUserIsMasterResponse,
    UpdateMasterResponse,
    RegisterMasterResponse,
    GetFullUserInfoResponse,
)
from src.sso.constants import FORGET_PASSWORD_TOKEN_NAME
from src.request_utils import (
    FernetEnvironmentsKey,
    extract_url_error_message,
    extract_url_success_status_message
)

router = APIRouter(prefix="/sso", tags=["SSO"])
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
):
    """ Регистрация пользователя - Форма """
    if current_user.user is not None:
        encrypted_error = FernetEnvironmentsKey()
        encrypted_error_key = encrypted_error.encrypt("Вы уже зарегистрированы!")

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
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    """ Аутентификация пользователя - Форма """
    if current_user.user is not None:
        encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
        encrypted_error = encryptor.encrypt("У вас активная сессия!")

        return RedirectResponse(url=f"/?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "success_message": extract_url_success_status_message(request=request),
            "error_message": extract_url_error_message(request=request),
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
        response = set_cookie(response, cookie)

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


@router.get("/profile", response_class=HTMLResponse, name="profile")
async def profile_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    if current_user.user is not None:
        master: GetUserIsMasterResponse = await master_by_user_dependency(
            user_id=current_user.user.id,
            request=request,
            cookies=current_user.cookies,
        )

        response: Response = templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "tab": request.query_params.get("tab") if request.query_params.get("tab") else "main",
                "user": current_user.user,
                "master": master.master if master.master else None,
                "error_message": extract_url_error_message(request=request),
                "success_message": extract_url_success_status_message(request=request)
            }
        )

        for cookie in current_user.cookies:
            response = set_cookie(response, cookie)

        return response

    return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)


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
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    """ Повторная отправка письма подтверждения почты - Форма """
    if current_user.user is not None:
        encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
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
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    """ Восстановление пароля для не аутентифицированного пользователя - Форма """
    if current_user.user is not None:
        encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
        encrypted_error = encryptor.encrypt("Для смены забытого пароля вам необходима форма в профиле")

        return RedirectResponse(
            url=f"/sso/profile?error={encrypted_error}&tab=security",
            status_code=status.HTTP_303_SEE_OTHER
        )

    error_message_from_url: Optional[str] = extract_url_error_message(request=request)
    return templates.TemplateResponse(
        request=request,
        name="forget-password-form.html",
        context={
            "error_message": error_message_from_url
        }
    )


@router.post("/forget-password-form", response_class=HTMLResponse, name="forget-password-form")
async def process_send_forget_password_message(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: SendForgetPasswordMessageResponse = Depends(send_forget_password_message_dependency)
):
    """ Восстановление пароля в профиле через форму - Процесс"""
    encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
    encrypted_success_message = encryptor.encrypt(
        "Письмо о смене пароля отправлено на почту, указанную при регистрации!"
    )
    if current_user.user is not None:
        if result.error is not None:
            encrypted_error = encryptor.encrypt("Необходима почта, указанная при регистрации")
            return RedirectResponse(
                url=f"/sso/profile?error={encrypted_error}&tab=security",
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url=f"/sso/profile?message={encrypted_success_message}&tab=security",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if result.error is not None:
        encrypted_error = encryptor.encrypt(str(result.error))
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


@router.post("/change-password", response_class=HTMLResponse, name="change-password")
async def process_change_password(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: ChangePasswordResponse = Depends(change_password_dependency)
):
    """ Ручка авторизованного пользователя для смены пароля - Процесс """
    encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
    if current_user.user is None:
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error_key: str = encryptor.encrypt(str(result.error))

        return RedirectResponse(
            url=f"/sso/profile?error={encrypted_error_key}&tab=security",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: str = encryptor.encrypt("Вы успешно поменяли пароль!")
    response: Response = RedirectResponse(
        url=f"/sso/profile?message={encrypted_message}&tab=security",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.post("/update_user_profile", response_class=HTMLResponse, name="update_user_profile")
async def process_update_user_profile(
        request: Request,
        result: UpdateUserProfileResponse = Depends(update_user_profile_dependency),
):
    """ Ручка авторизованного пользователя для изменения данных о себе: никнейм, телеграм, телефон - Процесс """
    current_user: GetMeResponse = await get_me_dependency(request=request, cookies=result.cookies)

    encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
    if current_user.user is None:
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(str(result.error))  # type: ignore[no-redef]

        return RedirectResponse(
            url=f"/sso/profile?error={encrypted_error}&tab=main",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: str = encryptor.encrypt("Вы успешно поменяли данные о себе")
    response: Response = RedirectResponse(
        url=f"/sso/profile?message={encrypted_message}&tab=main",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.post("/update-master", response_class=HTMLResponse, name="update-master")
async def process_update_master(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: UpdateMasterResponse = Depends(update_master_info_dependency),
):
    encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
    if current_user.user is None:
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(str(result.error))

        return RedirectResponse(
            url=f"/sso/profile?error={encrypted_error}&tab=master",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: str = encryptor.encrypt("Вы успешно поменяли данные о мастере")
    response: Response = RedirectResponse(
        url=f"/sso/profile?message={encrypted_message}&tab=master",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.post("/register-master", response_class=HTMLResponse, name="register-master")
async def register_master(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: RegisterMasterResponse = Depends(register_master_dependency),
):
    encryptor: FernetEnvironmentsKey = FernetEnvironmentsKey()
    if current_user.user is None:
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(str(result.error))

        return RedirectResponse(
            url=f"/sso/profile?error={encrypted_error}&tab=master",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: FernetEnvironmentsKey = FernetEnvironmentsKey()
    encrypted_message_key: str = encrypted_message.encrypt("Вы успешно стали мастером!")

    response: Response = RedirectResponse(
        url=f"/sso/profile?message={encrypted_message_key}&tab=master",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.get("/find-users", response_class=HTMLResponse, name="find_users")
async def find_users_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
):
    error_message: Optional[str] = extract_url_error_message(request=request)
    return templates.TemplateResponse(
        request=request,
        name="find-users-form.html",
        context={
            "user": current_user.user if current_user.user else None,
            "error_message": error_message
        }
    )


@router.post("/users/{query_params}", response_class=HTMLResponse, name="get_user_info")
async def find_get_user_info(
        request: Request,
        result: GetFullUserInfoResponse = Depends(get_user_info_dependency)
):
    if result.user is None:
        encrypted_error = FernetEnvironmentsKey()
        encrypted_error_key = encrypted_error.encrypt("user_not_found")

        return RedirectResponse(
            url=f"/sso/find-users?error={encrypted_error_key}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    context = {
        "user": result.user if result.user else None,
        "master": result.master if result.master else None,
    }

    return templates.TemplateResponse(request=request, name="user-info.html", context=context)
