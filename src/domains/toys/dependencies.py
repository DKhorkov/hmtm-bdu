from typing import Optional, List
from math import ceil as math_ceil
from fastapi import Query, Depends

from graphql_client import extract_error_message
from graphql_client.variables.toys import (
    ToysCatalogVariables,
    ToyByIDVariables,
    ToysCounterFiltersVariables
)
from graphql_client.queries.toys import (
    ToysCatalogQuery,
    ToysCounterQuery,
    AllToysCategoriesQuery,
    AllToysTagsQuery,
    ToyByIDQuery
)
from graphql_client.dto import GQLResponse
from src.core.cache.ttl_dto import CacheTTL
from src.core.config import config
from src.core.common.constants import DEFAULT_ERROR_MESSAGE
from src.domains.sso.constants import SSO_ERROR_MAPPER
from src.domains.toys.constants import TOYS_PER_PAGE
from src.core.common.parsers import Parse
from src.domains.toys.dto import (
    ToysCategoriesResponse,
    ToysTagsResponse,
    ToysCatalogResponse,
    ToyByIDResponse
)
from src.domains.toys.models import (
    ToyCategory,
    ToyTag,
    ToyAttachment,
    ToyForCatalog,
    ToyFilters,
    ToyForCard,
    MasterForToyCard,
    UserForToyCard,
)
from src.core.cache.wrappers import RedisWrappers


async def toys_categories() -> ToysCategoriesResponse:
    result: ToysCategoriesResponse = ToysCategoriesResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.execute(
            query=AllToysCategoriesQuery.to_gql(),
            variable_values={}
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.categories = gql_response.result["categories"]

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка получения категорий игрушек"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


async def toys_tags():
    result: ToysTagsResponse = ToysTagsResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.execute(
            query=AllToysTagsQuery.to_gql(),
            variable_values={}
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        result.tags = gql_response.result["tags"]

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибку получения тегов игрушек"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


@RedisWrappers.redis_cache(ttl=CacheTTL.TOYS.TOYS_CATALOG, redis=config.redis_as_cache)
async def toys_catalog(
        page: int = Query(default=1, ge=1, description=f"Номер страницы (по {TOYS_PER_PAGE} записей на страницу)"),
        # Filters
        search: Optional[str] = Query(default=None),
        max_price: Optional[str] = Query(default=None),
        min_price: Optional[str] = Query(default=None),
        quantity_floor: Optional[str] = Query(default=None),
        categories: Optional[List[int]] = Query(default=None),
        tags: Optional[List[int]] = Query(default=None),
        sort_order: Optional[str] = Query(default=None),
        # Others
        all_toys_categories: ToysCategoriesResponse = Depends(toys_categories),
        all_toys_tags: ToysTagsResponse = Depends(toys_tags),
) -> ToysCatalogResponse:
    result: ToysCatalogResponse = ToysCatalogResponse()

    result.filters = ToyFilters(
        search=search if search else None,
        price_floor=float(min_price) if min_price else None,
        price_ceil=float(max_price) if max_price else None,
        quantity_floor=int(quantity_floor) if quantity_floor else None,
        category_ids=categories,
        tag_ids=tags,
        created_at_order_by_asc=True if sort_order == "oldest" else False,
    )

    try:
        if page < 1:
            raise Exception("Номер страницы должен быть не менее 1")
        offset: int = (page - 1) * TOYS_PER_PAGE

        gql_response: GQLResponse = await config.graphql_client.execute(
            query=ToysCatalogQuery.to_gql(),
            variable_values=ToysCatalogVariables(
                offset=offset,
                limit=TOYS_PER_PAGE,
                filters=result.filters
            ).to_dict()
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        for toy_response in gql_response.result["toys"]:
            toy = ToyForCatalog(
                id=toy_response["id"],
                category=ToyCategory(name=toy_response["category"]["name"]),
                name=toy_response["name"],
                description=toy_response["description"],
                price=round(toy_response["price"], 2),
                quantity=toy_response["quantity"],
                created_at=Parse.datetime(toy_response["createdAt"]),
                tags=[ToyTag(name=tag["name"]) for tag in toy_response["tags"]],
                attachments=[ToyAttachment(link=attachments["link"]) for attachments in toy_response["attachments"]],
            )
            result.toys.append(toy)  # type: ignore[union-attr]

        total_toys_count: GQLResponse = await config.graphql_client.execute(
            query=ToysCounterQuery.to_gql(),
            variable_values=ToysCounterFiltersVariables(
                filters=result.filters
            ).to_dict()
        )

        result.categories = all_toys_categories.categories
        result.tags = all_toys_tags.tags
        result.total_pages = math_ceil(total_toys_count.result["toysCounter"] / TOYS_PER_PAGE)
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


@RedisWrappers.redis_cache(ttl=CacheTTL.TOYS.TOY_BY_ID, redis=config.redis_as_cache)
async def toy_by_id(
        toy_id: int
) -> ToyByIDResponse:
    result: ToyByIDResponse = ToyByIDResponse()

    try:
        gql_response: GQLResponse = await config.graphql_client.execute(
            query=ToyByIDQuery.to_gql(),
            variable_values=ToyByIDVariables(
                id=toy_id,
            ).to_dict()
        )

        if "errors" in gql_response.result:
            raise Exception(gql_response.result["errors"][0])

        response = gql_response.result["toy"]
        result.toy = ToyForCard(
            id=response["id"],
            master=MasterForToyCard(
                id=response["master"]["id"],
                user=UserForToyCard(
                    avatar=response["master"]["user"]["avatar"],
                    display_name=response["master"]["user"]["displayName"],
                )
            ),
            category=ToyCategory(name=response["category"]["name"]),
            name=response["name"],
            description=response["description"],
            price=round(response["price"], 2),
            quantity=response["quantity"],
            created_at=Parse.datetime(response["createdAt"]),
            tags=[ToyTag(name=tag["name"]) for tag in response["tags"]],
            attachments=[ToyAttachment(link=attachments["link"]) for attachments in response["attachments"]],
        )

    except Exception as err:
        error: str = SSO_ERROR_MAPPER.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отображения карточки товара"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result
