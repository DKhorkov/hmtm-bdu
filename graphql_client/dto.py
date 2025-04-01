from dataclasses import dataclass
from typing import Dict, Any, Optional
from multidict import CIMultiDictProxy


@dataclass(frozen=True)
class GQLResponse:
    result: Dict[str, Any]
    headers: Optional[CIMultiDictProxy[str]]
