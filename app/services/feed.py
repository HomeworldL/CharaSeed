from __future__ import annotations

from collections import defaultdict

from sqlalchemy.orm import Session

from app.search_types import SearchResult
from app.services.catalog import discovery_profile
from app.services.search import search_service
from app.site_profiles import SITE_ORDER, SITE_PROFILES


def _seed_weights(profile: dict[str, list[str]]) -> dict[str, int]:
    weights: dict[str, int] = defaultdict(int)
    for index, query in enumerate(profile["recent_searches"][:5]):
        weights[query] += 8 - index
    for index, name in enumerate(profile["top_characters"][:5]):
        weights[name] += 7 - index
    for index, name in enumerate(profile["top_works"][:5]):
        weights[name] += 6 - index
    for index, name in enumerate(profile["top_tags"][:6]):
        weights[name] += 4 - index
    return dict(sorted(weights.items(), key=lambda item: item[1], reverse=True))


def _queries_for_site(site: str, profile: dict[str, list[str]]) -> list[str]:
    ordered: list[str] = []
    groups = []
    if site == "hpoi":
        groups = [profile["recent_searches"], profile["top_characters"], profile["top_works"], profile["top_tags"]]
    elif site == "zerochan":
        groups = [profile["top_characters"], profile["top_works"], profile["recent_searches"]]
    else:
        groups = [profile["top_characters"], profile["top_works"], profile["top_tags"], profile["recent_searches"]]

    seen: set[str] = set()
    for group in groups:
        for value in group:
            lowered = value.lower()
            if lowered in seen:
                continue
            ordered.append(value)
            seen.add(lowered)
            if len(ordered) >= 2:
                return ordered
    return ordered


def _score_result(result: SearchResult, profile: dict[str, list[str]]) -> tuple[int, list[str]]:
    haystack = " ".join(
        [
            result.title or "",
            result.subtitle or "",
            " ".join(result.tags),
            str(result.meta.get("character") or ""),
            str(result.meta.get("copyright") or ""),
            str(result.meta.get("artist") or ""),
            str(result.meta.get("primary_tag") or ""),
            " ".join(result.meta.get("labels", [])),
        ]
    ).lower()

    score = 0
    reasons: list[str] = []

    for label, bonus in (
        ("top_characters", 5),
        ("top_works", 4),
        ("top_tags", 3),
        ("recent_searches", 4),
    ):
        for signal in profile[label][:4]:
            if signal.lower() in haystack:
                score += bonus
                reasons.append(signal)
                break

    if result.source_site in profile["preferred_sites"][:2]:
        score += 2
    if result.source_site == "hpoi" and result.item_type == "figure":
        score += 1
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


def _mix_results(site_results: dict[str, list[SearchResult]], limit: int = 18) -> list[SearchResult]:
    ordered_sites = sorted(site_results, key=lambda site: len(site_results[site]), reverse=True)
    cursors = {site: 0 for site in ordered_sites}
    mixed: list[SearchResult] = []
    while len(mixed) < limit:
        advanced = False
        for site in ordered_sites:
            cursor = cursors[site]
            if cursor >= len(site_results[site]):
                continue
            mixed.append(site_results[site][cursor])
            cursors[site] += 1
            advanced = True
            if len(mixed) >= limit:
                break
        if not advanced:
            break
    return mixed


def _summary(profile: dict[str, list[str]], seeds: dict[str, int]) -> str:
    headline = list(seeds)[:3]
    if not headline:
        return "今天先从你近期可能感兴趣的角色、作品和模型候选开始。"
    if len(headline) == 1:
        return f"今天更偏向 {headline[0]} 附近的内容。"
    if len(headline) == 2:
        return f"今天更偏向 {headline[0]} 和 {headline[1]} 附近的内容。"
    return f"今天更偏向 {headline[0]}、{headline[1]} 和 {headline[2]} 附近的内容。"


async def build_today_feed(session: Session, owner_id: int) -> dict:
    profile = discovery_profile(session, owner_id)
    seeds = _seed_weights(profile)
    if not seeds:
        profile["recent_searches"] = ["初音未来", "Asuna", "Genshin Impact"]
        seeds = _seed_weights(profile)

    site_queries = {site: _queries_for_site(site, profile) for site in SITE_ORDER}
    scored_results: dict[str, list[SearchResult]] = {}
    site_counts: dict[str, int] = {}

    for site, queries in site_queries.items():
        gathered: list[SearchResult] = []
        for query in queries:
            response = await search_service.search(query, sites=[site], limit_per_site=4)
            gathered.extend(response.results)
        deduped = _dedupe_results(gathered)
        for result in deduped:
            feed_score, feed_reason = _score_result(result, profile)
            result.meta["feed_score"] = feed_score
            result.meta["feed_reason"] = feed_reason
        scored_results[site] = sorted(deduped, key=lambda item: item.meta.get("feed_score", 0), reverse=True)
        site_counts[site] = len(scored_results[site])

    mixed_results = _mix_results(scored_results, limit=18)
    return {
        "summary": _summary(profile, seeds),
        "signals": list(seeds)[:6],
        "site_counts": site_counts,
        "site_queries": site_queries,
        "profile": profile,
        "mixed_results": mixed_results,
    }


async def build_site_feed(session: Session, owner_id: int, site: str) -> dict:
    profile = discovery_profile(session, owner_id)
    if not any(profile.values()):
        profile["recent_searches"] = ["初音未来", "Asuna", "Genshin Impact"]
    queries = _queries_for_site(site, profile) or SITE_PROFILES[site]["examples"][:2]
    gathered: list[SearchResult] = []
    for query in queries:
        response = await search_service.search(query, sites=[site], limit_per_site=8)
        gathered.extend(response.results)
    results = _dedupe_results(gathered)
    for result in results:
        feed_score, feed_reason = _score_result(result, profile)
        result.meta["feed_score"] = feed_score
        result.meta["feed_reason"] = feed_reason
    return {
        "site": site,
        "queries": queries,
        "results": sorted(results, key=lambda item: item.meta.get("feed_score", 0), reverse=True)[:12],
        "profile": profile,
    }
