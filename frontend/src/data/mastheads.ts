export type MastheadKind = 'home' | 'section' | 'event' | 'fallback';

export type MastheadVariant = {
  id: string;
  kind: MastheadKind;
  title: string;
  subtitle: string;
  imageUrl: string;
  accentColor: string;
};

const GENERATED_MASTHEAD_IMAGE = '/media/site/masthead-background-v1.jpg';

const HOME_MASTHEAD: MastheadVariant = {
  id: 'home',
  kind: 'home',
  title: 'Endurance.Net',
  subtitle: 'News,Blogs',
  imageUrl: GENERATED_MASTHEAD_IMAGE,
  accentColor: '#a86e16',
};

const FALLBACK_MASTHEAD: MastheadVariant = {
  id: 'archive',
  kind: 'fallback',
  title: 'Endurance.Net',
  subtitle: 'Archive',
  imageUrl: GENERATED_MASTHEAD_IMAGE,
  accentColor: '#70460c',
};

const TEVIS_2026_MASTHEAD: MastheadVariant = {
  id: 'event-tevis-2026',
  kind: 'event',
  title: '2026 Tevis Cup',
  subtitle: 'Event Coverage',
  imageUrl: GENERATED_MASTHEAD_IMAGE,
  accentColor: '#6f1d1b',
};

const SECTION_MASTHEADS = {
  news: {
    id: 'section-news',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'News,Blogs',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#12346f',
  },
  featured: {
    id: 'section-featured-stories',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Story Archive',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#7a1616',
  },
  events: {
    id: 'section-events',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Events',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#9a6313',
  },
  results: {
    id: 'section-results',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Results',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#5d6f22',
  },
  galleries: {
    id: 'section-galleries',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Photo Galleries',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#7c4f13',
  },
  streams: {
    id: 'section-streams',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Streams',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#355f7a',
  },
  community: {
    id: 'section-community',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Community',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
    accentColor: '#8a4b16',
  },
  learn: {
    id: 'section-learn-aerc',
    kind: 'section',
    title: 'Endurance.Net',
    subtitle: 'Learn,AERC',
    imageUrl: GENERATED_MASTHEAD_IMAGE,
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
