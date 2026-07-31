import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { useApi } from '../hooks/useApi';
import { fetchEvents, fetchHomepageAssets, fetchNews } from '../api/endpoints';
import { legacyAssetUrl } from '../utils/legacyAssets';
import type { HomepageAsset, News } from '../types';

const advertiserNames = [
  'Belesemo Arabians',
  'Cypress Trails Equestrian Center, Sales, Training, Boarding',
  'Distance Depot Tack and Equipment',
  'DWA Arabians',
  'Endurance Ride Photographers Guild',
  'EuroXciser',
  'Owyhee Endurance Rides',
  'Parry Harness and Tack/Running Bear',
  'PNER',
  'Slypner Gear Trail Supplies',
  'SWITnDR',
  'Synergist Saddles',
  'Tevis Cup Magic',
  'Steph Teeter Artistry',
  'Centropix Kloud PEMF',
];

function AssetImageLink({ asset, className }: { asset: HomepageAsset; className: string }) {
  const image = (
    <img src={legacyAssetUrl(asset.imageUrl)} alt={asset.altText || asset.title} loading="lazy" />
  );

  if (asset.linkUrl.startsWith('/')) {
    return (
      <Link to={asset.linkUrl} className={className} title={asset.title}>
        {image}
      </Link>
    );
  }

  return (
    <a href={asset.linkUrl} className={className} rel="noreferrer" target="_blank" title={asset.title}>
      {image}
    </a>
  );
}

function StoryTile({ story }: { story: News }) {
  return (
    <Link to={`/news/${story.id}`} className="legacy-story-tile">
      {story.imageUrl && (
        <img src={legacyAssetUrl(story.imageUrl)} alt="" loading="lazy" />
      )}
      <span>{story.title}</span>
    </Link>
  );
}

function firstParagraph(story: News): string {
  return story.content.split(/\n\s*\n/)[0]?.trim() || story.summary;
}

function HeadlineLink({ story }: { story: News }) {
  return (
    <li className="legacy-headline-item">
      <Link to={`/news/${story.id}`} className="legacy-headline-link" aria-describedby={`headline-tip-${story.id}`}>
        <span className="legacy-headline-title">{story.title}</span>
        <span className="legacy-headline-summary">{story.summary}</span>
        <span id={`headline-tip-${story.id}`} className="legacy-headline-tooltip" role="tooltip">
          <strong>{story.title}</strong>
          <span>{firstParagraph(story)}</span>
        </span>
      </Link>
    </li>
  );
}

