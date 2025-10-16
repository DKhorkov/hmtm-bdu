from dataclasses import dataclass, field
from typing import Optional, Dict, List

from src.core.common.dto import BaseResponse, BoolResponse
from src.domains.toys.core.models import ToyForCatalog, ToyFilters, ToyForCard


@dataclass
class ToysCategoriesResponse(BaseResponse):
    categories: Optional[Dict[str, int | str]] = None


@dataclass
class ToysTagsResponse(BaseResponse):
    tags: Optional[Dict[str, int | str]] = None


@dataclass
class ToysCatalogResponse(ToysCategoriesResponse, ToysTagsResponse):
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    toys: List[ToyForCatalog] = field(default_factory=list)
    filters: Optional[ToyFilters] = None


@dataclass
class ToyByIDResponse(BoolResponse):
    toy: Optional[ToyForCard] = None
