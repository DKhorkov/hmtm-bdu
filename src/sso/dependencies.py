import io

from math import ceil as math_ceil
from typing import Annotated, Dict, Optional, BinaryIO, List
from fastapi import Form, Request, UploadFile, File, Depends, Query

from src.cookies import CookiesConfig
from src.sso.datetime_parser import DatetimeParser
from graphql_client.dto import GQLResponse
from src.config import config
from src.sso.constants import ERRORS_MAPPING, FORGET_PASSWORD_TOKEN_NAME, TOYS_FIXED_LIMIT
from src.constants import DEFAULT_ERROR_MESSAGE
from graphql_client import (
    RegisterUserVariables,
    LoginUserVariables,
    VerifyUserEmailVariables,
    SendVerifyEmailMessageVariables,
    SendForgetPasswordMessageVariables,
    ChangePasswordVariables,
    ForgetPasswordVariables,
    UpdateUserProfileVariables,
    UpdateMasterVariables,
    RegisterMasterVariables,
    GetMasterByUserVariables,
    GetUserByIDVariables,
    GetUserByEmailVariables,
    ToysCatalogVariables,
    ToyByIDVariables,

    RegisterUserMutation,
    LoginUserMutation,
    VerifyUserEmailMutation,
    RefreshTokensMutation,
    SendVerifyEmailMessageMutation,
    SendForgetPasswordMessageMutation,
    ChangePasswordMutation,
    ChangeForgetPasswordMutation,
    UpdateUserProfileMutation,
    UpdateMasterMutation,
    RegisterMasterMutation,

    GetUserByIDQuery,
    GetUserByEmailQuery,
    ToysCatalogQuery,
    GetMeQuery,
    GetMasterByUserQuery,
    ToysCounterQuery,
    AllToysCategoriesQuery,
    AllToysTagsQuery,
    ToyByIDQuery,

    extract_error_message,

    ResponseProcessor as GQLResponseProcessor,
)
from src.sso.dto import (
    LoginResponse,
    GetMeResponse,
    RegisterResponse,
    VerifyEmailResponse,
    SendVerifyEmailMessageResponse,
    SendForgetPasswordMessageResponse,
    ChangePasswordResponse,
    ChangeForgetPasswordResponse,
    UpdateUserProfileResponse,
    RefreshTokensResponse,
    GetUserIsMasterResponse,
    UpdateMasterResponse,
    RegisterMasterResponse,
    GetFullUserInfoResponse,
    ToysCatalogResponse,
    ToysCategoriesResponse,
    ToysTagsResponse,
    ToyByIDResponse,
)
from src.sso.models import Master, UserInfo, Toy, ToysFilters
from src.sso.utils import user_from_dict
from src.request_utils import FernetEnvironmentsKey


async def encryptor() -> FernetEnvironmentsKey:
    return FernetEnvironmentsKey()


