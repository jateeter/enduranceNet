import type { StreamSource } from '../types';

export function sourceRssUrl(stream: StreamSource) {
  return stream.canonicalRssUrl ?? stream.remoteUrl;
}

export function dateLabel(value?: string) {
  if (!value) return 'Archive';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value.slice(0, 10);
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(parsed);
}

export function hostLabel(value?: string) {
  if (!value) return 'Legacy cache';
  try {
    return new URL(value).hostname.replace(/^www\./, '');
  } catch {
    return value;
  }
}

export function htmlToText(value?: string) {
  if (!value) return '';
  return value
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}
