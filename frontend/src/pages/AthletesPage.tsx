import AthleteCard from '../components/AthleteCard';
import LegacySectionHeader from '../components/LegacySectionHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchAthletes } from '../api/endpoints';
import { MessageSquareText } from 'lucide-react';

export default function AthletesPage() {
  const { data: athletes, loading, error } = useApi(fetchAthletes);

  return (
    <div className="page">
      <LegacySectionHeader
        title="Ridecamp"
        subtitle="Community archive migration for legacy Ridecamp people, horses, message history, and shared knowledge."
        banner="/images/banner_sm_right_ridecamp.jpg"
        icon={<MessageSquareText size={28} />}
      />

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
