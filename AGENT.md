# CharaSeed Agent Reference

## Project Status
CharaSeed is currently a single-user local anime collection hub built around:
- a dedicated homepage `/home` with a real-time today feed
- a separate search page `/discover`
- a unified collection model centered on `items`
- collection, editing, tagging, entity grouping, and source preview

## Current Implemented Features
- Homepage:
  - mixed today-feed waterfall
  - refreshable homepage candidate feed
  - per-site expansion panels for supported sources
- Search:
  - site-aware search UI with button switching
  - natural-language search flow without hard `image / figure / entry` search restriction in the UI
  - source-specific helper text and result-detail rendering
- Collection:
  - collect from search results
  - manual item creation
  - item detail editing
  - tags, rating, status, character/work/original/artist linking
- Organization:
  - library page
  - entity pages
  - related-item display
- Data and APIs:
  - SQLite persistence
  - JSON APIs for search, items, entities, and tags
  - search history recording for recommendation input

## Current Supported Sources
- Danbooru
- Safebooru
- Zerochan
- Hpoi

## Code Framework

### App Structure
- `app/main.py`
  - FastAPI entrypoint
  - page routes
  - fragment routes
  - JSON API routes
- `app/models.py`
  - SQLAlchemy models
  - users, items, entities, tags, search events
- `app/db.py`
  - engine, session, base model setup
- `app/adapters/`
  - one source adapter per site
  - isolates parsing and source-specific request behavior
- `app/services/catalog.py`
  - core item creation, update, entity/tag linking, search-history recording
- `app/services/search.py`
  - adapter orchestration and cross-site search aggregation
- `app/services/feed.py`
  - today-feed generation logic
- `app/site_profiles.py`
  - site-level UI copy and search semantics
- `app/templates/`
  - Jinja pages and HTMX partials
- `app/static/styles.css`
  - shared visual system and page styling

### Architectural Principles
- `items` remain the core object.
- Source-specific behavior stays inside adapters.
- UI pages can be server-rendered, but core actions should remain API-compatible.
- The schema remains single-user in operation but multi-user ready in shape.

## Reference Documents
- Product brief:
  - [anime_collection_product_brief.md](/home/ccs/repositories/CharaSeed/anime_collection_product_brief.md)
- Current design spec:
  - [2026-03-17-anime-collection-mvp-design.md](/home/ccs/repositories/CharaSeed/docs/superpowers/specs/2026-03-17-anime-collection-mvp-design.md)
- Next-work backlog:
  - [TODO.md](/home/ccs/repositories/CharaSeed/TODO.md)

## Working Guidance
- Prefer expanding adapters incrementally rather than mixing source logic into pages.
- Keep homepage and search page distinct in purpose:
  - `/home` is for discovery and recommendation
  - `/discover` is for explicit search
- When changing recommendation behavior, update both feed logic and the spec/TODO if the scope changes.
- When adding new sources, document each source's query semantics before shipping the adapter.
