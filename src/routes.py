from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

main_router = APIRouter(tags=["Main"])
templates = Jinja2Templates(directory="templates")


@main_router.get("/", response_class=HTMLResponse, name="home_page")
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")
