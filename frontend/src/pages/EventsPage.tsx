import EventCard from '../components/EventCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents } from '../api/endpoints';
import { Calendar } from 'lucide-react';

export default function EventsPage() {
  const { data: events, loading, error } = useApi(fetchEvents);

  return (
    <div className="page">
      <div className="page-header">
        <Calendar size={40} />
        <h1>Endurance Events</h1>
        <p>Discover the world's most prestigious endurance competitions across running, triathlon, cycling, and more.</p>
      </div>

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
