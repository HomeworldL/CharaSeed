from __future__ import annotations

import asyncio
from collections import defaultdict, deque
import random
import re
import time
from typing import Any

from sqlalchemy.orm import Session

from app.search_types import SearchResult
from app.services.catalog import discovery_profile
from app.services.search import search_service
from app.site_profiles import SITE_ORDER, SITE_PROFILES


RECENT_EXPOSURES: dict[int, deque[str]] = defaultdict(lambda: deque(maxlen=160))


def _rng_for(*parts: object) -> random.Random:
    seed = "|".join(str(part) for part in parts)
    return random.Random(seed)


def _seed_weights(profile: dict[str, list[str]]) -> dict[str, int]:
    weights: dict[str, int] = defaultdict(int)
    for index, query in enumerate(profile["recent_searches"][:6]):
        weights[query] += 7 - index
    for index, name in enumerate(profile["top_characters"][:6]):
        weights[name] += 7 - index
    for index, name in enumerate(profile["top_works"][:5]):
        weights[name] += 6 - index
    for index, name in enumerate(profile["top_tags"][:6]):
        weights[name] += 4 - index
    for index, name in enumerate(profile["top_artists"][:4]):
        weights[name] += 3 - index
    return dict(sorted(weights.items(), key=lambda item: item[1], reverse=True))


def _fallback_profile() -> dict[str, list[str]]:
    return {
        "recent_searches": ["初音未来", "Asuna", "Genshin Impact"],
        "top_tags": ["白发", "长发", "制服"],
        "top_characters": ["初音未来", "Asuna"],
        "top_works": ["Genshin Impact", "Sword Art Online"],
        "top_artists": [],
        "preferred_sites": ["danbooru", "zerochan", "hpoi"],
    }


def _mixed_home_sites() -> list[str]:
    return [site for site in SITE_ORDER if SITE_PROFILES.get(site, {}).get("supports_mixed_home")]


def _has_cjk(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)


def _normalize_booru_query(query: str) -> str | None:
    cleaned = query.strip().lower()
    if not cleaned or _has_cjk(cleaned):
        return None
    if any(token in cleaned for token in ("figure", "model", "toy", "merch", "goods")):
        return None
    tokens = re.findall(r"[a-z0-9_()]+", cleaned)
    if not tokens or len(tokens) > 4:
        return None
    if len(tokens) > 1 and all("_" not in token for token in tokens):
        return "_".join(tokens)
    return " ".join(tokens)


def _normalize_query_for_site(site: str, query: str) -> str | None:
    stripped = query.strip()
    if not stripped:
        return None
    if site in {"danbooru", "yandere", "konachan"}:
        return _normalize_booru_query(stripped)
    return stripped


def _queries_for_site(site: str, profile: dict[str, list[str]], refresh_token: str) -> list[str]:
    rng = _rng_for(site, refresh_token, time.strftime("%Y-%m-%d"))
    weighted = _seed_weights(profile)
    ordered = list(weighted)
    if not ordered:
        ordered = SITE_PROFILES[site]["examples"][:]
    rng.shuffle(ordered)
    picks: list[str] = []
    seen: set[str] = set()
    candidates = ordered + SITE_PROFILES[site]["examples"]
    for value in candidates:
        normalized = _normalize_query_for_site(site, value)
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        picks.append(normalized)
        if len(picks) >= 3:
            break
    return picks[:3]


def _exposure_penalty(owner_id: int, result: SearchResult) -> int:
    key = f"{result.source_site}:{result.external_id}"
    recent = RECENT_EXPOSURES[owner_id]
    return sum(1 for item in recent if item == key) * 4


def _mark_exposures(owner_id: int, results: list[SearchResult]) -> None:
    recent = RECENT_EXPOSURES[owner_id]
    for result in results:
        recent.appendleft(f"{result.source_site}:{result.external_id}")


def _score_result(result: SearchResult, profile: dict[str, list[str]], owner_id: int, refresh_token: str) -> tuple[int, list[str]]:
    haystack = " ".join(
        [
            result.title or "",
            result.subtitle or "",
            " ".join(result.tags),
            str(result.meta.get("character") or ""),
            str(result.meta.get("copyright") or ""),
            str(result.meta.get("artist") or ""),
            str(result.meta.get("primary_tag") or ""),
            str(result.meta.get("maker") or ""),
            " ".join(result.meta.get("labels", [])),
        ]
    ).lower()
    rng = _rng_for(owner_id, refresh_token, result.source_site, result.external_id)
    score = rng.randint(0, 6)
    reasons: list[str] = []

    for label, bonus in (
        ("top_characters", 6),
        ("top_works", 5),
        ("top_tags", 3),
        ("recent_searches", 4),
        ("top_artists", 3),
    ):
        for signal in profile[label][:4]:
            if signal.lower() in haystack:
                score += bonus
                reasons.append(signal)
                break

    if result.source_site in profile["preferred_sites"][:2]:
        score += 2
    if result.source_site == "hpoi" and result.item_type == "figure":
        score += 2

    score -= _exposure_penalty(owner_id, result)

    if not reasons:
        reasons.append(SITE_PROFILES[result.source_site]["label"])
    return score, reasons[:3]


