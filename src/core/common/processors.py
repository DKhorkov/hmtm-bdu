from typing import Optional, Dict, Any

from fastapi import Request, Response

from src.core.common.constants import UNKNOWN_ERROR
from src.core.cookies.processors import CookieCompressor
from src.core.mappers.sso import SSO_OPERATION_CODE_MAPPER


class ResponseProcessor:

    @staticmethod
    def set_operation_response(response: Response, key: str, value: str) -> None:
        compressed_data: Optional[str] = CookieCompressor.compress(value)

        if not compressed_data:
            return

        response.set_cookie(key=key, value=compressed_data)

    @staticmethod
    def set_bulk_operation_response(response: Response, context: Dict[str, str]) -> None:
        for key, value in context.items():
            compressed_data: Optional[str] = CookieCompressor.compress(value)

            if not compressed_data:
                continue

            response.set_cookie(key=key, value=compressed_data)


class RequestProcessor:

    @staticmethod
    def get_operation_info(request: Request, key: str) -> Optional[str]:
        decompressed_value: Optional[Any] = CookieCompressor.decompress(request.cookies.get(key))

        if not decompressed_value:
            return None

        else:
            message: str = SSO_OPERATION_CODE_MAPPER.get(decompressed_value, UNKNOWN_ERROR)

        return message

    @staticmethod
    def get_payload_info(request: Request, key: str) -> Optional[str]:
        decompressed_value: Optional[Any] = CookieCompressor.decompress(request.cookies.get(key))

        if not decompressed_value:
            return ""

        return decompressed_value
