from fastapi import APIRouter, Request, Depends, status
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
)
from src.sso.constants import FORGET_PASSWORD_TOKEN_NAME
from src.sso.datetime_parser import DatetimeParser

router = APIRouter(prefix="/sso", tags=["SSO"])
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
):
    if current_user.user is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register", response_class=HTMLResponse, name="register")
async def process_register(
        request: Request,
        result: RegisterResponse = Depends(process_register_dependency)
):
    if result.error is not None:
        return templates.TemplateResponse(request=request, name="register.html", context={"error": result.error})

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": "На ваш email отправлено письмо для подтверждения регистрации, пожалуйста проверьте"}
    )


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    if current_user.user is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login", response_class=HTMLResponse, name="login")
async def process_login(
        request: Request,
        result: LoginResponse = Depends(process_login_dependency)
):
    if result.error is not None:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": result.error})

    response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.get("/verify-email/{verify_email_token}", response_class=HTMLResponse, name="verify_email")
async def verify_email(
        request: Request,
        result: VerifyEmailResponse = Depends(verify_email_dependency)
):
    if result.error is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"message": "Ваша почта успешно подтверждена"}
        )

    return templates.TemplateResponse(request=request, name="login.html", context={"error": result.error})


@router.get("/profile", response_class=HTMLResponse, name="profile")
async def profile_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    if current_user.user is not None:
        response: Response = templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "tab": "main",  # Вкладка
                "user": current_user.user,  # Авторизация
                "is_editing": False,
                # Основные параметры:
                "username": current_user.user.display_name,
                "email": current_user.user.email,
                "phone": current_user.user.phone if current_user.user.phone is not None else "Отсутствует",
                "telegram": current_user.user.telegram if current_user.user.telegram is not None else "Отсутствует",
                "created_at": DatetimeParser.parse(current_user.user.created_at),
                "avatar": current_user.user.avatar,
                # Дополнительные параметры:
                "email_verified": current_user.user.email_confirmed,
                "phone_verified": current_user.user.phone_confirmed,
                "telegram_verified": current_user.user.telegram_confirmed
            }
        )

        for cookie in current_user.cookies:
            response = set_cookie(response, cookie)

        return response

    return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/logout", response_class=RedirectResponse, name="logout")
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in request.cookies:
        response.delete_cookie(key=cookie)

    return response


@router.get("/verify-email-letter-form", response_class=RedirectResponse, name="verify-email-letter")
async def verify_email_letter_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    if current_user.user is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="verify-email-letter-form.html")


@router.post("/verify-email-letter-form", response_class=HTMLResponse, name="verify-email-letter")
async def process_verify_email_letter(
        request: Request,
        result: SendVerifyEmailMessageResponse = Depends(send_verify_email_message_dependency)
):
    if result.error is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"message": "Повторное письмо для подтверждения почты было отправлено"}
        )

    return templates.TemplateResponse(
        request=request,
        name="verify-email-letter-form.html",
        context={"error": result.error}
    )


@router.get("/forget-password-form", response_class=RedirectResponse, name="forget-password-form")
async def forget_pass_form_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency)
):
    if current_user.user is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="forget-password-form.html")


@router.post("/forget-password-form", response_class=HTMLResponse, name="forget-password-form")
async def process_forget_pass(
        request: Request,
        result: SendForgetPasswordMessageResponse = Depends(send_forget_password_message_dependency)
):
    if result.error is None:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"message": "Письмо для смены пароля отправлено на электронную почту"}
        )

    return templates.TemplateResponse(
        request=request,
        name="forget-password-form.html",
        context={"error": result.error}
    )


@router.get("/forget-password/{forget_password_token}", response_class=HTMLResponse, name="change-forget-password")
async def forget_password_page(
        request: Request,
        forget_password_token: str
):
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
async def process_forget_password(
        request: Request,
        result: ChangeForgetPasswordResponse = Depends(change_forget_password_dependency)
):
    if result.error is None:
        response: Response = templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"message": "Пароль успешно обновлен"}
        )
        response.delete_cookie(key=FORGET_PASSWORD_TOKEN_NAME)

        return response

    return templates.TemplateResponse(
        request=request,
        name="change-forget-password.html",
        context={"error": result.error}
    )


@router.post("/change-password", response_class=HTMLResponse, name="change-password")
async def process_change_password(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: ChangePasswordResponse = Depends(change_password_dependency)
):
    if result.error is None:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "user": current_user.user,
                "security_message": "Ваш пароль успешно обновлен",
                # Активная вкладка:
                "tab": "security",
                # Основные параметры:
                "username": current_user.user.display_name,
                "email": current_user.user.email,
                "phone": current_user.user.phone if current_user.user.phone is not None else "Отсутствует",
                "telegram": current_user.user.telegram if current_user.user.telegram is not None else "Отсутствует",
                "created_at": DatetimeParser.parse(current_user.user.created_at),
                "avatar": current_user.user.avatar,
                # Дополнительные параметры:
                "email_verified": current_user.user.email_confirmed,
                "phone_verified": current_user.user.phone_confirmed,
                "telegram_verified": current_user.user.telegram_confirmed
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": current_user.user,
            "security_error": result.error,
            # Активная вкладка:
            "tab": "security",
            # Основные параметры:
            "username": current_user.user.display_name,
            "email": current_user.user.email,
            "phone": current_user.user.phone if current_user.user.phone is not None else "Отсутствует",
            "telegram": current_user.user.telegram if current_user.user.telegram is not None else "Отсутствует",
            "created_at": DatetimeParser.parse(current_user.user.created_at),
            "avatar": current_user.user.avatar,
            # Дополнительные параметры:
            "email_verified": current_user.user.email_confirmed,
            "phone_verified": current_user.user.phone_confirmed,
            "telegram_verified": current_user.user.telegram_confirmed
        }
    )


@router.post("/confirm-edit-profile", response_class=HTMLResponse, name="confirm-edit-profile")
async def confirm_edit_profile(
        request: Request,
        result: UpdateUserProfileResponse = Depends(update_user_profile_dependency),
        current_user: GetMeResponse = Depends(get_me_dependency),
):
    if result.error is None:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "user": current_user.user,
                "tab": "main",
                "main_message": "Вы успешно поменяли данные о профиле",
                # Основные параметры:
                "username": current_user.user.display_name,
                "email": current_user.user.email,
                "phone": current_user.user.phone if current_user.user.phone is not None else "Отсутствует",
                "telegram": current_user.user.telegram if current_user.user.telegram is not None else "Отсутствует",
                "created_at": DatetimeParser.parse(current_user.user.created_at),
                "avatar": current_user.user.avatar,
                # Дополнительные параметры:
                "email_verified": current_user.user.email_confirmed,
                "phone_verified": current_user.user.phone_confirmed,
                "telegram_verified": current_user.user.telegram_confirmed
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user": current_user.user,
            "tab": "main",
            "main_error": result.error,
            # Основные параметры:
            "username": current_user.user.display_name,
            "email": current_user.user.email,
            "phone": current_user.user.phone if current_user.user.phone is not None else "Отсутствует",
            "telegram": current_user.user.telegram if current_user.user.telegram is not None else "Отсутствует",
            "created_at": DatetimeParser.parse(current_user.user.created_at),
            "avatar": current_user.user.avatar,
            # Дополнительные параметры:
            "email_verified": current_user.user.email_confirmed,
            "phone_verified": current_user.user.phone_confirmed,
            "telegram_verified": current_user.user.telegram_confirmed
        }
    )
