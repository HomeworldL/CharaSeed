from __future__ import annotations

import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


ANILIST_QUERY = """
query ($search: String, $perPage: Int) {
  Page(perPage: $perPage) {
    media(search: $search, type: ANIME) {
      id
      siteUrl
      title {
        romaji
        english
        native
      }
      coverImage {
        large
        medium
      }
      genres
      averageScore
      format
      status
    }
  }
}
"""


class AniListAdapter(SearchAdapter):
    site_name = "anilist"
    base_url = "https://graphql.anilist.co"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.post(
                self.base_url,
                json={"query": ANILIST_QUERY, "variables": {"search": query, "perPage": limit}},
            )
            response.raise_for_status()
            payload = response.json()

        media_list = payload.get("data", {}).get("Page", {}).get("media", [])
        results: list[SearchResult] = []
        for media in media_list:
            title = media.get("title") or {}
            label = title.get("english") or title.get("romaji") or title.get("native") or f"AniList #{media['id']}"
            alt_title = title.get("native") or title.get("romaji") or title.get("english")
            results.append(
                SearchResult(
                    external_id=str(media["id"]),
                    source_site=self.site_name,
                    item_type="anime",
                    title=label,
                    subtitle=alt_title if alt_title != label else None,
                    preview_url=(media.get("coverImage") or {}).get("large") or (media.get("coverImage") or {}).get("medium"),
                    original_url=(media.get("coverImage") or {}).get("large"),
                    source_url=media.get("siteUrl") or f"https://anilist.co/anime/{media['id']}",
                    tags=(media.get("genres") or [])[:10],
                    meta={
                        "score": media.get("averageScore"),
                        "format": media.get("format"),
                        "status": media.get("status"),
                    },
                    raw=media,
                )
            )
        return results
