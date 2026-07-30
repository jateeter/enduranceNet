import { useApi } from '../hooks/useApi';
import { fetchResults } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { BadgeDollarSign, Clock, Medal, Trophy } from 'lucide-react';

export default function ResultsPage() {
  const { data: results, loading, error } = useApi(fetchResults);

  const grouped = results
    ? results.reduce<Record<string, typeof results>>((acc, r) => {
        const key = `${r.eventName} (${r.year})`;
        acc[key] = acc[key] ? [...acc[key], r] : [r];
        return acc;
      }, {})
    : {};

  return (
    <div className="page">
      <div className="page-header">
        <BadgeDollarSign size={40} />
        <h1>Classifieds</h1>
        <p>Migration staging for legacy horses, tack, trailers, jobs, and other marketplace listings.</p>
      </div>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {results && (
        <div className="results-container">
          {Object.entries(grouped).map(([event, eventResults]) => (
            <div key={event} className="results-group">
              <h2><Trophy size={20} /> {event}</h2>
              <div className="results-table-wrapper">
                <table className="results-table">
                  <thead>
                    <tr>
                      <th><Medal size={14} /> Place</th>
                      <th>Athlete</th>
                      <th>Category</th>
                      <th><Clock size={14} /> Finish Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {eventResults
                      .sort((a, b) => a.place - b.place)
                      .map((r) => (
                        <tr key={r.id} className={r.place === 1 ? 'gold' : ''}>
                          <td className="place-cell">
                            {r.place}
                          </td>
                          <td>{r.athleteName}</td>
                          <td>{r.category}</td>
                          <td className="time-cell">{r.finishTime}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
