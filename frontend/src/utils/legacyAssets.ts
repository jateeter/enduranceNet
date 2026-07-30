const LEGACY_MEDIA_PREFIX = '/legacy-media';

export function legacyAssetUrl(url?: string): string | undefined {
  if (!url) return undefined;
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) return url;
  if (url.startsWith('/')) return `${LEGACY_MEDIA_PREFIX}${url}`;
  return `${LEGACY_MEDIA_PREFIX}/${url}`;
}
