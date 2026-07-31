# --- !Ups

CREATE TABLE stream_sources (
  id BIGINT PRIMARY KEY,
  slug VARCHAR(128) NOT NULL UNIQUE,
  title VARCHAR(255) NOT NULL,
  provider VARCHAR(64) NOT NULL,
  feed_format VARCHAR(64) NOT NULL,
  remote_url VARCHAR(1024),
  local_cache_path VARCHAR(1024),
  legacy_url VARCHAR(1024),
  default_presentation VARCHAR(128) NOT NULL,
  active BOOLEAN NOT NULL,
  notes TEXT
);

CREATE TABLE stream_entries (
  id BIGINT PRIMARY KEY,
  source_id BIGINT NOT NULL REFERENCES stream_sources(id),
  provider_entry_id VARCHAR(512) NOT NULL,
  title VARCHAR(512) NOT NULL,
  summary_html TEXT,
  content_html TEXT,
  author VARCHAR(255),
  published_at VARCHAR(64),
  updated_at VARCHAR(64),
  alternate_url VARCHAR(1024),
  self_url VARCHAR(1024),
  related_url VARCHAR(1024),
  comments_url VARCHAR(1024),
  checksum_sha256 VARCHAR(64)
);

CREATE UNIQUE INDEX stream_entries_source_provider_id_idx
  ON stream_entries(source_id, provider_entry_id);

INSERT INTO stream_sources (id, slug, title, provider, feed_format, remote_url, local_cache_path, legacy_url, default_presentation, active, notes) VALUES
  (1, 'where-in-the-world', 'Where in the World', 'blogger', 'atom-1.0', 'http://www.blogger.com/feeds/7290526037745122441/posts/default', '/channels/whereintheworld/atom.xml', 'http://feeds.endurance.net/whereintheworld/', 'popup-channel-card', TRUE, 'Blogger Atom stream rendered by legacy channel XSLT with popup/list variants.'),
  (2, 'merri-travels', 'Merri Travels', 'blogger-local-cache', 'atom-1.0', 'http://merritravels.endurance.net/feeds/posts/default', '/merri/MerriTravels.xml', '/blogger/', 'atom-list', TRUE, 'Legacy blogger/index_content.html loads this local cache through atomlist_Items.xsl.'),
  (3, 'wec-news', 'WEC News Feed', 'blogger-archive', 'atom-blogger', 'https://www.blogger.com/atom/6751438', '/2006WEC/wecnews_atom.xml', '/2006WEC/NewsFeed/', 'event-story-list', FALSE, 'Archived 2006 WEC Blogger feed rendered into event-story surfaces.'),
  (4, 'endurance-net-feeds', 'Endurance.Net Feeds', 'opml', 'opml', NULL, '/channels/EnduranceNetFeeds.xml', '/channels/', 'stream-directory', FALSE, 'OPML registry of channel groups and feed bookmarks.'),
  (5, 'rss-headline-sample', 'RSS Headline Sample', 'rss-local-cache', 'rss-2.0', NULL, '/channels/rss-samples.xml', '/channels/', 'rss-list', FALSE, 'Placeholder registry record for RSS list transform parity fixtures.');

INSERT INTO stream_entries (id, source_id, provider_entry_id, title, summary_html, content_html, author, published_at, updated_at, alternate_url, self_url, related_url, comments_url, checksum_sha256) VALUES
  (1, 1, 'tag:blogger.com,1999:blog-7290526037745122441', 'Where in the World stream snapshot', 'Following the travels of Endurance.Net riders around the world.', NULL, 'Endurance.Net', NULL, NULL, 'http://feeds.endurance.net/whereintheworld/', 'http://www.blogger.com/feeds/7290526037745122441/posts/default', NULL, NULL, NULL),
  (2, 2, 'merri-travels-local-cache', 'Merri Travels local Blogger cache', 'Local feed snapshot rendered by atomlist_Items.xsl on the legacy Blogger landing page.', NULL, 'Merri Melde', NULL, NULL, 'http://merritravels.endurance.net/', 'http://merritravels.endurance.net/feeds/posts/default', NULL, NULL, NULL),
  (3, 3, 'tag:blogger.com,1999:blog-6751438', '2006 WEC Blogger archive', 'Archived WEC Blogger Atom feed used by event-story presentation routes.', NULL, 'Endurance.Net', NULL, NULL, '/2006WEC/NewsFeed/', 'https://www.blogger.com/atom/6751438', NULL, NULL, NULL);

# --- !Downs

DROP TABLE IF EXISTS stream_entries;
DROP TABLE IF EXISTS stream_sources;
