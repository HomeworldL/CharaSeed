from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class EShuushuuAdapter(SearchAdapter):
    site_name = "e_shuushuu"
    base_url = "https://e-shuushuu.net/api/v1"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(timeout=settings.site_request_timeout_seconds, trust_env=settings.http_trust_env) as client:
            tags_response = await client.get(f"{self.base_url}/tags/", params={"search": query})
            tags_response.raise_for_status()
            tags = tags_response.json().get("tags", [])

            matched_tags = [
                tag for tag in tags
                if query.lower() in (tag.get("title") or "").lower()
            ][:3]
            if not matched_tags:
                return []

            gathered: list[dict] = []
            seen_ids: set[int] = set()
            per_tag_limit = max(4, limit // len(matched_tags))
            for tag in matched_tags:
                images_response = await client.get(
                    f"{self.base_url}/images/",
                    params={"tags": tag["tag_id"], "per_page": per_tag_limit},
                )
                images_response.raise_for_status()
                for image in images_response.json().get("images", []):
                    image_id = image.get("image_id")
                    if image_id in seen_ids:
                        continue
                    seen_ids.add(image_id)
                    gathered.append(image)
                    if len(gathered) >= limit:
                        break
                if len(gathered) >= limit:
                    break

        results: list[SearchResult] = []
        for image in gathered[:limit]:
            tags = image.get("tags", [])
            title = next((tag.get("title") for tag in tags if tag.get("type_name") == "Character"), None)
            source = next((tag.get("title") for tag in tags if tag.get("type_name") == "Source"), None)
            artist = next((tag.get("title") for tag in tags if tag.get("type_name") == "Artist"), None)
            results.append(
                SearchResult(
                    external_id=str(image["image_id"]),
                    source_site=self.site_name,
                    item_type="image",
                    title=title or source or f"E-shuushuu #{image['image_id']}",
                    subtitle=artist,
                    preview_url=image.get("medium_url") or image.get("thumbnail_url"),
                    original_url=image.get("url") or image.get("medium_url"),
                    source_url=image.get("url") or f"https://e-shuushuu.net/image/{image['image_id']}/",
                    tags=[tag.get("title") for tag in tags if tag.get("title")][:16],
                    meta={
                        "dimensions": f"{image.get('width')}x{image.get('height')}",
                        "rating": image.get("rating"),
                    },
                    raw=image,
                )
            )
        return results
