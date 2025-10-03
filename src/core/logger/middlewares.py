from time import perf_counter
from typing import Callable, Awaitable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


from src.core.logger.enums import Levels
from src.core.logger.logger import Logger


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(  # type: ignore
            self,
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response | None:
        start_time: float = perf_counter()
        logger: Logger = request.app.state.logger

        try:
            response: Response = await call_next(request)
            process_time: float = perf_counter() - start_time

            await logger.write_log(
                level=Levels.INFO,
                message=f"URL: {request.url.path} Статус: {response.status_code} Время запроса: {round(process_time, 5)}",
            )

            return response

        except Exception as error:
            await logger.write_log(
                level=Levels.ERROR,
                message=f"URL: {request.url.path} Статус: {Levels.ERROR} Ошибка: {error}"
            )
