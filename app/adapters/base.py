from __future__ import annotations

from abc import ABC, abstractmethod

from app.search_types import SearchResult


class SearchAdapter(ABC):
    site_name: str

    @abstractmethod
    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        raise NotImplementedError
