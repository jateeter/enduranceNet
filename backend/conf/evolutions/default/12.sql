# --- !Ups

DELETE FROM legacy_redirects WHERE id BETWEEN 100 AND 117;
DELETE FROM legacy_redirects WHERE legacy_url IN (
  '/international/USA/2026TevisCup',
  '/international/USA/2026TevisCup/',
  '/international/USA/2026TevisCup/index.html',
  '/international/USA/2026TevisCup/indexInternal.html',
  '/international/USA/2026TevisCup/eventHeader.html',
  '/international/USA/2026TevisCup/eventTrailer.html',
  '/international/USA/2026TevisCup/menuIndex.html',
  '/international/USA/2026TevisCup/storyIndex.html',
  '/international/USA/2026TevisCup/notes.html',
  '/international/USA/2026TevisCup/notes01.html',
  '/international/USA/2026TevisCup/gallery.html',
  '/international/USA/2026TevisCup/gallery/index.html',
  '/international/USA/2026TevisCup/galleryInternal.html',
  '/international/USA/2026TevisCup/photoIndex.html',
  '/international/USA/2026TevisCup/resultsIndex.html',
  '/international/USA/2026TevisCup/rightDiv.html',
  '/international/USA/2026TevisCup/thumbnailRotator.html',
  '/international/USA/2026TevisCup/specialGallery/index.html'
);

INSERT INTO legacy_redirects (id, legacy_url, target_url, status_code, reason) VALUES
  (117, '/international/USA/2026TevisCup', '/events/2026-tevis-cup', 301, '2026 Tevis Cup root migrated to the event microsite.'),
  (100, '/international/USA/2026TevisCup/', '/events/2026-tevis-cup', 301, '2026 Tevis Cup root migrated to the event microsite.'),
  (101, '/international/USA/2026TevisCup/index.html', '/events/2026-tevis-cup', 301, '2026 Tevis Cup wrapper migrated to the event microsite.'),
  (102, '/international/USA/2026TevisCup/indexInternal.html', '/events/2026-tevis-cup', 301, '2026 Tevis Cup internal include migrated to the event microsite.'),
  (103, '/international/USA/2026TevisCup/eventHeader.html', '/events/2026-tevis-cup', 301, '2026 Tevis Cup header include represented by the microsite masthead.'),
  (104, '/international/USA/2026TevisCup/eventTrailer.html', '/events/2026-tevis-cup', 301, '2026 Tevis Cup trailer include represented by the microsite layout.'),
  (105, '/international/USA/2026TevisCup/menuIndex.html', '/events/2026-tevis-cup', 301, '2026 Tevis Cup menu include represented by microsite section navigation.'),
  (106, '/international/USA/2026TevisCup/storyIndex.html', '/events/2026-tevis-cup#stories', 301, '2026 Tevis Cup story index migrated to microsite stories.'),
  (107, '/international/USA/2026TevisCup/notes.html', '/events/2026-tevis-cup#notes', 301, '2026 Tevis Cup notes wrapper migrated to microsite notes.'),
  (108, '/international/USA/2026TevisCup/notes01.html', '/events/2026-tevis-cup#notes', 301, '2026 Tevis Cup notes page migrated to microsite notes.'),
  (109, '/international/USA/2026TevisCup/gallery.html', '/events/2026-tevis-cup#gallery', 301, '2026 Tevis Cup gallery wrapper migrated to microsite media.'),
  (110, '/international/USA/2026TevisCup/gallery/index.html', '/events/2026-tevis-cup#gallery', 301, '2026 Tevis Cup gallery index migrated to microsite media.'),
  (111, '/international/USA/2026TevisCup/galleryInternal.html', '/events/2026-tevis-cup#gallery', 301, '2026 Tevis Cup gallery include migrated to microsite media.'),
  (112, '/international/USA/2026TevisCup/photoIndex.html', '/events/2026-tevis-cup#gallery', 301, '2026 Tevis Cup photo index migrated to microsite media.'),
  (113, '/international/USA/2026TevisCup/resultsIndex.html', '/events/2026-tevis-cup#results', 301, '2026 Tevis Cup results index migrated to microsite results.'),
  (114, '/international/USA/2026TevisCup/rightDiv.html', '/events/2026-tevis-cup', 301, '2026 Tevis Cup sidebar include represented by microsite cards.'),
  (115, '/international/USA/2026TevisCup/thumbnailRotator.html', '/events/2026-tevis-cup#gallery', 301, '2026 Tevis Cup thumbnail rotator migrated to microsite media.'),
  (116, '/international/USA/2026TevisCup/specialGallery/index.html', '/events/2026-tevis-cup#gallery', 301, '2026 Tevis Cup special gallery migrated to microsite media.');

# --- !Downs

DELETE FROM legacy_redirects WHERE id BETWEEN 100 AND 117;
