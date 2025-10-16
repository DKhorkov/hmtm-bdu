from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from .register import register_page, process_register
from .login import login_page, process_login
from .logout import logout_process
from .email import verify_email, verify_email_letter_page, process_verify_email_letter
from .password import (
    forget_password_page,
    process_send_forget_password_message,
    forget_password_form_page,
    process_change_forget_password
)


class SsoV1Router:
    router = APIRouter(prefix="/sso", tags=["SSO"])

    router.get(path="/register", response_class=HTMLResponse, name="register")(register_page)
    router.post(path="/register", response_class=HTMLResponse, name="register")(process_register)

    router.get(path="/login", response_class=HTMLResponse, name="login")(login_page)
    router.post(path="/login", response_class=HTMLResponse, name="login")(process_login)

    router.post(path="/logout", response_class=RedirectResponse, name="logout")(logout_process)

    router.get(
        path="/verify-email/{verify_email_token}", response_class=HTMLResponse, name="verify-email"
    )(verify_email)

    router.get(
        path="/verify-email-letter-form", response_class=HTMLResponse, name="verify-email-letter"
    )(verify_email_letter_page)
    router.post(
        path="/verify-email-letter-form", response_class=HTMLResponse, name="verify-email-letter"
    )(process_verify_email_letter)

    router.get(
        path="/forget-password-form", response_class=HTMLResponse, name="forget-password-form"
    )(forget_password_form_page)
    router.post(
        path="/forget-password-form", response_class=HTMLResponse, name="forget-password-form"
    )(process_send_forget_password_message)

    router.get(
        path="/forget-password/{forget_password_token}", response_class=HTMLResponse, name="change-forget-password"
    )(forget_password_page)
    router.post(
        path="/forget-password", response_class=HTMLResponse, name="change-forget-password"
    )(process_change_forget_password)
