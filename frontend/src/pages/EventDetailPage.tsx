import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { fetchEvent, fetchResultsByEvent } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { legacyAssetUrl } from '../utils/legacyAssets';
import { ArrowLeft, Calendar, Camera, ExternalLink, FileText, Image, MapPin, Trophy } from 'lucide-react';

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: event, loading, error } = useApi(() => fetchEvent(Number(id)));
  const { data: results } = useApi(() => fetchResultsByEvent(Number(id)));
  const legacyHub = event?.registrationUrl?.endsWith('/') ? `${event.registrationUrl}index.html` : event?.registrationUrl;
  const bannerUrl = event?.registrationUrl?.endsWith('/')
    ? legacyAssetUrl(`${event.registrationUrl}banner_block.jpg`)
    : undefined;

  return (
    <div className="page page-narrow">
      <Link to="/events" className="back-link">
        <ArrowLeft size={16} /> Back to Events
      </Link>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {event && (
        <div className="event-detail">
          {bannerUrl && <img className="article-image event-hero-image" src={bannerUrl} alt="" loading="lazy" />}
          <div className="card-badge">{event.eventType}</div>
          <h1>{event.name}</h1>
          <div className="card-meta">
            <span>
              <Calendar size={14} />
              {new Date(event.date).toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric',
              })}
            </span>
            <span><MapPin size={14} /> {event.location}</span>
          </div>
          <p className="article-lead">{event.description}</p>
          <div className="event-info-grid">
            <div className="info-block">
              <h4>Distance</h4>
              <p>{event.distance}</p>
            </div>
            <div className="info-block">
              <h4>Location</h4>
              <p>{event.location}</p>
            </div>
          </div>
          {event.registrationUrl && (
            <div className="event-link-grid">
              {legacyHub && (
                <a href={legacyAssetUrl(legacyHub)} target="_blank" rel="noopener noreferrer" className="info-block event-link-block">
                  <ExternalLink size={18} />
                  <span>Legacy hub</span>
                  <p>{event.registrationUrl}</p>
                </a>
              )}
              <a href={legacyAssetUrl(`${event.registrationUrl}banner_block.jpg`)} target="_blank" rel="noopener noreferrer" className="info-block event-link-block">
                <Image size={18} />
                <span>Banner media</span>
                <p>Resolved through /legacy-media/</p>
              </a>
              <a href="/results" className="info-block event-link-block">
                <Trophy size={18} />
                <span>Results archive</span>
                <p>{results?.length ?? 0} staged result rows</p>
              </a>
              <a href={legacyAssetUrl(event.registrationUrl)} target="_blank" rel="noopener noreferrer" className="info-block event-link-block">
                <Camera size={18} />
                <span>Gallery source</span>
                <p>Media references tracked by manifest reports</p>
              </a>
            </div>
          )}

          {results && results.length > 0 && (
            <div className="results-table-wrapper">
              <table className="results-table">
                <thead>
                  <tr>
                    <th><Trophy size={14} /> Place</th>
                    <th>Entry</th>
                    <th>Category</th>
                    <th><FileText size={14} /> Status</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result) => (
                    <tr key={result.id}>
                      <td className="place-cell">{result.place}</td>
                      <td>{result.athleteName}</td>
                      <td>{result.category}</td>
                      <td>{result.finishTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
