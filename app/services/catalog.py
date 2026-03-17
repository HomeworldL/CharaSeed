from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import Entity, Item, ItemAsset, ItemEntity, ItemTag, SearchEvent, Tag, User


ITEM_LOAD_OPTIONS = (
    joinedload(Item.assets),
    joinedload(Item.item_entities).joinedload(ItemEntity.entity),
    joinedload(Item.item_tags).joinedload(ItemTag.tag),
)


def init_database(session: Session) -> None:
    default_user = session.scalar(select(User).where(User.username == "local"))
    if default_user is None:
        session.add(User(username="local", display_name="Local Collector"))
        session.commit()


def record_search_event(session: Session, owner_id: int, query: str, selected_site: str) -> None:
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        return
    latest = session.scalar(
        select(SearchEvent)
        .where(SearchEvent.owner_id == owner_id)
        .order_by(SearchEvent.created_at.desc())
        .limit(1)
    )
    if latest and latest.query == cleaned_query and latest.selected_site == selected_site:
        return
    session.add(SearchEvent(owner_id=owner_id, query=cleaned_query, selected_site=selected_site))
    session.commit()


def default_user(session: Session) -> User:
    user = session.scalar(select(User).where(User.username == "local"))
    if user is None:
        init_database(session)
        user = session.scalar(select(User).where(User.username == "local"))
    assert user is not None
    return user


def slugify(value: str) -> str:
    lowered = value.strip().lower()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", lowered)
    return slug.strip("-") or "untitled"


def split_tokens(value: str | None) -> list[str]:
    if not value:
        return []
    tokens = re.split(r"[,;\n]+", value)
    return [token.strip() for token in tokens if token.strip()]


def dedupe_key_for_payload(payload: dict[str, Any]) -> str | None:
    source_site = payload.get("source_site")
    source_id = payload.get("source_id")
    source_url = payload.get("source_url")
    original_url = payload.get("original_url")
    preview_url = payload.get("preview_url")
    if source_site and source_id:
        return f"{source_site}:{source_id}"
    if source_url:
        return source_url
    if original_url or preview_url:
        digest = hashlib.sha1(f"{payload.get('title','')}|{original_url or preview_url}".encode()).hexdigest()
        return f"hash:{digest}"
    return None


