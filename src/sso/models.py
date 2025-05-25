from dataclasses import dataclass
from typing import Optional, Dict, List


@dataclass
class User:
    id: str
    display_name: str
    email: str
    email_confirmed: bool
    phone: Optional[str]
    phone_confirmed: bool
    telegram: Optional[str]
    telegram_confirmed: bool
    avatar: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class Master:
    id: int
    info: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class UserInfo:
    id: str
    display_name: str
    email: str
    phone: Optional[str]
    telegram: Optional[str]
    avatar: Optional[str]
    created_at: str


@dataclass
class Toy:
    id: int
    master: Dict[str, Dict[str, str]]  # {"master": {"id": ..., user{"id": ..., ...}, ...}}
    category: Dict[str, str]  # {"name": ..., ...}
    name: str
    description: str
    price: float
    quantity: int
    created_at: str
    tags: List[Dict[str, str]]  # [{"name" : ...}, {"name": ...}, ...]
    attachments: List[Dict[str, str]]


@dataclass
class Categories:
    id: int
    name: str


@dataclass
class ToysFilters:
    search: Optional[str]
    price_ceil: Optional[float]
    price_floor: Optional[float]
    quantity_floor: Optional[int]
    category_id: Optional[int]
    tags_id: Optional[List[int]]
    created_at_order_by_asc: Optional[bool]
