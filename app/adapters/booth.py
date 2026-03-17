from __future__ import annotations

from urllib.parse import quote, urljoin
import re

from bs4 import BeautifulSoup
import httpx

from app.adapters.base import SearchAdapter
from app.config import settings
from app.search_types import SearchResult


class BoothAdapter(SearchAdapter):
    site_name = "booth"
    base_url = "https://booth.pm"

    async def search(self, query: str, limit: int = 12) -> list[SearchResult]:
        search_path = f"/en/search/{quote(query.strip(), safe='')}"
        async with httpx.AsyncClient(
            timeout=settings.site_request_timeout_seconds,
            follow_redirects=True,
            trust_env=settings.http_trust_env,
        ) as client:
            response = await client.get(urljoin(self.base_url, search_path))
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results: list[SearchResult] = []
        for card in soup.select("li.item-card")[:limit]:
            title_link = card.select_one(".item-card__title a[href]")
            preview_link = card.select_one(".item-card__thumbnail-image")
            shop_link = card.select_one(".item-card__shop-name-anchor")
            category_link = card.select_one(".item-card__category-anchor")
            if not title_link:
                continue

            href = title_link.get("href", "")
            external_id = (card.get("data-product-id") or href.rstrip("/").split("/")[-1]).strip()
            preview_url = self._preview_url(preview_link)
            category = category_link.get_text(" ", strip=True) if category_link else None
            event_name = self._text(card.select_one(".eventname-flag__name"))
            shop_name = self._text(card.select_one(".item-card__shop-name"))
            badge_names = [
                image.get("alt", "").strip()
                for image in card.select(".l-item-card-badge img[alt]")
                if image.get("alt", "").strip()
            ]
            tags = [tag for tag in [category, event_name, *badge_names] if tag]
            price = card.get("data-product-price")
            results.append(
                SearchResult(
                    external_id=external_id,
                    source_site=self.site_name,
                    item_type="model",
                    title=title_link.get_text(" ", strip=True),
                    subtitle=shop_name,
                    preview_url=preview_url,
                    original_url=preview_url,
                    source_url=urljoin(self.base_url, href),
                    tags=tags[:12],
                    meta={
                        "category": category,
                        "shop": shop_name,
                        "event": event_name,
                        "price": price,
                    },
                    raw={
                        "href": href,
                        "price": price,
                        "category": category,
                        "shop_name": shop_name,
                        "event_name": event_name,
                        "badge_names": badge_names,
                    },
                )
            )
        return results

    def _preview_url(self, node) -> str | None:
        if not node:
            return None
        direct = node.get("data-original")
        if direct:
            return direct
        style = node.get("style", "")
        match = re.search(r"url\((['\"]?)(.+?)\1\)", style)
        return match.group(2) if match else None

    def _text(self, node) -> str | None:
        if not node:
            return None
        value = node.get_text(" ", strip=True)
        return value or None
