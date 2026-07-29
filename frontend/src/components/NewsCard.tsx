import { Link } from 'react-router-dom';
import { Clock, User, Tag, ArrowRight } from 'lucide-react';
import type { News } from '../types';

interface Props {
  news: News;
}

export default function NewsCard({ news }: Props) {
  const formattedDate = new Date(news.publishedAt).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <div className="card">
      <div className="card-badge">{news.category}</div>
      <h3>{news.title}</h3>
      <div className="card-meta">
        <span><User size={14} /> {news.author}</span>
        <span><Clock size={14} /> {formattedDate}</span>
      </div>
      <p className="card-description">{news.summary}</p>
      <div className="card-footer">
        <span className="card-tag"><Tag size={12} /> {news.category}</span>
        <Link to={`/news/${news.id}`} className="btn btn-sm">
          Read more <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
