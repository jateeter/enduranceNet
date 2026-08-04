import { Link } from 'react-router-dom';
import { Calendar, MapPin, ArrowRight } from 'lucide-react';
import type { Event } from '../types';
import { liveEventBannerUrl } from '../data/liveEventBanners';

interface Props {
  event: Event;
}

export default function EventCard({ event }: Props) {
  const formattedDate = new Date(event.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const bannerUrl = liveEventBannerUrl(event.registrationUrl);
  const detailPath = event.id === 1 ? '/events/2026-tevis-cup' : `/events/${event.id}`;

  return (
    <div className="card">
      {bannerUrl && <img className="card-image card-image-banner" src={bannerUrl} alt="" loading="lazy" />}
      <div className="card-badge">{event.eventType}</div>
      <h3>{event.name}</h3>
      <div className="card-meta">
        <span><Calendar size={14} /> {formattedDate}</span>
        <span><MapPin size={14} /> {event.location}</span>
      </div>
      <p className="card-description">{event.description}</p>
      <div className="card-footer">
        <span className="card-distance">{event.distance}</span>
        <Link to={detailPath} className="btn btn-sm">
          Details <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
