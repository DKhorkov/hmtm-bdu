from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from multidict import CIMultiDictProxy


@dataclass
class GQLResponse:
    result: Dict[str, Any] = field(default_factory=dict)
    headers: Optional[CIMultiDictProxy[str]] = None
    error: Optional[Any] = None
