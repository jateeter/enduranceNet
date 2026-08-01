import { Link, useParams } from 'react-router-dom';
import { ArrowLeft, ExternalLink, Radio, Rss } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import StreamEntryCard from '../components/StreamEntryCard';
import { fetchStreamEntriesForSource, fetchStreamSource } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import type { StreamSource } from '../types';
import { dateLabel, hostLabel, sourceRssUrl } from '../utils/streamFormat';
import { streamPresentationLabel, streamPresentationXslt } from '../utils/streamPresentation';

function StreamActionLinks({ stream }: { stream: StreamSource }) {
  const rssUrl = sourceRssUrl(stream);

  return (
    <div className="stream-card-actions stream-detail-actions">
      {rssUrl && (
        <a href={rssUrl} target="_blank" rel="noreferrer">
          <Rss size={15} />
          RSS
        </a>
      )}
      {stream.canonicalAtomUrl && (
        <a href={stream.canonicalAtomUrl} target="_blank" rel="noreferrer">
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
    </div>
  );
}

function EmptyStreamEntries({ stream }: { stream: StreamSource }) {
  return (
    <section className="stream-empty-panel">
      <h2>Entry import pending</h2>
      <p>
        This stream is part of the validated Endurance.Net Blogger corpus, but normalized entries have not been imported into
        the NextGen database yet. The source links remain available so the archive is visible instead of becoming a dead end.
      </p>
      <StreamActionLinks stream={stream} />
    </section>
  );
}

export default function StreamDetailPage() {
  const { slug = '' } = useParams();
  const { data: stream, loading: streamLoading, error: streamError } = useApi(() => fetchStreamSource(slug));
  const { data: entries, loading: entriesLoading, error: entriesError } = useApi(() => fetchStreamEntriesForSource(slug));
  const loading = streamLoading || entriesLoading;
  const error = streamError ?? entriesError;

  return (
    <div className="streams-page stream-detail-page">
      <Link to="/streams" className="stream-back-link">
        <ArrowLeft size={15} />
        Streams
      </Link>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {stream && (
        <>
          <header className="streams-header stream-detail-header">
            <div>
              <span className="stream-eyebrow">{stream.streamGroup ?? 'Archive'}</span>
              <h1>{stream.title}</h1>
              <p>{stream.notes ?? 'Validated Endurance.Net stream source.'}</p>
            </div>
            <div className="streams-counts">
              <strong>{entries?.length ?? 0}</strong>
              <span>entries</span>
              <strong>{stream.active ? 'Yes' : 'No'}</strong>
              <span>active</span>
            </div>
          </header>

          <dl className="stream-detail-meta">
            <div>
              <dt>Updated</dt>
              <dd>{dateLabel(stream.latestCachedEntry)}</dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>{hostLabel(stream.legacyUrl ?? sourceRssUrl(stream))}</dd>
            </div>
            <div>
              <dt>Blog ID</dt>
              <dd>{stream.bloggerBlogId ?? 'OPML'}</dd>
            </div>
            <div>
              <dt>Local cache</dt>
              <dd>{stream.localCachePath ?? 'Legacy feed registry'}</dd>
            </div>
            <div>
              <dt>Presentation</dt>
              <dd>{streamPresentationLabel(stream)}</dd>
            </div>
          </dl>

          <StreamActionLinks stream={stream} />
          <div className="stream-transform-profile stream-detail-transform-profile">
            <span>{streamPresentationLabel(stream)}</span>
            <small>{streamPresentationXslt(stream).join(', ')}</small>
          </div>

          {entries && entries.length > 0 ? (
            <section className="stream-entry-list" aria-label={`${stream.title} entries`}>
              {entries.map((entry) => (
                <StreamEntryCard key={entry.id} entry={entry} stream={stream} showStreamTitle={false} />
              ))}
            </section>
          ) : (
            <EmptyStreamEntries stream={stream} />
          )}
        </>
      )}
    </div>
  );
}
