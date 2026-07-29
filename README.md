# EnduranceNet

> The next generation of [endurance.net](https://www.endurance.net) — reborn for the modern web.

A fully containerised, HTTPS-first endurance sports platform built with **React + TypeScript** (frontend) and **Scala Play Framework** (backend), served securely via **Nginx** in a **Docker Compose** stack.

---

## Architecture

```
Internet
   │
   ▼
┌─────────────────────────────┐
│  Nginx (reverse proxy)      │  ← TLS termination (Let's Encrypt)
│  Port 80  → 443 redirect    │
│  Port 443 → HTTPS           │
└────────────┬────────────────┘
             │
      ┌──────┴──────┐
      ▼             ▼
┌──────────┐  ┌──────────────────────┐
│ Frontend │  │  Backend             │
│ React SPA│  │  Scala Play REST API │
│ (Nginx)  │  │  Port 9000           │
└──────────┘  └──────────────────────┘
```

| Service      | Technology                        | Port (internal) |
|-------------|-----------------------------------|-----------------|
| **nginx**   | Nginx 1.27 (TLS + reverse proxy)  | 80, 443         |
| **frontend**| React 19 + TypeScript + Vite      | 80 (container)  |
| **backend** | Scala 3 + Play Framework 3.x      | 9000            |
| **certbot** | Let's Encrypt (prod only)         | —               |

---

## Prerequisites

| Tool          | Version |
|--------------|---------|
| Docker        | ≥ 24    |
| Docker Compose| ≥ 2.20  |

---

## Quick Start (Local / Development)

```bash
# Clone
git clone https://github.com/jateeter/enduranceNet.git
cd enduranceNet

# Copy environment config
cp .env.example .env   # edit DOMAIN, APPLICATION_SECRET, EMAIL

# Build and start all services
docker compose up --build

# Browse
open http://localhost
```

The API is available at `http://localhost/api/health`.

---

## Production Deployment (HTTPS + Let's Encrypt)

### 1. Prepare your server

- A Linux server with a public IP address
- DNS A/AAAA record pointing your domain to that IP
- Docker and Docker Compose installed
- Ports 80 and 443 open in your firewall

### 2. Set environment variables

```bash
export DOMAIN=www.endurance.net
export EMAIL=admin@endurance.net
export APPLICATION_SECRET=$(openssl rand -base64 48)
```

Or create a `.env` file (never commit it):

```env
DOMAIN=www.endurance.net
EMAIL=admin@endurance.net
APPLICATION_SECRET=<your-secret-min-32-chars>
```

### 3. Bootstrap TLS and start the stack

```bash
# One-time setup: obtain Let's Encrypt certificate and start everything
./scripts/init-letsencrypt.sh
```

### 4. Subsequent deploys

```bash
./scripts/deploy.sh
```

This rebuilds images, performs a rolling restart, and confirms the stack is running.

---

## Services and API

### Health check

```
GET /api/health
```

### Events

```
GET /api/events          – list all events
GET /api/events/:id      – get a single event
```

### News

```
GET /api/news            – list all news articles
GET /api/news/:id        – get a single article
```

### Athletes

```
GET /api/athletes        – list all athletes
GET /api/athletes/:id    – get a single athlete profile
```

### Results

```
GET /api/results         – all race results
GET /api/results/:eventId – results for a specific event
```

---

## Development

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev   # http://localhost:3000 with hot-reload
```

API calls are proxied to `http://localhost:9000` (see `vite.config.ts`).

### Backend (Scala + Play)

```bash
cd backend
sbt run       # http://localhost:9000
```

Requires Java 21+ and sbt 1.9+.

### Linting & Type-checking

```bash
cd frontend
npm run build   # type-checks + production build
```

---

## Security Highlights

- **HTTPS only** in production — HTTP redirects to HTTPS (301)
- **HSTS** with 1-year max-age, includeSubDomains, preload
- **Modern TLS**: TLS 1.2 / 1.3 only, strong cipher suite
- **OCSP stapling** for fast certificate validation
- **Security headers**: X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy
- **Rate limiting** on API (20 req/s) and web (60 req/s) routes via Nginx
- **Internal Docker network** — backend is not exposed to the host
- **Application secret** injected via environment variable, never hard-coded

---

## Repository Structure

```
enduranceNet/
├── frontend/              # React + TypeScript SPA
│   ├── src/
│   │   ├── api/           # Axios API client + endpoints
│   │   ├── components/    # Reusable UI components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Route-level page components
│   │   └── types/         # TypeScript interfaces
│   ├── Dockerfile
│   └── vite.config.ts
├── backend/               # Scala 3 + Play Framework API
│   ├── app/
│   │   ├── controllers/   # HTTP controllers
│   │   └── models/        # Data models
│   ├── conf/
│   │   ├── application.conf
│   │   └── routes
│   ├── test/              # ScalaTest specs
│   └── Dockerfile
├── nginx/                 # Reverse proxy configuration
│   ├── nginx.conf
│   └── Dockerfile
├── scripts/
│   ├── init-letsencrypt.sh  # One-time TLS bootstrap
│   └── deploy.sh            # Production deploy
├── docker-compose.yml       # Base stack definition
├── docker-compose.prod.yml  # Production overrides (HTTPS + certbot)
├── .env.example             # Environment variable template
└── README.md
```

---

## License

See [LICENSE](LICENSE).
