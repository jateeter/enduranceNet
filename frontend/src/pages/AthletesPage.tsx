import AthleteCard from '../components/AthleteCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchAthletes } from '../api/endpoints';
import { Users } from 'lucide-react';

export default function AthletesPage() {
  const { data: athletes, loading, error } = useApi(fetchAthletes);

  return (
    <div className="page">
      <div className="page-header">
        <Users size={40} />
        <h1>Athletes</h1>
        <p>Meet the elite endurance athletes pushing the limits of human performance.</p>
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
