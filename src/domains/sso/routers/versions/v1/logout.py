from fastapi import Request, status
from fastapi.responses import RedirectResponse, Response


async def logout_process(request: Request):
    response: Response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    for cookie in request.cookies:
        response.delete_cookie(key=cookie)

    return response
