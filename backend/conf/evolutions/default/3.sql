# --- !Ups

CREATE TABLE homepage_assets (
  id BIGINT PRIMARY KEY,
  placement VARCHAR(128) NOT NULL,
  title VARCHAR(255) NOT NULL,
  image_url VARCHAR(1024) NOT NULL,
  link_url VARCHAR(1024) NOT NULL,
  alt_text VARCHAR(255) NOT NULL,
  source_legacy_url VARCHAR(1024) NOT NULL,
  source_path VARCHAR(1024) NOT NULL,
  sort_order INTEGER NOT NULL
);

CREATE TABLE legacy_redirects (
  id BIGINT PRIMARY KEY,
  legacy_url VARCHAR(1024) NOT NULL,
  target_url VARCHAR(1024) NOT NULL,
  status_code INTEGER NOT NULL,
  reason VARCHAR(255) NOT NULL
);

INSERT INTO homepage_assets (id, placement, title, image_url, link_url, alt_text, source_legacy_url, source_path, sort_order) VALUES
  (1, 'current_news_sponsor', 'Drinkers of the Wind Arabians', 'http://www.endurance.net/ads/AdvertiserLogos/DWALogo.jpg', 'https://dwarabians.com/', 'Drinkers of the Wind Arabians logo', '/CurrentNews/', '/CurrentNews/indexInternal.html', 1),
  (2, 'featured_story', 'Butheeb selected for the FEI Endurance World Championship 2026', 'https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjpCyKg1VR7SWKTXobOhXfIX5X6gtAAJfcoJcDXj5dUnqKdH8d3WIgZexv2sfzyjqIdBizbRywtzAxzCGKcKcov3FuDT0ktP6tkXkxEBGojCGC2a-DnEEZ0uF_Po8VEZROPNDx8aUydut2A0lY-oIAeiK211cLszr45iGYDQwj1E6_L_ql493Av/w400-h65/FEIEnduranceLogo.png', '/news/4', 'FEI Endurance logo for the Butheeb World Championship story', '/FeaturedStories/#UAEWEC', '/index_content.html', 1),
  (3, 'featured_story', 'Ann Kratochvil Passes Away', 'http://www.endurance.net/merri/102615/0909OC_430.jpg', '/news/5', 'Ann Kratochvil memorial image', '/FeaturedStories/#AnnKratochvil', '/index_content.html', 2),
  (4, 'featured_story', 'Angie Field Rochna 1965 - 2026', 'https://cdn.tukioswebsites.com/410fc4c4-ebe4-4dfd-9bb7-776a4cf396e9/lg', '/news/6', 'Angie Field Rochna memorial image', '/FeaturedStories/#AngieRochna', '/index_content.html', 3),
  (5, 'event_coverage', 'City of Rocks', '/international/USA/2026CityOfRocks/banner_block.jpg', '/events/2', 'City of Rocks event coverage banner', '/international/USA/2026CityOfRocks/', '/index_content.html', 1),
  (6, 'event_coverage', 'Midnight Rider', '/international/USA/2026MidnightRider/banner_block.jpg', '/events', 'Midnight Rider event coverage banner', '/international/USA/2026MidnightRider/', '/index_content.html', 2),
  (7, 'event_coverage', 'Tom Quilty', '/international/Australia/2026TomQuilty/banner_block.jpg', '/events/4', 'Tom Quilty event coverage banner', '/international/Australia/2026TomQuilty/', '/index_content.html', 3),
  (8, 'event_coverage', 'Tevis Cup', '/international/USA/2026TevisCup/banner_block.jpg', '/events/1', 'Tevis Cup event coverage banner', '/international/USA/2026TevisCup/', '/index_content.html', 4),
  (9, 'event_coverage', 'Mongol Derby', '/international/Mongolia/2026MongolDerby/banner_block.jpg', '/events/3', 'Mongol Derby event coverage banner', '/international/Mongolia/2026MongolDerby/', '/index_content.html', 5),
  (10, 'social', 'Endurance.Net on Twitter', '/images/twitter.jpg', 'https://twitter.com/endurancenet', 'Twitter logo', '/', '/index_content.html', 1),
  (11, 'social', 'Endurance.Net on Instagram', '/img/instagramLogo.png', 'https://www.instagram.com/endurancenet', 'Instagram logo', '/', '/index_content.html', 2),
  (12, 'advertiser', 'Belesemo Arabians', 'http://www.endurance.net/ads/AdvertiserLogos/BelesemoArabians_150.jpg', '/belesemo/', 'Belesemo Arabians logo', '/', '/index_content.html', 1),
  (13, 'advertiser', 'Cypress Trails Equestrian Center', 'http://www.endurance.net/ads/AdvertiserLogos/CypressTrails_150.jpg', 'https://cypresstrailsranch.com/', 'Cypress Trails Equestrian Center logo', '/', '/index_content.html', 2),
  (14, 'advertiser', 'Distance Depot Tack', 'http://www.endurance.net/ads/AdvertiserLogos/TheDistanceDepot_150.jpg', 'http://www.thedistancedepot.com', 'Distance Depot Tack logo', '/', '/index_content.html', 3),
  (15, 'advertiser', 'Endurance Ride Photographers Guild', 'http://www.endurance.net/advertisers/EnduranceRidePhotographersGuild/EnduranceRidePhotographersGuildImage.png', '/advertisers/EnduranceRidePhotographersGuild.html', 'Endurance Ride Photographers Guild logo', '/', '/index_content.html', 4),
  (16, 'advertiser', 'Owyhee Endurance Rides', 'http://www.endurance.net/ads/AdvertiserLogos/IdahoEnduranceRides_150.jpg', '/oreana/owyheeendurancerides.html', 'Owyhee Endurance Rides logo', '/', '/index_content.html', 5),
  (17, 'advertiser', 'Slypner Gear Trail Supplies', 'http://www.endurance.net/ads/AdvertiserLogos/Slypner_150.jpg', 'https://www.slypnergear.com/', 'Slypner Gear Trail Supplies logo', '/', '/index_content.html', 6);

