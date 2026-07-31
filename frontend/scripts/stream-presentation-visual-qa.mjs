import { chromium } from 'playwright-core';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const appUrl = process.env.APP_URL ?? 'http://127.0.0.1:4177';
const outputDir = path.resolve(process.cwd(), '..', 'output', 'playwright', 'stream-presentation-modes');
const chromePath = process.env.CHROME_EXECUTABLE_PATH ?? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const modes = [
  'atom-list',
  'popup-channel-card',
  'single-entry-html',
  'event-story-list',
  'rss-list',
  'google-reader-frontpage',
];

await mkdir(outputDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: chromePath,
  headless: true,
});

const artifacts = [];

try {
  const page = await browser.newPage({ viewport: { width: 1366, height: 900 } });
  await page.goto(`${appUrl}/streams/presentation-preview`, { waitUntil: 'networkidle' });

  for (const mode of modes) {
    const count = await page.locator(`[data-mode="${mode}"]`).count();
    if (count !== 1) {
      throw new Error(`Expected one fixture for ${mode}, found ${count}`);
    }
  }

  const desktopPath = path.join(outputDir, 'desktop-all-modes.png');
  await page.screenshot({ path: desktopPath, fullPage: true });
  artifacts.push(desktopPath);

  await page.locator('[data-mode="popup-channel-card"] .stream-entry-card').hover();
  const popupPath = path.join(outputDir, 'desktop-popup-hover.png');
  await page.locator('[data-mode="popup-channel-card"]').screenshot({ path: popupPath });
  artifacts.push(popupPath);

  await page.locator('[data-mode="popup-channel-card"] .stream-entry-card').focus();
  const focusPath = path.join(outputDir, 'desktop-popup-keyboard-focus.png');
  await page.locator('[data-mode="popup-channel-card"]').screenshot({ path: focusPath });
  artifacts.push(focusPath);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${appUrl}/streams/presentation-preview`, { waitUntil: 'networkidle' });
  const mobilePath = path.join(outputDir, 'mobile-all-modes.png');
  await page.screenshot({ path: mobilePath, fullPage: true });
  artifacts.push(mobilePath);

  const report = {
    generatedAt: new Date().toISOString(),
    appUrl,
    modes,
    artifacts,
  };
  await writeFile(path.join(outputDir, 'report.json'), `${JSON.stringify(report, null, 2)}\n`, 'utf8');
  console.log(JSON.stringify(report, null, 2));
} finally {
  await browser.close();
}
