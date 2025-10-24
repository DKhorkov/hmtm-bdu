from typing import Optional, List
from math import ceil as math_ceil

from fastapi import Depends, Query

from graphql_client.dto import GQLResponse
from graphql_client.queries.toys import ToysCatalogQuery, ToysCounterQuery
from graphql_client.variables.toys import ToysCatalogVariables, ToysCounterFiltersVariables

from graphql_client import BFFGQLClient
from src.core.cache.redis import Redis
from src.core.cache.ttl_dto import CacheTTL
from src.core.cache.wrappers import RedisWrappers
from src.core.common.parsers import ModelParser
from src.core.exc.exceptions_handlers import set_error_key
from src.core.root.state import GlobalAppState
from src.domains.toys.core.constants import TOYS_PER_PAGE
from src.domains.toys.core.dto import ToysCategoriesResponse, ToysCatalogResponse, ToysTagsResponse
from src.domains.toys.core.models import ToyFilters
from src.domains.toys.dependencies.metadata import ToysMetadataDependenciesRepository


class ToysCatalogDependenciesRepository:

    @staticmethod
    @RedisWrappers.redis_cache(ttl=CacheTTL.TOYS.TOYS_CATALOG)
    async def toys_catalog(
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
            redis: Redis = Depends(GlobalAppState.redis_client),  # noqa  # Для корректной работы

            page: int = Query(default=1, description=f"Номер страницы (по {TOYS_PER_PAGE} записей на страницу)"),
            search: Optional[str] = Query(default=None),
            max_price: Optional[str] = Query(default=None),
            min_price: Optional[str] = Query(default=None),
            quantity_floor: Optional[str] = Query(default=None),
            categories: Optional[List[int]] = Query(default=None),
            tags: Optional[List[int]] = Query(default=None),
            sort_order: Optional[str] = Query(default=None),

            all_toys_categories: ToysCategoriesResponse = Depends(ToysMetadataDependenciesRepository.toys_categories),
            all_toys_tags: ToysTagsResponse = Depends(ToysMetadataDependenciesRepository.toys_tags)
    ) -> ToysCatalogResponse:
        result: ToysCatalogResponse = ToysCatalogResponse()

        search_page: int = page
        if page < 1:
            search_page = 1

        result.filters = ToyFilters(
            search=search or None,
            price_floor=float(min_price) if min_price else None,
            price_ceil=float(max_price) if max_price else None,
            quantity_floor=int(quantity_floor) if quantity_floor else None,
            category_ids=categories,
            tag_ids=tags,
            created_at_order_by_asc=True if sort_order == "oldest" else False
        )

        gql_response: GQLResponse = await gql_client.execute(
            query=ToysCatalogQuery.to_gql(),
            params=ToysCatalogVariables(
                offset=(search_page - 1) * TOYS_PER_PAGE,
                limit=TOYS_PER_PAGE,
                filters=result.filters
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        else:
            for toy_response in gql_response.result["toys"]:
                result.toys.append(ModelParser.toy_for_catalog_from_dict(toy_response))

            total_toys_count: GQLResponse = await gql_client.execute(
                query=ToysCounterQuery.to_gql(),
                params=ToysCounterFiltersVariables(filters=result.filters).to_dict()
            )

            result.categories = all_toys_categories.categories
            result.tags = all_toys_tags.tags
            result.total_pages = math_ceil(total_toys_count.result["toysCounter"] / TOYS_PER_PAGE)
            result.current_page = search_page

        return result