INSERT INTO legacy_redirects (id, legacy_url, target_url, status_code, reason) VALUES
  (1, '/', '/', 301, 'Homepage preserved as the React root route.'),
  (2, '/index.html', '/', 301, 'Legacy PHP-rendered homepage wrapper now resolves to the React root route.'),
  (3, '/index_content.html', '/', 301, 'Legacy homepage include content is represented by structured homepage sections.'),
  (4, '/CurrentNews/', '/news', 301, 'Current News digest route migrated to the React news index.'),
  (5, '/CurrentNews/index.html', '/news', 301, 'Current News PHP wrapper migrated to the React news index.'),
  (6, '/CurrentNews/indexInternal.html', '/news', 301, 'Current News include content migrated to the React news index.'),
  (7, '/CurrentNews/#TRBG', '/news/7', 301, 'Known legacy Current News anchor mapped to imported Tahoe Rim news record.'),
  (8, '/CurrentNews/#ChinaRide', '/news/8', 301, 'Known legacy Current News anchor mapped to imported China Ride news record.'),
  (9, '/FeaturedStories/', '/featured-stories', 301, 'Featured Stories route migrated to the React featured stories index.'),
  (10, '/FeaturedStories/index.html', '/featured-stories', 301, 'Featured Stories PHP wrapper migrated to the React featured stories index.'),
  (11, '/FeaturedStories/indexInternal.html', '/featured-stories', 301, 'Featured Stories include content migrated to the React featured stories index.'),
  (12, '/FeaturedStories/#UAEWEC', '/news/4', 301, 'Known legacy Featured Stories anchor mapped to imported Butheeb record.'),
  (13, '/FeaturedStories/#AnnKratochvil', '/news/5', 301, 'Known legacy Featured Stories anchor mapped to imported Ann Kratochvil record.'),
  (14, '/FeaturedStories/#AngieRochna', '/news/6', 301, 'Known legacy Featured Stories anchor mapped to imported Angie Rochna record.');

# --- !Downs

DROP TABLE IF EXISTS legacy_redirects;
DROP TABLE IF EXISTS homepage_assets;
