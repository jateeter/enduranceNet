import { chromium } from 'playwright-core';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const appUrl = process.env.APP_URL ?? process.env.BASE_URL ?? 'http://localhost';
const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright', 'mastheads');
const chromePath = process.env.CHROME_EXECUTABLE_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const routes = [
  { name: 'home', path: '/', variant: 'home' },
  { name: 'news', path: '/news', variant: 'section-news' },
  { name: 'featured-stories', path: '/featured-stories', variant: 'section-featured-stories' },
  { name: 'events', path: '/events', variant: 'section-events' },
  { name: 'results', path: '/results', variant: 'section-results' },
  { name: 'galleries', path: '/galleries', variant: 'section-galleries' },
  { name: 'community', path: '/community', variant: 'section-community' },
  { name: 'streams', path: '/streams', variant: 'section-streams' },
  { name: 'learn-aerc', path: '/athletes', variant: 'section-learn-aerc' },
  { name: 'tevis-event', path: '/events/2026-tevis-cup', variant: 'event-tevis-2026' },
  { name: 'tevis-deep-link', path: '/international/USA/2026TevisCup/gallery.html', variant: 'event-tevis-2026' },
  { name: 'not-found', path: '/not-a-real-endurance-route', variant: 'archive' },
];

const viewports = [
  { name: 'desktop', width: 1366, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];

function routeUrl(routePath) {
  return new URL(routePath, `${appUrl.replace(/\/$/, '')}/`).toString();
}

function sameOriginUrl(url) {
  if (!url.startsWith('/')) return url;
  return new URL(url, `${appUrl.replace(/\/$/, '')}/`).toString();
}

await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
});

const report = {
  generatedAt: new Date().toISOString(),
  appUrl,
  routes: [],
  failures: [],
};

try {
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });

    for (const route of routes) {
      const url = routeUrl(route.path);
      const response = await page.goto(url, { waitUntil: 'networkidle' });
      const routeStatus = response?.status() ?? 0;

      const mastheadReport = await page.evaluate(() => {
        const mastheads = [...document.querySelectorAll('.masthead')];
        const masthead = mastheads[0];
        const navbar = document.querySelector('.navbar');
        const rect = masthead?.getBoundingClientRect();
        const topElement = document.elementFromPoint(Math.max(1, window.innerWidth / 2), 8);

        return {
          count: mastheads.length,
          isFirstNavbarElement: navbar?.firstElementChild === masthead,
          variant: masthead?.getAttribute('data-masthead-variant') ?? '',
          kind: masthead?.getAttribute('data-masthead-kind') ?? '',
          image: masthead?.getAttribute('data-masthead-image') ?? '',
          top: rect?.top ?? null,
          height: rect?.height ?? null,
          isTopVisible: masthead ? Boolean(topElement?.closest('.masthead')) : false,
          title: masthead?.querySelector('.masthead-title')?.textContent?.trim() ?? '',
          subtitle: masthead?.querySelector('.masthead-subtitle')?.textContent?.trim() ?? '',
        };
      });

      const imageUrl = mastheadReport.image ? sameOriginUrl(mastheadReport.image) : '';
      const imageStatus = imageUrl ? await page.request.get(imageUrl).then((asset) => asset.status()) : 0;
      const screenshotPath = path.join(outputDir, `${route.name}-${viewport.name}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });

      const routeReport = {
        name: route.name,
        path: route.path,
        viewport: viewport.name,
        url,
        status: routeStatus,
        expectedVariant: route.variant,
        masthead: mastheadReport,
        mastheadImageStatus: imageStatus,
        screenshot: screenshotPath,
      };
      report.routes.push(routeReport);

      if (routeStatus >= 400 || routeStatus === 0) {
        report.failures.push({ ...routeReport, type: 'route-status' });
      }
      if (mastheadReport.count !== 1) {
        report.failures.push({ ...routeReport, type: 'masthead-count' });
      }
      if (!mastheadReport.isFirstNavbarElement || !mastheadReport.isTopVisible || mastheadReport.top !== 0) {
        report.failures.push({ ...routeReport, type: 'masthead-position' });
      }
      if (mastheadReport.variant !== route.variant) {
        report.failures.push({ ...routeReport, type: 'masthead-variant' });
      }
      if (imageStatus >= 400 || imageStatus === 0) {
        report.failures.push({ ...routeReport, type: 'masthead-image' });
      }
    }

    await page.close();
  }

  await writeFile(path.join(outputDir, 'report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report, null, 2));

  if (report.failures.length > 0) {
    process.exitCode = 1;
  }
} finally {
  await browser.close();
}
