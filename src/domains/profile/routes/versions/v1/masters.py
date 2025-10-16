from fastapi.responses import Response, RedirectResponse
from fastapi import status, Depends

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.processors import ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.profile.core.dto import UpdateMasterResponse, RegisterMasterResponse
from src.domains.profile.dependencies.master_user import MasterUserDependenciesRepository


async def process_update_master(
        result: UpdateMasterResponse = Depends(MasterUserDependenciesRepository.update_master)
):
    response: Response = RedirectResponse(url="/profile/me?tab=master", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)
    else:
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2202", response=response)

    for cookie in result.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response


async def register_master(
        result: RegisterMasterResponse = Depends(MasterUserDependenciesRepository.register_master)
):
    response: Response = RedirectResponse(url="/profile/me?tab=master", status_code=status.HTTP_303_SEE_OTHER)

    if result.error is not None:
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)
    else:
        ResponseProcessor.set_operation_response(key=SUCCESS_OPERATION_KEY, value="2203", response=response)

    for cookie in result.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response
