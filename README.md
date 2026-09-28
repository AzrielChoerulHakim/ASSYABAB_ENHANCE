# ASSYABAB / CAHAYA

**Dari ruang mengaji, menuju dunia.**

Independent presentation website for Pesantren Multimedia Assyabab. Native JavaScript, Canvas 2D landscapes and a scroll-controlled cinematic video. No npm install, backend, API key or paid runtime service is required.

## Video migration — draft delivery

This branch replaces the procedural WebGL Quran scene with the owner's 10-second video. **The five binary media files must be uploaded before merging.** They are provided separately in `ASSYABAB-VIDEO-ASSETS.zip`; extract it and preserve `assets/cinema/` at the repository root. The companion `ASSYABAB-VIDEO-PREVIEW.html` already embeds all assets and is ready to open offline. The active `main` branch has not been changed by this draft.

See [migration and delivery notes](docs/VIDEO-CINEMATIC.md) and [51-check report](docs/video-test-report.json). Older WebGL QA documents and `tests/test_browser.py` are historical and do not verify the replacement.

## Experience

Mountain illustration → Quran video → source-grounded education → multimedia composition tool → daily activities → teacher profiles → documentary gallery → contact. Chapter navigation, search (Ctrl/Cmd+K), image gallery, safe WhatsApp draft preparation and local 1280×800 PNG export remain. The optional guided journey can be stopped by scrolling, touching or Escape.

The video is paused, muted and inline; scrolling controls its time in either direction. Three text chapters follow the actual media position. Portrait mobile retains the whole 16:9 frame. Reduced motion, manual pause and Save-Data use three static frames. Media failure retains an image and offers retry.

## Open and export

With the media folder present, serve this directory as a static website. To produce the portable HTML, cache the checksum-pinned documentary photographs first:

```sh
python3 tools/fetch_assets.py
python3 tools/build_offline.py
```

The builder checks photo and video SHA-256 values before embedding. Do not replace source `index.html` with the generated HTML. WhatsApp and YouTube need internet only when opened. Deployment is separate from committing source.

## Source organization

```text
index.html                  Semantic page and controls
styles/main.css             Original site design
styles/cinema-video.css     Scoped video and mobile layouts
src/app.js                  Interactions and chapter timing
src/cinema-video.js         Lazy loading, seek queue and fallback
src/content.js              Source-based institutional content
src/landscape.js            Canvas 2D landscapes
assets/cinema/              Video, three stills and hash manifest
assets/manifest.json        Documentary image sources and hashes
tools/build_offline.py      Portable HTML builder
tests/test_cinema_video.py  New video regression checks
```

The legacy `renderer.js` and `scenes.js` remain for history but are not loaded. Photos reference the owner's earlier repository at a pinned commit; its application code is not loaded or changed.

## Content status

Institutional information and documentary photographs come from the owner-supplied `Pesantren Assyabab Profile and Programs.pptx`; see `docs/CONTENT-SOURCES.md`. Roles, contact information, fees, aid, admissions, diploma arrangements and photograph permissions need institutional confirmation before an official launch.

The new cinematic is an AI-assisted illustration supplied by the owner, not real campus footage. Its Arabic details are not verified Quran text. The design mark and editorial language are proposals, not asserted official branding. No analytics, automatic messaging, admissions database or runtime AI service is added. Search indexing remains intentionally disabled for this presentation.
