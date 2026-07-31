import { chromium } from 'playwright-core';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import {
  annotateMediaFailure,
  buildManifestLookup,
  buildWaiverLookup,
  readJsonl,
} from './media-regression-utils.mjs';

const appUrl = process.env.APP_URL ?? process.env.BASE_URL ?? 'http://127.0.0.1:4177';
const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright', 'production-regression');
const chromePath = process.env.CHROME_EXECUTABLE_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const failOnMedia = process.env.ALLOW_MEDIA_FAILURES !== 'true';
const mediaManifestPath = process.env.MEDIA_MANIFEST ?? process.env.IMAGE_MEDIA_MANIFEST ?? '';
const mediaWaiversPath = process.env.MEDIA_WAIVERS ?? process.env.MEDIA_WAIVER_FILE ?? '';

const routes = [
  { name: 'home', path: '/' },
  { name: 'streams', path: '/streams' },
  { name: 'stream-search', path: '/streams/search' },
  { name: 'stream-detail', path: '/streams/endurance-tracks' },
  { name: 'events', path: '/events' },
  { name: 'featured-stories', path: '/featured-stories' },
  { name: 'community', path: '/community' },
  { name: 'results', path: '/results' },
  { name: 'legacy-current-news', path: '/CurrentNews/' },
];

const viewports = [
  { name: 'desktop', width: 1366, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];

function routeUrl(routePath) {
  return new URL(routePath, `${appUrl.replace(/\/$/, '')}/`).toString();
}

function artifactName(routeName, viewportName) {
  return `${routeName}-${viewportName}.png`;
}

await mkdir(outputDir, { recursive: true });

const mediaManifestRows = mediaManifestPath ? await readJsonl(mediaManifestPath) : [];
const mediaWaiverRows = mediaWaiversPath ? await readJsonl(mediaWaiversPath) : [];
const manifestLookup = buildManifestLookup(mediaManifestRows, appUrl);
const waiverLookup = buildWaiverLookup(mediaWaiverRows);

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
});

const report = {
  generatedAt: new Date().toISOString(),
  appUrl,
  mediaManifest: mediaManifestPath,
  mediaWaivers: mediaWaiversPath,
  routes: [],
  failures: [],
  waivedFailures: [],
  artifacts: [],
};

try {
  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height } });

    for (const route of routes) {
      const url = routeUrl(route.path);
      const mediaFailures = [];
      const requestFailures = [];

      page.removeAllListeners('response');
      page.removeAllListeners('requestfailed');
      page.on('response', (response) => {
        const request = response.request();
        if (request.resourceType() === 'image' && response.status() >= 400) {
          mediaFailures.push({
            url: response.url(),
            status: response.status(),
          });
        }
      });
      page.on('requestfailed', (request) => {
        if (request.resourceType() === 'image') {
          requestFailures.push({
            url: request.url(),
            error: request.failure()?.errorText ?? 'request failed',
          });
        }
      });

      const response = await page.goto(url, { waitUntil: 'networkidle' });
      const status = response?.status() ?? 0;
      const screenshotPath = path.join(outputDir, artifactName(route.name, viewport.name));
      await page.screenshot({ path: screenshotPath, fullPage: true });
      report.artifacts.push(screenshotPath);

      const brokenImages = await page.locator('img').evaluateAll((images) =>
        images
          .map((image) => ({
            src: image.currentSrc || image.src,
            alt: image.getAttribute('alt') || '',
            naturalWidth: image.naturalWidth,
            naturalHeight: image.naturalHeight,
          }))
          .filter((image) => image.src && (image.naturalWidth === 0 || image.naturalHeight === 0)),
      );

      const context = { appUrl, manifestLookup, waiverLookup };
      const annotatedMediaFailures = mediaFailures.map((failure) => annotateMediaFailure(failure, context));
      const annotatedRequestFailures = requestFailures.map((failure) => annotateMediaFailure(failure, context));
      const annotatedBrokenImages = brokenImages.map((image) =>
        annotateMediaFailure({ ...image, url: image.src }, context),
      );

      const routeReport = {
        route: route.path,
        name: route.name,
        viewport: viewport.name,
        url,
        status,
        screenshot: screenshotPath,
        mediaFailures: annotatedMediaFailures,
        requestFailures: annotatedRequestFailures,
        brokenImages: annotatedBrokenImages,
      };
      report.routes.push(routeReport);

      if (status >= 400 || status === 0) {
        report.failures.push({
          type: 'route-status',
          route: route.path,
          viewport: viewport.name,
          status,
          url,
          screenshot: screenshotPath,
        });
      }
      for (const failure of [...annotatedMediaFailures, ...annotatedRequestFailures]) {
        const reportEntry = {
          type: 'media-request',
          route: route.path,
          viewport: viewport.name,
          ...failure,
          screenshot: screenshotPath,
        };
        if (failure.waived) {
          report.waivedFailures.push(reportEntry);
        } else {
          report.failures.push(reportEntry);
        }
      }
      for (const image of annotatedBrokenImages) {
        const reportEntry = {
          type: 'broken-img-element',
          route: route.path,
          viewport: viewport.name,
          ...image,
          screenshot: screenshotPath,
        };
        if (image.waived) {
          report.waivedFailures.push(reportEntry);
        } else {
          report.failures.push(reportEntry);
        }
      }
    }

    await page.close();
  }

  await writeFile(path.join(outputDir, 'report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report, null, 2));

  if (report.failures.length > 0 && failOnMedia) {
    process.exitCode = 1;
  }
} finally {
  await browser.close();
}
