from typing import Optional, Annotated

from fastapi import Form
from src.config import config
from src.sso.constants import ERRORS_MAPPING
from src.constants import DEFAULT_ERROR_MESSAGE
from graphql_client import (
    RegisterUserVariables,
    LoginUserVariables,
    UserVerifyEmailVariables,

    RegisterUserMutation,
    LoginUserMutation,
    VerifyUserEmailMutation,

    extract_error_message
)


async def process_register(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        display_name: Annotated[str, Form()]
) -> Optional[str]:
    try:
        await config.graphql_client.gql_query(
            query=RegisterUserMutation.to_gql(),
            variable_values=RegisterUserVariables(
                display_name=display_name,
                email=email,
                password=password
            ).to_dict()
        )

    except Exception as error:
        return ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка регистрации"
            ),
            DEFAULT_ERROR_MESSAGE
        )


async def process_login(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
) -> Optional[str]:
    try:
        await config.graphql_client.gql_query(
            query=LoginUserMutation.to_gql(),
            variable_values=LoginUserVariables(
                email=email,
                password=password
            ).to_dict()
        )

    except Exception as error:
        return ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка аутентификации"
            ),
            DEFAULT_ERROR_MESSAGE
        )


async def verify_email(  # type: ignore[return]
        verify_email_token: str,
) -> Optional[str]:
    try:
        await config.graphql_client.gql_query(
            query=VerifyUserEmailMutation.to_gql(),
            variable_values=UserVerifyEmailVariables(
                verify_email_token=verify_email_token,
            ).to_dict()
        )

    except Exception as error:
        return ERRORS_MAPPING.get(
            extract_error_message(
                error=str(error),
                default_message="Ошибка подтверждения email"
            ),
            DEFAULT_ERROR_MESSAGE
        )