def _dedupe_results(results: list[SearchResult]) -> list[SearchResult]:
    seen: set[tuple[str, str]] = set()
    unique: list[SearchResult] = []
    for result in results:
        key = (result.source_site, result.external_id)
        if key in seen:
            continue
        seen.add(key)
        unique.append(result)
    return unique


def _diversify_ranked_results(results: list[SearchResult], limit: int) -> list[SearchResult]:
    ordered = sorted(results, key=lambda item: item.meta.get("feed_score", 0), reverse=True)
    diversified: list[SearchResult] = []
    seen: set[tuple[str, str]] = set()
    for site in _mixed_home_sites():
        top = next((result for result in ordered if result.source_site == site), None)
        if not top:
            continue
        key = (top.source_site, top.external_id)
        if key in seen:
            continue
        diversified.append(top)
        seen.add(key)
        if len(diversified) >= limit:
            return diversified
    for result in ordered:
        key = (result.source_site, result.external_id)
        if key in seen:
            continue
        diversified.append(result)
        seen.add(key)
        if len(diversified) >= limit:
            break
    return diversified


async def build_site_feed(
    session: Session,
    owner_id: int,
    site: str,
    *,
    refresh_token: str,
    limit: int = 8,
    force_refresh: bool = False,
    mark_exposure: bool = True,
) -> dict[str, Any]:
    profile = discovery_profile(session, owner_id)
    if not any(profile.values()):
        profile = _fallback_profile()

    queries = _queries_for_site(site, profile, refresh_token)
    if not queries:
        queries = [
            normalized
            for normalized in (_normalize_query_for_site(site, example) for example in SITE_PROFILES[site]["examples"])
            if normalized
        ][:2]

    per_query_limit = min(limit, max(6, (limit // max(len(queries), 1)) + 4))
    tasks = [
        search_service.search_site(site, query, limit=per_query_limit, force_refresh=force_refresh)
        for query in queries
    ]
    responses = await asyncio.gather(*tasks)

    gathered: list[SearchResult] = []
    errors: list[str] = []
    for results, error in responses:
        if error:
            if error not in errors:
                errors.append(error)
            continue
        gathered.extend(results)

    results = _dedupe_results(gathered)
    for result in results:
        feed_score, feed_reason = _score_result(result, profile, owner_id, refresh_token)
        result.meta["feed_score"] = feed_score
        result.meta["feed_reason"] = feed_reason

    ranked = sorted(results, key=lambda item: item.meta.get("feed_score", 0), reverse=True)[:limit]
    if mark_exposure:
        _mark_exposures(owner_id, ranked)
    return {
        "site": site,
        "queries": queries,
        "results": ranked,
        "errors": errors,
    }


async def build_mixed_feed(
    session: Session,
    owner_id: int,
    *,
    refresh_token: str,
    limit: int = 12,
    force_refresh: bool = False,
) -> dict[str, Any]:
    active_sites = _mixed_home_sites()
    per_site_limit = min(limit, max(4, (limit // max(len(active_sites), 1)) + 3))
    tasks = [
        build_site_feed(
            session,
            owner_id,
            site,
            refresh_token=f"{refresh_token}:{site}",
            limit=per_site_limit,
            force_refresh=force_refresh,
            mark_exposure=False,
        )
        for site in active_sites
    ]
    responses = await asyncio.gather(*tasks)

    combined: list[SearchResult] = []
    errors: dict[str, list[str]] = {}
    for feed in responses:
        combined.extend(feed["results"])
        if feed["errors"]:
            errors[feed["site"]] = feed["errors"]

    unique = [
        result
        for result in _dedupe_results(combined)
        if result.meta.get("site_notice") != "browser-challenge"
    ]
    ranked = _diversify_ranked_results(unique, limit)
    _mark_exposures(owner_id, ranked)
    return {
        "site": "all",
        "queries": [],
        "results": ranked,
        "errors": errors,
    }
