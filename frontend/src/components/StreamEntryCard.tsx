import { ExternalLink } from 'lucide-react';
import type { StreamEntry, StreamSource } from '../types';
import { dateLabel, htmlToText, sourceRssUrl } from '../utils/streamFormat';
import {
  streamPresentationClass,
  streamPresentationCta,
  streamPresentationLabel,
  streamPresentationSummaryLimit,
} from '../utils/streamPresentation';

interface StreamEntryCardProps {
  entry: StreamEntry;
  stream: StreamSource;
  showStreamTitle?: boolean;
}

export default function StreamEntryCard({ entry, stream, showStreamTitle = true }: StreamEntryCardProps) {
  const summaryLimit = streamPresentationSummaryLimit(stream);
  const importedSummary = htmlToText(entry.summaryHtml ?? entry.contentHtml);
  const summary = importedSummary.length > summaryLimit
    ? `${importedSummary.slice(0, summaryLimit).trim()}...`
    : importedSummary || 'No imported summary is available for this entry yet.';
  const entryUrl = entry.alternateUrl ?? entry.relatedUrl ?? stream.legacyUrl ?? sourceRssUrl(stream);
  const presentationLabel = streamPresentationLabel(stream);
  const ctaLabel = streamPresentationCta(stream);

  return (
    <article className={`stream-entry-card ${streamPresentationClass(stream)}`} tabIndex={0}>
      <header>
        <span>{entry.author ?? stream.title}</span>
        <time>{dateLabel(entry.publishedAt ?? entry.updatedAt)}</time>
      </header>
      <span className="stream-entry-mode">{presentationLabel}</span>
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
            {ctaLabel}
            <ExternalLink size={14} />
          </a>
        )}
      </footer>
    </article>
  );
}
