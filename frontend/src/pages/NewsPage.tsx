import NewsCard from '../components/NewsCard';
import LegacySectionHeader from '../components/LegacySectionHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchNews } from '../api/endpoints';
import { Newspaper } from 'lucide-react';

export default function NewsPage() {
  const { data: news, loading, error } = useApi(fetchNews);
  const currentNews = news?.filter((item) => item.category === 'Current News') ?? [];

  return (
    <div className="page">
      <LegacySectionHeader
        title="Current News"
        subtitle="The weekly Endurance.Net digest: ride coverage, international updates, galleries, and community notes."
        banner="/images/banner_sm_right_newsblogs.jpg"
        icon={<Newspaper size={28} />}
      />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {news && (
        <div className="news-list-grid">
          {currentNews.map((n) => (
            <NewsCard key={n.id} news={n} />
          ))}
        </div>
      )}
    </div>
  );
}
