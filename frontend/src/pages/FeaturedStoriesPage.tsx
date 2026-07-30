import NewsCard from '../components/NewsCard';
import LegacySectionHeader from '../components/LegacySectionHeader';
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
      <LegacySectionHeader
        title="Featured Stories"
        subtitle="Longer reads, memorials, international coverage, and community-history pieces from the Endurance.Net archive."
        banner="/images/ENbanner_right_stories.jpg"
        icon={<BookOpen size={28} />}
      />

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
