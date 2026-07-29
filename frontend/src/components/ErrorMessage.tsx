import { AlertTriangle } from 'lucide-react';

interface Props {
  message?: string;
}

export default function ErrorMessage({ message = 'Something went wrong.' }: Props) {
  return (
    <div className="error-container">
      <AlertTriangle size={36} />
      <p>{message}</p>
    </div>
  );
}
