import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';
import { legacyAssetUrl } from '../utils/legacyAssets';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/news', label: 'Current News' },
  { to: '/featured-stories', label: 'Featured Stories' },
  { to: '/events', label: 'Events' },
  { to: '/athletes', label: 'Ridecamp' },
  { to: '/results', label: 'Classifieds' },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);

  return (
    <nav className="navbar">
      <Link to="/" className="masthead" onClick={() => setOpen(false)}>
        <img src={legacyAssetUrl('/images/ENbanner_sm_left.jpg')} alt="Endurance.Net" />
        <img src={legacyAssetUrl('/images/ENbanner_sm_right.jpg')} alt="" />
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
