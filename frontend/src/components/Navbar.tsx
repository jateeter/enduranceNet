import { Link, useLocation } from 'react-router-dom';
import { Activity, Menu, X } from 'lucide-react';
import { useState } from 'react';

const navLinks = [
  { to: '/', label: 'Home' },
  { to: '/events', label: 'Events' },
  { to: '/news', label: 'News' },
  { to: '/athletes', label: 'Athletes' },
  { to: '/results', label: 'Results' },
];

export default function Navbar() {
  const { pathname } = useLocation();
  const [open, setOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand" onClick={() => setOpen(false)}>
          <Activity size={28} />
          <span>EnduranceNet</span>
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
