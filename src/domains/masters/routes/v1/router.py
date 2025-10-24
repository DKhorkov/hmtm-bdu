from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .catalog import masters_catalog


class MastersV1Router:
    router = APIRouter(
        prefix="/masters",
        tags=["MASTERS"]
    )

    router.get(
        path="/catalog",
        response_class=HTMLResponse,
        name="masters_catalog"
    )(masters_catalog)
