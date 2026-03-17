from __future__ import annotations

import asyncio
from collections import defaultdict, deque
import random
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
        lowered = value.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        picks.append(value)
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


def build_feed_shell(session: Session, owner_id: int, refresh_token: str | None = None) -> dict[str, Any]:
    profile = discovery_profile(session, owner_id)
    if not any(profile.values()):
        profile = _fallback_profile()

    refresh_token = refresh_token or str(time.time_ns())
    seeds = _seed_weights(profile)
    headline = list(seeds)[:3]
    if not headline:
        summary = "今天先从你近期可能感兴趣的角色、作品和模型候选开始。"
    elif len(headline) == 1:
        summary = f"今天更偏向 {headline[0]} 附近的内容。"
    elif len(headline) == 2:
        summary = f"今天更偏向 {headline[0]} 和 {headline[1]} 附近的内容。"
    else:
        summary = f"今天更偏向 {headline[0]}、{headline[1]} 和 {headline[2]} 附近的内容。"

    shuffled_sites = SITE_ORDER[:]
    _rng_for(owner_id, refresh_token).shuffle(shuffled_sites)
    return {
        "summary": summary,
        "signals": list(seeds)[:6],
        "refresh_token": refresh_token,
        "site_order": shuffled_sites,
    }


async def build_site_feed(
    session: Session,
    owner_id: int,
    site: str,
    *,
    refresh_token: str,
    limit: int = 8,
    force_refresh: bool = False,
) -> dict[str, Any]:
    profile = discovery_profile(session, owner_id)
    if not any(profile.values()):
        profile = _fallback_profile()

    queries = _queries_for_site(site, profile, refresh_token)
    if not queries:
        queries = SITE_PROFILES[site]["examples"][:2]

    tasks = [
        search_service.search_site(site, query, limit=max(3, min(limit, 6)), force_refresh=force_refresh)
        for query in queries
    ]
    responses = await asyncio.gather(*tasks)

    gathered: list[SearchResult] = []
    errors: list[str] = []
    for results, error in responses:
        if error:
            errors.append(error)
            continue
        gathered.extend(results)

    results = _dedupe_results(gathered)
    for result in results:
        feed_score, feed_reason = _score_result(result, profile, owner_id, refresh_token)
        result.meta["feed_score"] = feed_score
        result.meta["feed_reason"] = feed_reason

    ranked = sorted(results, key=lambda item: item.meta.get("feed_score", 0), reverse=True)[:limit]
    _mark_exposures(owner_id, ranked)
    return {
        "site": site,
        "queries": queries,
        "results": ranked,
        "errors": errors,
    }
