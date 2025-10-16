from typing import Optional
from math import ceil as math_ceil

from fastapi import Query, Depends

from graphql_client import BFFGQLClient
from graphql_client.variables.masters import (
    MastersCatalogVariables,
    MasterCounterVariables
)
from graphql_client.queries.masters import (
    MastersCatalogQuery,
    MastersCounterQuery
)
from graphql_client.dto import GQLResponse
from src.core.cache.redis import Redis
from src.core.common.parsers import DatetimeParser
from src.core.exc.exceptions_handlers import set_error_key
from src.core.state import GlobalAppState
from src.domains.masters.core.constants import MASTERS_PER_PAGE
from src.domains.masters.core.dto import MastersCatalogResponse
from src.domains.masters.core.models import (
    MasterForCatalog,
    MastersFilters
)
from src.core.cache.wrappers import RedisWrappers
from src.core.cache.ttl_dto import CacheTTL


class MastersCatalogDependenciesRepository:

    @staticmethod
    @RedisWrappers.redis_cache(ttl=CacheTTL.MASTERS.MASTERS_CATALOG)
    async def masters_catalog(
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
            redis: Redis = Depends(GlobalAppState.redis_client),  # noqa  # Требуется для корректной работы

            page: int = Query(default=1, description=f"Номер страницы (по {MASTERS_PER_PAGE} записей на страницу)"),
            search: Optional[str] = Query(default=""),
            sort_order: Optional[str] = Query(default=None),
    ) -> MastersCatalogResponse:
        result: MastersCatalogResponse = MastersCatalogResponse()

        search_page: int = page
        if page < 1:
            search_page = 1

        result.filters = MastersFilters(
            search=search,  # type: ignore
            created_at_order_by_asc=True if sort_order == "oldest" else False
        )

        gql_response: GQLResponse = await gql_client.execute(
            query=MastersCatalogQuery.to_gql(),
            variable_values=MastersCatalogVariables(
                limit=MASTERS_PER_PAGE,
                offset=(search_page - 1) * MASTERS_PER_PAGE,
                filters=result.filters
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        else:
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
                        created_at=DatetimeParser.parse_iso_format(master["createdAt"]),
                    )
                )

            result.total_pages = math_ceil(total_masters_count.result["mastersCounter"] / MASTERS_PER_PAGE)
            result.current_page = search_page

        return result
