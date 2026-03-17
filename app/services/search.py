from __future__ import annotations

import asyncio
from copy import deepcopy
import time

from app.config import settings
from app.adapters.anilist import AniListAdapter
from app.adapters.bangumi import BangumiAdapter
from app.adapters.danbooru import DanbooruAdapter
from app.adapters.hpoi import HpoiAdapter
from app.adapters.safebooru import SafebooruAdapter
from app.adapters.sketchfab import SketchfabAdapter
from app.adapters.yandere import YandereAdapter
from app.adapters.zerochan import ZerochanAdapter
from app.search_types import SearchResponse, SearchResult
from app.site_profiles import SITE_PROFILES, SITE_REGISTRY


class SearchService:
    def __init__(self) -> None:
        self.adapters = {
            "danbooru": DanbooruAdapter(),
            "safebooru": SafebooruAdapter(),
            "zerochan": ZerochanAdapter(),
            "hpoi": HpoiAdapter(),
            "yandere": YandereAdapter(),
            "bangumi": BangumiAdapter(),
            "anilist": AniListAdapter(),
            "sketchfab": SketchfabAdapter(),
        }
        self._cache: dict[tuple[str, str, int], tuple[float, list[SearchResult]]] = {}

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

    async def search_site(
        self,
        site: str,
        query: str,
        *,
        limit: int = 8,
        force_refresh: bool = False,
    ) -> tuple[list[SearchResult], str | None]:
        _site, results, error = await self._search_site(site, query, limit, force_refresh=force_refresh)
        return results, error

    async def _search_site(
        self,
        site: str,
        query: str,
        limit: int,
        *,
        force_refresh: bool = False,
    ) -> tuple[str, list[SearchResult], str | None]:
        profile = SITE_REGISTRY.get(site)
        if profile and not profile.get("is_available", False):
            return site, [], profile.get("status_note") or "当前后端暂未接通"
        cache_key = (site, query.strip().lower(), limit)
        if not force_refresh:
            cached = self._cache.get(cache_key)
            if cached and (time.monotonic() - cached[0]) <= settings.search_cache_ttl_seconds:
                return site, deepcopy(cached[1]), None
        try:
            results = await asyncio.wait_for(
                self.adapters[site].search(query, limit=limit),
                timeout=settings.site_request_timeout_seconds + 0.5,
            )
            self._cache[cache_key] = (time.monotonic(), deepcopy(results))
            return site, results, None
        except Exception as exc:  # noqa: BLE001
            return site, [], str(exc)


search_service = SearchService()
site_profiles = SITE_PROFILES
