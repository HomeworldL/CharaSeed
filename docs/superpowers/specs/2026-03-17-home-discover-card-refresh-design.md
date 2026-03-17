# CharaSeed Home / Discover UI Refresh Design

## Goal
- Simplify the homepage into a single site-switched feed.
- Remove oversized explanatory blocks from homepage and discover page.
- Make result cards visually consistent even when source metadata length varies.
- Add a direct `conda + python` local startup path to the README.

## Approved Scope

### Homepage
- Remove the current `Today Feed` title, signal chips, and separate site detail panel.
- Replace the top area with a compact toolbar:
  - left: source site switch buttons
  - right: `刷新主页候选` and `进入搜索页`
- Keep a single result container below the toolbar.
- Initial load fetches the default site's home candidates.
- Switching site buttons reloads the shared result container for that site.
- Refresh reloads the currently active site only.

### Discover
- Remove the large `Discover` hero card.
- Keep the search form, site switcher, description, and example chips.
- Reduce the visual weight of site guidance so search remains the primary focus.

### Result Cards
- Use one unified card layout for homepage feed and search results.
- Clamp titles to two lines.
- Clamp secondary tag text to two lines.
- Remove unstable long-form details such as dimensions, score, and feed reasons.
- Keep one stable object-type chip derived from `item_type` such as `图片`, `手办`, or fallback type labels.
- Keep `预览` and `归档收藏` pinned to the card bottom.

### Media Strategy
- This change only standardizes frontend presentation.
- Do not add image proxying, downloading, processing, or caching.
- Use a fixed media frame with consistent aspect ratio and cropping behavior so cards stay visually stable.
- Leave source-specific preview URL upgrades for later work.

### Documentation
- Add `conda` setup and startup commands to the README.
- Keep `uv` instructions available as an alternative path.

## Implementation Notes
- Reuse a shared partial for result cards to avoid homepage and search drift.
- Keep existing search and collect routes intact.
- Prefer minimal route changes: adapt homepage feed fragments instead of introducing a new page flow.

## Validation
- Run the existing test suite.
- Verify homepage site switching still loads HTMX results.
- Verify discover page site switching still updates helper copy and example chips.
