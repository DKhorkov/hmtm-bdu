from typing import Dict, Any

from fastapi import Request, Depends, status
from fastapi.responses import RedirectResponse, Response

from src.core.common.constants import ERROR_OPERATION_KEY, SUCCESS_OPERATION_KEY
from src.core.common.dependencies import CommonAuthBaseRepository
from src.core.common.dto import GetMeResponse
from src.core.common.processors import ResponseProcessor, RequestProcessor
from src.core.cookies.processors import CookieProcessor
from src.domains.toys import TOYS_TEMPLATES
from src.domains.toys.core.dto import ToysCatalogResponse
from src.domains.toys.dependencies.catalog import ToysCatalogDependenciesRepository


async def toys_catalog(
        request: Request,
        current_user: GetMeResponse = Depends(CommonAuthBaseRepository.get_me),
        result: ToysCatalogResponse = Depends(ToysCatalogDependenciesRepository.toys_catalog),
):
    if result.error is not None:
        response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, value=result.error, response=response)

    else:
        context: Dict[str, Any] = {
            "user": current_user.user or None,
            "current_page": result.current_page,
            "total_pages": result.total_pages,
            "toys": result.toys,
            "categories": result.categories,
            "tags": result.tags,
            "error_message": RequestProcessor.get_operation_info(key=ERROR_OPERATION_KEY, request=request),
            "success_message": RequestProcessor.get_operation_info(key=SUCCESS_OPERATION_KEY, request=request)
        }
        response: Response = TOYS_TEMPLATES.TemplateResponse(  # type: ignore
            request=request,
            name="toys-catalog.html",
            context=context
        )
        CookieProcessor.delete_temp_cookies(request=request, response=response)

        for cookie in current_user.cookies:
            CookieProcessor.set_cookie(response, cookie)

    return response
