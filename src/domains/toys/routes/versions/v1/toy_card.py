from typing import Dict, Any

from fastapi import Request, Depends, status
from fastapi.responses import RedirectResponse, Response

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dependencies import CommonAuthBaseRepository
from src.core.common.dto import GetMeResponse
from src.core.common.processors import ResponseProcessor, RequestProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.toys import TOYS_TEMPLATES
from src.domains.toys.core.dto import ToyByIDResponse
from src.domains.toys.dependencies.toy_card import ToyInfoDependenciesRepository


async def toy_by_id(
        request: Request,
        current_user: GetMeResponse = Depends(CommonAuthBaseRepository.get_me),
        result: ToyByIDResponse = Depends(ToyInfoDependenciesRepository.toy_by_id)
):
    if result.error is not None:
        response: Response = RedirectResponse(url="/toys/catalog", status_code=status.HTTP_303_SEE_OTHER)
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)

    else:
        context: Dict[str, Any] = {
            "user": current_user.user or None,
            "toy": result.toy,
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
        response: Response = TOYS_TEMPLATES.TemplateResponse(  # type: ignore
            request=request, name="toy-page.html", context=context
        )
        CookieProcessor.delete_temp_cookies(request=request, response=response)

    for cookie in current_user.cookies:
        CookieProcessor.set_cookie(response, cookie)

    return response
