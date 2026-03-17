from __future__ import annotations

import asyncio

from app.adapters.danbooru import DanbooruAdapter
from app.adapters.hpoi import HpoiAdapter
from app.adapters.safebooru import SafebooruAdapter
from app.adapters.zerochan import ZerochanAdapter
from app.search_types import SearchResponse, SearchResult
from app.site_profiles import SITE_PROFILES


class SearchService:
    def __init__(self) -> None:
        self.adapters = {
            "danbooru": DanbooruAdapter(),
            "safebooru": SafebooruAdapter(),
            "zerochan": ZerochanAdapter(),
            "hpoi": HpoiAdapter(),
        }

    async def search(
        self,
        query: str,
        sites: list[str] | None = None,
        item_types: list[str] | None = None,
        limit_per_site: int = 8,
    ) -> SearchResponse:
        active_sites = [site for site in (sites or list(self.adapters)) if site in self.adapters]
        tasks = [self._search_site(site, query, limit_per_site) for site in active_sites]
        responses = await asyncio.gather(*tasks)

        results: list[SearchResult] = []
        errors: dict[str, str] = {}
        for site, site_results, error in responses:
            if error:
                errors[site] = error
                continue
            results.extend(site_results)

        if item_types:
            results = [result for result in results if result.item_type in item_types]

        return SearchResponse(results=results, errors=errors)

    async def _search_site(self, site: str, query: str, limit: int) -> tuple[str, list[SearchResult], str | None]:
        try:
            results = await self.adapters[site].search(query, limit=limit)
            return site, results, None
        except Exception as exc:  # noqa: BLE001
            return site, [], str(exc)


search_service = SearchService()
site_profiles = SITE_PROFILES
