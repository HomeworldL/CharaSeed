# CharaSeed Collector Showcase UI Refresh Design

## Goal
Upgrade the current frontend into a cohesive collector-showcase interface aligned with the product brief:
- visual-first browsing
- warm personal ownership instead of admin-tool aesthetics
- consistent discovery, search, collection, and archive flows
- maintainable Jinja + HTMX implementation

## Design Direction
### Core direction
- Main style: `Otaku Atelier`
- Structural influence: `Editorial Collector`
- Interaction influence: `Motion-Driven Gallery`

### Positioning
CharaSeed should feel like a personal anime collection showroom:
- not a generic dashboard
- not a public wiki
- not a cute scrapbook toy
- not a brutalist experiment

It should feel like a curated private exhibition space for characters, works, figures, and visual taste.

## Approved Visual System
### Mood
- warm paper and display-case atmosphere
- refined collector warmth rather than playful pastel softness
- light-mode first, with tinted neutrals instead of flat gray

### Color strategy
- background: cream, paper, warm ivory
- surface tones: parchment, lacquered beige, soft panel white
- dark anchor: deep ink / blue-black for headings and active controls
- accents: coral lacquer and muted gold-apricot

### Typography
- serif display for titles and exhibit-style headings
- clean sans for body, metadata, filters, and controls
- stronger hierarchy for titles, softer metadata, lighter supporting copy

### Surface language
- reduce generic glassmorphism
- use layered showcase panels with borders, subtle gradients, and restrained shadow depth
- unify shells, cards, tags, and filters with the same collector-gallery vocabulary

### Motion
- restrained motion only
- page/section fade and rise on load
- card hover illumination and lift
- smooth state transitions for HTMX swaps and filter toggles
- support `prefers-reduced-motion`

## Approved Page Roles
### `/home`
Role: private daily exhibition hall

Purpose:
- lead with emotional discovery
- highlight today-feed as curated showcase content
- make source switching feel like moving across display sections

### `/discover`
Role: high-quality search gallery

Purpose:
- keep search efficient while reducing tool-like flatness
- turn helper content and site selectors into directional navigation cues
- make result cards feel collectible before they are collected

### `/library`
Role: personal collection cabinet

Purpose:
- maximize ownership and archive feeling
- make filters feel like a curation tray, not a backend form
- emphasize status, rating, entities, and edit affordances for owned items

### `/entities` and detail pages
Role: quiet archive and curation pages

Purpose:
- reinforce preference accumulation
- make item/entity relationships feel deliberate and organized
- shift from browsing energy to archive clarity

## Approved Component Changes
### Global shell
- redesign header into a gallery-guide bar with stronger brand block
- introduce page hero/opening sections for key pages
- tighten vertical rhythm and container hierarchy

### Card system
Unify around three related card families:
- hero cards for page openings and featured feed content
- collection cards for results and library items
- entity cards for archive/index pages

Shared improvements:
- stable image framing
- clearer metadata hierarchy
- stronger active/hover states
- consistent action layout and spacing

### Controls and filters
- redesign group/site switches as curated section toggles
- upgrade library filters to read like collector controls
- unify buttons, chips, inputs, and select elements into one control language

### Modal and detail treatment
- restyle preview and collect modals as exhibit information panels
- improve visual flow between image, metadata, and actions
- make forms easier to scan and less visually noisy

### Empty, loading, and error states
- turn system states into in-world collection language
- keep feedback calm, readable, and consistent

## Frontend UI Standards
The redesign must satisfy the project's frontend-design expectations and practical web UI norms:
- preserve the existing visual language where structure already works, but raise quality consistently
- avoid generic AI-looking gradients, glass cards, and repetitive equal-sized grids
- keep layout responsive on mobile and desktop
- maintain readable contrast in light mode
- provide visible keyboard focus states
- preserve semantic HTML and HTMX interaction reliability
- avoid layout-jitter hover effects
- avoid heavy animation dependencies
- keep touch targets usable and controls visually clear

## Implementation Boundaries
- Do not replace Jinja + HTMX with a frontend framework
- Do not redesign core route structure or backend behavior
- Focus on shared templates and shared styles first, then page-specific enhancements
- Prefer CSS-driven polish over complex JavaScript
- Preserve existing forms and API integration contracts

## Validation
- review `/home`, `/discover`, `/library`, `/entities`, `/entities/{id}`, `/items/{id}`, and modal partials
- verify responsive behavior around mobile and tablet breakpoints
- check focus visibility, loading states, empty states, and hover stability
- confirm shared card and control styles remain consistent across pages
