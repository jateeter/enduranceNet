# --- !Ups

CREATE TABLE cms_media_assets (
  id VARCHAR(32) PRIMARY KEY,
  source_path VARCHAR(2048) NOT NULL UNIQUE,
  legacy_url VARCHAR(2048) NOT NULL,
  public_url VARCHAR(2048) NOT NULL,
  cms_public_url VARCHAR(2048) NOT NULL,
  storage_key VARCHAR(2048) NOT NULL,
  asset_kind VARCHAR(32) NOT NULL,
  mime_type VARCHAR(255),
  extension VARCHAR(64),
  size_bytes BIGINT,
  checksum_sha256 VARCHAR(64),
  width INTEGER,
  height INTEGER,
  title VARCHAR(512),
  alt_text VARCHAR(512),
  credit VARCHAR(512),
  source_context VARCHAR(128) NOT NULL,
  import_status VARCHAR(64) NOT NULL,
  staged_path VARCHAR(2048),
  scanned_at VARCHAR(64)
);

CREATE INDEX cms_media_assets_checksum_idx ON cms_media_assets(checksum_sha256);
CREATE INDEX cms_media_assets_kind_idx ON cms_media_assets(asset_kind);

CREATE TABLE cms_media_blockers (
  blocker_key VARCHAR(128) PRIMARY KEY,
  blocker_type VARCHAR(64) NOT NULL,
  source_path VARCHAR(2048),
  referenced_url VARCHAR(2048),
  resolved_path VARCHAR(2048),
  reason TEXT NOT NULL,
  status VARCHAR(64) NOT NULL,
  detected_at VARCHAR(64)
);

CREATE INDEX cms_media_blockers_status_idx ON cms_media_blockers(status);
CREATE INDEX cms_media_blockers_type_idx ON cms_media_blockers(blocker_type);

# --- !Downs

DROP TABLE IF EXISTS cms_media_blockers;
DROP TABLE IF EXISTS cms_media_assets;
