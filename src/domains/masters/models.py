from dataclasses import dataclass


@dataclass
class MasterForCatalog:
    id: int
    info: str
    created_at: str


@dataclass
class MastersFilters:
    search: str
    created_at_order_by_asc: bool
