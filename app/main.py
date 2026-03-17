from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, SessionLocal, engine, get_session
from app.models import Entity
from app.services.catalog import (
    create_or_update_item,
    default_user,
    get_entity,
    get_item,
    grouped_entities,
    init_database,
    list_items,
    list_tags,
    payload_from_json,
    related_items,
    serialize_entity,
    serialize_item,
    slugify,
    split_tokens,
)
from app.services.search import search_service


BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def bootstrap_storage() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        init_database(session)


bootstrap_storage()


@app.on_event("startup")
def on_startup() -> None:
    bootstrap_storage()


@app.get("/", response_class=HTMLResponse)
def root() -> RedirectResponse:
    return RedirectResponse(url="/discover", status_code=302)


@app.get("/discover", response_class=HTMLResponse)
def discover(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "discover.html",
        {
            "request": request,
            "query": "",
            "results": [],
            "errors": {},
            "selected_sites": ["danbooru", "safebooru", "zerochan", "hpoi"],
            "selected_types": [],
        },
    )


@app.get("/fragments/search-results", response_class=HTMLResponse)
async def search_results_fragment(
    request: Request,
    q: str = Query(..., min_length=1),
    sites: list[str] | None = Query(default=None),
    item_types: list[str] | None = Query(default=None),
) -> HTMLResponse:
    search_response = await search_service.search(q, sites=sites, item_types=item_types, limit_per_site=8)
    return templates.TemplateResponse(
        "partials/search_results.html",
        {
            "request": request,
            "results": search_response.results,
            "errors": search_response.errors,
            "query": q,
        },
    )


@app.get("/fragments/item-preview", response_class=HTMLResponse)
def item_preview_fragment(
    request: Request,
    source_site: str,
    external_id: str,
    item_type: str,
    title: str,
    source_url: str,
    preview_url: str | None = None,
    original_url: str | None = None,
    subtitle: str | None = None,
    tags_text: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        "partials/item_preview.html",
        {
            "request": request,
            "result": {
                "source_site": source_site,
                "external_id": external_id,
                "item_type": item_type,
                "title": title,
                "source_url": source_url,
                "preview_url": preview_url,
                "original_url": original_url,
                "subtitle": subtitle,
                "tags_text": tags_text or "",
            }
        },
    )


@app.get("/fragments/collect-form", response_class=HTMLResponse)
def collect_form_fragment(
    request: Request,
    source_site: str,
    external_id: str,
    item_type: str,
    title: str,
    source_url: str,
    preview_url: str | None = None,
    original_url: str | None = None,
    subtitle: str | None = None,
    tags_text: str | None = None,
) -> HTMLResponse:
    payload = {
        "source_site": source_site,
        "source_id": external_id,
        "item_type": item_type,
        "title": title,
        "source_url": source_url,
        "preview_url": preview_url,
        "original_url": original_url,
        "subtitle": subtitle,
        "tags_text": tags_text or "",
    }
    return templates.TemplateResponse("partials/collect_form.html", {"request": request, "payload": payload})


