import { Link } from 'react-router-dom';
import { BookOpen, Camera, ChevronRight, Globe2, Newspaper } from 'lucide-react';

const stats = [
  { icon: <Newspaper size={28} />, value: 'Current', label: 'Weekly News Digest' },
  { icon: <BookOpen size={28} />, value: 'Featured', label: 'Stories & Memorials' },
  { icon: <Camera size={28} />, value: 'Archive', label: 'Ride Galleries' },
  { icon: <Globe2 size={28} />, value: 'Global', label: 'Endurance Coverage' },
];

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <div className="hero-badge">Endurance Riding News · Stories · Events</div>
        <h1>
          Endurance.Net<br />
          <span className="hero-highlight">Next Generation</span><br />
          Archive & Newsroom
        </h1>
        <p className="hero-subtitle">
          The modern home for endurance riding current news, featured stories,
          event coverage, galleries, Ridecamp history, classifieds, and advertiser
          resources migrated from the legacy PHP site.
        </p>
        <div className="hero-actions">
          <Link to="/news" className="btn btn-primary">
            Current News <ChevronRight size={18} />
          </Link>
          <Link to="/featured-stories" className="btn btn-outline">
            Featured Stories
          </Link>
        </div>
      </div>

      <div className="hero-stats">
        {stats.map(({ icon, value, label }) => (
          <div key={label} className="stat-card">
            <div className="stat-icon">{icon}</div>
            <div className="stat-value">{value}</div>
            <div className="stat-label">{label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
