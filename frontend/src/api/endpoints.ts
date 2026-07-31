import apiClient from './client';
import type { Event, HomepageAsset, LegacyRedirect, News, Athlete, PhotoGallery, Result, StreamEntry, StreamEntrySearchResult, StreamSource } from '../types';

export const fetchEvents = (): Promise<Event[]> =>
  apiClient.get<Event[]>('/events').then((r) => r.data);

export const fetchEvent = (id: number): Promise<Event> =>
  apiClient.get<Event>(`/events/${id}`).then((r) => r.data);

export const fetchNews = (): Promise<News[]> =>
  apiClient.get<News[]>('/news').then((r) => r.data);

export const fetchNewsItem = (id: number): Promise<News> =>
  apiClient.get<News>(`/news/${id}`).then((r) => r.data);

export const fetchHomepageAssets = (): Promise<HomepageAsset[]> =>
  apiClient.get<HomepageAsset[]>('/homepage-assets').then((r) => r.data);

export const fetchLegacyRedirects = (): Promise<LegacyRedirect[]> =>
  apiClient.get<LegacyRedirect[]>('/legacy-redirects').then((r) => r.data);

export const fetchStreamSources = (): Promise<StreamSource[]> =>
  apiClient.get<StreamSource[]>('/streams').then((r) => r.data);

export const fetchStreamSource = (slug: string): Promise<StreamSource> =>
  apiClient.get<StreamSource>(`/streams/${slug}`).then((r) => r.data);

export const fetchStreamEntries = (): Promise<StreamEntry[]> =>
  apiClient.get<StreamEntry[]>('/stream-entries').then((r) => r.data);

export const searchStreamEntries = (params: Record<string, string>): Promise<StreamEntrySearchResult[]> =>
  apiClient.get<StreamEntrySearchResult[]>('/stream-entries/search', { params }).then((r) => r.data);

export const fetchStreamEntriesForSource = (slug: string): Promise<StreamEntry[]> =>
  apiClient.get<StreamEntry[]>(`/streams/${slug}/entries`).then((r) => r.data);

export const fetchAthletes = (): Promise<Athlete[]> =>
  apiClient.get<Athlete[]>('/athletes').then((r) => r.data);

export const fetchAthlete = (id: number): Promise<Athlete> =>
  apiClient.get<Athlete>(`/athletes/${id}`).then((r) => r.data);

export const fetchResults = (): Promise<Result[]> =>
  apiClient.get<Result[]>('/results').then((r) => r.data);

export const fetchResultsByEvent = (eventId: number): Promise<Result[]> =>
  apiClient.get<Result[]>(`/results/${eventId}`).then((r) => r.data);

export const fetchGalleries = (): Promise<PhotoGallery[]> =>
  apiClient.get<PhotoGallery[]>('/galleries').then((r) => r.data);

export const fetchGallery = (slug: string): Promise<PhotoGallery> =>
  apiClient.get<PhotoGallery>(`/galleries/${slug}`).then((r) => r.data);

export const checkHealth = (): Promise<{ status: string; version: string }> =>
  apiClient.get('/health').then((r) => r.data);
