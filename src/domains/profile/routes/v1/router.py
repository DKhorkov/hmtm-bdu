from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from .profile import profile_page
from .masters import process_update_master, register_master
from .users import process_change_password, process_update_user_profile


class ProfileV1Router:
    router = APIRouter(
        prefix="/profile",
        tags=["PROFILE"]
    )

    router.get(
        path="/me",
        response_class=HTMLResponse,
        name="profile"
    )(profile_page)

    router.post(
        path="/update-master",
        response_class=RedirectResponse,
        name="update-master"
    )(process_update_master)
    router.post(
        path="/register-master",
        response_class=RedirectResponse,
        name="register-master"
    )(register_master)

    router.post(
        path="/change-password",
        response_class=RedirectResponse,
        name="change-password"
    )(process_change_password)
    router.post(
        path="/update_user_profile",
        response_class=RedirectResponse,
        name="update_user_profile"
    )(process_update_user_profile)
