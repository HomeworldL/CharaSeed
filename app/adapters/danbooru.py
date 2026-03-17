from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class DanbooruAdapter(SearchAdapter):
    site_name = "danbooru"
    base_url = "https://danbooru.donmai.us"
    user_agent = "CharaSeed/0.1 (public search)"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            headers={"User-Agent": self.user_agent},
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(
                f"{self.base_url}/posts.json",
                params={"tags": query, "limit": limit},
            )
            if response.status_code == 422:
                raise RuntimeError("Danbooru 查询语法不兼容，已跳过该推荐词")
            if response.status_code == 403 and "Just a moment" in response.text[:256]:
                raise RuntimeError("Danbooru 当前需要浏览器验证，后端公开搜索暂不可用")
            response.raise_for_status()
            posts = response.json()

        results: list[SearchResult] = []
        for post in posts:
            title_bits = [post.get("tag_string_character"), post.get("tag_string_copyright")]
            title = " / ".join([bit for bit in title_bits if bit]) or f"Danbooru #{post['id']}"
            results.append(
                SearchResult(
                    external_id=str(post["id"]),
                    source_site=self.site_name,
                    item_type="image",
                    title=title,
                    subtitle=post.get("tag_string_artist") or None,
                    preview_url=post.get("large_file_url") or post.get("file_url") or post.get("preview_file_url"),
                    original_url=post.get("file_url") or post.get("large_file_url"),
                    source_url=f"{self.base_url}/posts/{post['id']}",
                    tags=(post.get("tag_string", "") or "").split()[:24],
                    meta={
                        "rating": post.get("rating"),
                        "score": post.get("score"),
                        "dimensions": f"{post.get('image_width')}x{post.get('image_height')}",
                        "character": post.get("tag_string_character"),
                        "copyright": post.get("tag_string_copyright"),
                        "artist": post.get("tag_string_artist"),
                    },
                    raw=post,
                )
            )
        return results
