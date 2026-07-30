import AthleteCard from '../components/AthleteCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchAthletes } from '../api/endpoints';
import { MessageSquareText } from 'lucide-react';

export default function AthletesPage() {
  const { data: athletes, loading, error } = useApi(fetchAthletes);

  return (
    <div className="page">
      <div className="page-header">
        <MessageSquareText size={40} />
        <h1>Ridecamp</h1>
        <p>Community archive migration for legacy Ridecamp people, horses, message history, and shared knowledge.</p>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {athletes && (
        <div className="card-grid card-grid-wide">
          {athletes.map((a) => (
            <AthleteCard key={a.id} athlete={a} />
          ))}
        </div>
      )}
    </div>
  );
}
