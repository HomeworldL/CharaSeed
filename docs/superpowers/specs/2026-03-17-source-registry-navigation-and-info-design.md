# CharaSeed Source Registry, Layered Navigation, And Info Page Design

## Goal
- Register all current and TODO sources in one unified source registry.
- Redesign homepage and discover page around source groups and site buttons.
- Add an info page that acts as an internal navigation and external reference directory.

## Approved Scope

### Source Registry
- Every current source and every TODO source must exist in one registry.
- Registry fields include:
  - source group
  - label and descriptions
  - example queries
  - search/home support flags
  - current availability
  - status note for limited sources
  - external links such as homepage, API docs, or references
- Searchable sources work immediately through adapters.
- Limited sources still appear in navigation and info views with clear feedback.

### Discover Page
- Discover uses a two-level source selector:
  - left rail for source groups
  - right button row for sites in the active group
- Search remains single-site search.
- The `all` group shows all registered sites but not a synthetic `All` search mode.

### Homepage
- Homepage uses grouped navigation with expansion behavior.
- Top row shows group buttons such as `所有站点`, `图片站点`, `手办站点`, `动画站点`, `3D站点`.
- The active group expands its site buttons below.
- `所有站点` keeps the synthetic `All` homepage feed button.
- Available sources can power homepage mixed feed; unavailable sources only show explicit errors when selected.

### Info Page
- Add a new top-level navigation entry named `资讯`.
- The page lists:
  - internal pages
  - grouped external sources
  - API / developer docs
  - GitHub / reference repositories
- Each item shows a one-line description and link set.

## Implementation Notes
- Existing profiles should be derived from the registry instead of maintained separately.
- Search service should short-circuit unavailable sources with their status note.
- Homepage mixed feed should only use sources marked available for mixed feed.
- Templates should render grouped navigation from registry data instead of hardcoded button lists.

## Validation
- Verify `/home`, `/discover`, and `/info` all render with grouped navigation.
- Verify unavailable TODO sources show clear feedback instead of silent failure.
- Verify available sources still search correctly.
- Run tests and route sanity checks.
