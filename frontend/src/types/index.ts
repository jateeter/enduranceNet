export interface Event {
  id: number;
  name: string;
  eventType: string;
  date: string;
  location: string;
  distance: string;
  description: string;
  registrationUrl?: string;
}

export interface EventMicrositeSection {
  id: string;
  title: string;
  kind: string;
  legacyUrl: string;
  summary: string;
  body: string;
  ctaLabel: string;
}

export interface EventMicrositeMedia {
  id: string;
  title: string;
  kind: string;
  publicUrl: string;
  sourcePath: string;
  altText: string;
  status: string;
}

export interface EventMicrositeBlocker {
  sourcePath: string;
  reason: string;
  status: string;
}

export interface EventMicrosite {
  eventId: number;
  slug: string;
  title: string;
  subtitle: string;
  date: string;
  location: string;
  distance: string;
  heroImageUrl: string;
  legacyRootUrl: string;
  overview: string;
  sections: EventMicrositeSection[];
  media: EventMicrositeMedia[];
  blockers: EventMicrositeBlocker[];
  legacyUrls: string[];
}

export interface News {
  id: number;
  title: string;
  summary: string;
  content: string;
  author: string;
  publishedAt: string;
  category: string;
  imageUrl?: string;
}

export interface HomepageAsset {
  id: number;
  placement: string;
  title: string;
  imageUrl: string;
  linkUrl: string;
  altText: string;
  sourceLegacyUrl: string;
  sourcePath: string;
  sortOrder: number;
}

export interface LegacyRedirect {
  id: number;
  legacyUrl: string;
  targetUrl: string;
  statusCode: number;
  reason: string;
}

export interface StreamSource {
  id: number;
  slug: string;
  title: string;
  provider: string;
  feedFormat: string;
  remoteUrl?: string;
  localCachePath?: string;
  legacyUrl?: string;
  defaultPresentation: string;
  active: boolean;
  bloggerBlogId?: string;
  canonicalAtomUrl?: string;
  canonicalRssUrl?: string;
  latestCachedEntry?: string;
  streamGroup?: string;
  notes?: string;
}

export interface StreamEntry {
  id: number;
  sourceId: number;
  providerEntryId: string;
  title: string;
  summaryHtml?: string;
  contentHtml?: string;
  author?: string;
  publishedAt?: string;
  updatedAt?: string;
  alternateUrl?: string;
  selfUrl?: string;
  relatedUrl?: string;
  commentsUrl?: string;
  checksumSha256?: string;
}

export interface StreamEntrySearchResult {
  entry: StreamEntry;
  source: StreamSource;
}

export interface Athlete {
  id: number;
  name: string;
  sport: string;
  country: string;
  bio: string;
  achievements: string[];
  imageUrl?: string;
}

export interface Result {
  id: number;
  eventId: number;
  eventName: string;
  athleteName: string;
  finishTime: string;
  place: number;
  category: string;
  year: number;
}

export interface PhotoGalleryItem {
  id: string;
  position: number;
  caption: string;
  thumbnailUrl: string;
  fullImageUrl: string;
  thumbnailSourcePath: string;
  fullImageSourcePath: string;
  itemPageSourcePath: string;
}

export interface PhotoGallery {
  id: string;
  slug: string;
  title: string;
  sourceRoot: string;
  legacyUrl: string;
  pattern: string;
  itemCount: number;
  parserVersion: string;
  items: PhotoGalleryItem[];
}
