from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    external_id: str
    source_site: str
    item_type: str
    title: str
    subtitle: str | None
    preview_url: str | None
    original_url: str | None
    source_url: str
    tags: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    results: list[SearchResult]
    errors: dict[str, str]
