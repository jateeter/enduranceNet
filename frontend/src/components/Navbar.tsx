import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { useState } from 'react';

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

  return (
    <nav className={`navbar${isHomePage ? ' navbar-home' : ' navbar-interior'}`}>
      {isHomePage && (
        <Link to="/" className="masthead" onClick={() => setOpen(false)}>
          <span className="masthead-title">Endurance.Net</span>
          <span className="masthead-subtitle">News,Blogs</span>
        </Link>
      )}
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
