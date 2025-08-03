from typing import Optional
from math import ceil as math_ceil

from fastapi import Query

from graphql_client import (
    extract_error_message,
    MastersCatalogQuery,
    MastersCatalogVariables,
    MastersCounterQuery,
    MasterCounterVariables,
)
from graphql_client.dto import GQLResponse
from src.common.config import config
from src.common.constants import DEFAULT_ERROR_MESSAGE
from src.common.datetime_parser import DatetimeParser
from src.masters.constants import MASTERS_PER_PAGE
from src.masters.dto import MastersCatalogResponse
from src.masters.models import MasterForCatalog, MastersFilters
from src.sso.constants import ERRORS_MAPPING
from src.cache.wrappings import redis_cache
from src.cache.ttl_models import CacheTTL


@redis_cache(ttl=CacheTTL.MASTERS.MASTERS_CATALOG)
async def masters_catalog(
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
            search=search,  # type: ignore[arg-type]
            created_at_order_by_asc=True if sort_order == "oldest" else False,
        )

        gql_response: GQLResponse = await config.graphql_client.gql_query(
            query=MastersCatalogQuery.to_gql(),
            variable_values=MastersCatalogVariables(
                limit=MASTERS_PER_PAGE,
                offset=offset,
                filters=result.filters
            ).to_dict()
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        total_masters_count: GQLResponse = await config.graphql_client.gql_query(
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
                    created_at=DatetimeParser.parse(master["createdAt"]),
                )
            )

        result.total_pages = math_ceil(total_masters_count.result["mastersCounter"] / MASTERS_PER_PAGE)
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
