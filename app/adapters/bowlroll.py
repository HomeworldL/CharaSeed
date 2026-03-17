from __future__ import annotations

from urllib.parse import urljoin

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class BowlRollAdapter(SearchAdapter):
    site_name = "bowlroll"
    base_url = "https://bowlroll.net"
    api_url = f"{base_url}/api/file/search-by-keyword-files"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(
                self.api_url,
                params={"word": query, "page": 1},
            )
            response.raise_for_status()
            payload = response.json()

        results: list[SearchResult] = []
        for file_item in payload.get("files", [])[:limit]:
            file_id = file_item.get("id")
            if not file_id:
                continue
            restrictions = self._restrictions(file_item.get("download_control") or {})
            subtitle = file_item.get("user_name") or None
            results.append(
                SearchResult(
                    external_id=str(file_id),
                    source_site=self.site_name,
                    item_type="model",
                    title=file_item.get("title") or f"BowlRoll #{file_id}",
                    subtitle=subtitle,
                    preview_url=file_item.get("thumbnail"),
                    original_url=file_item.get("thumbnail"),
                    source_url=urljoin(self.base_url, f"/file/{file_id}"),
                    tags=restrictions[:8],
                    meta={
                        "uploader": subtitle,
                        "upload_at": file_item.get("upload_at"),
                        "download_count": file_item.get("download_count"),
                    },
                    raw=file_item,
                )
            )
        return results

    def _restrictions(self, control: dict) -> list[str]:
        tags: list[str] = []
        if control.get("auth_check"):
            tags.append("需认证")
        if control.get("public_check"):
            tags.append("公开")
        if control.get("download_key"):
            tags.append("需提取码")
        if control.get("expire_datetime"):
            tags.append("限时")
        return tags
