# CharaSeed Agent Guide

## Product
- CharaSeed is a personal anime collection hub centered on discovery, visual preview, collecting, and lightweight organization.
- The core object is a unified `item` that can represent `image`, `figure`, or `entry`.
- First priority is a usable single-user local app. Data shapes must stay ready for future multi-user Web/App expansion.

## Stack
- Backend: FastAPI
- Storage: SQLite + SQLAlchemy
- UI: Jinja templates with HTMX and light Alpine/vanilla JS behavior
- Search: source adapters that normalize public site results into one internal model

## Current MVP Scope
- Multi-source search across Danbooru, Safebooru, Zerochan, and Hpoi
- Unified result cards with preview
- Collect into local library with tags, rating, status, character, and work links
- Browse library with filtering
- Theme/entity pages
- Item detail editing and source preview

## Constraints
- Prefer stable public endpoints or publicly accessible HTML pages
- Do not download original assets in the MVP
- Keep adapter failures isolated so one source outage does not break the page
- Keep schema light; avoid heavy knowledge-graph modeling

## Engineering Notes
- Treat `items` as the center of the model
- Keep source-specific parsing inside `app/adapters/`
- Preserve JSON API compatibility even when adding server-rendered pages
- Leave `owner_id` in core tables even if the MVP uses one default user
