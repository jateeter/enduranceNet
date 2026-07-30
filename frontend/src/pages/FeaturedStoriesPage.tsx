import NewsCard from '../components/NewsCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchNews } from '../api/endpoints';
import { BookOpen } from 'lucide-react';

export default function FeaturedStoriesPage() {
  const { data: news, loading, error } = useApi(fetchNews);
  const stories = news?.filter((item) => item.category === 'Featured Stories') ?? [];

  return (
    <div className="page">
      <div className="page-header">
        <BookOpen size={40} />
        <h1>Featured Stories</h1>
        <p>Longer reads, memorials, international coverage, and community-history pieces from the Endurance.Net archive.</p>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {news && (
        <div className="card-grid card-grid-wide">
          {stories.map((story) => (
            <NewsCard key={story.id} news={story} />
          ))}
        </div>
      )}
    </div>
  );
}
