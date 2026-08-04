import { Link } from 'react-router-dom';
import LegacySectionHeader from '../components/LegacySectionHeader';
import { legacyAssetUrl } from '../utils/legacyAssets';
import { BadgeDollarSign, ExternalLink, Megaphone, MessageSquareText, ShieldCheck } from 'lucide-react';

const advertisers = [
  {
    name: 'Belesemo Arabians',
    logo: '/ads/AdvertiserLogos/BelesemoArabians_150.jpg',
    href: '/belesemo/',
    placement: 'Legacy homepage sponsor',
  },
  {
    name: 'Distance Depot Tack',
    logo: '/ads/AdvertiserLogos/TheDistanceDepot_150.jpg',
    href: 'http://www.thedistancedepot.com',
    placement: 'Legacy advertiser logo',
  },
  {
    name: 'Endurance Ride Photographers Guild',
    logo: '/advertisers/EnduranceRidePhotographersGuild/EnduranceRidePhotographersGuildImage.png',
    href: '/advertisers/EnduranceRidePhotographersGuild.html',
    placement: 'Advertiser page and logo asset',
  },
];

const classifieds = [
  { category: 'Horses', legacyUrl: '/ClassifiedAds/Horses/', status: 'Read-only archive target' },
  { category: 'Tack', legacyUrl: '/ClassifiedAds/Tack/', status: 'Read-only archive target' },
  { category: 'Trailers', legacyUrl: '/ClassifiedAds/Trailers/', status: 'Read-only archive target' },
  { category: 'Jobs and services', legacyUrl: '/ClassifiedAds/', status: 'Moderation review before editable rebuild' },
];

const ridecampLinks = [
  { title: 'Ridecamp Friend', legacyUrl: '/RidecampFriend/index.html' },
  { title: 'Ridecamp archive root', legacyUrl: '/ridecamp/' },
  { title: 'Recent Ridecamp index', legacyUrl: '/RidecampFriend/index_oldrecent.html' },
];

function archiveHref(url: string) {
  if (url.startsWith('http')) return url;
  return legacyAssetUrl(url) ?? url;
}

export default function CommunityArchivePage() {
  return (
    <div className="page">
      <LegacySectionHeader
        title="Community Archive"
        subtitle="Read-only migration surface for advertisers, classifieds, and Ridecamp community archives."
        banner="/media/live-2def95ecb7616872/banner_sm_right_classified.jpg"
        icon={<MessageSquareText size={28} />}
      />

      <div className="community-grid">
        <section id="advertisers" className="community-panel">
          <div className="section-header">
            <h2><Megaphone size={18} /> Advertisers</h2>
          </div>
          <div className="asset-grid">
            {advertisers.map((advertiser) => (
              <a key={advertiser.name} className="asset-link" href={archiveHref(advertiser.href)} target="_blank" rel="noreferrer">
                <span className="asset-image-wrap">
                  <img src={legacyAssetUrl(advertiser.logo)} alt="" loading="lazy" />
                </span>
                <span className="asset-title">{advertiser.name}</span>
                <span className="community-note">{advertiser.placement}</span>
              </a>
            ))}
          </div>
        </section>

        <section id="classifieds" className="community-panel">
          <div className="section-header">
            <h2><BadgeDollarSign size={18} /> Classifieds</h2>
          </div>
          <div className="community-list">
            {classifieds.map((item) => (
              <a key={item.category} className="community-list-item" href={archiveHref(item.legacyUrl)} target="_blank" rel="noreferrer">
                <span>{item.category}</span>
                <small>{item.status}</small>
                <ExternalLink size={15} />
              </a>
            ))}
          </div>
        </section>

        <section id="ridecamp" className="community-panel">
          <div className="section-header">
            <h2><MessageSquareText size={18} /> Ridecamp</h2>
          </div>
          <div className="community-list">
            {ridecampLinks.map((item) => (
              <a key={item.title} className="community-list-item" href={archiveHref(item.legacyUrl)} target="_blank" rel="noreferrer">
                <span>{item.title}</span>
                <small>{item.legacyUrl}</small>
                <ExternalLink size={15} />
              </a>
            ))}
          </div>
        </section>

        <section className="community-panel community-panel-wide">
          <div className="section-header">
            <h2><ShieldCheck size={18} /> Privacy and Moderation</h2>
          </div>
          <p className="community-copy">
            These community areas are migrated as read-only archives first. Classified and Ridecamp content can include old contact details,
            personal messages, sale status, and community moderation context, so editable NextGen workflows should only be enabled after
            a review of privacy, retention, and takedown handling.
          </p>
          <Link to="/results" className="btn btn-outline">View staged results archive</Link>
        </section>
      </div>
    </div>
  );
}
