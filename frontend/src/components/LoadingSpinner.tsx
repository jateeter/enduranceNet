import { Loader2 } from 'lucide-react';

interface Props {
  message?: string;
}

export default function LoadingSpinner({ message = 'Loading…' }: Props) {
  return (
    <div className="loading-container">
      <Loader2 className="spin" size={36} />
      <p>{message}</p>
    </div>
  );
}
