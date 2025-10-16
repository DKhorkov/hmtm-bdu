from typing import Dict, Any

from graphql_client.constants import GQL_SERVER_ERROR

GQL_ERRORS_MAPPER: Dict[str, Any] = {
    'rpc error: code = FailedPrecondition desc = validation error: invalid password': "4001",
    "rpc error: code = Internal desc = wrong password": "4003",
    'rpc error: code = FailedPrecondition desc = email does not meet the requirements': "4004",
    'rpc error: code = FailedPrecondition desc = display name not meet the requirements': "4005",
    'rpc error: code = AlreadyExists desc = user with provided email already exists': "4006",
    'rpc error: code = Unauthenticated desc = wrong password': "4007",
    'permission denied: User with this email has not confirmed it': "4008",
    "rpc error: code = FailedPrecondition desc = provided email has been already confirmed": "4009",
    "rpc error: code = FailedPrecondition desc = New password can not be equal to old password": "4010",
    "invalid file extension=.webp": "4011",
    "rpc error: code = FailedPrecondition desc = telegram not meet the requirements": "4012",
    "rpc error: code = FailedPrecondition desc = phone not meet the requirements": "4013",
    "rpc error: code = NotFound desc = master not found": "4014",
    'rpc error: code = AlreadyExists desc = master already exists': "4015",
    "rpc error: code = FailedPrecondition desc = validation error: invalid display name": "4016",
    'rpc error: code = NotFound desc = user not found': "4017",
    "accessToken cookie not found": "4018",
    "rpc error: code = Unauthenticated desc = JWT token is invalid or has expired%!(EXTRA string=)": "4019",
    "rpc error: code = FailedPrecondition desc = validation error: invalid email address": "4021",
    "rpc error: code = Master not found": "4030",
    "rpc error: code = Internal desc = validation error: invalid master info": "4031",

    "rpc error: code = GQL_SERVER_DISCONNECTED": "5000",
    "rpc error: code = GQL_CONNECTION_ERROR": "5010",
    "Unknown error": "5001",
    GQL_SERVER_ERROR: "5001",
}
