from typing import Optional

from fastapi import Request

from src.core.common.constants import DEFAULT_ERROR_MESSAGE, REQUEST_ENVIRONMENTS_MAPPING
from src.core.common.encryptor import Cryptography


class UrlExtractors:

    @staticmethod
    def error_from_url(request: Request, cryptography: Cryptography) -> Optional[str]:
        error_key: Optional[str] = request.query_params.get("error")

        if not error_key:
            return None

        return REQUEST_ENVIRONMENTS_MAPPING.get(cryptography.decrypt(error_key), DEFAULT_ERROR_MESSAGE)  # type: ignore

    @staticmethod
    def success_message_from_url(request: Request, cryptography: Cryptography) -> Optional[str]:
        message_key: Optional[str] = request.query_params.get("message")

        if not message_key:
            return None

        return REQUEST_ENVIRONMENTS_MAPPING.get(cryptography.decrypt(message_key), DEFAULT_ERROR_MESSAGE)  # type: ignore
