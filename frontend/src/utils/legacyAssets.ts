const LEGACY_ASSET_BASE = 'http://www.endurance.net';

export function legacyAssetUrl(url?: string): string | undefined {
  if (!url) return undefined;
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) return url;
  if (url.startsWith('/')) return `${LEGACY_ASSET_BASE}${url}`;
  return `${LEGACY_ASSET_BASE}/${url}`;
}
