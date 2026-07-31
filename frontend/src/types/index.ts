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
