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

export function buildManifestLookup(manifestRows, appUrl) {
  const lookup = new Map();
  for (const row of manifestRows) {
    const metadata = {
      sourcePath: row.source_path ?? '',
      cmsAssetId: row.cms_asset_id ?? row.id ?? '',
      assetKind: row.asset_kind ?? '',
      checksumSha256: row.checksum_sha256 ?? '',
    };
    for (const value of [row.public_url, row.cms_public_url, row.legacy_url]) {
      if (!value) continue;
      lookup.set(value, metadata);
      lookup.set(absoluteUrl(appUrl, value), metadata);
      try {
        const parsed = new URL(absoluteUrl(appUrl, value));
        lookup.set(parsed.pathname, metadata);
      } catch {
        // Ignore non-URL lookup values; direct keys above still apply.
      }
    }
    if (metadata.sourcePath) {
      lookup.set(metadata.sourcePath, metadata);
      lookup.set(`/legacy-media/${metadata.sourcePath.replace(/^\/+/, '')}`, metadata);
    }
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
    };
  }
  return {
    sourcePath: '',
    cmsAssetId: '',
    assetKind: '',
    checksumSha256: '',
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
    waived: Boolean(waiverKey),
    waiverReason: waiverKey ? context.waiverLookup.get(waiverKey) : '',
    waiverKey,
  };
}
