from fastapi import Depends, status
from fastapi.responses import RedirectResponse, Response

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.processors import ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.profile.core.dto import ChangePasswordResponse, UpdateUserProfileResponse
from src.domains.profile.dependencies.password import PasswordDependenciesRepository
from src.domains.profile.dependencies.users import UserProfileDependenciesRepository


async def process_change_password(
        result: ChangePasswordResponse = Depends(PasswordDependenciesRepository.change_password)
):
    response: Response = RedirectResponse(url="/profile/me?tab=security", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)
    else:
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2201", response=response)

    for cookie in result.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response


async def process_update_user_profile(
        result: UpdateUserProfileResponse = Depends(UserProfileDependenciesRepository.update_user_profile),
):
    response: Response = RedirectResponse(url="/profile/me?tab=main", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)
    else:
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2204", response=response)

    for cookie in result.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response
