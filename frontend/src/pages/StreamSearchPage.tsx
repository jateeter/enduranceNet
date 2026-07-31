import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { ArrowLeft, Search } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import StreamEntryCard from '../components/StreamEntryCard';
import { searchStreamEntries } from '../api/endpoints';
import type { StreamEntrySearchResult } from '../types';

const streamGroups = [
  'Active News',
  'Community',
  'Event & Team Archives',
  'News Archives',
  'Photo & Travel Journals',
  'Resources',
  'Archive',
];

function paramsObject(searchParams: URLSearchParams) {
  const params: Record<string, string> = {};
  ['q', 'group', 'active', 'year'].forEach((key) => {
    const value = searchParams.get(key);
    if (value) params[key] = value;
  });
  return params;
}

export default function StreamSearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') ?? '');
  const [results, setResults] = useState<StreamEntrySearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const group = searchParams.get('group') ?? '';
  const active = searchParams.get('active') ?? '';
  const year = searchParams.get('year') ?? '';
  const activeFilterCount = ['q', 'group', 'active', 'year'].filter((key) => searchParams.get(key)).length;
  const sourceCount = useMemo(() => new Set(results.map((result) => result.source.slug)).size, [results]);

  useEffect(() => {
    setQuery(searchParams.get('q') ?? '');
    setLoading(true);
    setError(null);

    searchStreamEntries(paramsObject(searchParams))
      .then((data) => {
        setResults(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message ?? 'Unable to search stream entries');
        setLoading(false);
      });
  }, [searchParams]);

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    setSearchParams(next);
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    updateParam('q', query.trim());
  }

  return (
    <div className="streams-page stream-search-page">
      <Link to="/streams" className="stream-back-link">
        <ArrowLeft size={15} />
        Streams
      </Link>

      <header className="streams-header stream-search-header">
        <div>
          <span className="stream-eyebrow">Endurance.Net RSS</span>
          <h1>Corpus Search</h1>
          <p>Search imported stream entries across active and archival Blogger sources with source provenance preserved.</p>
        </div>
        <div className="streams-counts">
          <strong>{results.length}</strong>
          <span>entries</span>
          <strong>{sourceCount}</strong>
          <span>sources</span>
        </div>
      </header>

      <section className="stream-search-panel" aria-label="RSS corpus filters">
        <form className="stream-search-form" onSubmit={submitSearch}>
          <label>
            <span>Search</span>
            <div className="stream-search-input">
              <Search size={16} />
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Title, summary, author, source" />
            </div>
          </label>
          <button type="submit">Apply</button>
        </form>

        <div className="stream-search-grid">
          <label>
            <span>Group</span>
            <select value={group} onChange={(event) => updateParam('group', event.target.value)}>
              <option value="">All groups</option>
              {streamGroups.map((streamGroup) => (
                <option key={streamGroup} value={streamGroup}>{streamGroup}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Status</span>
            <select value={active} onChange={(event) => updateParam('active', event.target.value)}>
              <option value="">Active and archive</option>
              <option value="true">Active streams</option>
              <option value="false">Archive streams</option>
            </select>
          </label>
          <label>
            <span>Year</span>
            <input value={year} onChange={(event) => updateParam('year', event.target.value.replace(/\D/g, '').slice(0, 4))} placeholder="YYYY" />
          </label>
          <button type="button" onClick={() => setSearchParams(new URLSearchParams())} disabled={activeFilterCount === 0}>
            Reset
          </button>
        </div>
      </section>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && (
        <>
          <div className="stream-search-results-header">
            <strong>{results.length}</strong>
            <span>matched entries from {sourceCount} sources</span>
          </div>
          {results.length > 0 ? (
            <section className="stream-entry-list" aria-label="RSS corpus search results">
              {results.map((result) => (
                <StreamEntryCard key={`${result.source.slug}-${result.entry.id}`} entry={result.entry} stream={result.source} />
              ))}
            </section>
          ) : (
            <section className="stream-empty-panel">
              <h2>No matching entries</h2>
              <p>Try a broader text search, clear the year, or include both active and archival streams.</p>
            </section>
          )}
        </>
      )}
    </div>
  );
}
