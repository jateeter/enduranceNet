import { Link } from 'react-router-dom';
import Hero from '../components/Hero';
import EventCard from '../components/EventCard';
import NewsCard from '../components/NewsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents, fetchNews } from '../api/endpoints';
import { ArrowRight, BadgeDollarSign, Mail, MessageSquareText } from 'lucide-react';

export default function HomePage() {
  const events = useApi(fetchEvents);
  const news = useApi(fetchNews);
  const currentNews = news.data?.filter((item) => item.category !== 'Featured Stories') ?? [];
  const featuredStories = news.data?.filter((item) => item.category === 'Featured Stories') ?? [];

  return (
    <>
      <Hero />

      {/* Current News */}
      <section className="section">
        <div className="section-header">
          <h2>This Week's Current News</h2>
          <Link to="/news" className="btn btn-outline btn-sm">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {news.loading && <LoadingSpinner />}
        {news.error && <ErrorMessage message={news.error} />}
        {news.data && (
          <div className="card-grid">
            {currentNews.slice(0, 3).map((n) => (
              <NewsCard key={n.id} news={n} />
            ))}
          </div>
        )}
      </section>

      {/* Featured Stories */}
      <section className="section section-alt">
        <div className="section-header">
          <h2>This Week's Featured Stories</h2>
          <Link to="/featured-stories" className="btn btn-outline btn-sm">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {news.loading && <LoadingSpinner />}
        {news.error && <ErrorMessage message={news.error} />}
        {news.data && (
          <div className="card-grid">
            {featuredStories.slice(0, 3).map((n) => (
              <NewsCard key={n.id} news={n} />
            ))}
          </div>
        )}
      </section>

      {/* Event Coverage */}
      <section className="section">
        <div className="section-header">
          <h2>Event Coverage Archive</h2>
          <Link to="/events" className="btn btn-outline btn-sm">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {events.loading && <LoadingSpinner />}
        {events.error && <ErrorMessage message={events.error} />}
        {events.data && (
          <div className="card-grid">
            {events.data.slice(0, 3).map((e) => (
              <EventCard key={e.id} event={e} />
            ))}
          </div>
        )}
      </section>

      <section className="section section-alt">
        <div className="section-header">
          <h2>Community & Marketplace</h2>
        </div>
        <div className="feature-grid">
          <Link to="/athletes" className="feature-link">
            <MessageSquareText size={24} />
            <span>Ridecamp</span>
            <p>Community archives, history, and migration staging for legacy message pages.</p>
          </Link>
          <Link to="/results" className="feature-link">
            <BadgeDollarSign size={24} />
            <span>Classifieds</span>
            <p>Marketplace migration target for horses, tack, trailers, jobs, and related listings.</p>
          </Link>
          <a href="mailto:merri@endurance.net" className="feature-link">
            <Mail size={24} />
            <span>Contact</span>
            <p>Legacy contact path preserved while the new editorial workflow is built.</p>
          </a>
        </div>
      </section>
    </>
  );
}
