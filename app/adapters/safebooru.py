from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class SafebooruAdapter(SearchAdapter):
    site_name = "safebooru"
    base_url = "https://safebooru.org"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(
                f"{self.base_url}/index.php",
                params={"page": "dapi", "s": "post", "q": "index", "json": 1, "tags": query, "limit": limit},
            )
            response.raise_for_status()
            posts = response.json()

        results: list[SearchResult] = []
        for post in posts:
            results.append(
                SearchResult(
                    external_id=str(post["id"]),
                    source_site=self.site_name,
                    item_type="image",
                    title=f"Safebooru #{post['id']}",
                    subtitle=post.get("rating"),
                    preview_url=post.get("sample_url") or post.get("file_url") or post.get("preview_url"),
                    original_url=post.get("file_url") or post.get("sample_url"),
                    source_url=f"{self.base_url}/index.php?page=post&s=view&id={post['id']}",
                    tags=(post.get("tags", "") or "").split()[:24],
                    meta={
                        "score": post.get("score"),
                        "dimensions": f"{post.get('width')}x{post.get('height')}",
                    },
                    raw=post,
                )
            )
        return results
