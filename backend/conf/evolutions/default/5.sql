# --- !Ups

INSERT INTO events (id, name, event_type, event_date, location, distance, description, registration_url) VALUES
  (5, 'FEI Endurance World Championship', 'Endurance Championship', '2026-10-17', 'AlUla, Saudi Arabia', '160 km', 'World championship coverage migrated from the Saudi Arabia event hub, current-news references, analysis pages, banners, and static qualification documents.', '/international/SaudiArabia/2026WorldEnduranceChampionship/'),
  (6, 'Owyhee Endurance Rides', 'Ride Series', '2026-05-01', 'Idaho, USA', '25/50/75/100 miles', 'Owyhee and Oreana ride-series pages combine recurring event coverage, sponsor references, local media, results placeholders, and historical ride documents.', '/oreana/');

# --- !Downs

DELETE FROM events WHERE id IN (5, 6);
