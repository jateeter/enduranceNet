import type { StreamSource } from '../types';

const modeLabels: Record<string, string> = {
  'atom-list': 'Atom list',
  'popup-channel-card': 'Popup cards',
  'single-entry-html': 'Single entry',
  'event-story-list': 'Event stories',
  'rss-list': 'RSS list',
  'google-reader-frontpage': 'Reader frontpage',
};

export function streamPresentationMode(stream: StreamSource) {
  return stream.defaultPresentation || 'rss-list';
}

export function streamPresentationLabel(stream: StreamSource) {
  const mode = streamPresentationMode(stream);
  return modeLabels[mode] ?? mode.replace(/-/g, ' ');
}

export function streamPresentationClass(stream: StreamSource) {
  return `stream-mode-${streamPresentationMode(stream).replace(/[^a-z0-9]+/gi, '-')}`;
}
