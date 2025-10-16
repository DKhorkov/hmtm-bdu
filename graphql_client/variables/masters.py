from dataclasses import dataclass
from typing import Dict, Any

from src.domains.masters.core.models import MastersFilters


@dataclass(frozen=True)
class MastersCatalogVariables:
    limit: int
    offset: int
    filters: MastersFilters

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        return {
            "input": {
                "pagination": {
                    "limit": self.limit,
                    "offset": self.offset,
                },
                "filters": {
                    "search": self.filters.search,
                    "createdAtOrderByAsc": self.filters.created_at_order_by_asc,
                }
            }
        }


@dataclass(frozen=True)
class MasterCounterVariables:
    filters: MastersFilters

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filters": {
                "search": self.filters.search,
                "createdAtOrderByAsc": self.filters.created_at_order_by_asc,
            }
        }
