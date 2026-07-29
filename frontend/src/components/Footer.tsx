import { Activity, GitFork, Send, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <Activity size={24} />
          <span>EnduranceNet</span>
          <p>The next generation endurance sports community — est. 1995, reborn {year}.</p>
        </div>

        <div className="footer-links">
          <div>
            <h4>Explore</h4>
            <ul>
              <li><Link to="/events">Events</Link></li>
              <li><Link to="/news">News</Link></li>
              <li><Link to="/athletes">Athletes</Link></li>
              <li><Link to="/results">Results</Link></li>
            </ul>
          </div>
          <div>
            <h4>Community</h4>
            <ul>
              <li><a href="#about">About</a></li>
              <li><a href="#contact">Contact</a></li>
              <li><a href="#privacy">Privacy Policy</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-social">
          <h4>Connect</h4>
          <div className="social-icons">
            <a href="https://github.com" aria-label="GitHub"><GitFork size={20} /></a>
            <a href="https://x.com" aria-label="X / Twitter"><Send size={20} /></a>
            <a href="mailto:info@endurance.net" aria-label="Email"><Mail size={20} /></a>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {year} EnduranceNet. All rights reserved.</p>
      </div>
    </footer>
  );
}
