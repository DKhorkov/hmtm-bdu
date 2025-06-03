import sys
import os

# Adding ./src to python path for running from console purpose:
sys.path.append(os.getcwd())

from uvicorn import run as uvicorn_run

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.root.routes import router as main_router
from src.sso.routes import router as sso_router
from src.toys.routes import router as toys_router
from src.profile.routes import router as profile_router
from src.root.utils import lifespan
from src.logging.middlewares import LoggerMiddleware

app = FastAPI(lifespan=lifespan)

app.add_middleware(LoggerMiddleware)  # type: ignore
app.include_router(main_router)
app.include_router(sso_router)
app.include_router(profile_router)
app.include_router(toys_router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/scripts", StaticFiles(directory="scripts/js"), name="scripts")

if __name__ == "__main__":
    uvicorn_run(app, host="0.0.0.0", port=8090)
