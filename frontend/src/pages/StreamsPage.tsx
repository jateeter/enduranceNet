import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, ExternalLink, Radio, Rss } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchStreamSources } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import type { StreamSource } from '../types';
import { dateLabel, hostLabel } from '../utils/streamFormat';

const groupOrder = [
  'Active News',
  'Community',
  'Event & Team Archives',
  'News Archives',
  'Photo & Travel Journals',
  'Resources',
  'Archive',
];

function StreamCard({ stream }: { stream: StreamSource }) {
  const rssUrl = stream.canonicalRssUrl ?? stream.remoteUrl;
  const atomUrl = stream.canonicalAtomUrl;

  return (
    <article className={`stream-card${stream.active ? ' stream-card-active' : ''}`}>
      <header className="stream-card-header">
        <span className="stream-badge">{stream.streamGroup ?? 'Archive'}</span>
        <h2><Link to={`/streams/${stream.slug}`}>{stream.title}</Link></h2>
      </header>
      <dl className="stream-meta-grid">
        <div>
          <dt>Updated</dt>
          <dd>{dateLabel(stream.latestCachedEntry)}</dd>
        </div>
        <div>
          <dt>Source</dt>
          <dd>{hostLabel(stream.legacyUrl ?? stream.canonicalRssUrl)}</dd>
        </div>
        <div>
          <dt>Blog ID</dt>
          <dd>{stream.bloggerBlogId ?? 'OPML'}</dd>
        </div>
      </dl>
      <div className="stream-source-path">{stream.localCachePath ?? 'Legacy feed registry'}</div>
      <footer className="stream-card-actions">
        <Link to={`/streams/${stream.slug}`}>
          <BookOpen size={15} />
          Entries
        </Link>
        {rssUrl && (
          <a href={rssUrl} target="_blank" rel="noreferrer">
            <Rss size={15} />
            RSS
          </a>
        )}
        {atomUrl && (
          <a href={atomUrl} target="_blank" rel="noreferrer">
            <Radio size={15} />
            Atom
          </a>
        )}
        {stream.legacyUrl && (
          <a href={stream.legacyUrl} target="_blank" rel="noreferrer">
            <ExternalLink size={15} />
            Legacy
          </a>
        )}
      </footer>
    </article>
  );
}

export default function StreamsPage() {
  const { data, loading, error } = useApi(fetchStreamSources);
  const [selectedGroup, setSelectedGroup] = useState('Active News');
  const streams = data?.filter((stream) => stream.provider === 'blogger') ?? [];
  const groups = useMemo(() => {
    const present = new Set(streams.map((stream) => stream.streamGroup ?? 'Archive'));
    return groupOrder.filter((group) => present.has(group));
  }, [streams]);
  const visibleGroup = groups.includes(selectedGroup) ? selectedGroup : groups[0];
  const visibleStreams = streams.filter((stream) => (stream.streamGroup ?? 'Archive') === visibleGroup);
  const activeCount = streams.filter((stream) => stream.active).length;

  return (
    <div className="streams-page">
      <header className="streams-header">
        <div>
          <span className="stream-eyebrow">Endurance.Net RSS</span>
          <h1>Information Streams</h1>
        </div>
        <div className="streams-counts">
          <strong>{activeCount}</strong>
          <span>active</span>
          <strong>{streams.length}</strong>
          <span>validated</span>
        </div>
      </header>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {streams.length > 0 && (
        <>
          <nav className="stream-group-tabs" aria-label="RSS stream groups">
            {groups.map((group) => (
              <button
                key={group}
                type="button"
                className={group === visibleGroup ? 'active' : ''}
                onClick={() => setSelectedGroup(group)}
              >
                {group}
                <span>{streams.filter((stream) => (stream.streamGroup ?? 'Archive') === group).length}</span>
              </button>
            ))}
          </nav>

          <section className="stream-list" aria-label={`${visibleGroup} streams`}>
            {visibleStreams.map((stream) => (
              <StreamCard key={stream.id} stream={stream} />
            ))}
          </section>
        </>
      )}
    </div>
  );
}
