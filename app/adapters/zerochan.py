from __future__ import annotations

from urllib.parse import quote_plus, urljoin

from bs4 import BeautifulSoup
import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class ZerochanAdapter(SearchAdapter):
    site_name = "zerochan"
    base_url = "https://www.zerochan.net"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        headers = {"User-Agent": settings.zerochan_user_agent}
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            headers=headers,
            follow_redirects=True,
            trust_env=False,
        ) as client:
            direct_json = await client.get(f"{self.base_url}/{quote_plus(query)}", params={"json": "", "l": limit})
            content_type = direct_json.headers.get("content-type", "")
            if "application/json" in content_type:
                return self._parse_json_results(direct_json.json())

            search_page = await client.get(f"{self.base_url}/search", params={"q": query})
            search_page.raise_for_status()
            soup = BeautifulSoup(search_page.text, "html.parser")

            alt_json = soup.select_one('link[rel="alternate"][type="application/json"]')
            if alt_json and alt_json.get("href"):
                json_response = await client.get(urljoin(self.base_url, alt_json["href"]))
                json_response.raise_for_status()
                return self._parse_json_results(json_response.json())

            return self._parse_html_results(soup, limit)

    def _parse_json_results(self, payload: dict) -> list[SearchResult]:
        results: list[SearchResult] = []
        for item in payload.get("items", []):
            tag_name = item.get("tag") or "Zerochan"
            results.append(
                SearchResult(
                    external_id=str(item["id"]),
                    source_site=self.site_name,
                    item_type="image",
                    title=tag_name,
                    subtitle=item.get("source"),
                    preview_url=item.get("thumbnail"),
                    original_url=item.get("source"),
                    source_url=f"{self.base_url}/{item['id']}",
                    tags=item.get("tags", [])[:24],
                    meta={"dimensions": f"{item.get('width')}x{item.get('height')}"},
                    raw=item,
                )
            )
        return results

    def _parse_html_results(self, soup: BeautifulSoup, limit: int) -> list[SearchResult]:
        results: list[SearchResult] = []
        for thumb in soup.select("#thumbs li")[:limit]:
            link = thumb.select_one("a")
            image = thumb.select_one("img")
            if not link or not image:
                continue
            href = link.get("href", "")
            external_id = href.strip("/").split(".")[0] or href.strip("/")
            results.append(
                SearchResult(
                    external_id=str(external_id),
                    source_site=self.site_name,
                    item_type="image",
                    title=image.get("alt") or f"Zerochan {external_id}",
                    subtitle=None,
                    preview_url=image.get("src"),
                    original_url=image.get("src"),
                    source_url=urljoin(self.base_url, href),
                    tags=[],
                    meta={},
                    raw={"href": href},
                )
            )
        return results
