import { Link } from 'react-router-dom';
import { ChevronRight, Activity, Users, Trophy, Globe } from 'lucide-react';

const stats = [
  { icon: <Activity size={28} />, value: '500+', label: 'Events Tracked' },
  { icon: <Users size={28} />, value: '50K+', label: 'Athletes' },
  { icon: <Trophy size={28} />, value: '1M+', label: 'Race Results' },
  { icon: <Globe size={28} />, value: '80+', label: 'Countries' },
];

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-content">
        <div className="hero-badge">Est. 1995 · Reborn for a New Era</div>
        <h1>
          The World's Premier<br />
          <span className="hero-highlight">Endurance Sports</span><br />
          Community
        </h1>
        <p className="hero-subtitle">
          From ultramarathons to IRONMAN triathlons, cycling grand tours to mountain races —
          EnduranceNet is your home for news, events, athletes, and results from the world's
          most demanding sports.
        </p>
        <div className="hero-actions">
          <Link to="/events" className="btn btn-primary">
            Explore Events <ChevronRight size={18} />
          </Link>
          <Link to="/news" className="btn btn-outline">
            Latest News
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
