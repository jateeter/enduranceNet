import type { StreamSource } from '../types';

interface StreamPresentationProfile {
  label: string;
  legacyXslt: string[];
  entryLimit: number;
  summaryLength: number;
  ctaLabel: string;
}

const fallbackProfile: StreamPresentationProfile = {
  label: 'RSS list',
  legacyXslt: ['channels/xslTemplates/rssList.xsl'],
  entryLimit: 25,
  summaryLength: 260,
  ctaLabel: 'Read story',
};

const presentationProfiles: Record<string, StreamPresentationProfile> = {
  'atom-list': {
    label: 'Atom list',
    legacyXslt: ['channels/xslTemplates/atomlist_Items.xsl'],
    entryLimit: 25,
    summaryLength: 280,
    ctaLabel: 'Read dispatch',
  },
  'popup-channel-card': {
    label: 'Popup cards',
    legacyXslt: ['channels/xslTemplates/atomlist_popup.xsl'],
    entryLimit: 25,
    summaryLength: 340,
    ctaLabel: 'Open item',
  },
  'single-entry-html': {
    label: 'Single entry',
    legacyXslt: ['channels/xslTemplates/atomsingle.xsl'],
    entryLimit: 1,
    summaryLength: 520,
    ctaLabel: 'Open entry',
  },
  'event-story-list': {
    label: 'Event stories',
    legacyXslt: ['channels/xslTemplates/atom_eventStoryList.xsl'],
    entryLimit: 40,
    summaryLength: 300,
    ctaLabel: 'Read event story',
  },
  'rss-list': fallbackProfile,
  'google-reader-frontpage': {
    label: 'Reader frontpage',
    legacyXslt: ['channels/xslTemplates/googleReaderAtom_frontPage.xsl'],
    entryLimit: 12,
    summaryLength: 220,
    ctaLabel: 'Read headline',
  },
  'stream-directory': {
    label: 'Stream directory',
    legacyXslt: ['channels/EnduranceNetFeeds.xml'],
    entryLimit: 100,
    summaryLength: 180,
    ctaLabel: 'Open source',
  },
};

export function streamPresentationMode(stream: StreamSource) {
  return stream.defaultPresentation || 'rss-list';
}

export function streamPresentationProfile(stream: StreamSource) {
  return presentationProfiles[streamPresentationMode(stream)] ?? fallbackProfile;
}

export function streamPresentationLabel(stream: StreamSource) {
  return streamPresentationProfile(stream).label;
}

export function streamPresentationClass(stream: StreamSource) {
  return `stream-mode-${streamPresentationMode(stream).replace(/[^a-z0-9]+/gi, '-')}`;
}

export function streamPresentationXslt(stream: StreamSource) {
  return streamPresentationProfile(stream).legacyXslt;
}

export function streamPresentationCta(stream: StreamSource) {
  return streamPresentationProfile(stream).ctaLabel;
}

export function streamPresentationSummaryLimit(stream: StreamSource) {
  return streamPresentationProfile(stream).summaryLength;
}
