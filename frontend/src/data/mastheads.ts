export type MastheadKind = 'home' | 'section' | 'event' | 'fallback';

export type MastheadVariant = {
  id: string;
  kind: MastheadKind;
  title: string;
  subtitle: string;
  imageUrl: string;
  accentColor: string;
};

// Live legacy masthead and event banner assets staged by scripts/live_masthead_crawler.py.
const LIVE_NEWS_MASTHEAD = '/media/live-92af7d5218e4bd86/banner_sm_right_newsblogs.jpg';
const LIVE_EVENTS_MASTHEAD = '/media/live-9dbaeeb73a8053b0/banner_sm_right_events.jpg';
const LIVE_MARKET_MASTHEAD = '/media/live-2d6103e14a9f1541/banner_sm_right_market.jpg';
const LIVE_LEARN_MASTHEAD = '/media/live-a25cf78837f4a147/banner_sm_right_learn.jpg';
const LIVE_TEVIS_2026_MASTHEAD = '/media/live-12da323153a36982/banner_block.jpg';

const HOME_MASTHEAD: MastheadVariant = {
  id: 'home',
  kind: 'home',
  title: 'Endurance.Net',
  subtitle: 'News,Blogs',
  imageUrl: LIVE_NEWS_MASTHEAD,
  accentColor: '#a86e16',
};

const FALLBACK_MASTHEAD: MastheadVariant = {
  id: 'archive',
  kind: 'fallback',
  title: 'Endurance.Net',
  subtitle: 'Archive',
  imageUrl: LIVE_NEWS_MASTHEAD,
  accentColor: '#70460c',
};

const TEVIS_2026_MASTHEAD: MastheadVariant = {
  id: 'event-tevis-2026',
  kind: 'event',
  title: '2026 Tevis Cup',
  subtitle: 'Event Coverage',
  imageUrl: LIVE_TEVIS_2026_MASTHEAD,
  accentColor: '#6f1d1b',
};

const SECTION_MASTHEADS = {
  news: {
    id: 'section-news',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'News,Blogs',
    imageUrl: LIVE_NEWS_MASTHEAD,
    accentColor: '#12346f',
  },
  featured: {
    id: 'section-featured-stories',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Story Archive',
    imageUrl: LIVE_NEWS_MASTHEAD,
    accentColor: '#7a1616',
  },
  events: {
    id: 'section-events',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Events',
    imageUrl: LIVE_EVENTS_MASTHEAD,
    accentColor: '#9a6313',
  },
  results: {
    id: 'section-results',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Results',
    imageUrl: LIVE_EVENTS_MASTHEAD,
    accentColor: '#5d6f22',
  },
  galleries: {
    id: 'section-galleries',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Photo Galleries',
    imageUrl: LIVE_EVENTS_MASTHEAD,
    accentColor: '#7c4f13',
  },
  streams: {
    id: 'section-streams',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Streams',
    imageUrl: LIVE_NEWS_MASTHEAD,
    accentColor: '#355f7a',
  },
  community: {
    id: 'section-community',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Community',
    imageUrl: LIVE_MARKET_MASTHEAD,
    accentColor: '#8a4b16',
  },
  learn: {
    id: 'section-learn-aerc',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Learn,AERC',
    imageUrl: LIVE_LEARN_MASTHEAD,
    accentColor: '#215f46',
  },
} satisfies Record<string, MastheadVariant>;

function normalizePath(pathname: string): string {
  const cleanPath = pathname.split(/[?#]/, 1)[0] || '/';
  return cleanPath.replace(/\/+$/, '') || '/';
}

function isTevis2026Route(pathname: string): boolean {
  return (
    pathname === '/events/1' ||
    pathname === '/events/2026-tevis-cup' ||
    pathname.startsWith('/international/USA/2026TevisCup')
  );
}

export function resolveMastheadVariant(pathname: string): MastheadVariant {
  const normalized = normalizePath(pathname);

  if (normalized === '/' || normalized === '/index.html' || normalized === '/index_content.html') {
    return HOME_MASTHEAD;
  }

  if (isTevis2026Route(normalized)) {
    return TEVIS_2026_MASTHEAD;
  }

  if (normalized.startsWith('/CurrentNews') || normalized === '/news' || normalized.startsWith('/news/')) {
    return SECTION_MASTHEADS.news;
  }

  if (
    normalized.startsWith('/FeaturedStories') ||
    normalized === '/featured-stories' ||
    normalized.startsWith('/featured-stories/')
  ) {
    return SECTION_MASTHEADS.featured;
  }

  if (normalized === '/events' || normalized.startsWith('/events/')) {
    return SECTION_MASTHEADS.events;
  }

  if (normalized === '/results' || normalized.startsWith('/results/')) {
    return SECTION_MASTHEADS.results;
  }

  if (
    normalized === '/galleries' ||
    normalized.startsWith('/galleries/') ||
    normalized.startsWith('/gallery/') ||
    normalized.toLowerCase().includes('/gallery')
  ) {
    return SECTION_MASTHEADS.galleries;
  }

  if (normalized === '/streams' || normalized.startsWith('/streams/')) {
    return SECTION_MASTHEADS.streams;
  }

  if (
    normalized === '/community' ||
    normalized.startsWith('/community/') ||
    normalized.startsWith('/ClassifiedAds') ||
    normalized.startsWith('/Ridecamp')
  ) {
    return SECTION_MASTHEADS.community;
  }

  if (normalized === '/athletes' || normalized.startsWith('/athletes/')) {
    return SECTION_MASTHEADS.learn;
  }

  return FALLBACK_MASTHEAD;
}
