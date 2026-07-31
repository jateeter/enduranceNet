import StreamEntryCard from '../components/StreamEntryCard';
import type { StreamEntry, StreamSource } from '../types';

const modes = [
  { mode: 'atom-list', title: 'Atom List', group: 'Active News' },
  { mode: 'popup-channel-card', title: 'Popup Channel Card', group: 'Photo & Travel Journals' },
  { mode: 'single-entry-html', title: 'Single Entry HTML', group: 'News Archives' },
  { mode: 'event-story-list', title: 'Event Story List', group: 'Event & Team Archives' },
  { mode: 'rss-list', title: 'RSS List', group: 'Resources' },
  { mode: 'google-reader-frontpage', title: 'Google Reader Frontpage', group: 'Archive' },
];

function sourceFor(index: number, mode: string, title: string, group: string): StreamSource {
  return {
    id: 9000 + index,
    slug: `preview-${mode}`,
    title,
    provider: 'fixture',
    feedFormat: mode.includes('rss') ? 'rss-2.0' : 'atom-1.0',
    defaultPresentation: mode,
    active: index < 2,
    streamGroup: group,
    legacyUrl: `http://feeds.endurance.net/preview/${mode}/`,
    localCachePath: `/channels/preview/${mode}.xml`,
  };
}

function entryFor(index: number, mode: string, title: string): StreamEntry {
  return {
    id: 10000 + index,
    sourceId: 9000 + index,
    providerEntryId: `fixture-${mode}`,
    title: `${title} Fixture Headline`,
    summaryHtml:
      "<p>This first paragraph is the accessible preview content for the legacy stream mode. <script>alert('blocked')</script><img src='http://www.endurance.net/images/news.jpg' /></p>",
    author: 'Endurance.Net',
    publishedAt: '2026-07-31T00:00:00Z',
    alternateUrl: `http://feeds.endurance.net/preview/${mode}/story.html`,
  };
}

export default function StreamPresentationPreviewPage() {
  return (
    <div className="streams-page stream-preview-page">
      <header className="streams-header stream-search-header">
        <div>
          <span className="stream-eyebrow">Visual QA</span>
          <h1>Stream Presentation Modes</h1>
          <p>Fixture rendering for legacy RSS and Blogger presentation compatibility.</p>
        </div>
        <div className="streams-counts">
          <strong>{modes.length}</strong>
          <span>modes</span>
          <strong>2</strong>
          <span>viewports</span>
        </div>
      </header>

      <section className="stream-entry-list stream-preview-grid" aria-label="Presentation mode fixture cards">
        {modes.map(({ mode, title, group }, index) => (
          <div key={mode} data-mode={mode}>
            <StreamEntryCard entry={entryFor(index, mode, title)} stream={sourceFor(index, mode, title, group)} />
          </div>
        ))}
      </section>
    </div>
  );
}
