# CharaSeed MVP Design

## Goal
Build the first usable version of a personal anime collection site that supports real multi-source search, unified preview, local collecting, lightweight organization, and detail editing.

## Approved Architecture
- Stack: FastAPI + SQLite + Jinja templates + HTMX
- Modules:
  - `web` for pages and fragments
  - `api` for reusable JSON endpoints
  - `adapters` for source-specific search integration
  - `domain` for collect, dedupe, organize, and filtering logic
  - `storage` for SQLAlchemy models and persistence
- Deployment target: local single-user, with multi-user expansion preserved by schema shape

## Approved Data Model
### Core tables
- `users`
- `items`
- `item_assets`
- `entities`
- `item_entities`
- `tags`
- `item_tags`

### Future-ready tables
- `search_saved_queries`
- `item_links`

### Modeling principles
- `items` are the canonical collected object
- `entities` are user-curated theme pages like character and work
- `tags` stay lightweight and flexible
- dedupe is based on `(source_site, source_id)`, `source_url`, and derived `dedupe_key`

## Approved Information Architecture
### Pages
- `/discover`: search, preview, collect
- `/library`: browse and filter collected items
- `/entities`: theme index
- `/entities/{id}`: theme detail
- `/items/{id}`: item detail and editing
- `/items/new`: manual add

### Interaction surfaces
- result preview modal
- collect/edit form modal

## Approved API Shape
### Search
- `GET /api/search`
- `GET /api/search/preview`

### Items
- `GET /api/items`
- `POST /api/items`
- `GET /api/items/{id}`
- `PATCH /api/items/{id}`

### Entities
- `GET /api/entities`
- `POST /api/entities`
- `GET /api/entities/{id}`
- `PATCH /api/entities/{id}`
- `POST /api/entities/resolve`

### Tags
- `GET /api/tags`
- `POST /api/tags/resolve`

## Implementation Decision
Implement the MVP with real adapters for:
- Danbooru
- Safebooru
- Zerochan
- Hpoi

Adapter strategy:
- Danbooru and Safebooru use public JSON endpoints
- Zerochan uses a custom user-agent and API/HTML fallback
- Hpoi uses public HTML search parsing
- each adapter failure is isolated and returned as partial source failure

## Explicit Non-Goals
- user accounts
- social/community features
- subscriptions and scheduled crawling
- local asset downloading
- recommendation system
- heavy graph modeling

## Delivery Target
The first coded version must let the user:
- search across supported sources
- preview results
- collect an item into the local database
- add tags, rating, and character/work links
- browse and filter the collection
- open theme pages
- edit an item and follow the original source
