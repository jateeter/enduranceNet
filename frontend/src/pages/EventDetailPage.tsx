import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { fetchEvent } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { ArrowLeft, Calendar, MapPin, ExternalLink } from 'lucide-react';

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: event, loading, error } = useApi(() => fetchEvent(Number(id)));

  return (
    <div className="page page-narrow">
      <Link to="/events" className="back-link">
        <ArrowLeft size={16} /> Back to Events
      </Link>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {event && (
        <div className="event-detail">
          <div className="card-badge">{event.eventType}</div>
          <h1>{event.name}</h1>
          <div className="card-meta">
            <span>
              <Calendar size={14} />
              {new Date(event.date).toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric',
              })}
            </span>
            <span><MapPin size={14} /> {event.location}</span>
          </div>
          <p className="article-lead">{event.description}</p>
          <div className="event-info-grid">
            <div className="info-block">
              <h4>Distance</h4>
              <p>{event.distance}</p>
            </div>
            <div className="info-block">
              <h4>Location</h4>
              <p>{event.location}</p>
            </div>
          </div>
          {event.registrationUrl && (
            <a
              href={event.registrationUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              Register Now <ExternalLink size={14} />
            </a>
          )}
        </div>
      )}
    </div>
  );
}
