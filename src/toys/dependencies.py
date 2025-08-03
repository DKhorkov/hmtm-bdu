from typing import Optional, List
from math import ceil as math_ceil
from fastapi import Query, Depends

from graphql_client import (
    AllToysCategoriesQuery,
    extract_error_message,
    AllToysTagsQuery,
    ToysCatalogQuery,
    ToysCatalogVariables,
    ToysCounterQuery,
    ToyByIDQuery,
    ToyByIDVariables,
    ToysCounterFiltersVariables
)
from graphql_client.dto import GQLResponse
from src.cache.ttl_models import CacheTTL
from src.common.config import config
from src.common.constants import DEFAULT_ERROR_MESSAGE
from src.sso.constants import ERRORS_MAPPING
from src.toys.constants import TOYS_PER_PAGE
from src.common.datetime_parser import DatetimeParser
from src.toys.dto import (
    ToysCategoriesResponse,
    ToysTagsResponse,
    ToysCatalogResponse,
    ToyByIDResponse
)
from src.toys.models import (
    ToyCategory,
    ToyTag,
    ToyAttachment,
    ToyForCatalog,
    ToyFilters,
    ToyForCard,
    MasterForToyCard,
    UserForToyCard,
)
from src.cache.wrappings import redis_cache


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
                default_message="Ошибка получения категорий игрушек"
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
                default_message="Ошибку получения тегов игрушек"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


@redis_cache(ttl=CacheTTL.TOYS.TOYS_CATALOG)
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

        gql_response: GQLResponse = await config.graphql_client.gql_query(
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
                created_at=DatetimeParser.parse(toy_response["createdAt"]),
                tags=[ToyTag(name=tag["name"]) for tag in toy_response["tags"]],
                attachments=[ToyAttachment(link=attachments["link"]) for attachments in toy_response["attachments"]],
            )
            result.toys.append(toy)  # type: ignore[union-attr]

        total_toys_count: GQLResponse = await config.graphql_client.gql_query(
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
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отображения каталога"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result


@redis_cache(ttl=CacheTTL.TOYS.TOY_BY_ID)
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
            created_at=DatetimeParser.parse(response["createdAt"]),
            tags=[ToyTag(name=tag["name"]) for tag in response["tags"]],
            attachments=[ToyAttachment(link=attachments["link"]) for attachments in response["attachments"]],
        )

    except Exception as err:
        error: str = ERRORS_MAPPING.get(
            extract_error_message(
                error=str(err),
                default_message="Ошибка отображения карточки товара"
            ),
            DEFAULT_ERROR_MESSAGE
        )

        result.error = error

    return result
