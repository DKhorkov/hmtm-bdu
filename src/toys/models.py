from dataclasses import dataclass
from typing import List, Optional


@dataclass
class UserForToyCard:
    display_name: str
    avatar: str


@dataclass
class MasterForToyCard:
    id: int
    user: UserForToyCard


@dataclass
class ToyCategory:
    name: str


@dataclass
class ToyTags:
    name: str


@dataclass
class ToyAttachments:
    link: str


@dataclass
class BaseToyModel:
    id: str
    category: ToyCategory
    name: str
    description: str
    price: float
    quantity: int
    created_at: str
    tags: List[ToyTags]
    attachments: List[ToyAttachments]


@dataclass
class ToyForCatalog(BaseToyModel):
    pass


@dataclass
class ToyForCard(BaseToyModel):
    master: MasterForToyCard


@dataclass
class ToyFilters:
    search: Optional[str]
    price_ceil: Optional[float]
    price_floor: Optional[float]
    quantity_floor: Optional[int]
    category_ids: Optional[List[int]]
    tag_ids: Optional[List[int]]
    created_at_order_by_asc: Optional[bool]