async def process_register(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()],
        display_name: Annotated[str, Form()]
) -> RegisterResponse:
    result: RegisterResponse = RegisterResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=RegisterUserMutation.to_gql(),
            variable_values=RegisterUserVariables(
                display_name=display_name,
                email=email,
                password=password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка регистрации"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def process_login(  # type: ignore[return]
        email: Annotated[str, Form()],
        password: Annotated[str, Form()]
) -> LoginResponse:
    result: LoginResponse = LoginResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=LoginUserMutation.to_gql(),
            variable_values=LoginUserVariables(
                email=email,
                password=password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

        if gql_response.headers is not None:
            result.cookies = GQLResponseProcessor(gql_response=gql_response).get_cookies()

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка аутентификации"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def verify_email(  # type: ignore[return]
        verify_email_token: str
) -> VerifyEmailResponse:
    result: VerifyEmailResponse = VerifyEmailResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=VerifyUserEmailMutation.to_gql(),
            variable_values=VerifyUserEmailVariables(
                verify_email_token=verify_email_token,
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка подтверждения email"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def refresh_tokens(
        request: Request,
        cookies: Optional[List[CookiesConfig]] = None
) -> RefreshTokensResponse:
    result: RefreshTokensResponse = RefreshTokensResponse()

    actual_cookies: Dict[str, str] = request.cookies
    if cookies:
        for cookie in cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_refresh_tokens: GQLResponse = await config.graphql_client.gql_query(
            query=RefreshTokensMutation.to_gql(),
            variable_values={},
            cookies=actual_cookies
        )

        if "errors" in gql_refresh_tokens.result:
            result.error = gql_refresh_tokens.result["errors"][0]["message"]
            return result

        result.result = True
        result.headers = gql_refresh_tokens.headers  # type: ignore[assignment]

        if gql_refresh_tokens.headers is not None:
            result.cookies = GQLResponseProcessor(gql_response=gql_refresh_tokens).get_cookies()

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка обновления токенов"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def get_me(
        request: Request,
        cookies: Optional[List[CookiesConfig]] = None
) -> GetMeResponse:
    result: GetMeResponse = GetMeResponse()

    if not cookies and len(request.cookies) == 0:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if cookies:
        for cookie in cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        if request.cookies:
            gql_response: GQLResponse = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )
            if "errors" in gql_response.result:
                raise Exception

            result.user = user_from_dict(gql_response.result["me"])

    except Exception:
        try:
            refreshed_tokens: RefreshTokensResponse = await refresh_tokens(request=request, cookies=cookies)

            if refreshed_tokens.error is not None:
                result.error = refreshed_tokens.error
                return result

            result.headers = refreshed_tokens.headers
            result.cookies = refreshed_tokens.cookies

            actual_cookies = {}
            for cookie in refreshed_tokens.cookies:
                actual_cookies[cookie.KEY] = cookie.VALUE

            gql_get_me: GQLResponse = await config.graphql_client.gql_query(
                query=GetMeQuery.to_gql(),
                variable_values={},
                cookies=actual_cookies
            )

            if "errors" in gql_get_me.result:
                result.error = gql_get_me.result["errors"][0]["message"]
                return result

            result.user = user_from_dict(gql_get_me.result["me"])

        except Exception as err:
            error = ERRORS_MAPPING.get(
                extract_error_message(
                    error=str(err),
                    default_message="Ошибка проверки cookies"
                ),
                DEFAULT_ERROR_MESSAGE
            )
            result.error = error

    return result


