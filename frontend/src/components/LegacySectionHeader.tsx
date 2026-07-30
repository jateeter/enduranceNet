import type { ReactNode } from 'react';
import { legacyAssetUrl } from '../utils/legacyAssets';

interface Props {
  title: string;
  subtitle: string;
  banner: string;
  icon: ReactNode;
}

export default function LegacySectionHeader({ title, subtitle, banner, icon }: Props) {
  return (
    <div className="legacy-page-header">
      <div className="legacy-page-banner">
        <img src={legacyAssetUrl('/images/ENbanner_sm_left.jpg')} alt="Endurance.Net" />
        <img src={legacyAssetUrl(banner)} alt="" />
      </div>
      <div className="legacy-page-title">
        <span className="legacy-page-icon">{icon}</span>
        <div>
          <h1>{title}</h1>
          <p>{subtitle}</p>
        </div>
      </div>
    </div>
  );
}
