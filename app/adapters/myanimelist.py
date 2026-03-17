from __future__ import annotations

import os

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class MyAnimeListAdapter(SearchAdapter):
    site_name = "myanimelist"
    official_base_url = "https://api.myanimelist.net/v2"
    jikan_base_url = "https://api.jikan.moe/v4"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        client_id = os.getenv("MAL_CLIENT_ID")
        if client_id:
            try:
                return await self._search_official(query, limit, client_id)
            except Exception:
                pass
        return await self._search_jikan(query, limit)

    async def _search_official(self, query: str, limit: int, client_id: str) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=settings.site_request_timeout_seconds, trust_env=settings.http_trust_env) as client:
            response = await client.get(
                f"{self.official_base_url}/anime",
                params={
                    "q": query,
                    "limit": limit,
                    "fields": "alternative_titles,main_picture,synopsis,genres,mean,media_type,status",
                },
                headers={"X-MAL-CLIENT-ID": client_id},
            )
            response.raise_for_status()
            payload = response.json()

        results: list[SearchResult] = []
        for item in payload.get("data", []):
            node = item.get("node") or {}
            alt = node.get("alternative_titles") or {}
            title = node.get("title") or f"MyAnimeList #{node.get('id')}"
            subtitle = alt.get("en") or alt.get("ja")
            picture = node.get("main_picture") or {}
            results.append(
                SearchResult(
                    external_id=str(node["id"]),
                    source_site=self.site_name,
                    item_type="anime",
                    title=title,
                    subtitle=subtitle if subtitle != title else None,
                    preview_url=picture.get("large") or picture.get("medium"),
                    original_url=picture.get("large") or picture.get("medium"),
                    source_url=f"https://myanimelist.net/anime/{node['id']}",
                    tags=[genre.get("name") for genre in node.get("genres", []) if genre.get("name")][:10],
                    meta={
                        "score": node.get("mean"),
                        "status": node.get("status"),
                        "format": node.get("media_type"),
                    },
                    raw=node,
                )
            )
        return results

    async def _search_jikan(self, query: str, limit: int) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=settings.site_request_timeout_seconds, trust_env=settings.http_trust_env) as client:
            response = await client.get(
                f"{self.jikan_base_url}/anime",
                params={"q": query, "limit": limit},
            )
            response.raise_for_status()
            payload = response.json()

        results: list[SearchResult] = []
        for item in payload.get("data", []):
            images = item.get("images") or {}
            webp = images.get("webp") or {}
            jpg = images.get("jpg") or {}
            title = item.get("title_english") or item.get("title") or item.get("title_japanese") or f"MAL #{item['mal_id']}"
            subtitle = item.get("title_japanese") or item.get("title")
            results.append(
                SearchResult(
                    external_id=str(item["mal_id"]),
                    source_site=self.site_name,
                    item_type="anime",
                    title=title,
                    subtitle=subtitle if subtitle != title else None,
                    preview_url=webp.get("large_image_url") or jpg.get("large_image_url") or webp.get("image_url") or jpg.get("image_url"),
                    original_url=webp.get("large_image_url") or jpg.get("large_image_url") or webp.get("image_url") or jpg.get("image_url"),
                    source_url=item.get("url") or f"https://myanimelist.net/anime/{item['mal_id']}",
                    tags=[genre.get("name") for genre in item.get("genres", []) if genre.get("name")][:10],
                    meta={
                        "score": item.get("score"),
                        "status": item.get("status"),
                        "format": item.get("type"),
                    },
                    raw=item,
                )
            )
        return results
