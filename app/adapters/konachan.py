from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class KonachanAdapter(SearchAdapter):
    site_name = "konachan"
    base_url = "https://konachan.com"
    user_agent = "CharaSeed/0.1 (public search)"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            headers={"User-Agent": self.user_agent},
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(f"{self.base_url}/post.json", params={"tags": query, "limit": limit})
            if response.status_code == 403 and "Just a moment" in response.text[:256]:
                raise RuntimeError("Konachan 当前需要浏览器验证，后端公开搜索暂不可用")
            response.raise_for_status()
            posts = response.json()

        results: list[SearchResult] = []
        for post in posts:
            title = post.get("tags", "").split()[:2]
            results.append(
                SearchResult(
                    external_id=str(post["id"]),
                    source_site=self.site_name,
                    item_type="image",
                    title=" / ".join(title) or f"Konachan #{post['id']}",
                    subtitle=post.get("rating"),
                    preview_url=post.get("sample_url") or post.get("jpeg_url") or post.get("preview_url"),
                    original_url=post.get("file_url") or post.get("jpeg_url"),
                    source_url=f"{self.base_url}/post/show/{post['id']}",
                    tags=(post.get("tags", "") or "").split()[:24],
                    meta={
                        "rating": post.get("rating"),
                        "score": post.get("score"),
                        "dimensions": f"{post.get('width')}x{post.get('height')}",
                    },
                    raw=post,
                )
            )
        return results
