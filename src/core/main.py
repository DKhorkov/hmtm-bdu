import sys
import os

# Adding ./src to python path for running from console purpose:
sys.path.append(os.getcwd())

from uvicorn import run as uvicorn_run

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.routes import router as main_router
from src.domains.sso.routes import router as sso_router
from src.domains.toys.routes import router as toys_router
from src.domains.profile.routes import router as profile_router
from src.domains.masters.routes import router as masters_router
from src.core.lifespan import lifespan
from src.core.logger.middlewares import LoggerMiddleware

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggerMiddleware)  # type: ignore
app.include_router(main_router)
app.include_router(sso_router)
app.include_router(profile_router)
app.include_router(toys_router)
app.include_router(masters_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/scripts", StaticFiles(directory="scripts/js"), name="scripts")

if __name__ == "__main__":
    uvicorn_run(app, host="0.0.0.0", port=8090)
