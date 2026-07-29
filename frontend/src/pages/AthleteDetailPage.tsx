import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { fetchAthlete } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { ArrowLeft, Globe, Trophy } from 'lucide-react';

export default function AthleteDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: athlete, loading, error } = useApi(() => fetchAthlete(Number(id)));

  return (
    <div className="page page-narrow">
      <Link to="/athletes" className="back-link">
        <ArrowLeft size={16} /> Back to Athletes
      </Link>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {athlete && (
        <div className="athlete-profile">
          <div className="card-badge">{athlete.sport}</div>
          <h1>{athlete.name}</h1>
          <div className="card-meta">
            <span><Globe size={14} /> {athlete.country}</span>
          </div>
          <p className="article-lead">{athlete.bio}</p>
          <h2><Trophy size={20} /> Achievements</h2>
          <ul className="achievement-list-full">
            {athlete.achievements.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
