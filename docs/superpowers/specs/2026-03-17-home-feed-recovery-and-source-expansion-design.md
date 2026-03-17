# CharaSeed Home Feed Recovery And Source Expansion Design

## Goal
- Restore a default homepage recommendation experience with an `All` mixed feed.
- Fix homepage single-site switching and Danbooru query failures.
- Add the first expansion batch of public sources across image, figure, anime, and 3D content.

## Approved Scope

### Homepage Feed
- Restore `All` as the default homepage mode.
- Homepage toolbar shows `All` plus individual site buttons.
- `All` mode returns one mixed feed assembled from multiple site-specific search runs.
- Single-site mode continues to use the same card layout and shared result container.
- Mixed mode degrades per site: one failing source should not blank the entire homepage.

### Query Adaptation
- Add site-aware query normalization for homepage recommendation seeds.
- Danbooru only receives safe tag-like queries.
- Seeds that obviously do not fit Danbooru tag syntax are skipped or replaced with site examples.
- Other sites keep natural-language seeds with fallback to examples if needed.

### Rendering Fixes
- Fix homepage fragment rendering so single-site results actually render cards.
- Keep the unified card partial introduced in the prior UI refresh.

### Source Expansion
- Image:
  - `Konachan`
  - `Yande.re`
- Figure:
  - `MyFigureCollection` as `figure`
- Anime:
  - `AniList` as `anime`
- 3D:
  - `Sketchfab` as `model`

### Source Boundaries
- Each new source only supports public search and normalized result cards.
- No login, import, pagination browsing, detail crawlers, or private APIs.
- All sources continue to map into the current `SearchResult` structure.

## Implementation Notes
- Extend site profiles and search service registration for the new adapters.
- Add a mixed homepage builder that reuses the current feed ranking and dedupe logic.
- Introduce a shared helper for per-site homepage seed generation and sanitization.
- Add `anime` to item type labels and relevant UI selectors.
- Keep the current discover/search route structure intact.

## Validation
- Verify `/home` loads mixed results by default.
- Verify switching homepage buttons between `All` and single sites changes output.
- Verify Danbooru no longer emits homepage 422 errors for natural-language seeds.
- Verify discover page loads each new source without server errors.
- Run tests and route sanity checks.
