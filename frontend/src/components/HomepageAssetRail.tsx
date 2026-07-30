import { Link } from 'react-router-dom';
import { ExternalLink } from 'lucide-react';
import type { HomepageAsset } from '../types';
import { legacyAssetUrl } from '../utils/legacyAssets';

interface Props {
  title: string;
  assets: HomepageAsset[];
  variant?: 'compact' | 'logo';
}

function AssetLink({ asset }: { asset: HomepageAsset }) {
  const content = (
    <>
      <span className="asset-image-wrap">
        <img src={legacyAssetUrl(asset.imageUrl)} alt={asset.altText} loading="lazy" />
      </span>
      <span className="asset-title">{asset.title}</span>
      {!asset.linkUrl.startsWith('/') && <ExternalLink size={13} aria-hidden="true" />}
    </>
  );

  if (asset.linkUrl.startsWith('/')) {
    return (
      <Link to={asset.linkUrl} className="asset-link">
        {content}
      </Link>
    );
  }

  return (
    <a href={asset.linkUrl} className="asset-link" rel="noreferrer" target="_blank">
      {content}
    </a>
  );
}

export default function HomepageAssetRail({ title, assets, variant = 'compact' }: Props) {
  if (assets.length === 0) return null;

  return (
    <div className={`asset-rail asset-rail-${variant}`}>
      <div className="asset-rail-header">
        <h3>{title}</h3>
      </div>
      <div className="asset-grid">
        {assets.map((asset) => (
          <AssetLink key={asset.id} asset={asset} />
        ))}
      </div>
    </div>
  );
}