export default function HomePage() {
  const events = useApi(fetchEvents);
  const news = useApi(fetchNews);
  const homepageAssets = useApi(fetchHomepageAssets);
  const currentNews = news.data?.filter((item) => item.category === 'Current News') ?? [];
  const featuredStories = news.data?.filter((item) => item.category === 'Featured Stories') ?? [];
  const assetsFor = (placement: string) =>
    homepageAssets.data?.filter((asset) => asset.placement === placement) ?? [];
  const headlineStories = [
    ...currentNews,
    ...featuredStories,
    ...(news.data?.filter((item) => item.category !== 'Current News' && item.category !== 'Featured Stories') ?? []),
  ].filter((item, index, list) => list.findIndex((candidate) => candidate.id === item.id) === index);
  const leadStory = featuredStories[0] ?? news.data?.[0];
  const photoStory = news.data?.find((item) => item.imageUrl && item.category === 'Event Coverage') ?? leadStory;
  const sponsorAsset = assetsFor('current_news_sponsor')[0];
  const socialAssets = assetsFor('social');
  const eventAssets = assetsFor('event_coverage');
  const advertiserAssets = assetsFor('advertiser');

  return (
    <div className="legacy-landing">
      <div className="legacy-portal-grid">
        <section className="legacy-news-column">
          <div className="legacy-card legacy-headlines-card legacy-focal-card">
          <header className="legacy-card-title">
            <h1>This Week's Current News</h1>
          </header>
          <div className="legacy-card-body">
            {news.loading && <LoadingSpinner />}
            {news.error && <ErrorMessage message={news.error} />}
            <ul className="legacy-headline-list">
              {headlineStories.slice(0, 9).map((story) => (
                <HeadlineLink key={story.id} story={story} />
              ))}
              <li className="legacy-headline-more">
                <Link to="/news">More news...</Link>
              </li>
            </ul>
          </div>
          </div>

          {homepageAssets.loading && <LoadingSpinner />}
          {homepageAssets.error && <ErrorMessage message={homepageAssets.error} />}
          <div className="legacy-sponsor-block legacy-card legacy-focal-card">
            <header className="legacy-card-title">
              <h2>This news roundup brought to you by our friends at DWA Arabians</h2>
            </header>
            <div className="legacy-card-body">
              {sponsorAsset && <AssetImageLink asset={sponsorAsset} className="legacy-sponsor-image" />}
              <p>Quality Arabians bred for Endurance</p>
            </div>
          </div>

          <div className="legacy-book-block legacy-card">
            <header className="legacy-card-title">
              <Link to="/featured-stories">Got Endurance Books? We do here!</Link>
            </header>
            <div className="legacy-card-body">
              <img src={legacyAssetUrl('/images/Graphic_booksign.jpg')} alt="Books" loading="lazy" />
            </div>
          </div>
        </section>

        <section className="legacy-feature-column legacy-card legacy-focal-card">
          <header className="legacy-card-title">
            <div className="legacy-box-heading">This week's Featured Stories:</div>
          </header>
          <div className="legacy-card-body">
            {leadStory && (
              <Link to={`/news/${leadStory.id}`} className="legacy-feature-lead">
                <span>{leadStory.title}</span>
              </Link>
            )}
            <div className="legacy-feature-assets">
              {assetsFor('featured_story').slice(0, 3).map((asset) => (
                <AssetImageLink key={asset.id} asset={asset} className="legacy-feature-asset" />
              ))}
            </div>
            <div className="legacy-feature-list">
              {featuredStories.slice(1, 4).map((story) => (
                <StoryTile key={story.id} story={story} />
              ))}
            </div>
          </div>
        </section>

        <section className="legacy-media-column legacy-card">
          <div className="legacy-social-row legacy-card-title">
            <span>Follow EN on ...</span>
            {socialAssets.map((asset) => (
              <AssetImageLink key={asset.id} asset={asset} className="legacy-social-icon" />
            ))}
          </div>

          <div className="legacy-card-body">
            {photoStory?.imageUrl && (
              <Link to={`/news/${photoStory.id}`} className="legacy-photo-feature">
                <img src={legacyAssetUrl(photoStory.imageUrl)} alt="" />
                <span>{photoStory.title}</span>
                <em>Photos by Merri Melde</em>
              </Link>
            )}

            <div className="legacy-event-archive">
              <h2>*Event Coverage Archive*</h2>
              <h3>Just Happened!</h3>
              <div className="legacy-event-tiles legacy-event-tiles-three">
                {eventAssets.slice(0, 3).map((asset) => (
                  <AssetImageLink key={asset.id} asset={asset} className="legacy-event-tile" />
                ))}
              </div>
              {events.error && <ErrorMessage message={events.error} />}
              <h3>Coming up in 2026!</h3>
              <div className="legacy-event-tiles">
                {eventAssets.slice(3, 5).map((asset) => (
                  <AssetImageLink key={asset.id} asset={asset} className="legacy-event-tile" />
                ))}
              </div>
              {events.data && (
                <Link to="/events" className="legacy-plain-link">
                  {events.data.length} migrated event records
                </Link>
              )}
            </div>
          </div>
        </section>

        <aside className="legacy-ad-column legacy-card" aria-label="Endurance.Net advertisers">
          <div className="legacy-ad-logos">
            {advertiserAssets.slice(1, 3).map((asset) => (
              <AssetImageLink key={asset.id} asset={asset} className="legacy-ad-logo" />
            ))}
          </div>
          <div className="legacy-ad-directory">
            <header className="legacy-card-title">
              <h2>All Endurance.Net Advertisers</h2>
            </header>
            {[...advertiserNames, ...advertiserAssets.map((asset) => asset.title)]
              .filter((name, index, list) => list.indexOf(name) === index)
              .slice(0, 15)
              .map((name) => (
                <Link key={name} to="/community#advertisers">{name}</Link>
              ))}
          </div>
        </aside>
      </div>

      <div className="legacy-ad-thanks">
        THANK YOU to our Advertisers! <Link to="/community#advertisers">Click here</Link> for their bios,
        and their specials. Click below for their websites!
      </div>
    </div>
  );
}
