from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class MyFigureCollectionAdapter(SearchAdapter):
    site_name = "myfigurecollection"
    base_url = "https://myfigurecollection.net"
    user_agent = "CharaSeed/0.1 (public search)"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(f"{self.base_url}/browse.v4.php", params={"keywords": query, "rootId": 0})
            if response.status_code == 403 and "Just a moment" in response.text[:512]:
                raise RuntimeError("MyFigureCollection 当前触发浏览器验证，后端公开搜索暂不可用")
            response.raise_for_status()

        return [
            SearchResult(
                external_id=f"search:{quote_plus(query)}",
                source_site=self.site_name,
                item_type="figure",
                title=f"MyFigureCollection 搜索：{query}",
                subtitle="当前站点需要浏览器验证",
                preview_url=None,
                original_url=None,
                source_url=f"{self.base_url}/browse.v4.php?keywords={quote_plus(query)}&rootId=0",
                tags=["手办", "收藏社区", "浏览器验证"],
                meta={"site_notice": "browser-challenge"},
                raw={},
            )
        ]
