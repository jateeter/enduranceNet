import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { type CSSProperties, useState } from 'react';
import { resolveMastheadVariant } from '../data/mastheads';
import { legacyAssetUrl } from '../utils/legacyAssets';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/news', label: 'Current News' },
  { to: '/featured-stories', label: 'News Archive' },
  { to: '/community#advertisers', label: 'Shop/Advertise' },
  { to: '/community#ridecamp', label: 'Ridecamp' },
  { to: '/community#classifieds', label: 'Classified' },
  { to: '/streams', label: 'Streams' },
  { to: '/events', label: 'Events' },
  { to: '/galleries', label: 'Photos' },
  { to: '/athletes', label: 'Learn/AERC' },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);
  const isHomePage = pathname === '/';
  const masthead = resolveMastheadVariant(pathname);
  const mastheadImageUrl = legacyAssetUrl(masthead.imageUrl) ?? masthead.imageUrl;
  const mastheadStyle = {
    '--masthead-bg': `url("${mastheadImageUrl}")`,
    '--masthead-accent': masthead.accentColor,
  } as CSSProperties;

  return (
    <nav className={`navbar${isHomePage ? ' navbar-home' : ' navbar-interior'}`}>
      <Link
        to="/"
        className={`masthead${isHomePage ? ' masthead-home' : ' masthead-interior'} masthead-${masthead.kind}`}
        style={mastheadStyle}
        data-masthead-variant={masthead.id}
        data-masthead-kind={masthead.kind}
        data-masthead-image={mastheadImageUrl}
        aria-label={`${masthead.title} ${masthead.subtitle} masthead`}
        onClick={() => setOpen(false)}
      >
        <span className="masthead-title">{masthead.title}</span>
        <span className="masthead-subtitle">{masthead.subtitle}</span>
      </Link>
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand" onClick={() => setOpen(false)}>
          <span className="brand-mark">@</span>
          <span>Endurance.Net</span>
        </Link>

        <button className="navbar-toggle" onClick={() => setOpen(!open)} aria-label="Toggle menu">
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>

        <ul className={`navbar-links${open ? ' open' : ''}`}>
          {navLinks.map(({ to, label }) => (
            <li key={to}>
              <Link
                to={to}
                className={pathname === to ? 'active' : ''}
                onClick={() => setOpen(false)}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
