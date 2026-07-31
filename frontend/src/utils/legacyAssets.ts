const LEGACY_MEDIA_PREFIX = '/legacy-media';
const LEGACY_HOSTS = new Set(['endurance.net', 'www.endurance.net']);

export function legacyAssetUrl(url?: string): string | undefined {
  if (!url) return undefined;
  if (url.startsWith('data:')) return url;
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url);
      if (LEGACY_HOSTS.has(parsed.hostname.toLowerCase())) {
        return `${LEGACY_MEDIA_PREFIX}${parsed.pathname}${parsed.search}`;
      }
      return url;
    } catch {
      return url;
    }
  }
  if (url.startsWith('/')) return `${LEGACY_MEDIA_PREFIX}${url}`;
  return `${LEGACY_MEDIA_PREFIX}/${url}`;
}
