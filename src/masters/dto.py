from typing import List, Optional
from dataclasses import dataclass, field

from src.masters.models import MasterForCatalog, MastersFilters


@dataclass
class MastersCatalogResponse:
    masters: List[MasterForCatalog] = field(default_factory=list)
    error: Optional[str] = None
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    filters: Optional[MastersFilters] = None
