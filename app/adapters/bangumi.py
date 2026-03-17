from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class BangumiAdapter(SearchAdapter):
    site_name = "bangumi"
    base_url = "https://api.bgm.tv"
    user_agent = "CharaSeed/0.1 (public search)"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            headers={"User-Agent": self.user_agent},
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(f"{self.base_url}/search/subject/{query}", params={"type": 2})
            response.raise_for_status()
            payload = response.json()

        results: list[SearchResult] = []
        for item in (payload.get("list") or [])[:limit]:
            images = item.get("images") or {}
            title = item.get("name_cn") or item.get("name") or f"Bangumi #{item['id']}"
            subtitle = item.get("name") if item.get("name") and item.get("name") != title else None
            results.append(
                SearchResult(
                    external_id=str(item["id"]),
                    source_site=self.site_name,
                    item_type="anime",
                    title=title,
                    subtitle=subtitle,
                    preview_url=images.get("large") or images.get("common") or images.get("medium"),
                    original_url=images.get("large") or images.get("common"),
                    source_url=item.get("url") or f"https://bgm.tv/subject/{item['id']}",
                    tags=["动画", "Bangumi"],
                    meta={
                        "air_date": item.get("air_date"),
                    },
                    raw=item,
                )
            )
        return results
