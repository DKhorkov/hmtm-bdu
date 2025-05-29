from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Response, Request, Depends, status, APIRouter
from starlette.templating import Jinja2Templates

from src.cookies import set_cookie
from src.utils import FernetEnvironmentsKey, encryptor as encryptor_dependency
from src.sso.dto import GetMeResponse
from src.toys.dto import ToysCatalogResponse, ToyByIDResponse
from src.common.dependencies import get_me as get_me_dependency
from src.toys.dependencies import (
    toys_catalog as toys_catalog_dependency,
    toy_by_id as toy_by_id_dependency,
)

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/toys", tags=["Toys"])


@router.get(path="/catalog", response_class=HTMLResponse, name="toys_catalog")
async def toys_catalog(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: ToysCatalogResponse = Depends(toys_catalog_dependency),
        encryptor: FernetEnvironmentsKey = Depends(encryptor_dependency)
):
    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(result.error)

        return RedirectResponse(
            url=f"/?error={encrypted_error}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    context = {
        "user": current_user.user if current_user.user else None,
        "current_page": result.current_page,
        "total_pages": result.total_pages,
        "toys": result.toys,
        "categories": result.categories,
        "tags": result.tags,
    }
    response: Response = templates.TemplateResponse(
        request=request,
        name="toys-catalog.html",
        context=context
    )

    for cookie in current_user.cookies:
        response = set_cookie(response, cookie)

    return response


@router.get("/catalog/{toy_id}", response_class=HTMLResponse, name="toy_by_id")
async def toy_by_id(
        request: Request,
        current_user: GetMeResponse = Depends(get_me_dependency),
        result: ToyByIDResponse = Depends(toy_by_id_dependency),
        encryptor: FernetEnvironmentsKey = Depends(encryptor_dependency)
):
    if result.error is not None:
        encrypted_error: str = encryptor.encrypt(result.error)

        return RedirectResponse(
            url=f"/toys/catalog?error={encrypted_error}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    context = {
        "user": current_user.user if current_user.user else None,
        "toy": result.toy
    }
    response: Response = templates.TemplateResponse(request=request, name="toy-page.html", context=context)

    for cookie in current_user.cookies:
        response = set_cookie(response, cookie)

    return response