async def send_verify_email_message(
        email: Annotated[str, Form()]
) -> SendVerifyEmailMessageResponse:
    result: SendVerifyEmailMessageResponse = SendVerifyEmailMessageResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=SendVerifyEmailMessageMutation().to_gql(),
            variable_values=SendVerifyEmailMessageVariables(
                email=email
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки письма подтверждения электронной почты"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def send_forget_password_message(
        email: Annotated[str, Form()]
) -> SendForgetPasswordMessageResponse:
    result: SendForgetPasswordMessageResponse = SendForgetPasswordMessageResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=SendForgetPasswordMessageMutation().to_gql(),
            variable_values=SendForgetPasswordMessageVariables(
                email=email
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки письма для восстановления забытого пароля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def change_forget_password(
        request: Request,
        new_password: Annotated[str, Form()]
) -> ChangeForgetPasswordResponse:
    result: ChangeForgetPasswordResponse = ChangeForgetPasswordResponse()
    try:
        forget_password_token: Optional[str] = request.cookies.get(FORGET_PASSWORD_TOKEN_NAME)
        if forget_password_token is None:
            result.error = "Ошибка: Токен не найден, попробуйте перейти по ссылке из письма повторно"
            return result

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=ChangeForgetPasswordMutation().to_gql(),
            variable_values=ForgetPasswordVariables(
                forget_password_token=forget_password_token,
                new_password=new_password
            ).to_dict()
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки формы для смены забытого пароля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def change_password(
        request: Request,
        old_password: Annotated[str, Form()],
        new_password: Annotated[str, Form()],
        current_user: GetMeResponse = Depends(get_me)
) -> ChangePasswordResponse:
    result: ChangePasswordResponse = ChangePasswordResponse()

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=ChangePasswordMutation().to_gql(),
            variable_values=ChangePasswordVariables(
                old_password=old_password,
                new_password=new_password
            ).to_dict(),
            cookies=actual_cookies,
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отправки формы для смены пароля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def update_user_profile(
        request: Request,
        username: Annotated[str | None, Form()],
        phone: Annotated[str | None, Form()],
        telegram: Annotated[str | None, Form()],
        avatar: Annotated[UploadFile | None, File()],
        current_user: GetMeResponse = Depends(get_me),
) -> UpdateUserProfileResponse:
    result: UpdateUserProfileResponse = UpdateUserProfileResponse()
    upload_file: Optional[BinaryIO] = None

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        if avatar and avatar.size is not None and avatar.size > 0:
            upload_file = io.BytesIO(await avatar.read())
            upload_file.name = avatar.filename

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=UpdateUserProfileMutation().to_gql(),
            variable_values=UpdateUserProfileVariables(
                display_name=username,
                phone=phone if (phone != "Отсутствует" and phone != "") else None,
                telegram=telegram if (telegram != "Отсутствует" and telegram != "") else None,
                avatar=upload_file,
            ).to_dict(),
            upload_files=True,
            cookies=actual_cookies,
        )

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def master_by_user(
        user_id: str,
        request: Request,
        cookies: Optional[List[CookiesConfig]] = None,
) -> GetUserIsMasterResponse:
    result: GetUserIsMasterResponse = GetUserIsMasterResponse()

    if not cookies and len(request.cookies) == 0:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if cookies:
        for cookie in cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=GetMasterByUserQuery().to_gql(),
            variable_values=GetMasterByUserVariables(
                id=user_id,
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.master = Master(
            id=gql_response.result["masterByUser"]["id"],
            info=gql_response.result["masterByUser"]["info"],
            created_at=DatetimeParser.parse(gql_response.result["masterByUser"]["createdAt"]),
            updated_at=DatetimeParser.parse(gql_response.result["masterByUser"]["updatedAt"]),
        )

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def update_master(
        request: Request,
        info: Annotated[str | None, Form()],
        current_user: GetMeResponse = Depends(get_me),
) -> UpdateMasterResponse:
    result: UpdateMasterResponse = UpdateMasterResponse()

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        master: GetUserIsMasterResponse = await master_by_user(
            user_id=current_user.user.id,  # type: ignore[union-attr]
            request=request,
            cookies=current_user.cookies,
        )

        if master.master is None:
            result.error = "Не удалось найти мастера"
            return result

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=UpdateMasterMutation().to_gql(),
            variable_values=UpdateMasterVariables(
                id=master.master.id,
                info=info
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            result.error = gql_response.result["errors"][0]["message"]
            return result

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def register_master(
        request: Request,
        info: Annotated[str | None, Form()],
        current_user: GetMeResponse = Depends(get_me),
) -> RegisterMasterResponse:
    result: RegisterMasterResponse = RegisterMasterResponse()

    if current_user.error:
        result.error = "Пользователь не найден"
        return result

    actual_cookies: Dict[str, str] = request.cookies
    if current_user.cookies:
        result.cookies = current_user.cookies
        for cookie in current_user.cookies:
            actual_cookies[cookie.KEY] = cookie.VALUE

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=RegisterMasterMutation().to_gql(),
            variable_values=RegisterMasterVariables(
                info=info,
            ).to_dict(),
            cookies=actual_cookies,
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.result = True
        result.headers = gql_response.headers  # type: ignore[assignment]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def get_user_info(
        query_params: str,
) -> GetFullUserInfoResponse:
    result: GetFullUserInfoResponse = GetFullUserInfoResponse(errors=[])

    user_info: Dict[str, Dict[str, str]]
    query_key: str

    try:
        if query_params.isdigit():
            user_response: GQLResponse = await config.graphql_client.gql_query(
                query=GetUserByIDQuery().to_gql(),
                variable_values=GetUserByIDVariables(
                    id=int(query_params),
                ).to_dict(),
            )

            if "errors" in user_response.result:
                raise Exception(user_response.result["errors"][0])

            query_key = "user"

        else:
            user_response: GQLResponse = await config.graphql_client.gql_query(  # type: ignore[no-redef]
                query=GetUserByEmailQuery().to_gql(),
                variable_values=GetUserByEmailVariables(
                    email=query_params,
                ).to_dict(),
            )

            if "errors" in user_response.result:
                raise Exception(user_response.result["errors"][0])

            query_key = "userByEmail"

        user_info: Dict[str, Dict[str, str]] = user_response.result  # type: ignore[no-redef]

        result.user = UserInfo(
            id=user_info[query_key]["id"],
            display_name=user_info[query_key]["displayName"],
            email=user_info[query_key]["email"],
            phone=user_info[query_key]["phone"],
            telegram=user_info[query_key]["telegram"],
            avatar=user_info[query_key]["avatar"],
            created_at=DatetimeParser.parse(user_info[query_key]["createdAt"]),
        )

        master: GQLResponse = await config.graphql_client.gql_query(
            query=GetMasterByUserQuery().to_gql(),
            variable_values=GetMasterByUserVariables(
                id=result.user.id,
            ).to_dict(),
        )

        if "errors" not in master.result:
            result.master = Master(
                id=master.result["masterByUser"]["id"],
                info=master.result["masterByUser"]["info"],
                created_at=DatetimeParser.parse(master.result["masterByUser"]["createdAt"]),
                updated_at=DatetimeParser.parse(master.result["masterByUser"]["updatedAt"]),
            )
        else:
            result.errors.append(master.result["errors"][0]["message"])  # type: ignore[union-attr]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.errors.append(error)  # type: ignore[union-attr]

    return result


async def toys_categories() -> ToysCategoriesResponse:
    result: ToysCategoriesResponse = ToysCategoriesResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=AllToysCategoriesQuery.to_gql(),
            variable_values={}
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.categories = gql_response.result["categories"]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def toys_tags():
    result: ToysTagsResponse = ToysTagsResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=AllToysTagsQuery.to_gql(),
            variable_values={}
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.tags = gql_response.result["tags"]

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка изменения профиля"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def toys_catalog(
        page: int = Query(default=1, ge=1, description="Номер страницы (по 10 записей на одной)"),
        # Filters
        search: Optional[str] = Query(default=None),
        max_price: Optional[str] = Query(default=None),
        min_price: Optional[str] = Query(default=None),
        quantity_floor: Optional[str] = Query(default=None),
        categories: Optional[int] = Query(default=None),
        tags: Optional[List[int]] = Query(default=None),
        sort_order: Optional[str] = Query(default=None),
        # Others
        all_toys_categories: ToysCategoriesResponse = Depends(toys_categories),
        all_toys_tags: ToysTagsResponse = Depends(toys_tags),
) -> ToysCatalogResponse:
    result: ToysCatalogResponse = ToysCatalogResponse(toys=[])

    result.filters = ToysFilters(
        search=search if search else None,
        price_floor=float(min_price) if min_price else None,
        price_ceil=float(max_price) if max_price else None,
        quantity_floor=int(quantity_floor) if quantity_floor else None,
        category_id=categories,
        tags_id=tags,
        created_at_order_by_asc=True if sort_order == "oldest" else False,
    )

    try:
        if page < 1:
            raise Exception("Номер страницы должен быть не менее 1")
        offset: int = (page - 1) * TOYS_FIXED_LIMIT

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=ToysCatalogQuery.to_gql(),
            variable_values=ToysCatalogVariables(
                offset=offset,
                limit=TOYS_FIXED_LIMIT,
                filters=result.filters
            ).to_dict()
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        for toys in gql_response.result["toys"]:
            toy = Toy(
                id=toys["id"],
                master=toys["master"],
                category=toys["category"],
                name=toys["name"],
                description=toys["description"],
                price=round(toys["price"], 2),
                quantity=toys["quantity"],
                created_at=DatetimeParser.parse(toys["createdAt"]),
                tags=toys["tags"],
                attachments=toys["attachments"]
            )
            result.toys.append(toy)  # type: ignore[union-attr]

        total_toys_count: GQLResponse = await config.graphql_client.gql_query(
            query=ToysCounterQuery.to_gql(),
            variable_values={}
        )

        result.categories = all_toys_categories.categories
        result.tags = all_toys_tags.tags
        result.total_pages = math_ceil(total_toys_count.result["toysCounter"] / TOYS_FIXED_LIMIT)
        result.current_page = page

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отображения каталога"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def toy_by_id(
        toy_id: int
) -> ToyByIDResponse:
    result: ToyByIDResponse = ToyByIDResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=ToyByIDQuery.to_gql(),
            variable_values=ToyByIDVariables(
                id=toy_id,
            ).to_dict()
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        toy_response = gql_response.result["toy"]
        result.toy = Toy(
            id=toy_response["id"],
            master=toy_response["master"],
            category=toy_response["category"],
            name=toy_response["name"],
            description=toy_response["description"],
            price=round(toy_response["price"], 2),
            quantity=toy_response["quantity"],
            created_at=DatetimeParser.parse(toy_response["createdAt"]),
            tags=toy_response["tags"],
            attachments=toy_response["attachments"]
        )

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отображения каталога"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result
