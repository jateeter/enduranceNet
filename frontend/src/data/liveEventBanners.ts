const LIVE_EVENT_BANNERS_BY_ROOT: Record<string, string> = {
  '/international/Australia/2026TomQuilty/': '/media/live-27d1a102b2430136/banner_block.jpg',
  '/international/Mongolia/2026MongolDerby/': '/media/live-e886c90209ff4de8/banner_block.jpg',
  '/international/USA/2026MidnightRider/': '/media/live-21d96ea3c60a094e/banner_block.jpg',
  '/international/USA/2026SpanishPeaks/': '/media/live-2f3c28ead0f4ee91/banner_block.jpg',
  '/international/USA/2026TevisCup/': '/media/live-12da323153a36982/banner_block.jpg',
  '/international/USA/2026WahatoyaCup/': '/media/live-bf1b43cf7105e749/banner_block.jpg',
};

export function liveEventBannerUrl(legacyRootUrl?: string): string | undefined {
  if (!legacyRootUrl) return undefined;
  const normalizedRoot = legacyRootUrl.endsWith('/') ? legacyRootUrl : `${legacyRootUrl}/`;
  return LIVE_EVENT_BANNERS_BY_ROOT[normalizedRoot];
}
