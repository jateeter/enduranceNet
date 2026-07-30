const legacyAnchorTargets: Record<string, string> = {
  '/CurrentNews/#TRBG': '/news/7',
  '/CurrentNews/#ChinaRide': '/news/8',
  '/FeaturedStories/#UAEWEC': '/news/4',
  '/FeaturedStories/#AnnKratochvil': '/news/5',
  '/FeaturedStories/#AngieRochna': '/news/6',
};

const legacyPathTargets: Record<string, string> = {
  '/index.html': '/',
  '/index_content.html': '/',
  '/CurrentNews': '/news',
  '/CurrentNews/': '/news',
  '/CurrentNews/index.html': '/news',
  '/CurrentNews/indexInternal.html': '/news',
  '/FeaturedStories': '/featured-stories',
  '/FeaturedStories/': '/featured-stories',
  '/FeaturedStories/index.html': '/featured-stories',
  '/FeaturedStories/indexInternal.html': '/featured-stories',
  '/newsblogs': '/news',
  '/newsblogs/': '/news',
  '/newsblogs/index.html': '/news',
  '/events/': '/events',
  '/events/index.html': '/events',
  '/ClassifiedAds': '/community#classifieds',
  '/ClassifiedAds/': '/community#classifieds',
  '/ClassifiedAds/index.html': '/community#classifieds',
  '/RidecampFriend': '/community#ridecamp',
  '/RidecampFriend/': '/community#ridecamp',
  '/RidecampFriend/index.html': '/community#ridecamp',
};

export function resolveLegacyRedirect(pathname: string, hash = ''): string {
  const pathWithHash = `${pathname}${hash}`;
  return legacyAnchorTargets[pathWithHash] ?? legacyPathTargets[pathname] ?? '/';
}
