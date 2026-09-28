# Cahaya: video cinematic replacement

## Delivery status

The text implementation is staged on `feat/veo-scroll-cinematic-20260928`. Keep this PR in draft until the five binary media assets under `assets/cinema/` are uploaded. They are supplied in the accompanying `ASSYABAB-VIDEO-ASSETS.zip`; the GitHub connector in this session has no local-file upload action. `main` was deliberately not changed. A working self-contained preview with all media is supplied separately as `ASSYABAB-VIDEO-PREVIEW.html`.

Extract the asset ZIP and upload its `assets` folder to the root of this branch, retaining subfolders. Do not upload the ZIP itself as the video source. Run the offline builder and regression checks, then merge only after confirming the deployed asset URLs work.

## What changed

`index.html` loads `src/cinema-video.js` and `styles/cinema-video.css` instead of the procedural Quran renderer. Legacy `renderer.js` and `scenes.js` are retained for history but are not loaded. All other page sections and source-based information are preserved. The original `tests/test_browser.py` and older QA reports describe the legacy WebGL build, not this migration.

The supplied 10-second video starts with an already-open Quran, passes behind a curtain, and reveals a student at a multimedia workstation. The video stays muted, inline and paused; scrolling seeks its timeline in either direction. Text tracks the decoded media position, not an ahead-of-video scroll estimate.

| Chapter | Video progress | Jump target |
| --- | --- | --- |
| Sumber | 0–24% | 2% |
| Cahaya | 24–57% | 34% |
| Karya | 57–100% | 87% |

Copy fades around the curtain transition (43–60%). Mobile portrait preserves the whole 16:9 image and places text below it, rather than cutting the Quran or student out of a tall crop.

## Media

Both MP4 deliveries are H.264, yuv420p, 24 fps, with no audio, fast-start metadata and a 12-frame keyframe interval. Desktop is 1280×720 / 3,287,269 bytes; mobile is 960×540 / 1,494,367 bytes. Source footage is unchanged; compression does not repair AI-generated geometry. Three 960×540 JPEG stills are extracted at 0, 3.5 and 8.9 seconds. Exact checksums are in `assets/cinema/manifest.json`.

The browser selects one video on first load and does not fetch another variant on resize. An IntersectionObserver delays source assignment until near the cinema section. One seek is processed at a time; the latest scroll target is retained. Seeking stops at rest and outside the active area.

Reduced-motion, manual motion pause, Save-Data and `?media=off` use three stills. A failed or stalled video leaves a visible still and a retry action. The 15-second loading and 5-second seeking timeouts are graceful-degradation guards, not performance promises. The portable HTML embeds both variants, so its file size is larger even in reduced-motion mode.

## Verification

51 assertions passed in Chromium 144.0.7559.96: 31 desktop, 12 mobile viewport, 8 reduced-motion/error/Save-Data. See `docs/video-test-report.json` for exact browser metadata, source hashes and individual results. Visual screenshots were reviewed on desktop and 390×844 portrait; layout checks also cover 360×640 and 844×390.

These are offline browser tests. A media error was injected to exercise the fallback handler. Live hosting, HTTP range/network behavior, Safari/iOS, physical phones, no-JavaScript rendering, hardware FPS and Lighthouse were not verified. Native noscript markup remains, but no successful no-JavaScript browser run is claimed.

```sh
python3 tools/fetch_assets.py
python3 tools/build_offline.py
# Development only: Python Playwright + Pillow, and Chromium required.
ASSYABAB_BROWSER=/usr/bin/chromium python3 tests/test_cinema_video.py --part desktop
ASSYABAB_BROWSER=/usr/bin/chromium python3 tests/test_cinema_video.py --part mobile
ASSYABAB_BROWSER=/usr/bin/chromium python3 tests/test_cinema_video.py --part fallback
```

## Content provenance

This is an owner-supplied AI-assisted illustrative film, not documentary footage of the actual pesantren or a geographic reconstruction. Generated Arabic details in the film are not verified Quran text and must not be treated as a reading reference. The page and source modal make this distinction. The photographs and institutional information retain their original source provenance. No AI service is called when the page runs.
