# ASSYABAB / CAHAYA

**Dari ruang mengaji, menuju dunia.**

A cinematic presentation for Pesantren Multimedia Assyabab. The Quran-to-studio
sequence is now a graded, scroll-controlled film, replacing the procedural 3D
book and computer scene. The existing illustrated mountains and birds remain.

## Preview

Open `index.html` directly, or use a current Node.js runtime:

```sh
node tools/serve.mjs
```

Visit `http://127.0.0.1:4173`. The local server supports video byte-range requests.
No npm dependencies, backend, API key, or paid service is needed by the site.
Deploy this folder to a static host that serves MP4 files as `video/mp4` and
supports range requests. This commit does not change hosting configuration.

## Film and atmosphere

- The owner's supplied 10-second film is trimmed to 9.5 seconds, subtly graded,
  muted, and encoded with a keyframe every six frames for responsive reverse seeking.
- Native scroll controls the film with light, time-based smoothing. The page never
  intercepts the wheel or forces scroll steps. Chapter buttons and a skip link remain.
- Mobile uses a smaller encode; portrait layouts retain the entire 16:9 composition.
  Short landscape screens use compact captions over a full-bleed film.
  Missing video falls back to its poster
  with an explicit retry; the rest of the website still works.
- Reduced motion uses a stationary scene with explicit chapter selection. The
  manual motion pause keeps the page height stable and freezes decorative motion.
- Scroll gives grass, leaves and valley mist a shared, signed breeze which eases
  back to calm. Thin clouds pass through daylight shafts over the mountains.
- Mist gives the large opening wordmark depth and connects the landscape to the
  film; a warm light transition leads out toward the education story.
- The education ornament draws itself as it enters the viewport, then rotates
  gently. The night landscape has warm fireflies and small reflections on water.
- These effects share the page's animation clock and respect motion pause,
  reduced motion and hidden tabs. Existing birds remain; no extra birds were added.
- **Suara air** is optional synthesized water ambience, generated on-device with
  Web Audio. It starts only after a click, has a volume control, fades off, and
  suspends in hidden tabs. It is not a campus recording or a Quran recitation.
- The optional **Putar perjalanan** guides the scroll for about 35 seconds. Escape,
  manual scroll or touch stops it. Sound remains a separate opt-in control.

See [video preparation and media checksums](docs/VIDEO.md).

## Content and tools

The education, curriculum, daily-life, teacher and gallery sections remain. The
composition studio exports a real 1280×800 PNG; search runs locally; contact forms
prepare a WhatsApp draft without submitting or sending it automatically.

The photos are now mirrored locally. `assets/manifest.json` retains the pinned
original URLs and SHA-256 values. The illustrations and supplied film are artistic
interpretations, not documentation of the real campus. Small text in the film is
not presented as Quran reading material. Institutional information is based on
the owner-supplied profile; see `docs/CONTENT-SOURCES.md`.

## Offline presentation

```sh
python tools/build_offline.py
```

The generated `ASSYABAB-CAHAYA.html` embeds scripts, styles, photos, posters and
both video encodes (about 16 MB). It works without a server. WhatsApp and YouTube
need internet only when their links are opened. Keep this export separate from
`index.html`. If local documentary assets are missing, run `python tools/fetch_assets.py`.

## Verification

```sh
python -m unittest discover -s tests -p test_video_source.py
python tests/test_browser.py
```

Browser checks require Python Playwright, Pillow and Chromium/Chrome/Edge.
`ASSYABAB_TEST_BROWSER` selects an installed Chromium-family executable;
`ASSYABAB_TEST_URL=http://127.0.0.1:4173` tests the served build instead of the
portable export. See `docs/QA.md` for the exact verification and its limits.

## Source map

| Path | Purpose |
| --- | --- |
| `src/scroll-video.js` | Lazy loading, coalesced seeking, smoothing and fallback |
| `src/ambience.js` | Optional water audio and subtle landscape details |
| `src/landscape.js` | Existing native Canvas landscapes and birds |
| `src/atmosphere.js` | Shared-wind layers, mist transitions, wordmark depth and geometry |
| `src/app.js` | Page interaction, chapters, dialogs and creative tools |
| `styles/film.css` | Responsive film composition |
| `styles/ambience.css` | Leaves, ripples and audio controls |
| `styles/atmosphere.css` | Mist, light transitions and progressive ornament styling |
| `tools/prepare_video.py` | Reproducible video grade and encoding |

This is still a presentation site: no enrollment database, payments, analytics,
or automatic message delivery. Search indexing remains intentionally disabled.
