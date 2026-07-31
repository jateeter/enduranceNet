import { ExternalLink } from 'lucide-react';
import type { StreamEntry, StreamSource } from '../types';
import { dateLabel, htmlToText, sourceRssUrl } from '../utils/streamFormat';

interface StreamEntryCardProps {
  entry: StreamEntry;
  stream: StreamSource;
  showStreamTitle?: boolean;
}

export default function StreamEntryCard({ entry, stream, showStreamTitle = true }: StreamEntryCardProps) {
  const summary = htmlToText(entry.summaryHtml ?? entry.contentHtml) || 'No imported summary is available for this entry yet.';
  const entryUrl = entry.alternateUrl ?? entry.relatedUrl ?? stream.legacyUrl ?? sourceRssUrl(stream);

  return (
    <article className="stream-entry-card" tabIndex={0}>
      <header>
        <span>{entry.author ?? stream.title}</span>
        <time>{dateLabel(entry.publishedAt ?? entry.updatedAt)}</time>
      </header>
      <h2>
        {entryUrl ? (
          <a href={entryUrl} target="_blank" rel="noreferrer" title={summary}>
            {entry.title}
          </a>
        ) : (
          entry.title
        )}
      </h2>
      <p>{summary}</p>
      <footer>
        <span>{showStreamTitle ? stream.title : stream.streamGroup ?? 'Archive'}</span>
        {entryUrl && (
          <a href={entryUrl} target="_blank" rel="noreferrer">
            Read story
            <ExternalLink size={14} />
          </a>
        )}
      </footer>
    </article>
  );
}
