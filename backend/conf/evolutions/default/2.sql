# --- !Ups

INSERT INTO news (id, title, summary, content, author, published_at, category, image_url) VALUES
  (4, 'Butheeb selected as replacement host for the FEI Endurance World Championship 2026', 'Featured WEC coverage from the legacy homepage and Featured Stories surface.', 'The legacy homepage promotes the 2026 World Endurance Championship host update as both a current-news item and a featured story. The NextGen migration keeps that dual editorial role visible while preserving source provenance in later importer passes.', 'Endurance.Net', '2026-07-29', 'Featured Stories', '/international/SaudiArabia/2026WorldEnduranceChampionship/banner.jpg'),
  (5, 'Ann Kratochvil Passes Away', 'Featured memorial content from the legacy Featured Stories page.', 'Memorial and community-history pieces are a distinct part of Endurance.Net. They should remain discoverable beside event coverage and current news rather than being flattened into generic sport news.', 'Endurance.Net', '2026-07-29', 'Featured Stories', '/merri/102615/0909OC_430.jpg'),
  (6, 'Angie Field Rochna 1965 - 2026', 'Featured memorial content from the legacy Featured Stories page.', 'Featured Stories includes personal histories, memorials, and community records that need stable legacy deep links and careful archive treatment.', 'Endurance.Net', '2026-07-29', 'Featured Stories', NULL),
  (7, '2026 Tahoe Rim photos by Bill Gore', 'Current News photo coverage surfaced from the legacy weekly digest.', 'Photo-led current-news entries should connect article summaries to gallery and media-asset records as the importer matures.', 'Endurance.Net', '2026-07-29', 'Current News', NULL),
  (8, 'China Equestrian endurance riding competition opens in north China county', 'International current-news item from the legacy digest.', 'Current News aggregates external reporting, local ride coverage, international competition updates, and Endurance.Net archive links.', 'Endurance.Net', '2026-07-29', 'Current News', NULL);

# --- !Downs

DELETE FROM news WHERE id IN (4, 5, 6, 7, 8);
