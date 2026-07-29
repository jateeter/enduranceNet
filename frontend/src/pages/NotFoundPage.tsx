import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div className="page page-narrow" style={{ textAlign: 'center', paddingTop: '4rem' }}>
      <h1 style={{ fontSize: '6rem', margin: 0 }}>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you're looking for doesn't exist or has been moved.</p>
      <Link to="/" className="btn btn-primary">
        <Home size={16} /> Go Home
      </Link>
    </div>
  );
}
