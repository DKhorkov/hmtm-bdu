from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

main_router = APIRouter(tags=["Main"])
templates = Jinja2Templates(directory="templates")


@main_router.get("/", response_class=HTMLResponse, name="home_page")
async def home_page(request: Request):
    '''
    # TODO  создать депенденсю, котоорая будет возвщать ДТО с теккущим юзером (GetMeReponse)
    1) дергать депенденси get_me. Если есть ответ - то отрисовываем страницу с профилем и войти
    2) если получили ошибку - дергаем ручку рефреТокенс. Если получили ошибку - возвращаем базовую страничку с
    кнопками войти и зарегаться
    3) иначе делаем запрос снова к get_me и делаем логику из 1 пункта + ставим куки, котоыре получили из рефрешТокенс.

    вся логика запросов должна быть в депенденси.
    В роуте просто получаешь датакласс с юзером и ошибкой. Если ошибка есть - страничка с войти и зарегаться
    если нет ошибки и есть юзер - страничка с профилем и выйти
    '''

    return templates.TemplateResponse(request=request, name="homepage.html")
