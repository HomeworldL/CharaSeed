# CharaSeed TODO

## Priority Tracks

### 1. Performance, Recommendation Quality, and UX Corrections
- Improve today-feed recommendation quality so refreshes are not effectively identical.
- Speed up homepage refresh and search requests.
- Review request strategy for local proxy interaction and avoid unnecessary waiting on slow sources.
- Use clearer preview images instead of overly blurry thumbnails when the source provides better preview variants.
- Align preview / collect / action controls consistently across cards.
- Autofill character, work, artist, maker, and related metadata during collect whenever source data already contains them.
- Add delete support for collected items.
- Replace item status labels with Chinese labels in the UI.
- Remove the standalone `新增条目` page and move manual entry into the library page.
- Remove the current homepage explanatory block that feels redundant.
- Ensure library filters are fully implemented and applied correctly.

### 2. Image Source Expansion
- Pixiv
- Gelbooru
- Konachan
- Yande.re
- E-shuushuu
- MiniTokyo

### 3. Figure, Anime, and 3D Source Expansion
- Figure sources:
  - AmiAmi
  - MyFigureCollection
- Anime sources:
  - Bangumi
  - MyAnimeList
  - AniList
  - AniDB
- 3D / asset sources:
  - Sketchfab
  - BOOTH
  - BowlRoll
  - aPlayBox / 模之屋

### 4. External Collection Import
- Add a library import flow for pulling a logged-in user's collection/favorites from external sites.
- Design the import flow around cookies / authenticated sessions, mapping, dedupe, and source-specific import adapters.
