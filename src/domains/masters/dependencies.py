from typing import Optional
from math import ceil as math_ceil

from fastapi import Query, Depends

from graphql_client import extract_error_message, GraphQLClient
from graphql_client.variables.masters import (
    MastersCatalogVariables,
    MasterCounterVariables
)
from graphql_client.queries.masters import (
    MastersCatalogQuery,
    MastersCounterQuery
)
from graphql_client.dto import GQLResponse
from src.core.common.constants import DEFAULT_ERROR_MESSAGE
from src.core.common.parsers import DatetimeParsers
from src.core.state import GlobalAppState
from src.domains.masters.constants import MASTERS_PER_PAGE
from src.domains.masters.dto import MastersCatalogResponse
from src.domains.masters.models import (
    MasterForCatalog,
    MastersFilters
)
from src.domains.sso.constants import SSO_ERROR_MAPPER
from src.core.cache.wrappers import RedisWrappers
from src.core.cache.ttl_dto import CacheTTL


@RedisWrappers.redis_cache(ttl=CacheTTL.MASTERS.MASTERS_CATALOG)
async def masters_catalog(
        gql_client: GraphQLClient = Depends(GlobalAppState.gql_client),  # noqa
        page: int = Query(default=1, ge=1, description=f"Номер страницы (по {MASTERS_PER_PAGE} записей на страницу)"),
        search: Optional[str] = Query(default=""),
        sort_order: Optional[str] = Query(default=None),
) -> MastersCatalogResponse:
    result: MastersCatalogResponse = MastersCatalogResponse()

    try:
        if page < 1:
            raise Exception("Номер страницы должен быть не менее 1")
        offset: int = (page - 1) * MASTERS_PER_PAGE

        result.filters = MastersFilters(
            search=search,  # type: ignore
            created_at_order_by_asc=True if sort_order == "oldest" else False,
        )

        gql_response: GQLResponse = await gql_client.execute(
            query=MastersCatalogQuery.to_gql(),
            variable_values=MastersCatalogVariables(
                limit=MASTERS_PER_PAGE,
                offset=offset,
                filters=result.filters
            ).to_dict()
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        total_masters_count: GQLResponse = await gql_client.execute(
            query=MastersCounterQuery.to_gql(),
            variable_values=MasterCounterVariables(
                filters=result.filters,
            ).to_dict()
        )

        for master in gql_response.result["masters"]:
            result.masters.append(
                MasterForCatalog(
                    id=master["id"],
                    info=master["info"],
                    created_at=DatetimeParsers.parse_iso_format(master["createdAt"]),
                )
            )

        result.total_pages = math_ceil(total_masters_count.result["mastersCounter"] / MASTERS_PER_PAGE)
        result.current_page = page

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отображения каталога"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result
