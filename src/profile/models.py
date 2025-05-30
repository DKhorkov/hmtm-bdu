from dataclasses import dataclass
from typing import Optional


@dataclass
class Master:
    id: int
    info: Optional[str]
    created_at: str
    updated_at: str
