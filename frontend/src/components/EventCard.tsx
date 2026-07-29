import { Link } from 'react-router-dom';
import { Calendar, MapPin, ArrowRight } from 'lucide-react';
import type { Event } from '../types';

interface Props {
  event: Event;
}

export default function EventCard({ event }: Props) {
  const formattedDate = new Date(event.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="card">
      <div className="card-badge">{event.eventType}</div>
      <h3>{event.name}</h3>
      <div className="card-meta">
        <span><Calendar size={14} /> {formattedDate}</span>
        <span><MapPin size={14} /> {event.location}</span>
      </div>
      <p className="card-description">{event.description}</p>
      <div className="card-footer">
        <span className="card-distance">{event.distance}</span>
        <Link to={`/events/${event.id}`} className="btn btn-sm">
          Details <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
