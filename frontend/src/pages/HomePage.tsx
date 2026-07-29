import { Link } from 'react-router-dom';
import Hero from '../components/Hero';
import EventCard from '../components/EventCard';
import NewsCard from '../components/NewsCard';
import AthleteCard from '../components/AthleteCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents, fetchNews, fetchAthletes } from '../api/endpoints';
import { ArrowRight } from 'lucide-react';

export default function HomePage() {
  const events = useApi(fetchEvents);
  const news = useApi(fetchNews);
  const athletes = useApi(fetchAthletes);

  return (
    <>
      <Hero />

      {/* Featured Events */}
      <section className="section">
        <div className="section-header">
          <h2>Upcoming Events</h2>
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

      {/* Latest News */}
      <section className="section section-alt">
        <div className="section-header">
          <h2>Latest News</h2>
          <Link to="/news" className="btn btn-outline btn-sm">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {news.loading && <LoadingSpinner />}
        {news.error && <ErrorMessage message={news.error} />}
        {news.data && (
          <div className="card-grid">
            {news.data.slice(0, 3).map((n) => (
              <NewsCard key={n.id} news={n} />
            ))}
          </div>
        )}
      </section>

      {/* Featured Athletes */}
      <section className="section">
        <div className="section-header">
          <h2>Featured Athletes</h2>
          <Link to="/athletes" className="btn btn-outline btn-sm">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        {athletes.loading && <LoadingSpinner />}
        {athletes.error && <ErrorMessage message={athletes.error} />}
        {athletes.data && (
          <div className="card-grid">
            {athletes.data.slice(0, 3).map((a) => (
              <AthleteCard key={a.id} athlete={a} />
            ))}
          </div>
        )}
      </section>
    </>
  );
}
