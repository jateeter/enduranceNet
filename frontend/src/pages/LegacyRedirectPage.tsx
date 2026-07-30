import { Navigate, useLocation } from 'react-router-dom';
import { resolveLegacyRedirect } from '../data/legacyRedirects';

export default function LegacyRedirectPage() {
  const location = useLocation();
  const target = resolveLegacyRedirect(location.pathname, location.hash);

  return <Navigate to={target} replace state={{ legacyRedirectFrom: `${location.pathname}${location.hash}` }} />;
}
