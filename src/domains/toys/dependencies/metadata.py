from typing import Optional

from fastapi import Depends

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.queries.toys import AllToysCategoriesQuery, AllToysTagsQuery

from src.core.root.state import GlobalAppState
from src.domains.toys.core.dto import ToysCategoriesResponse, ToysTagsResponse


class ToysMetadataDependenciesRepository:

    @staticmethod
    async def toys_categories(
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> Optional[ToysCategoriesResponse]:
        gql_response: GQLResponse = await gql_client.execute(query=AllToysCategoriesQuery.to_gql(), params={})

        if gql_response.error:
            return None

        return ToysCategoriesResponse(categories=gql_response.result["categories"])

    @staticmethod
    async def toys_tags(
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client)
    ) -> Optional[ToysTagsResponse]:
        gql_response: GQLResponse = await gql_client.execute(query=AllToysTagsQuery.to_gql(), params={})

        if gql_response.error:
            return None

        return ToysTagsResponse(tags=gql_response.result["tags"])
