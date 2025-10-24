from typing import List, Optional
from dataclasses import dataclass, field

<<<<<<<< HEAD:src/domains/masters/core/dto.py
from src.core.common.dto import BaseResponse
from src.domains.masters.core.models import MasterForCatalog, MastersFilters
========
from src.domains.masters.models import MasterForCatalog, MastersFilters
>>>>>>>> main:src/domains/masters/dto.py


@dataclass
class MastersCatalogResponse(BaseResponse):
    masters: List[MasterForCatalog] = field(default_factory=list)
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    filters: Optional[MastersFilters] = None
