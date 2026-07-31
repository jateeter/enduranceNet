const LEGACY_MEDIA_PREFIX = '/legacy-media';
const CMS_MEDIA_PREFIX = '/media';
const LEGACY_HOSTS = new Set(['endurance.net', 'www.endurance.net', 'feeds.endurance.net']);
const LEGACY_ABSOLUTE_URL_PATTERN =
  /https?:\/\/(?:endurance\.net|www\.endurance\.net|feeds\.endurance\.net)(?:\/[^"'\s<>)]*)?/gi;

export function legacyAssetUrl(url?: string): string | undefined {
  if (!url) return undefined;
  if (url.startsWith('data:') || url.startsWith(`${LEGACY_MEDIA_PREFIX}/`) || url.startsWith(`${CMS_MEDIA_PREFIX}/`)) {
    return url;
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    try {
      const parsed = new URL(url);
      if (LEGACY_HOSTS.has(parsed.hostname.toLowerCase())) {
        return `${LEGACY_MEDIA_PREFIX}${parsed.pathname}${parsed.search}${parsed.hash}`;
      }
      return url;
    } catch {
      return url;
    }
  }
  if (url.startsWith('/')) return `${LEGACY_MEDIA_PREFIX}${url}`;
  return `${LEGACY_MEDIA_PREFIX}/${url}`;
}

export function rewriteLegacyMediaReferences(value: string): string {
  return value.replace(LEGACY_ABSOLUTE_URL_PATTERN, (match) => legacyAssetUrl(match) ?? match);
}
