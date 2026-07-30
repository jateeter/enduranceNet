# Legacy Theme And Branding

This visual migration keeps the NextGen React app close to the current Endurance.Net PHP site while avoiding the fixed-position layout that makes the legacy homepage fragile.

## Palette

| Token | NextGen value | Legacy source cue | Usage |
| --- | --- | --- | --- |
| `--color-primary` | `#a86e16` | `/include/siteHeader.html` navigation and homepage advertiser header | Masthead navigation, borders, sponsor/advertiser accents |
| `--color-red` | `#c60000` | Homepage Current News and Featured Stories headline links use red editorial labels | Section titles, story badges, primary actions |
| `--color-bg` | `#d8d4b6` | Tan framing from legacy side navigation and boxed table borders | Page background |
| `--color-bg-alt` | `#eee9cf` | Muted tan/cream section breaks from older Endurance.Net templates | Alternating bands |
| `--color-surface` | `#ffffff` | Legacy content panels and homepage columns | Cards, lists, page headers, rails |
| `--color-border` | `#bb8d46` | Legacy tan borders around navigation/content areas | Primary card and panel borders |
| `--color-border-soft` | `#d8c096` | Softer tan table/header edges | Secondary borders |

## Source Graphics

The theme uses live legacy graphics through manifested URLs until #11 replaces them with managed imported assets.

- Masthead: `/images/ENbanner_sm_left.jpg` and `/images/ENbanner_sm_right.jpg`
- Current News section: `/images/banner_sm_right_newsblogs.jpg`
- Featured Stories section: `/images/ENbanner_right_stories.jpg`
- Events section: `/images/banner_sm_right_events.jpg`
- Ridecamp section: `/images/banner_sm_right_ridecamp.jpg`
- Classifieds section: `/images/banner_sm_right_classified.jpg`
- Homepage event coverage: `banner_block.jpg` images from the legacy event microsite paths
- Sponsor and advertiser rails: `homepage_assets` records seeded from `/index_content.html`, `/CurrentNews/indexInternal.html`, and `/FeaturedStories/indexInternal.html`

## Layout Direction

- Homepage uses a compact portal layout: Current News headline list plus story cards, followed by featured story, event, sponsor, social, and advertiser rails.
- Section pages use legacy banner headers and card/list grids.
- Cards keep shallow radius, tan borders, dense text, and small badges so the site reads as an Endurance.Net archive/news portal rather than a generic sports landing page.
- CSS avoids fixed positioning from the PHP templates; responsive grids collapse on mobile to prevent overlap.
