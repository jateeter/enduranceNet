# Production Visual And Media Regression Checks

Issue: https://github.com/jateeter/enduranceNet/issues/59

The release visual/media smoke is:

```bash
cd frontend
APP_URL=https://nextgen.example.org npm run visual:production
```

For local preview:

```bash
cd frontend
npm run build
npm run preview -- --host 127.0.0.1 --port 4177
APP_URL=http://127.0.0.1:4177 npm run visual:production
```

The script captures desktop and mobile screenshots for the core migrated
surfaces:

- `/`
- `/streams`
- `/streams/search`
- `/streams/endurance-tracks`
- `/events`
- `/featured-stories`
- `/community`
- `/results`
- `/CurrentNews/`

Outputs are ignored under `output/playwright/production-regression/`:

- one full-page screenshot per route and viewport
- `report.json` with route status, screenshot path, image request failures,
  failed image elements, and aggregate failures

The command exits non-zero when a route returns a 4xx/5xx status, an image
request fails, or an `img` element has no rendered dimensions. Set
`ALLOW_MEDIA_FAILURES=true` only when generating exploratory reports for known
legacy blockers.
