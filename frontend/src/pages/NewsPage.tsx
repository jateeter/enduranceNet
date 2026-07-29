import NewsCard from '../components/NewsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchNews } from '../api/endpoints';
import { Newspaper } from 'lucide-react';

export default function NewsPage() {
  const { data: news, loading, error } = useApi(fetchNews);

  return (
    <div className="page">
      <div className="page-header">
        <Newspaper size={40} />
        <h1>Latest News</h1>
        <p>Stay current with the latest stories from the world of endurance sports.</p>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {news && (
        <div className="card-grid card-grid-wide">
          {news.map((n) => (
            <NewsCard key={n.id} news={n} />
          ))}
        </div>
      )}
    </div>
  );
}
