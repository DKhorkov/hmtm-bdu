from typing import Union

from fastapi import Depends, status
from fastapi.responses import RedirectResponse

from src.sso import get_me as get_me_dependency
from src.sso.dto import GetMeResponse
from src.utils import (
    FernetEnvironmentsKey,
    encryptor as encryptor_dependency
)


async def active_user_session(
        current_user: GetMeResponse = Depends(get_me_dependency),
        encryptor: FernetEnvironmentsKey = Depends(encryptor_dependency)
) -> Union[RedirectResponse, None]:
    if current_user.user is None:
        encrypted_error: str = encryptor.encrypt(str(current_user.error))
        return RedirectResponse(f"/sso/login?error={encrypted_error}", status_code=status.HTTP_303_SEE_OTHER)

    return None
