import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { fetchNewsItem } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { ArrowLeft, User, Clock, Tag } from 'lucide-react';
import { legacyAssetUrl } from '../utils/legacyAssets';

export default function NewsDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: news, loading, error } = useApi(() => fetchNewsItem(Number(id)));

  return (
    <div className="page page-narrow">
      <Link to="/news" className="back-link">
        <ArrowLeft size={16} /> Back to News
      </Link>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {news && (
        <article className="article">
          <div className="card-badge">{news.category}</div>
          <h1>{news.title}</h1>
          {news.imageUrl && (
            <img className="article-image" src={legacyAssetUrl(news.imageUrl)} alt="" />
          )}
          <div className="article-meta">
            <span><User size={14} /> {news.author}</span>
            <span>
              <Clock size={14} />
              {new Date(news.publishedAt).toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric',
              })}
            </span>
            <span><Tag size={14} /> {news.category}</span>
          </div>
          <p className="article-lead">{news.summary}</p>
          <div className="article-body">
            {news.content.split('\n').map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>
        </article>
      )}
    </div>
  );
}
