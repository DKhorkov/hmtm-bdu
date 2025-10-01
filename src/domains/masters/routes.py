from typing import Dict, Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from src.core.common.cookies import set_cookie
from src.core.common.dto import GetMeResponse
from src.core.common.utils import Cryptography
from src.core.common.dependencies import get_me as get_me_dependency
from src.core.config import config
from src.domains.masters.dependencies import masters_catalog as masters_catalog_dependency
from src.domains.masters.dto import MastersCatalogResponse

router: APIRouter = APIRouter(prefix="/masters", tags=["Masters"])
templates: Jinja2Templates = Jinja2Templates(directory="templates")


@router.get("/catalog", response_class=HTMLResponse, name="masters_catalog")
async def masters_catalog(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: MastersCatalogResponse = Depends(masters_catalog_dependency),
        encryptor: Cryptography = Depends(config.get_encryptor),
):
    if result.error:
        encrypted_error: str = encryptor.encrypt(result.error)

        return RedirectResponse(
            url=f"/?error={encrypted_error}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    context: Dict[str, Any] = {
        "user": current_user.user if current_user.user else None,
        "current_page": result.current_page,
        "total_pages": result.total_pages,
        "masters": result.masters,
    }

    response: Response = templates.TemplateResponse(
        request=request,
        name="masters-catalog.html",  # Реализовать Фронт
        context=context
    )

    for cookie in current_user.cookies:
        set_cookie(response, cookie)

    return response