@app.post("/items/create")
def create_item_from_form(
    request: Request,
    source_site: str = Form(default="manual"),
    source_id: str | None = Form(default=None),
    item_type: str = Form(default="image"),
    title: str = Form(...),
    subtitle: str | None = Form(default=None),
    description: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    preview_url: str | None = Form(default=None),
    original_url: str | None = Form(default=None),
    status: str = Form(default="collected"),
    rating: int | None = Form(default=None),
    tags_text: str | None = Form(default=None),
    character_names: str | None = Form(default=None),
    work_names: str | None = Form(default=None),
    original_names: str | None = Form(default=None),
    artist_names: str | None = Form(default=None),
    source_payload_json: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> Response:
    owner = default_user(session)
    payload = payload_from_json(
        {
            "source_site": source_site,
            "source_id": source_id,
            "item_type": item_type,
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "source_url": source_url,
            "preview_url": preview_url,
            "original_url": original_url,
            "status": status,
            "rating": rating,
            "tags_text": tags_text,
            "character_names": character_names,
            "work_names": work_names,
            "original_names": original_names,
            "artist_names": artist_names,
            "source_payload_json": source_payload_json,
        }
    )
    item = create_or_update_item(session, owner.id, payload)
    if request.headers.get("HX-Request") == "true":
        response = Response(status_code=204)
        response.headers["HX-Redirect"] = f"/items/{item.id}"
        return response
    return RedirectResponse(url=f"/items/{item.id}", status_code=303)


@app.get("/items/new", response_class=HTMLResponse)
def manual_new_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("manual_new.html", {"request": request})


@app.get("/library", response_class=HTMLResponse)
def library_page(
    request: Request,
    q: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    rating_gte: int | None = None,
    source_site: str | None = None,
    tag: str | None = None,
    character: str | None = None,
    work: str | None = None,
    sort: str = "recent",
    view: str = "grid",
    session: Session = Depends(get_session),
) -> HTMLResponse:
    owner = default_user(session)
    items = list_items(
        session,
        owner.id,
        query=q,
        item_type=item_type,
        status=status,
        rating_gte=rating_gte,
        source_site=source_site,
        tag=tag,
        character=character,
        work=work,
        sort=sort,
    )
    stats = {
        "total": len(items),
        "images": len([item for item in items if item.item_type == "image"]),
        "figures": len([item for item in items if item.item_type == "figure"]),
        "entries": len([item for item in items if item.item_type == "entry"]),
    }
    return templates.TemplateResponse(
        "library.html",
        {"request": request, "items": items, "stats": stats, "filters": request.query_params, "view": view},
    )


@app.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail_page(
    request: Request,
    item_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    owner = default_user(session)
    item = get_item(session, owner.id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return templates.TemplateResponse(
        "item_detail.html",
        {
            "request": request,
            "item": item,
            "related": related_items(session, owner.id, item),
            "character_names": ", ".join(
                link.entity.name for link in item.item_entities if link.entity.entity_type == "character"
            ),
            "work_names": ", ".join(
                link.entity.name for link in item.item_entities if link.entity.entity_type == "work"
            ),
            "original_names": ", ".join(
                link.entity.name for link in item.item_entities if link.entity.entity_type == "original"
            ),
            "artist_names": ", ".join(
                link.entity.name for link in item.item_entities if link.entity.entity_type == "artist"
            ),
            "tags_text": ", ".join(link.tag.name for link in item.item_tags),
        },
    )


@app.post("/items/{item_id}/edit")
def edit_item(
    item_id: int,
    source_site: str = Form(default="manual"),
    source_id: str | None = Form(default=None),
    item_type: str = Form(default="image"),
    title: str = Form(...),
    subtitle: str | None = Form(default=None),
    description: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    preview_url: str | None = Form(default=None),
    original_url: str | None = Form(default=None),
    status: str = Form(default="collected"),
    rating: int | None = Form(default=None),
    tags_text: str | None = Form(default=None),
    character_names: str | None = Form(default=None),
    work_names: str | None = Form(default=None),
    original_names: str | None = Form(default=None),
    artist_names: str | None = Form(default=None),
    session: Session = Depends(get_session),
) -> RedirectResponse:
    owner = default_user(session)
    current = get_item(session, owner.id, item_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Item not found")
    payload = {
        "source_site": source_site,
        "source_id": source_id,
        "item_type": item_type,
        "title": title,
        "subtitle": subtitle,
        "description": description,
        "source_url": source_url,
        "preview_url": preview_url,
        "original_url": original_url,
        "status": status,
        "rating": rating,
        "tags_text": tags_text,
        "character_names": character_names,
        "work_names": work_names,
        "original_names": original_names,
        "artist_names": artist_names,
    }
    payload["source_site"] = payload["source_site"] or current.source_site
    payload["source_id"] = payload["source_id"] or current.source_id
    item = create_or_update_item(session, owner.id, payload)
    return RedirectResponse(url=f"/items/{item.id}", status_code=303)


@app.get("/entities", response_class=HTMLResponse)
def entities_page(request: Request, session: Session = Depends(get_session)) -> HTMLResponse:
    owner = default_user(session)
    groups = grouped_entities(session, owner.id)
    return templates.TemplateResponse("entities.html", {"request": request, "groups": groups})


@app.get("/entities/{entity_id}", response_class=HTMLResponse)
def entity_detail_page(
    request: Request,
    entity_id: int,
    session: Session = Depends(get_session),
) -> HTMLResponse:
    owner = default_user(session)
    entity = get_entity(session, owner.id, entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    items = [link.item for link in entity.item_entities if link.item]
    return templates.TemplateResponse("entity_detail.html", {"request": request, "entity": entity, "items": items})


@app.get("/api/search", response_class=JSONResponse)
async def api_search(
    q: str,
    sites: list[str] | None = Query(default=None),
    item_types: list[str] | None = Query(default=None),
) -> JSONResponse:
    response = await search_service.search(q, sites=sites, item_types=item_types, limit_per_site=8)
    return JSONResponse(
        {
            "query": q,
            "results": [result.__dict__ for result in response.results],
            "errors": response.errors,
        }
    )


@app.get("/api/items", response_class=JSONResponse)
def api_items(
    q: str | None = None,
    item_type: str | None = None,
    status: str | None = None,
    rating_gte: int | None = None,
    source_site: str | None = None,
    tag: str | None = None,
    character: str | None = None,
    work: str | None = None,
    sort: str = "recent",
    session: Session = Depends(get_session),
) -> JSONResponse:
    owner = default_user(session)
    items = list_items(
        session,
        owner.id,
        query=q,
        item_type=item_type,
        status=status,
        rating_gte=rating_gte,
        source_site=source_site,
        tag=tag,
        character=character,
        work=work,
        sort=sort,
    )
    return JSONResponse({"items": [serialize_item(item) for item in items]})


@app.post("/api/items", response_class=JSONResponse)
async def api_create_item(request: Request, session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    payload = payload_from_json(await request.json())
    item = create_or_update_item(session, owner.id, payload)
    return JSONResponse(serialize_item(item), status_code=201)


@app.get("/api/items/{item_id}", response_class=JSONResponse)
def api_get_item(item_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    item = get_item(session, owner.id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return JSONResponse(serialize_item(item))


@app.patch("/api/items/{item_id}", response_class=JSONResponse)
async def api_patch_item(item_id: int, request: Request, session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    current = get_item(session, owner.id, item_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Item not found")
    payload = serialize_item(current)
    payload.update(payload_from_json(await request.json()))
    payload["tags_text"] = ", ".join(payload.get("tags", [])) if isinstance(payload.get("tags"), list) else payload.get("tags_text")
    if isinstance(payload.get("entities"), list):
        payload["character_names"] = ", ".join(entity["name"] for entity in payload["entities"] if entity["entity_type"] == "character")
        payload["work_names"] = ", ".join(entity["name"] for entity in payload["entities"] if entity["entity_type"] == "work")
    item = create_or_update_item(session, owner.id, payload)
    return JSONResponse(serialize_item(item))


@app.get("/api/entities", response_class=JSONResponse)
def api_entities(session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    groups = grouped_entities(session, owner.id)
    return JSONResponse(
        {
            entity_type: [
                {"count": entry["count"], **serialize_entity(entry["entity"])}
                for entry in entries
            ]
            for entity_type, entries in groups.items()
        }
    )


@app.post("/api/entities", response_class=JSONResponse)
async def api_create_entity(request: Request, session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    data = await request.json()
    entity = Entity(
        owner_id=owner.id,
        entity_type=data["entity_type"],
        name=data["name"],
        slug=slugify(data["name"]),
        description=data.get("description"),
        cover_image_url=data.get("cover_image_url"),
    )
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return JSONResponse(serialize_entity(entity), status_code=201)


@app.get("/api/entities/{entity_id}", response_class=JSONResponse)
def api_get_entity(entity_id: int, session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    entity = get_entity(session, owner.id, entity_id)
    if entity is None:
        raise HTTPException(status_code=404, detail="Entity not found")
    return JSONResponse(
        {
            **serialize_entity(entity),
            "items": [serialize_item(link.item) for link in entity.item_entities if link.item],
        }
    )


@app.post("/api/entities/resolve", response_class=JSONResponse)
async def api_resolve_entity(request: Request, session: Session = Depends(get_session)) -> JSONResponse:
    from app.services.catalog import get_or_create_entity

    owner = default_user(session)
    data = await request.json()
    names = split_tokens(data.get("name"))
    resolved = [serialize_entity(get_or_create_entity(session, owner.id, data["entity_type"], name)) for name in names]
    session.commit()
    return JSONResponse({"entities": resolved})


@app.get("/api/tags", response_class=JSONResponse)
def api_tags(q: str | None = None, session: Session = Depends(get_session)) -> JSONResponse:
    owner = default_user(session)
    tags = list_tags(session, owner.id, q)
    return JSONResponse({"tags": [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in tags]})


@app.post("/api/tags/resolve", response_class=JSONResponse)
async def api_resolve_tags(request: Request, session: Session = Depends(get_session)) -> JSONResponse:
    from app.services.catalog import get_or_create_tag

    owner = default_user(session)
    data = await request.json()
    tags = [get_or_create_tag(session, owner.id, name) for name in split_tokens(data.get("name"))]
    session.commit()
    return JSONResponse({"tags": [{"id": tag.id, "name": tag.name, "slug": tag.slug} for tag in tags]})
