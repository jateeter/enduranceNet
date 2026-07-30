import NewsCard from '../components/NewsCard';
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
      <div className="page-header">
        <Newspaper size={40} />
        <h1>Current News</h1>
        <p>The weekly Endurance.Net digest: ride coverage, international updates, galleries, and community notes.</p>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {news && (
        <div className="card-grid card-grid-wide">
          {currentNews.map((n) => (
            <NewsCard key={n.id} news={n} />
          ))}
        </div>
      )}
    </div>
  );
}
