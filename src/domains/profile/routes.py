from fastapi import Depends, APIRouter, status
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from src.core.common.cookies import set_cookie
from src.core.common.dependencies import get_me as get_me_dependency
from src.core.state import GlobalAppState
from src.domains.profile.dependencies import (
    change_password as change_password_dependency,
    update_user_profile as update_user_profile_dependency,
    user_with_master as user_with_master_dependency,
    update_master as update_master_info_dependency,
    register_master as register_master_dependency
)
from src.core.common.dto import GetMeResponse
from src.domains.profile.dto import (
    UpdateUserProfileResponse,
    ChangePasswordResponse,
    UpdateMasterResponse,
    RegisterMasterResponse
)
from src.core.common.extractors import UrlExtractors
from src.core.common.encryptor import Cryptography
from src.domains.profile.schemas import GetUserWithMasterResponse

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/me", response_class=HTMLResponse, name="profile")
async def profile_page(
        request: Request,
        result: GetUserWithMasterResponse = Depends(user_with_master_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    if not result.user:
        return RedirectResponse(url="/sso/login", status_code=status.HTTP_303_SEE_OTHER)

    response: Response = templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "tab": request.query_params.get("tab") if request.query_params.get("tab") else "main",
            "user": result.user,
            "master": result.master if result.master else None,
            "error_message": UrlExtractors.error_from_url(request=request, cryptography=encryptor),
            "success_message": UrlExtractors.success_message_from_url(request=request, cryptography=encryptor)
        }
    )

    for cookie in result.cookies:
        set_cookie(response, cookie)

    return response


@router.post("/change-password", response_class=HTMLResponse, name="change-password")
async def process_change_password(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: ChangePasswordResponse = Depends(change_password_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Ручка авторизованного пользователя для смены пароля - Процесс """
    if current_user.user is None:  # Нужен для Redirect на login-page, т.к ошибка из result - ошибка конкретной логики
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error_key: str = encryptor.encrypt(str(result.error))

        return RedirectResponse(
            url=f"/profile/me?error={encrypted_error_key}&tab=security",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: str = encryptor.encrypt("Вы успешно поменяли пароль!")
    response: Response = RedirectResponse(
        url=f"/profile/me?message={encrypted_message}&tab=security",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        set_cookie(response, cookie)

    return response


@router.post("/update_user_profile", response_class=HTMLResponse, name="update_user_profile")
async def process_update_user_profile(
        request: Request,
        result: UpdateUserProfileResponse = Depends(update_user_profile_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    """ Ручка авторизованного пользователя для изменения данных о себе: никнейм, телеграм, телефон - Процесс """
    current_user: GetMeResponse = await get_me_dependency(request=request, cookies=result.cookies)

    if current_user.user is None:  # Нужен для Redirect на login-page, т.к ошибка из result - ошибка конкретной логики
        return RedirectResponse(
            url=f"/sso/login?error={encryptor.encrypt(str(current_user.error))}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if result.error is not None:
        return RedirectResponse(
            url=f"/profile/me?error={encryptor.encrypt(str(result.error))}&tab=main",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: str = encryptor.encrypt("Вы успешно поменяли данные о себе")
    response: Response = RedirectResponse(
        url=f"/profile/me?message={encrypted_message}&tab=main",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        set_cookie(response, cookie)

    return response


@router.post("/update-master", response_class=HTMLResponse, name="update-master")
async def process_update_master(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: UpdateMasterResponse = Depends(update_master_info_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    if current_user.user is None:  # Нужен для Redirect на login-page, т.к ошибка из result - ошибка конкретной логики
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(str(result.error))  # type: ignore[no-redef]

        return RedirectResponse(
            url=f"/profile/me?error={encrypted_error}&tab=master",
            status_code=status.HTTP_303_SEE_OTHER
        )

    encrypted_message: str = encryptor.encrypt("Вы успешно поменяли данные о мастере")
    response: Response = RedirectResponse(
        url=f"/profile/me?message={encrypted_message}&tab=master",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        set_cookie(response, cookie)

    return response


@router.post("/register-master", response_class=HTMLResponse, name="register-master")
async def register_master(
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: RegisterMasterResponse = Depends(register_master_dependency),
        encryptor: Cryptography = Depends(GlobalAppState.cryptography)
):
    if current_user.user is None:  # Нужен для Redirect на login-page, т.к ошибка из result - ошибка конкретной логики
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(str(result.error))  # type: ignore[no-redef]

        return RedirectResponse(
            url=f"/profile/me?error={encrypted_error}&tab=master",
            status_code=status.HTTP_303_SEE_OTHER
        )

    response: Response = RedirectResponse(
        url=f"/profile/me?message={encryptor.encrypt("Вы успешно стали мастером!")}&tab=master",
        status_code=status.HTTP_303_SEE_OTHER
    )

    for cookie in result.cookies:
        set_cookie(response, cookie)

    return response
