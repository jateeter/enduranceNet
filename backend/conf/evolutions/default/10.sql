# --- !Ups

INSERT INTO legacy_redirects (id, legacy_url, target_url, status_code, reason) VALUES
  (25, '/2005PAC/Gallery/AsadorsS/', '/galleries/2005pac-gallery-asadorss', 301, 'Legacy Photoshop gallery root resolves to the migrated gallery detail route.'),
  (26, '/2005PAC/Gallery/AsadorsS/ThumbnailFrame.html', '/galleries/2005pac-gallery-asadorss', 301, 'Legacy Photoshop ThumbnailFrame wrapper resolves to the migrated gallery detail route.'),
  (27, '/2005PAC/Gallery/AsadorsS/index.html', '/galleries/2005pac-gallery-asadorss', 301, 'Legacy Photoshop index wrapper resolves to the migrated gallery detail route.'),
  (28, '/2005PAC/Gallery/AsadorsS/pages/IMG_0005.html', '/galleries/2005pac-gallery-asadorss', 301, 'Legacy Photoshop item page resolves to the migrated gallery detail route.'),
  (29, '/gallery/Nov4_WelcomeReception/', '/galleries/gallery-nov4-welcomereception', 301, 'Legacy Photoshop gallery root resolves to the migrated gallery detail route.'),
  (30, '/gallery/Nov4_WelcomeReception/index.html', '/galleries/gallery-nov4-welcomereception', 301, 'Legacy Photoshop index wrapper resolves to the migrated gallery detail route.'),
  (31, '/gallery/Nov4_WelcomeReception/index_2.html', '/galleries/gallery-nov4-welcomereception', 301, 'Legacy Photoshop paginated index resolves to the migrated gallery detail route.'),
  (32, '/gallery/Nov4_WelcomeReception/pages/IMG_6570.html', '/galleries/gallery-nov4-welcomereception', 301, 'Legacy Photoshop item page resolves to the migrated gallery detail route.');

# --- !Downs

DELETE FROM legacy_redirects WHERE id BETWEEN 25 AND 32;
