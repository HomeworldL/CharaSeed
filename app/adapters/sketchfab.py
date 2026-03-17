from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class SketchfabAdapter(SearchAdapter):
    site_name = "sketchfab"
    base_url = "https://api.sketchfab.com/v3"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(
                f"{self.base_url}/search",
                params={"type": "models", "q": query, "count": limit},
            )
            response.raise_for_status()
            payload = response.json()

        results: list[SearchResult] = []
        for model in payload.get("results", []):
            thumbnails = (model.get("thumbnails") or {}).get("images", [])
            preview = self._pick_thumbnail(thumbnails)
            tags = [tag.get("name") for tag in model.get("tags", []) if tag.get("name")]
            categories = [category.get("name") for category in model.get("categories", []) if category.get("name")]
            results.append(
                SearchResult(
                    external_id=model["uid"],
                    source_site=self.site_name,
                    item_type="model",
                    title=model.get("name") or f"Sketchfab {model['uid']}",
                    subtitle=(model.get("user") or {}).get("displayName") or (model.get("user") or {}).get("username"),
                    preview_url=preview,
                    original_url=preview,
                    source_url=model.get("viewerUrl") or model.get("embedUrl") or model.get("uri"),
                    tags=(tags + categories)[:16],
                    meta={
                        "face_count": model.get("faceCount"),
                        "vertex_count": model.get("vertexCount"),
                        "likes": model.get("likeCount"),
                    },
                    raw=model,
                )
            )
        return results

    def _pick_thumbnail(self, thumbnails: list[dict]) -> str | None:
        if not thumbnails:
            return None
        ordered = sorted(thumbnails, key=lambda item: (item.get("width") or 0, item.get("height") or 0), reverse=True)
        for thumb in ordered:
            if (thumb.get("width") or 0) >= 700:
                return thumb.get("url")
        return ordered[0].get("url")
