# Photoshop Gallery Migration Roadmap

The legacy site contains a large corpus of Adobe Photoshop-generated image
galleries. They appear in two dominant patterns:

- framed galleries with `ThumbnailFrame.html`, `pages/*.html`,
  `thumbnails/*.jpg`, and `images/*.jpg`
- paginated galleries with `index.html`, `index_2.html`, `pages/*.html`,
  `thumbnails/*.jpg`, and `images/*.jpg`

The source inventory currently identifies at least 116 `ThumbnailFrame.html`
gallery roots, plus gallery-style paginated sets under `gallery/`,
`pictures/`, and event microsite directories. Existing NextGen import only
captures coarse `gallery_manifests`, so the CMS migration needs a richer
gallery model with item-level thumbnail/full-image relationships, source page
provenance, ordering, blocker reports, and a React presentation.

## Completion Path

1. Generate a Photoshop-gallery corpus manifest from the source inventory and
   mounted legacy tree.
2. Parse thumbnail links, page links, full-size images, captions, dimensions,
   ordering, title, section/event context, and legacy URLs.
3. Emit CMS-ready gallery, gallery-item, media-link, blocker, and summary
   files without committing generated image artifacts.
4. Add CMS/Directus import SQL or JSONL handoff for gallery collections and
   immutable provenance fields.
5. Expose migrated galleries through the Scala API and React routes using
   canonical `/legacy-media/...` or `/media/...` URLs.
6. Redirect representative legacy gallery URLs to NextGen gallery views.
7. Add release checks for representative galleries, image load failures,
   missing thumbnails, missing full-size images, and waived blockers.

## Issue Map

- `032-photoshop-gallery-corpus-manifest.md`: parse legacy Photoshop galleries
  into item-level manifests.
- `033-cms-gallery-handoff.md`: emit CMS/Directus gallery import bundles and
  review fields.
- `034-gallery-api-and-react-presentation.md`: expose gallery list/detail APIs
  and React gallery views.
- `035-legacy-gallery-url-redirects.md`: map representative legacy gallery URLs
  into canonical NextGen routes.
- `036-gallery-release-verification.md`: add visual/media checks for gallery
  presentation and blockers.

## Done Means

- Every readable Photoshop gallery root has a stable gallery ID.
- Every parsed gallery item has thumbnail, page, full-image, source path,
  order, caption, and CMS media references where available.
- Missing thumbnails, unreadable sources, and missing full images are explicit
  blockers, not silent skips.
- Directus/CMS can import gallery records and preserve immutable legacy
  provenance while editors update captions, credits, and review status.
- The deployed NextGen app can browse representative galleries on localhost
  through a React route backed by the Scala API.
- The release gate fails on unwaived broken gallery thumbnails or full images.
