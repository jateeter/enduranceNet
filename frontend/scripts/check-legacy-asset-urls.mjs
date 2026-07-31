import assert from 'node:assert/strict';

import { legacyAssetUrl, rewriteLegacyMediaReferences } from '../src/utils/legacyAssets.ts';

const cases = [
  ['http://endurance.net/images/photo.jpg', '/legacy-media/images/photo.jpg'],
  ['https://www.endurance.net/images/photo.jpg?size=large', '/legacy-media/images/photo.jpg?size=large'],
  ['http://feeds.endurance.net/images/photo.jpg?x=1#caption', '/legacy-media/images/photo.jpg?x=1#caption'],
  ['/images/photo.jpg?cache=1', '/legacy-media/images/photo.jpg?cache=1'],
  ['images/photo.jpg', '/legacy-media/images/photo.jpg'],
  ['/legacy-media/images/photo.jpg?cache=1', '/legacy-media/images/photo.jpg?cache=1'],
  ['/media/legacy-asset/photo.jpg', '/media/legacy-asset/photo.jpg'],
  ['https://blogger.googleusercontent.com/img/a/photo.jpg', 'https://blogger.googleusercontent.com/img/a/photo.jpg'],
  ['data:image/png;base64,abc', 'data:image/png;base64,abc'],
];

for (const [input, expected] of cases) {
  assert.equal(legacyAssetUrl(input), expected, input);
}

const html = [
  '<img src="http://feeds.endurance.net/images/photo.jpg?x=1">',
  '<img src="https://www.endurance.net/images/other.jpg#caption">',
  '<img src="https://blogger.googleusercontent.com/img/a/photo.jpg">',
].join('');

assert.equal(
  rewriteLegacyMediaReferences(html),
  [
    '<img src="/legacy-media/images/photo.jpg?x=1">',
    '<img src="/legacy-media/images/other.jpg#caption">',
    '<img src="https://blogger.googleusercontent.com/img/a/photo.jpg">',
  ].join(''),
);

console.log('legacy asset URL rewrite checks passed');