def clean_payload(payload: dict[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str):
            stripped = value.strip()
            cleaned[key] = stripped or None
        else:
            cleaned[key] = value
    if cleaned.get("title"):
        cleaned["title"] = str(cleaned["title"])
    if cleaned.get("item_type"):
        cleaned["item_type"] = str(cleaned["item_type"])
    return cleaned


def get_or_create_tag(session: Session, owner_id: int, name: str) -> Tag:
    slug = slugify(name)
    tag = session.scalar(select(Tag).where(Tag.owner_id == owner_id, Tag.slug == slug))
    if tag:
        return tag
    tag = Tag(owner_id=owner_id, name=name.strip(), slug=slug)
    session.add(tag)
    session.flush()
    return tag


def get_or_create_entity(session: Session, owner_id: int, entity_type: str, name: str) -> Entity:
    slug = slugify(name)
    entity = session.scalar(
        select(Entity).where(
            Entity.owner_id == owner_id,
            Entity.entity_type == entity_type,
            Entity.slug == slug,
        )
    )
    if entity:
        return entity
    entity = Entity(owner_id=owner_id, entity_type=entity_type, name=name.strip(), slug=slug)
    session.add(entity)
    session.flush()
    return entity


def create_or_update_item(session: Session, owner_id: int, payload: dict[str, Any]) -> Item:
    payload = clean_payload(payload)
    dedupe_key = dedupe_key_for_payload(payload)
    item = None

    if payload.get("source_site") and payload.get("source_id"):
        item = session.scalar(
            select(Item).where(
                Item.owner_id == owner_id,
                Item.source_site == payload["source_site"],
                Item.source_id == payload["source_id"],
            )
        )
    if item is None and payload.get("source_url"):
        item = session.scalar(
            select(Item).where(Item.owner_id == owner_id, Item.source_url == payload["source_url"])
        )
    if item is None and dedupe_key:
        item = session.scalar(select(Item).where(Item.owner_id == owner_id, Item.dedupe_key == dedupe_key))

    if item is None:
        item = Item(owner_id=owner_id, item_type=payload["item_type"], title=payload["title"])
        session.add(item)
        session.flush()

    item.item_type = payload["item_type"]
    item.title = payload["title"]
    item.subtitle = payload.get("subtitle")
    item.description = payload.get("description")
    item.source_site = payload.get("source_site")
    item.source_id = payload.get("source_id")
    item.source_url = payload.get("source_url")
    item.preview_url = payload.get("preview_url")
    item.original_url = payload.get("original_url")
    item.status = payload.get("status") or "collected"
    item.rating = int(payload["rating"]) if payload.get("rating") else None
    item.dedupe_key = dedupe_key
    item.source_payload_json = payload.get("source_payload_json")

    item.assets.clear()
    for index, url in enumerate(_asset_urls(payload)):
        item.assets.append(ItemAsset(asset_type="image" if index else "preview", url=url, sort_order=index))

    item.item_tags.clear()
    for name in split_tokens(payload.get("tags_text")):
        tag = get_or_create_tag(session, owner_id, name)
        item.item_tags.append(ItemTag(tag=tag))

    item.item_entities.clear()
    for entity_type, relation_type, raw_names in (
        ("character", "primary", payload.get("character_names")),
        ("work", "related", payload.get("work_names")),
        ("original", "related", payload.get("original_names")),
        ("artist", "related", payload.get("artist_names")),
    ):
        for name in split_tokens(raw_names):
            entity = get_or_create_entity(session, owner_id, entity_type, name)
            if not entity.cover_image_url and payload.get("preview_url"):
                entity.cover_image_url = payload["preview_url"]
            item.item_entities.append(ItemEntity(entity=entity, relation_type=relation_type))

    session.commit()
    session.refresh(item)
    return session.scalar(select(Item).options(*ITEM_LOAD_OPTIONS).where(Item.id == item.id)) or item


def _asset_urls(payload: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for candidate in (payload.get("preview_url"), payload.get("original_url")):
        if candidate and candidate not in urls:
            urls.append(candidate)
    return urls


def list_items(
    session: Session,
    owner_id: int,
    *,
    query: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    rating_gte: int | None = None,
    source_site: str | None = None,
    tag: str | None = None,
    character: str | None = None,
    work: str | None = None,
    sort: str = "recent",
) -> list[Item]:
    stmt: Select[tuple[Item]] = select(Item).options(*ITEM_LOAD_OPTIONS).where(Item.owner_id == owner_id)

    if query:
        like = f"%{query}%"
        stmt = stmt.where(or_(Item.title.ilike(like), Item.subtitle.ilike(like), Item.description.ilike(like)))
    if item_type:
        stmt = stmt.where(Item.item_type == item_type)
    if status:
        stmt = stmt.where(Item.status == status)
    if rating_gte:
        stmt = stmt.where(Item.rating >= rating_gte)
    if source_site:
        stmt = stmt.where(Item.source_site == source_site)
    if tag:
        stmt = stmt.join(Item.item_tags).join(ItemTag.tag).where(Tag.slug == slugify(tag))
    if character:
        stmt = stmt.join(Item.item_entities).join(ItemEntity.entity).where(
            Entity.entity_type == "character",
            Entity.slug == slugify(character),
        )
    if work:
        stmt = stmt.join(Item.item_entities).join(ItemEntity.entity).where(
            Entity.entity_type == "work",
            Entity.slug == slugify(work),
        )

    stmt = stmt.distinct()

    if sort == "rating":
        stmt = stmt.order_by(Item.rating.desc().nullslast(), Item.collected_at.desc())
    elif sort == "updated":
        stmt = stmt.order_by(Item.updated_at.desc())
    else:
        stmt = stmt.order_by(Item.collected_at.desc())

    return list(session.scalars(stmt).unique())


def get_item(session: Session, owner_id: int, item_id: int) -> Item | None:
    stmt = select(Item).options(*ITEM_LOAD_OPTIONS).where(Item.owner_id == owner_id, Item.id == item_id)
    return session.scalar(stmt)


def grouped_entities(session: Session, owner_id: int) -> dict[str, list[dict[str, Any]]]:
    stmt = (
        select(Entity, func.count(ItemEntity.id))
        .outerjoin(Entity.item_entities)
        .where(Entity.owner_id == owner_id)
        .group_by(Entity.id)
        .order_by(Entity.entity_type, Entity.name)
    )
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entity, count in session.execute(stmt):
        groups[entity.entity_type].append({"entity": entity, "count": count})
    return groups


def get_entity(session: Session, owner_id: int, entity_id: int) -> Entity | None:
    stmt = (
        select(Entity)
        .options(selectinload(Entity.item_entities).selectinload(ItemEntity.item).joinedload(Item.assets))
        .where(Entity.owner_id == owner_id, Entity.id == entity_id)
    )
    return session.scalar(stmt)


def list_tags(session: Session, owner_id: int, query: str | None = None) -> list[Tag]:
    stmt = select(Tag).where(Tag.owner_id == owner_id).order_by(Tag.name)
    if query:
        stmt = stmt.where(Tag.name.ilike(f"%{query}%"))
    return list(session.scalars(stmt).unique())


def recent_search_queries(session: Session, owner_id: int, limit: int = 12) -> list[str]:
    stmt = (
        select(SearchEvent.query)
        .where(SearchEvent.owner_id == owner_id)
        .order_by(SearchEvent.created_at.desc())
        .limit(limit * 3)
    )
    seen: set[str] = set()
    results: list[str] = []
    for query in session.scalars(stmt):
        lowered = query.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        results.append(query)
        if len(results) >= limit:
            break
    return results


def discovery_profile(session: Session, owner_id: int) -> dict[str, list[str]]:
    recent_searches = recent_search_queries(session, owner_id, limit=8)

    top_tags_stmt = (
        select(Tag.name, func.count(ItemTag.id).label("weight"))
        .join(ItemTag, Tag.id == ItemTag.tag_id)
        .join(Item, Item.id == ItemTag.item_id)
        .where(Item.owner_id == owner_id)
        .group_by(Tag.id)
        .order_by(func.count(ItemTag.id).desc(), Tag.name.asc())
        .limit(8)
    )
    top_entity_stmt = (
        select(Entity.entity_type, Entity.name, func.count(ItemEntity.id).label("weight"))
        .join(ItemEntity, Entity.id == ItemEntity.entity_id)
        .join(Item, Item.id == ItemEntity.item_id)
        .where(Item.owner_id == owner_id)
        .group_by(Entity.id)
        .order_by(func.count(ItemEntity.id).desc(), Entity.name.asc())
        .limit(24)
    )
    source_stmt = (
        select(Item.source_site, func.count(Item.id).label("weight"))
        .where(Item.owner_id == owner_id, Item.source_site.is_not(None))
        .group_by(Item.source_site)
        .order_by(func.count(Item.id).desc())
        .limit(4)
    )

    characters: list[str] = []
    works: list[str] = []
    artists: list[str] = []
    for entity_type, name, _weight in session.execute(top_entity_stmt):
        if entity_type == "character" and len(characters) < 5:
            characters.append(name)
        elif entity_type == "work" and len(works) < 5:
            works.append(name)
        elif entity_type == "artist" and len(artists) < 4:
            artists.append(name)

    return {
        "recent_searches": recent_searches,
        "top_tags": [name for name, _weight in session.execute(top_tags_stmt)],
        "top_characters": characters,
        "top_works": works,
        "top_artists": artists,
        "preferred_sites": [site for site, _weight in session.execute(source_stmt) if site],
    }


def related_items(session: Session, owner_id: int, item: Item, limit: int = 6) -> list[Item]:
    entity_ids = [link.entity_id for link in item.item_entities]
    tag_ids = [link.tag_id for link in item.item_tags]
    if not entity_ids and not tag_ids:
        return []

    stmt = select(Item).options(*ITEM_LOAD_OPTIONS).where(Item.owner_id == owner_id, Item.id != item.id)
    clauses = []
    if entity_ids:
        clauses.append(Item.id.in_(select(ItemEntity.item_id).where(ItemEntity.entity_id.in_(entity_ids))))
    if tag_ids:
        clauses.append(Item.id.in_(select(ItemTag.item_id).where(ItemTag.tag_id.in_(tag_ids))))
    stmt = stmt.where(or_(*clauses)).order_by(Item.collected_at.desc()).limit(limit)
    return list(session.scalars(stmt).unique())


def serialize_item(item: Item) -> dict[str, Any]:
    return {
        "id": item.id,
        "item_type": item.item_type,
        "title": item.title,
        "subtitle": item.subtitle,
        "description": item.description,
        "source_site": item.source_site,
        "source_id": item.source_id,
        "source_url": item.source_url,
        "preview_url": item.preview_url,
        "original_url": item.original_url,
        "status": item.status,
        "rating": item.rating,
        "tags": [link.tag.name for link in item.item_tags],
        "entities": [
            {"id": link.entity.id, "name": link.entity.name, "entity_type": link.entity.entity_type}
            for link in item.item_entities
        ],
        "assets": [asset.url for asset in item.assets],
        "source_payload_json": item.source_payload_json,
    }


def serialize_entity(entity: Entity) -> dict[str, Any]:
    return {
        "id": entity.id,
        "entity_type": entity.entity_type,
        "name": entity.name,
        "slug": entity.slug,
        "description": entity.description,
        "cover_image_url": entity.cover_image_url,
    }


def payload_from_json(data: dict[str, Any]) -> dict[str, Any]:
    payload = dict(data)
    raw_payload = payload.get("source_payload_json") or payload.get("source_payload")
    if isinstance(raw_payload, str):
        payload["source_payload_json"] = json.loads(raw_payload) if raw_payload.strip() else None
    elif raw_payload is not None:
        payload["source_payload_json"] = raw_payload
    return payload
