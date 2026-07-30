import { Link } from 'react-router-dom';
import Hero from '../components/Hero';
import EventCard from '../components/EventCard';
import NewsCard from '../components/NewsCard';
import HomepageAssetRail from '../components/HomepageAssetRail';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents, fetchHomepageAssets, fetchNews } from '../api/endpoints';
import { ArrowRight, BadgeDollarSign, Mail, MessageSquareText } from 'lucide-react';

export default function HomePage() {
  const events = useApi(fetchEvents);
  const news = useApi(fetchNews);
  const homepageAssets = useApi(fetchHomepageAssets);
  const currentNews = news.data?.filter((item) => item.category === 'Current News') ?? [];
  const featuredStories = news.data?.filter((item) => item.category === 'Featured Stories') ?? [];
  const assetsFor = (placement: string) =>
    homepageAssets.data?.filter((asset) => asset.placement === placement) ?? [];

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
          <div className="legacy-home-grid">
            <div className="headline-panel">
              <ol className="headline-list">
                {currentNews.slice(0, 8).map((n) => (
                  <li key={n.id}>
                    <Link to={`/news/${n.id}`}>{n.title}</Link>
                    <span>{n.summary}</span>
                  </li>
                ))}
              </ol>
            </div>
            <div className="feature-card-stack">
              {currentNews.slice(0, 2).map((n) => (
                <NewsCard key={n.id} news={n} />
              ))}
            </div>
          </div>
        )}
        {homepageAssets.loading && <LoadingSpinner />}
        {homepageAssets.error && <ErrorMessage message={homepageAssets.error} />}
        <HomepageAssetRail title="Brought to you by" assets={assetsFor('current_news_sponsor')} variant="logo" />
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
          <div className="legacy-card-list">
            {featuredStories.slice(0, 3).map((n) => (
              <NewsCard key={n.id} news={n} />
            ))}
          </div>
        )}
        <HomepageAssetRail title="Featured Story Media" assets={assetsFor('featured_story')} />
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
        <HomepageAssetRail title="Legacy Homepage Event Blocks" assets={assetsFor('event_coverage')} />
      </section>

      <section className="section section-alt">
        <div className="section-header">
          <h2>Advertisers & Sponsors</h2>
          <Link to="/featured-stories" className="btn btn-outline btn-sm">
            Featured archive <ArrowRight size={14} />
          </Link>
        </div>
        <HomepageAssetRail title="Homepage Advertiser Manifest" assets={assetsFor('advertiser')} variant="logo" />
        <HomepageAssetRail title="Follow Endurance.Net" assets={assetsFor('social')} variant="logo" />
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
