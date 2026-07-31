import { Link } from 'react-router-dom';
import { Camera, Images, MapPinned } from 'lucide-react';
import ErrorMessage from '../components/ErrorMessage';
import LegacySectionHeader from '../components/LegacySectionHeader';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchGalleries } from '../api/endpoints';
import { useApi } from '../hooks/useApi';
import { legacyAssetUrl } from '../utils/legacyAssets';

export default function GalleriesPage() {
  const { data: galleries, loading, error } = useApi(fetchGalleries);

  return (
    <div className="page">
      <LegacySectionHeader
        title="Photo Galleries"
        subtitle="Migrated Photoshop image galleries with preserved thumbnails, source pages, and full-size legacy media links."
        banner="/images/ENbanner_sm_right_snapshots.jpg"
        icon={<Images size={28} />}
      />

      {loading && <LoadingSpinner />}
      {error && <ErrorMessage message={error} />}

      {galleries && (
        <>
          <div className="archive-toolbar">
            <div className="archive-stat-row">
              <span><Images size={16} /> {galleries.length} migrated gallery roots</span>
              <span><Camera size={16} /> {galleries.reduce((total, gallery) => total + gallery.itemCount, 0)} image records</span>
              <span><MapPinned size={16} /> Photoshop gallery corpus</span>
            </div>
          </div>

          <div className="gallery-list">
            {galleries.map((gallery) => (
              <Link key={gallery.id} className="gallery-list-item" to={`/galleries/${gallery.slug}`}>
                <div>
                  <h2>{gallery.title}</h2>
                  <p>{gallery.sourceRoot}</p>
                </div>
                <div className="gallery-list-meta">
                  <span>{gallery.pattern}</span>
                  <strong>{gallery.itemCount} images</strong>
                </div>
                {gallery.items[0]?.thumbnailUrl && (
                  <img src={legacyAssetUrl(gallery.items[0].thumbnailUrl)} alt="" loading="lazy" />
                )}
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
