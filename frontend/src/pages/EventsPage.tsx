import EventCard from '../components/EventCard';
import LegacySectionHeader from '../components/LegacySectionHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents } from '../api/endpoints';
import { Calendar } from 'lucide-react';

export default function EventsPage() {
  const { data: events, loading, error } = useApi(fetchEvents);

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
        <div className="card-grid card-grid-wide">
          {events.map((e) => (
            <EventCard key={e.id} event={e} />
          ))}
        </div>
      )}
    </div>
  );
}
