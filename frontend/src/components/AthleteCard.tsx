import { Link } from 'react-router-dom';
import { Globe, Trophy, ArrowRight } from 'lucide-react';
import type { Athlete } from '../types';

interface Props {
  athlete: Athlete;
}

export default function AthleteCard({ athlete }: Props) {
  return (
    <div className="card">
      <div className="card-badge">{athlete.sport}</div>
      <h3>{athlete.name}</h3>
      <div className="card-meta">
        <span><Globe size={14} /> {athlete.country}</span>
        <span><Trophy size={14} /> {athlete.achievements.length} achievements</span>
      </div>
      <p className="card-description">{athlete.bio}</p>
      <ul className="achievement-list">
        {athlete.achievements.slice(0, 2).map((a) => (
          <li key={a}>{a}</li>
        ))}
        {athlete.achievements.length > 2 && (
          <li className="more">+{athlete.achievements.length - 2} more</li>
        )}
      </ul>
      <div className="card-footer">
        <Link to={`/athletes/${athlete.id}`} className="btn btn-sm">
          Profile <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
