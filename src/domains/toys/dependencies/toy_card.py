from fastapi import Depends

from graphql_client import BFFGQLClient
from graphql_client.dto import GQLResponse
from graphql_client.queries.toys import ToyByIDQuery
from graphql_client.variables.toys import ToyByIDVariables

from src.core.cache.ttl_dto import CacheTTL
from src.core.cache.wrappers import RedisWrappers
from src.core.cache.redis import Redis
from src.core.common.parsers import ModelParser
from src.core.exc.exceptions_handlers import set_error_key
from src.core.root.state import GlobalAppState
from src.domains.toys.core.dto import ToyByIDResponse


class ToyInfoDependenciesRepository:

    @staticmethod
    @RedisWrappers.redis_cache(ttl=CacheTTL.TOYS.TOY_BY_ID)
    async def toy_by_id(
            toy_id: int,
            gql_client: BFFGQLClient = Depends(GlobalAppState.bff_gql_client),
            redis: Redis = Depends(GlobalAppState.redis_client)  # noqa  # Требуется для корректной работы
    ) -> ToyByIDResponse:
        result: ToyByIDResponse = ToyByIDResponse()

        gql_response: GQLResponse = await gql_client.execute(
            query=ToyByIDQuery.to_gql(),
            params=ToyByIDVariables(
                id=toy_id,
            ).to_dict()
        )

        if gql_response.error:
            set_error_key(response=result, exc=gql_response.error)

        else:
            result.toy = ModelParser.toy_for_card_from_dict(gql_response.result["toy"])

        return result
