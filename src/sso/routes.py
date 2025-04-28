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
)
from src.sso.constants import FORGET_PASSWORD_TOKEN_NAME

router = APIRouter(prefix="/sso", tags=["SSO"])
templates = Jinja2Templates(directory="templates")


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
):
    """ Регистрация пользователя - Форма """
    if current_user.user is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

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
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="login.html")


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
        current_user: GetMeResponse = Depends(get_me_dependency),
        master: GetUserIsMasterResponse = Depends(master_by_user_dependency),
):
    if current_user.user is not None:
        response: Response = templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "tab": "main",
                "user": current_user.user,
                "master": master.master if master.master else None,
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
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

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
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(request=request, name="forget-password-form.html")


@router.post("/forget-password-form", response_class=HTMLResponse, name="forget-password-form")
async def process_send_forget_password_message(
        request: Request,
        email: str = Form(...),
        result: SendForgetPasswordMessageResponse = Depends(send_forget_password_message_dependency)
):
    """ Восстановление пароля для не аутентифицированного пользователя - Процесс """
    if result.error is not None:
        return templates.TemplateResponse(
            request=request,
            name="forget-password-form.html",
            context={
                "error": result.error,
                "email": email,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"message": "Письмо для смены пароля отправлено на электронную почту"}
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
    return response


@router.post("/change-password", response_class=HTMLResponse, name="change-password")
async def process_change_password(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: ChangePasswordResponse = Depends(change_password_dependency)
):
    """ Ручка авторизованного пользователя для смены пароля - Процесс """
    if current_user.user is None:
        return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    master: GetUserIsMasterResponse = await master_by_user_dependency(cookies=result.cookies, request=request)
    context = {
        "user": current_user.user,
        "master": master.master if master.master else None,
        "tab": "security",
    }

    if result.error is None:
        context["security_message"] = "Вы успешно поменяли пароль"
    else:
        context["security_error"] = result.error

    response: Response = templates.TemplateResponse(
        request=request,
        name="profile.html",
        context=context
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

    if current_user.user is None:
        return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    master: GetUserIsMasterResponse = await master_by_user_dependency(cookies=result.cookies, request=request)
    context = {
        "user": current_user.user,
        "master": master.master if master.master else None,
        "tab": "main",
    }

    if result.error is None:
        context["main_message"] = "Вы успешно поменяли данные о профиле"
    else:
        context["main_error"] = result.error

    response: Response = templates.TemplateResponse(
        request=request,
        name="profile.html",
        context=context
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.post("/update-master", response_class=HTMLResponse, name="update-master")
async def process_update_master(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: UpdateMasterResponse = Depends(update_master_info_dependency),
):
    if current_user.user is None:
        return RedirectResponse("/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    master: GetUserIsMasterResponse = await master_by_user_dependency(cookies=result.cookies, request=request)
    context = {
        "user": current_user.user,
        "master": master.master if master.master else None,
        "tab": "master"
    }

    if result.error is None:
        context["master_message"] = "Вы успешно поменяли данные о мастере"
    else:
        context["master_error"] = result.error

    response: Response = templates.TemplateResponse(
        request=request,
        name="profile.html",
        context=context
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response


@router.post("/register-master", response_class=HTMLResponse, name="register-master")
async def register_master(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: RegisterMasterResponse = Depends(register_master_dependency),
):
    if current_user.user is None:
        return RedirectResponse("/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    master: GetUserIsMasterResponse = await master_by_user_dependency(cookies=result.cookies, request=request)
    context = {
        "user": current_user.user,
        "master": master.master if master.master is not None else None,
        "tab": "master"
    }

    if result.error is None:
        context["master_message"] = "Вы успешно отправили заявку на Мастера"
    else:
        context["master_error"] = result.error

    response: Response = templates.TemplateResponse(
        request=request,
        name="profile.html",
        context=context
    )

    for cookie in result.cookies:
        response = set_cookie(response, cookie)

    return response
