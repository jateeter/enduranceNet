import { Camera, GitFork, Mail, Mountain, Send } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          <Mountain size={24} />
          <span>Endurance.Net</span>
          <p>Endurance riding news, featured stories, event coverage, Ridecamp history, classifieds, and advertiser resources.</p>
        </div>

        <div className="footer-links">
          <div>
            <h4>Explore</h4>
            <ul>
              <li><Link to="/news">Current News</Link></li>
              <li><Link to="/featured-stories">Featured Stories</Link></li>
              <li><Link to="/events">Events</Link></li>
              <li><Link to="/results">Classifieds</Link></li>
            </ul>
          </div>
          <div>
            <h4>Community</h4>
            <ul>
              <li><Link to="/athletes">Ridecamp</Link></li>
              <li><a href="mailto:merri@endurance.net">Contact</a></li>
              <li><a href="#privacy">Privacy Policy</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-social">
          <h4>Connect</h4>
          <div className="social-icons">
            <a href="https://github.com/jateeter/enduranceNet" aria-label="GitHub"><GitFork size={20} /></a>
            <a href="https://twitter.com/endurancenet" aria-label="X / Twitter"><Send size={20} /></a>
            <a href="https://www.instagram.com/endurancenet" aria-label="Instagram"><Camera size={20} /></a>
            <a href="mailto:merri@endurance.net" aria-label="Email"><Mail size={20} /></a>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {year} Endurance.Net. All rights reserved.</p>
      </div>
    </footer>
  );
}
