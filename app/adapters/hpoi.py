from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class HpoiAdapter(SearchAdapter):
    site_name = "hpoi"
    base_url = "https://www.hpoi.net"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            follow_redirects=True,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(f"{self.base_url}/search", params={"keyword": query})
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SearchResult] = []
        for item in soup.select("li.media.ibox-content")[:limit]:
            title_link = item.select_one("h4.media-heading a")
            image = item.select_one("img.list-item-img")
            if not title_link:
                continue
            href = title_link.get("href", "")
            external_id = href.strip("/").split("/")[-1]
            labels = [node.get_text(strip=True) for node in item.select(".label.label-tag")]
            results.append(
                SearchResult(
                    external_id=external_id,
                    source_site=self.site_name,
                    item_type="figure",
                    title=title_link.get_text(" ", strip=True),
                    subtitle=" / ".join(labels[:3]) if labels else None,
                    preview_url=(image.get("data-src") or image.get("src")) if image else None,
                    original_url=urljoin(self.base_url, href),
                    source_url=urljoin(self.base_url, href),
                    tags=labels[1:8] if len(labels) > 1 else labels[:8],
                    meta={
                        "labels": labels,
                        "category": labels[0] if labels else None,
                        "maker": labels[1] if len(labels) > 1 else None,
                    },
                    raw={"href": href, "labels": labels},
                )
            )
        return results
