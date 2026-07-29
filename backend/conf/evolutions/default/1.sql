# --- !Ups

CREATE TABLE news (
  id BIGINT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  summary TEXT NOT NULL,
  content TEXT NOT NULL,
  author VARCHAR(255) NOT NULL,
  published_at VARCHAR(32) NOT NULL,
  category VARCHAR(128) NOT NULL,
  image_url VARCHAR(1024)
);

CREATE TABLE events (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  event_type VARCHAR(128) NOT NULL,
  event_date VARCHAR(32) NOT NULL,
  location VARCHAR(255) NOT NULL,
  distance VARCHAR(128) NOT NULL,
  description TEXT NOT NULL,
  registration_url VARCHAR(1024)
);

INSERT INTO news (id, title, summary, content, author, published_at, category, image_url) VALUES
  (1, '2026 Tevis Cup Coverage', 'Legacy event coverage for the Western States Trail Ride will migrate as an event microsite.', 'The Tevis Cup is one of Endurance.Net''s recurring high-value coverage areas. In the NextGen model it belongs to the event, event-page, gallery, result, and media asset domains rather than a generic endurance-sport news bucket.', 'Endurance.Net', '2026-07-29', 'Event Coverage', '/international/USA/2026TevisCup/banner_block.jpg'),
  (2, 'Current News Digest', 'The live Current News page is a curated digest backed by PHP wrappers and internal content fragments.', 'The legacy /CurrentNews/ route sets page metadata, includes the shared site header, renders indexInternal.html, and then includes the site trailer. Imported records must preserve anchors and source provenance for deep links.', 'Endurance.Net', '2026-07-29', 'Current News', '/images/banner_sm_right_newsblogs.jpg'),
  (3, '2026 World Endurance Championship Hub', 'Saudi Arabia WEC coverage spans a hub page, analysis pages, and current-news references.', 'The WEC material should migrate as structured event coverage while retaining static analysis-page legacy URLs such as team analyses and qualification requirements.', 'Endurance.Net', '2026-07-29', 'International', '/international/SaudiArabia/2026WorldEnduranceChampionship/banner.jpg');

INSERT INTO events (id, name, event_type, event_date, location, distance, description, registration_url) VALUES
  (1, 'Tevis Cup', 'Endurance Ride', '2026-07-18', 'California, USA', '100 miles', 'Western States Trail Ride coverage with legacy event pages, photos, news anchors, and archive material.', '/international/USA/2026TevisCup/'),
  (2, 'City of Rocks Pioneer', 'Endurance Ride', '2026-06-01', 'Idaho, USA', '25/50/55 miles', 'Recurring Idaho endurance ride represented in the legacy tree by yearly microsites, stories, and galleries.', '/international/USA/2026CityOfRocks/'),
  (3, 'Mongol Derby', 'Expedition Endurance', '2026-08-01', 'Mongolia', '1000 km', 'International endurance adventure coverage with news, rider stories, and event archive pages.', '/international/Mongolia/2026MongolDerby/'),
  (4, 'Tom Quilty Gold Cup', 'Endurance Championship', '2026-07-01', 'Australia', '160 km', 'Australian championship coverage represented by event pages, news references, and historical archive entries.', '/international/Australia/2026TomQuilty/');

# --- !Downs

DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS news;
