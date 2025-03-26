from dataclasses import dataclass
from typing import Dict, Any, Optional

from graphql import ExecutionResult
from multidict import CIMultiDictProxy


@dataclass(frozen=True)
class GQLResponse:
    result: Dict[str, Any] | ExecutionResult
    headers: Optional[CIMultiDictProxy[str]]
