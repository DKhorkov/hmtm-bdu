from typing import Dict, Any

from fastapi import Depends, Request, status
from fastapi.responses import RedirectResponse, Response

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dto import GetMeResponse
from src.core.common.dependencies import CommonAuthBaseRepository
from src.core.common.processors import ResponseProcessor, RequestProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.masters import MASTERS_TEMPLATES
from src.domains.masters.dependencies.catalog import MastersCatalogDependenciesRepository
from src.domains.masters.core.dto import MastersCatalogResponse


async def masters_catalog(
        request: Request,
        current_user: GetMeResponse = Depends(CommonAuthBaseRepository.get_me),
        result: MastersCatalogResponse = Depends(MastersCatalogDependenciesRepository.masters_catalog),
):
    if result.error is not None:
        response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)

    else:
        context: Dict[str, Any] = {
            "user": current_user.user or None,
            "current_page": result.current_page,
            "total_pages": result.total_pages,
            "masters": result.masters,
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }

        response: Response = MASTERS_TEMPLATES.TemplateResponse(  # type: ignore
            request=request,
            name="masters-catalog.html",  # Реализовать Фронт
            context=context
        )

        for cookie in current_user.cookies:
            CookieProcessor.set_cookie(response, cookie)

    return response
