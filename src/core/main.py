from sys import path as sys_path
from os import getcwd as os_getcwd

sys_path.append(os_getcwd())  # Добавление src/core/main.py пути для доступа из консоли

from uvicorn import run as uvicorn_run
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.exc.exceptions import RedirectViaException
from src.core.exc.exceptions_handlers import GlobalExceptionHandler
from src.core.lifespan import lifespan
from src.core.logger.middlewares import LoggerMiddleware

from src.core.routes import router as main_router
from src.domains.sso.routers import SSO_V1_ROUTER
from src.domains.masters.routes import MASTERS_V1_ROUTER
from src.domains.toys.routes import TOYS_V1_ROUTER
from src.domains.profile.routes import PROFILE_V1_ROUTER

app = FastAPI(lifespan=lifespan)

# Exception Handlers:
app.add_exception_handler(RedirectViaException, GlobalExceptionHandler.redirect_via_exception_handler)  # type: ignore

# Middlewares:
app.add_middleware(LoggerMiddleware)  # type: ignore

# Mount-files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/scripts", StaticFiles(directory="scripts/js"), name="scripts")

# Routers:
app.include_router(main_router)
app.include_router(SSO_V1_ROUTER)
app.include_router(TOYS_V1_ROUTER)
app.include_router(MASTERS_V1_ROUTER)
app.include_router(PROFILE_V1_ROUTER)

if __name__ == "__main__":
    uvicorn_run(app, host="0.0.0.0", port=8090)

"""
    Порядок инициализации FastAPI-Зависимостей для корректной работы:
    1. Lifespan
    2. Exception Handlers
    3. Middleware
    4. Mount-files
    5. Routers
    Примечания
    Порядок Routers и Mount-files может меняться, но принято монтировать файлы до "ручек"
"""
