# --- !Ups

UPDATE legacy_redirects
SET target_url = '/community#classifieds',
    reason = 'Legacy ClassifiedAds entry route resolves to the read-only community archive.'
WHERE id = 19;

UPDATE legacy_redirects
SET target_url = '/community#classifieds',
    reason = 'Legacy ClassifiedAds wrapper resolves to the read-only community archive.'
WHERE id = 20;

UPDATE legacy_redirects
SET target_url = '/community#ridecamp',
    reason = 'Legacy RidecampFriend entry route resolves to the Ridecamp community archive section.'
WHERE id = 21;

UPDATE legacy_redirects
SET target_url = '/community#ridecamp',
    reason = 'Legacy RidecampFriend wrapper resolves to the Ridecamp community archive section.'
WHERE id = 22;

INSERT INTO legacy_redirects (id, legacy_url, target_url, status_code, reason) VALUES
  (23, '/ClassifiedAds', '/community#classifieds', 301, 'Legacy ClassifiedAds entry route resolves to the read-only community archive.'),
  (24, '/RidecampFriend', '/community#ridecamp', 301, 'Legacy RidecampFriend entry route resolves to the Ridecamp community archive section.');

# --- !Downs

DELETE FROM legacy_redirects WHERE id IN (23, 24);

UPDATE legacy_redirects
SET target_url = '/results',
    reason = 'Legacy ClassifiedAds entry route resolves to the NextGen classifieds staging page.'
WHERE id = 19;

UPDATE legacy_redirects
SET target_url = '/results',
    reason = 'Legacy ClassifiedAds wrapper resolves to the NextGen classifieds staging page.'
WHERE id = 20;

UPDATE legacy_redirects
SET target_url = '/athletes',
    reason = 'Legacy RidecampFriend entry route resolves to the NextGen Ridecamp staging page.'
WHERE id = 21;

UPDATE legacy_redirects
SET target_url = '/athletes',
    reason = 'Legacy RidecampFriend wrapper resolves to the NextGen Ridecamp staging page.'
WHERE id = 22;
