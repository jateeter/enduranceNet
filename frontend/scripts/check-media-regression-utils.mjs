import assert from 'node:assert/strict';

import {
  annotateMediaFailure,
  buildManifestLookup,
  buildWaiverLookup,
} from './media-regression-utils.mjs';

const appUrl = 'http://localhost';
const manifestLookup = buildManifestLookup(
  [
    {
      source_path: 'images/photo.jpg',
      cms_asset_id: 'legacy-photo',
      public_url: '/legacy-media/images/photo.jpg',
      cms_public_url: '/media/legacy-photo/photo.jpg',
      asset_kind: 'image',
      checksum_sha256: 'sha-photo',
    },
  ],
  appUrl,
);
const waiverLookup = buildWaiverLookup([{ referenced_path: 'images/photo.jpg', reason: 'source withheld' }]);

const annotatedLegacy = annotateMediaFailure(
  { url: 'http://localhost/legacy-media/images/photo.jpg', status: 404 },
  { appUrl, manifestLookup, waiverLookup },
);
assert.equal(annotatedLegacy.sourcePath, 'images/photo.jpg');
assert.equal(annotatedLegacy.cmsAssetId, 'legacy-photo');
assert.equal(annotatedLegacy.waived, true);
assert.equal(annotatedLegacy.waiverReason, 'source withheld');

const annotatedCms = annotateMediaFailure(
  { url: 'http://localhost/media/legacy-photo/photo.jpg', status: 404 },
  { appUrl, manifestLookup, waiverLookup: new Map() },
);
assert.equal(annotatedCms.sourcePath, 'images/photo.jpg');
assert.equal(annotatedCms.cmsAssetId, 'legacy-photo');
assert.equal(annotatedCms.waived, false);

const inferredLegacy = annotateMediaFailure(
  { url: 'http://localhost/legacy-media/images/unknown.jpg', status: 404 },
  { appUrl, manifestLookup: new Map(), waiverLookup: new Map() },
);
assert.equal(inferredLegacy.sourcePath, 'images/unknown.jpg');
assert.equal(inferredLegacy.cmsAssetId, '');

console.log('media regression utility checks passed');
