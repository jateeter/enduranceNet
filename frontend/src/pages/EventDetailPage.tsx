import { useParams, Link } from 'react-router-dom';
import { useApi } from '../hooks/useApi';
import { fetchEvent, fetchEventMicrosite, fetchResultsByEvent } from '../api/endpoints';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { legacyAssetUrl } from '../utils/legacyAssets';
import { AlertTriangle, ArrowLeft, BookOpen, Calendar, Camera, ExternalLink, FileText, Image, Images, MapPin, Trophy } from 'lucide-react';

interface Props {
  eventId?: number;
}

export default function EventDetailPage({ eventId }: Props) {
  const { id } = useParams<{ id: string }>();
  const resolvedEventId = eventId ?? Number(id);
  const { data: event, loading, error } = useApi(() => fetchEvent(resolvedEventId));
  const { data: microsite } = useApi(() => fetchEventMicrosite(resolvedEventId).catch(() => null));
  const { data: results } = useApi(() => fetchResultsByEvent(resolvedEventId));
  const legacyHub = event?.registrationUrl?.endsWith('/') ? `${event.registrationUrl}index.html` : event?.registrationUrl;
  const bannerUrl = microsite?.heroImageUrl
    ? legacyAssetUrl(microsite.heroImageUrl)
    : event?.registrationUrl?.endsWith('/')
    ? legacyAssetUrl(`${event.registrationUrl}banner_block.jpg`)
    : undefined;
  const pageTitle = microsite?.title ?? event?.name;
  const pageSubtitle = microsite?.subtitle ?? event?.eventType;

  return (
    <div className="page page-narrow">
      <Link to="/events" className="back-link">
        <ArrowLeft size={16} /> Back to Events
      </Link>

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}
      {event && (
        <div className={`event-detail${microsite ? ' event-microsite' : ''}`}>
          {bannerUrl && <img className="article-image event-hero-image" src={bannerUrl} alt="" loading="lazy" />}
          <div className="card-badge">{pageSubtitle}</div>
          <h1>{pageTitle}</h1>
          <div className="card-meta">
            <span>
              <Calendar size={14} />
              {new Date(event.date).toLocaleDateString('en-US', {
                year: 'numeric', month: 'long', day: 'numeric',
              })}
            </span>
            <span><MapPin size={14} /> {event.location}</span>
          </div>
          <p className="article-lead">{microsite?.overview ?? event.description}</p>

          {microsite && (
            <>
              <nav className="microsite-nav" aria-label="Tevis Cup microsite sections">
                {microsite.sections.map((section) => (
                  <a key={section.id} href={`#${section.id}`}>{section.kind}</a>
                ))}
                <a href="#media">Media</a>
                <a href="#migration">Migration</a>
              </nav>

              <div className="microsite-section-grid">
                {microsite.sections.map((section) => (
                  <section key={section.id} id={section.id} className="microsite-section-card">
                    <div className="microsite-section-heading">
                      <span className="microsite-icon"><BookOpen size={18} /></span>
                      <div>
                        <span>{section.kind}</span>
                        <h2>{section.title}</h2>
                      </div>
                    </div>
                    <p className="microsite-summary">{section.summary}</p>
                    <p>{section.body}</p>
                    <a href={legacyAssetUrl(section.legacyUrl)} target="_blank" rel="noopener noreferrer" className="btn btn-sm btn-outline">
                      {section.ctaLabel} <ExternalLink size={14} />
                    </a>
                  </section>
                ))}
              </div>

              <section id="media" className="microsite-media-panel">
                <div className="microsite-panel-heading">
                  <Images size={20} />
                  <div>
                    <span>Readable Assets</span>
                    <h2>Tevis Media In The CMS Path</h2>
                  </div>
                </div>
                <div className="microsite-media-grid">
                  {microsite.media.map((item) => (
                    <a key={item.id} href={legacyAssetUrl(item.publicUrl)} target="_blank" rel="noopener noreferrer" className="microsite-media-card">
                      <img src={legacyAssetUrl(item.publicUrl)} alt={item.altText} loading="lazy" />
                      <div>
                        <span>{item.kind}</span>
                        <strong>{item.title}</strong>
                      </div>
                    </a>
                  ))}
                </div>
              </section>

              <section id="migration" className="microsite-migration-panel">
                <div className="microsite-panel-heading">
                  <AlertTriangle size={20} />
                  <div>
                    <span>Migration Status</span>
                    <h2>Unreadable Legacy Media Blockers</h2>
                  </div>
                </div>
                <ul>
                  {microsite.blockers.map((blocker) => (
                    <li key={blocker.sourcePath}>
                      <strong>{blocker.status}</strong>
                      <span>{blocker.sourcePath}</span>
                      <em>{blocker.reason}</em>
                    </li>
                  ))}
                </ul>
              </section>
            </>
          )}

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
              <a href={microsite ? '#media' : legacyAssetUrl(event.registrationUrl)} target={microsite ? undefined : '_blank'} rel={microsite ? undefined : 'noopener noreferrer'} className="info-block event-link-block">
                <Camera size={18} />
                <span>Gallery source</span>
                <p>{microsite ? `${microsite.media.length} readable assets surfaced` : 'Media references tracked by manifest reports'}</p>
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
