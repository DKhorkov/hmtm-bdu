from dataclasses import dataclass
from typing import Dict, Union, List, Any

from src.domains.toys.models import ToyFilters


@dataclass(frozen=True)
class ToysCatalogVariables:
    limit: int
    offset: int
    filters: ToyFilters

    def to_dict(self) -> Dict[str, Dict[str, Dict[str, Union[str, float, None, bool, int, List[int]]]]]:
        return {
            "input": {
                "pagination": {
                    "limit": self.limit,
                    "offset": self.offset,
                },
                "filters": {
                    "search": self.filters.search,
                    "priceCeil": self.filters.price_ceil,
                    "priceFloor": self.filters.price_floor,
                    "quantityFloor": self.filters.quantity_floor,
                    "categoryIDs": self.filters.category_ids,
                    "tagIDs": self.filters.tag_ids,
                    "createdAtOrderByAsc": self.filters.created_at_order_by_asc,
                }
            }
        }


@dataclass(frozen=True)
class ToyByIDVariables:
    id: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "id": self.id,
        }


@dataclass(frozen=True)
class ToysCounterFiltersVariables:
    filters: ToyFilters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filters": {
                "search": self.filters.search,
                "priceCeil": self.filters.price_ceil,
                "priceFloor": self.filters.price_floor,
                "quantityFloor": self.filters.quantity_floor,
                "categoryIDs": self.filters.category_ids,
                "tagIDs": self.filters.tag_ids,
                "createdAtOrderByAsc": self.filters.created_at_order_by_asc,
            }
        }
