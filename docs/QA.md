# Verification: scroll film and optional atmosphere

The procedural WebGL book/studio renderer has been removed. Verification now
checks decoded video frames and page behavior, rather than old shader results.

## Automated checks

`tests/test_browser.py` runs in a real Chromium-family browser using Playwright.
It checks the served source and the standalone offline export separately:

- Actual H.264 decode and nonempty pixels; first, curtain, studio, reverse and last frames.
- Scroll-to-time synchronization in both directions and coalesced seek completion.
- Eleven viewport sizes, including 320x568, 320x740 and 667x375 phone layouts;
  captions, chapter controls and the sound dock are checked for overlaps.
- The smaller mobile encode on a fresh mobile page. Portrait layouts retain the
  full composition; short landscape screens use a covering film with compact overlays.
- Reduced motion freezes the frame, with explicit chapter navigation still available.
- Missing/failed media retains the poster and working page controls.
- Sound is off on arrival/reload; a real user click creates/resumes Web Audio;
  volume changes and sound-off suspension work. Sound controls are inert behind menus.
- Menu focus, search, curriculum, daily palettes, teacher profiles, gallery,
  poster PNG export, contact draft validation, FAQ, and source disclosure.
- Main information remains usable without JavaScript.
- No page JavaScript errors, and no external network requests from the portable export.
- Real landscape pixel changes in daytime light/cloud, wind/grass/mist, and night
  firefly/reflection regions. Deterministic renderer probes verify that the complete
  canvas stays unchanged when paused despite time, wind, pointer and zoom input.
- Scroll direction reaches both landscapes and visible leaf layers; the wordmark
  and foreground mist move, chapter fog/light appear, and SVG strokes draw, rotate
  and retrace when scrolling back.
- Manual pause and system reduced motion freeze actual canvas pixels and computed
  SVG/CSS decoration styles. Reduced motion reveals the complete static geometry.
- Decorative overlays remain outside keyboard/pointer interaction. Visible mobile
  hero controls are checked for sound-dock collisions and actual pointer hit targets.

`tests/test_video_source.py` checks byte-exact media embedding, missing-resource
failure, and prevention of source overwrite in the portable exporter (3 checks).
`node --check` validates the edited JavaScript entry points.

The reports are `docs/test-report-source.json` and `docs/test-report.json` and
include browser version, actual results and source hashes. Screenshots are
reproducible with `python tools/render_check.py` and kept out of Git.

The final Windows run passed **123 served-source checks** and **124 portable-export
checks** in Microsoft Edge 154.0.4258.37. The portable run includes the additional
zero-network check. Both reports match the current application source bytes.
The exporter unit suite passed all **3 tests**. The rebuilt portable HTML payload is
15,719,595 UTF-8 bytes (about 15.0 MiB; local text-file line endings can add bytes).

## Visual and media review

The supplied film was inspected before editing, and graded frames were checked
across the Quran, curtain and editing-desk compositions. The desktop and mobile
encodes both fully decode to 228 frames with 38 keyframes and no audio track.
Their metadata, provenance and hashes are recorded in `VIDEO.md`.

Desktop and mobile screenshots were inspected. A narrow first caption on mobile,
a dropped rapid chapter seek in paused mode, page collapse on manual pause,
and caption/control collisions at short viewport heights were found and corrected.
Captions were shortened to keep the film prominent.

The nature pass inspected daylight, night, geometry, both chapter boundaries and
the mobile opening. The firefly/reflection contrast was adjusted after viewing the
actual night composition, and mobile opening controls were moved clear of the
sound dock. Pixel comparisons and DOM geometry checks complement this visual review.

The optional water sound is synthesized locally. Sample buffers at 44.1, 48 and
96 kHz were checked for finite values, headroom and continuity at the loop seam.
This is a technical audio check, not proof of a recorded natural environment.

## Limits

The browser tests run in headless Microsoft Edge/Chromium on Windows, not on
physical phones. They do not establish Safari/iOS behavior, low-end GPU/decoder
performance, mobile battery usage, all assistive technologies or Core Web Vitals.
The ordinary site and portable file are both tested locally; hosted delivery must
serve video with correct MIME type and byte ranges. GitHub repository publication
is separate from configuring or deploying a public website.

The original supplied-video detail and provenance mark are retained. The video
is illustrative, not documentary campus footage or Quran reading material.
