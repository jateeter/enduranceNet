# --- !Ups

INSERT INTO legacy_redirects (id, legacy_url, target_url, status_code, reason) VALUES
  (15, '/newsblogs/', '/news', 301, 'Legacy News Archive entry route currently resolves to the migrated news index.'),
  (16, '/newsblogs/index.html', '/news', 301, 'Legacy News Archive wrapper currently resolves to the migrated news index.'),
  (17, '/events/', '/events', 301, 'Legacy Events entry route resolves to the migrated events index.'),
  (18, '/events/index.html', '/events', 301, 'Legacy Events wrapper resolves to the migrated events index.'),
  (19, '/ClassifiedAds/', '/results', 301, 'Legacy ClassifiedAds entry route resolves to the NextGen classifieds staging page.'),
  (20, '/ClassifiedAds/index.html', '/results', 301, 'Legacy ClassifiedAds wrapper resolves to the NextGen classifieds staging page.'),
  (21, '/RidecampFriend/', '/athletes', 301, 'Legacy RidecampFriend entry route resolves to the NextGen Ridecamp staging page.'),
  (22, '/RidecampFriend/index.html', '/athletes', 301, 'Legacy RidecampFriend wrapper resolves to the NextGen Ridecamp staging page.');

# --- !Downs

DELETE FROM legacy_redirects WHERE id BETWEEN 15 AND 22;
