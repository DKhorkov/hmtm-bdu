from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .catalog import toys_catalog
from .toy_card import toy_by_id


class ToysV1Router:
    router = APIRouter(prefix="/toys", tags=["TOYS"])

    router.get(path="/catalog", response_class=HTMLResponse, name="toys_catalog")(toys_catalog)
    router.get(path="/catalog/{toy_id}", response_class=HTMLResponse, name="toy_by_id")(toy_by_id)
