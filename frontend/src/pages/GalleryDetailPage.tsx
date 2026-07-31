import { Link, useParams } from 'react-router-dom';
import { Camera, ExternalLink, Images } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import LegacySectionHeader from '../components/LegacySectionHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchGallery } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import { legacyAssetUrl } from '../utils/legacyAssets';

export default function GalleryDetailPage() {
  const { slug = '' } = useParams();
  const { data: gallery, loading, error } = useApi(() => fetchGallery(slug));

  return (
    <div className="page">
      <LegacySectionHeader
        title={gallery?.title ?? 'Photo Gallery'}
        subtitle={gallery ? `${gallery.itemCount} migrated Photoshop gallery images from ${gallery.sourceRoot}` : 'Migrated Photoshop gallery'}
        banner="/images/ENbanner_sm_right_snapshots.jpg"
        icon={<Camera size={28} />}
      />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {gallery && (
        <>
          <div className="gallery-detail-meta">
            <div>
              <span>Legacy source</span>
              <strong>{gallery.sourceRoot}</strong>
            </div>
            <div>
              <span>Pattern</span>
              <strong>{gallery.pattern}</strong>
            </div>
            <div>
              <span>Parser</span>
              <strong>{gallery.parserVersion}</strong>
            </div>
            <a href={legacyAssetUrl(gallery.legacyUrl)} target="_blank" rel="noreferrer">
              Legacy entry <ExternalLink size={14} />
            </a>
          </div>

          <div className="gallery-grid">
            {gallery.items.map((item) => (
              <a key={item.id} className="gallery-photo" href={legacyAssetUrl(item.fullImageUrl)} target="_blank" rel="noreferrer">
                <img src={legacyAssetUrl(item.thumbnailUrl)} alt={item.caption} loading="lazy" />
                <span>
                  <Images size={14} />
                  {item.caption || `Image ${item.position}`}
                </span>
                <small>{item.fullImageSourcePath}</small>
              </a>
            ))}
          </div>

          <Link to="/galleries" className="btn btn-outline">Back to galleries</Link>
        </>
      )}
    </div>
  );
}
