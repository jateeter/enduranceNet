import { readFile } from 'node:fs/promises';

export async function readJsonl(path) {
  if (!path) return [];
  const content = await readFile(path, 'utf8');
  return content
    .split(/\r?\n/)
    .filter((line) => line.trim())
    .map((line) => JSON.parse(line));
}

export function absoluteUrl(appUrl, value) {
  try {
    return new URL(value, `${appUrl.replace(/\/$/, '')}/`).toString();
  } catch {
    return value;
  }
}

function lookupValueSet(appUrl, value) {
  const values = new Set();
  if (!value) return values;
  values.add(value);
  values.add(absoluteUrl(appUrl, value));
  try {
    const parsed = new URL(absoluteUrl(appUrl, value));
    values.add(parsed.pathname);
    values.add(`${parsed.pathname}${parsed.search}`);
  } catch {
    // Direct keys above still apply.
  }
  return values;
}

function addManifestEntry(lookup, appUrl, values, metadata) {
  for (const value of values) {
    for (const key of lookupValueSet(appUrl, value)) {
      lookup.set(key, metadata);
    }
  }
  if (metadata.sourcePath) {
    lookup.set(metadata.sourcePath, metadata);
    lookup.set(`/legacy-media/${metadata.sourcePath.replace(/^\/+/, '')}`, metadata);
  }
}

function galleryItemMetadata(row, role, sourcePath) {
  return {
    sourcePath: sourcePath ?? '',
    cmsAssetId: row.cms_asset_id ?? row.id ?? '',
    assetKind: 'image',
    checksumSha256: row.checksum_sha256 ?? '',
    galleryId: row.gallery_id ?? '',
    gallerySlug: row.gallery_slug ?? '',
    galleryItemId: row.item_id ?? '',
    galleryPosition: row.position ?? '',
    galleryImageRole: role,
    itemPageSourcePath: row.item_page_source_path ?? '',
  };
}

export function buildManifestLookup(manifestRows, appUrl) {
  const lookup = new Map();
  for (const row of manifestRows) {
    if (row.gallery_slug || row.thumbnail_public_url || row.full_image_public_url) {
      addManifestEntry(
        lookup,
        appUrl,
        [row.thumbnail_public_url],
        galleryItemMetadata(row, 'thumbnail', row.thumbnail_source_path),
      );
      addManifestEntry(
        lookup,
        appUrl,
        [row.full_image_public_url],
        galleryItemMetadata(row, 'full-image', row.full_image_source_path),
      );
      continue;
    }
    const metadata = {
      sourcePath: row.source_path ?? '',
      cmsAssetId: row.cms_asset_id ?? row.id ?? '',
      assetKind: row.asset_kind ?? '',
      checksumSha256: row.checksum_sha256 ?? '',
      galleryId: '',
      gallerySlug: '',
      galleryItemId: '',
      galleryPosition: '',
      galleryImageRole: '',
      itemPageSourcePath: '',
    };
    addManifestEntry(lookup, appUrl, [row.public_url, row.cms_public_url, row.legacy_url], metadata);
  }
  return lookup;
}

export function buildWaiverLookup(rows) {
  const lookup = new Map();
  for (const row of rows) {
    const reason = row.reason ?? 'waived';
    for (const key of [row.url, row.referenced_url, row.referenced_path, row.source_path, row.cms_asset_id]) {
      if (key) lookup.set(String(key), reason);
    }
  }
  return lookup;
}

export function mediaMetadataForUrl(url, appUrl, manifestLookup) {
  const candidates = [url];
  try {
    const parsed = new URL(url, `${appUrl.replace(/\/$/, '')}/`);
    candidates.push(parsed.pathname);
    candidates.push(`${parsed.pathname}${parsed.search}`);
    if (parsed.pathname.startsWith('/legacy-media/')) {
      candidates.push(parsed.pathname.replace(/^\/legacy-media\//, ''));
    }
  } catch {
    // Keep the direct candidate only.
  }
  for (const candidate of candidates) {
    if (manifestLookup.has(candidate)) {
      return manifestLookup.get(candidate);
    }
  }
  const legacyPath = candidates.find((candidate) => candidate.startsWith('/legacy-media/'));
  if (legacyPath) {
    return {
      sourcePath: legacyPath.replace(/^\/legacy-media\//, ''),
      cmsAssetId: '',
      assetKind: 'image',
      checksumSha256: '',
      galleryId: '',
      gallerySlug: '',
      galleryItemId: '',
      galleryPosition: '',
      galleryImageRole: '',
      itemPageSourcePath: '',
    };
  }
  return {
    sourcePath: '',
    cmsAssetId: '',
    assetKind: '',
    checksumSha256: '',
    galleryId: '',
    gallerySlug: '',
    galleryItemId: '',
    galleryPosition: '',
    galleryImageRole: '',
    itemPageSourcePath: '',
  };
}

export function annotateMediaFailure(failure, context) {
  const metadata = mediaMetadataForUrl(failure.url ?? failure.src ?? '', context.appUrl, context.manifestLookup);
  const url = failure.url ?? failure.src ?? '';
  const waiverCandidates = [url, metadata.sourcePath, metadata.cmsAssetId].filter(Boolean);
  try {
    const parsed = new URL(url, `${context.appUrl.replace(/\/$/, '')}/`);
    waiverCandidates.push(parsed.pathname, `${parsed.pathname}${parsed.search}`);
  } catch {
    // Keep direct candidates.
  }
  const waiverKey = waiverCandidates.find((candidate) => context.waiverLookup.has(candidate)) ?? '';
  return {
    ...failure,
    sourcePath: metadata.sourcePath,
    cmsAssetId: metadata.cmsAssetId,
    assetKind: metadata.assetKind,
    checksumSha256: metadata.checksumSha256,
    galleryId: metadata.galleryId,
    gallerySlug: metadata.gallerySlug,
    galleryItemId: metadata.galleryItemId,
    galleryPosition: metadata.galleryPosition,
    galleryImageRole: metadata.galleryImageRole,
    itemPageSourcePath: metadata.itemPageSourcePath,
    waived: Boolean(waiverKey),
    waiverReason: waiverKey ? context.waiverLookup.get(waiverKey) : '',
    waiverKey,
  };
}
