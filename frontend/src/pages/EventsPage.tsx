import { useMemo, useState } from 'react';
import EventCard from '../components/EventCard';
import LegacySectionHeader from '../components/LegacySectionHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents } from '../api/endpoints';
import { Calendar, Filter, Globe2, MapPinned, Search } from 'lucide-react';

export default function EventsPage() {
  const { data: events, loading, error } = useApi(fetchEvents);
  const [year, setYear] = useState('all');
  const [country, setCountry] = useState('all');
  const [eventType, setEventType] = useState('all');
  const [query, setQuery] = useState('');

  const archive = useMemo(() => {
    const source = events ?? [];
    const years = Array.from(new Set(source.map((event) => new Date(event.date).getFullYear().toString()))).sort();
    const countries = Array.from(new Set(source.map((event) => event.location.split(',').pop()?.trim() ?? event.location))).sort();
    const eventTypes = Array.from(new Set(source.map((event) => event.eventType))).sort();
    const filtered = source.filter((event) => {
      const eventYear = new Date(event.date).getFullYear().toString();
      const eventCountry = event.location.split(',').pop()?.trim() ?? event.location;
      const searchable = `${event.name} ${event.location} ${event.description}`.toLowerCase();
      return (year === 'all' || eventYear === year)
        && (country === 'all' || eventCountry === country)
        && (eventType === 'all' || event.eventType === eventType)
        && (!query.trim() || searchable.includes(query.trim().toLowerCase()));
    });

    return { years, countries, eventTypes, filtered };
  }, [country, eventType, events, query, year]);

  return (
    <div className="page">
      <LegacySectionHeader
        title="Endurance Events"
        subtitle="Browse endurance riding coverage, international championships, ride-series pages, results, and gallery archives."
        banner="/images/banner_sm_right_events.jpg"
        icon={<Calendar size={28} />}
      />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {events && (
        <>
          <div className="archive-toolbar">
            <div className="archive-stat-row">
              <span><Calendar size={16} /> {events.length} migrated event hubs</span>
              <span><Globe2 size={16} /> {archive.countries.length} countries</span>
              <span><MapPinned size={16} /> {archive.eventTypes.length} coverage types</span>
            </div>
            <div className="archive-filter-grid">
              <label>
                <Filter size={14} />
                <select value={year} onChange={(event) => setYear(event.target.value)}>
                  <option value="all">All years</option>
                  {archive.years.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label>
                <Globe2 size={14} />
                <select value={country} onChange={(event) => setCountry(event.target.value)}>
                  <option value="all">All countries</option>
                  {archive.countries.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label>
                <MapPinned size={14} />
                <select value={eventType} onChange={(event) => setEventType(event.target.value)}>
                  <option value="all">All types</option>
                  {archive.eventTypes.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label>
                <Search size={14} />
                <input
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                  placeholder="Ride, region, or archive term"
                />
              </label>
            </div>
          </div>

          <div className="card-grid card-grid-wide">
            {archive.filtered.map((e) => (
              <EventCard key={e.id} event={e} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
