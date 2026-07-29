export interface Event {
  id: number;
  name: string;
  eventType: string;
  date: string;
  location: string;
  distance: string;
  description: string;
  registrationUrl?: string;
}

export interface News {
  id: number;
  title: string;
  summary: string;
  content: string;
  author: string;
  publishedAt: string;
  category: string;
  imageUrl?: string;
}

export interface Athlete {
  id: number;
  name: string;
  sport: string;
  country: string;
  bio: string;
  achievements: string[];
  imageUrl?: string;
}

export interface Result {
  id: number;
  eventId: number;
  eventName: string;
  athleteName: string;
  finishTime: string;
  place: number;
  category: string;
  year: number;
}
