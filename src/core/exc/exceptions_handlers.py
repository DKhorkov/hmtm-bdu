from ast import literal_eval as ast_literal_eval

from fastapi import Request, Response, status
from fastapi.responses import RedirectResponse

from graphql_client.constants import DEFAULT_GQL_ERROR, GQL_SERVER_ERROR
from src.core.common.dto import BaseResponse
from src.core.common.processors import ResponseProcessor
from src.core.cookies.processors import CookieProcessor
from src.core.exc.exceptions import RedirectViaException
from src.core.common.constants import ERROR_OPERATION_KEY, DEFAULT_ERROR_CODE
from src.core.mappers.graphql import GQL_ERRORS_MAPPER


class GlobalExceptionHandler:

    @staticmethod
    async def redirect_via_exception_handler(
            request: Request,  # noqa
            exception: RedirectViaException
    ) -> Response:
        response: Response = RedirectResponse(url=exception.url, status_code=status.HTTP_303_SEE_OTHER)
        ResponseProcessor.set_operation_response(key=ERROR_OPERATION_KEY, response=response, value=exception.value)

        if exception.cookies is not None:
            for cookie in exception.cookies:
                CookieProcessor.set_cookie(response, cookie)

        return response


def set_error_key(response: BaseResponse, exc: str) -> None:
    try:
        if exc.startswith(GQL_SERVER_ERROR):
            error: str = GQL_SERVER_ERROR
        else:
            error = ast_literal_eval(exc)["message"]

    except KeyError:
        error = DEFAULT_GQL_ERROR

    response.error = GQL_ERRORS_MAPPER.get(error, DEFAULT_ERROR_CODE)
