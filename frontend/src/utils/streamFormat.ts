import type { StreamSource } from '../types';
import { rewriteLegacyMediaReferences } from './legacyAssets';

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
  return sanitizeStreamHtml(value)
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

export function sanitizeStreamHtml(value?: string) {
  if (!value) return '';
  return rewriteLegacyMediaReferences(value)
    .replace(/<\s*(script|style|iframe|object|embed)[\s\S]*?<\s*\/\s*\1\s*>/gi, '')
    .replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, '')
    .replace(/\s(?:href|src)\s*=\s*(['"])\s*javascript:[\s\S]*?\1/gi, '');
}
