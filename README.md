# ASSYABAB / CAHAYA

**Dari ruang mengaji, menuju dunia.**

An independent cinematic presentation website for Pesantren Multimedia Assyabab, built for Azriel Choerul Hakim. This repository does not modify the earlier prototype.

## Open and present

Open `index.html` in a modern browser with WebGL2 enabled, or serve this directory as a static website. There is no npm installation, bundler, API key, paid service, or backend requirement.

The opening contains **Putar perjalanan**, an optional approximately 35-second guided scroll. Scroll manually or use Escape to stop. Chapter navigation and **Lewati sinematik** let visitors go straight to the information. The search shortcut is Ctrl/Cmd+K. A fullscreen control and decorative-motion pause control appear after scrolling.

### Fully offline presentation

The supplied source archive includes a local cache of the documentary photographs. From a fresh GitHub clone, fetch those images once, then build the portable file:

```sh
python3 tools/fetch_assets.py
python3 tools/build_offline.py
```

Open the resulting `ASSYABAB-CAHAYA.html`. It embeds CSS, JavaScript, SVG, and photographs and makes no automatic network requests. WhatsApp and YouTube links need internet only when opened. Do not replace the source `index.html` with this generated file.

**Photo transport:** the ordinary source website references seven public photographic assets pinned to commit `043c819554b6f804ddc5f7ffb9aa3965d21708c8` in the owner's earlier repository. The old repository is read-only for this project; none of its HTML, CSS, or JavaScript is loaded. `assets/manifest.json` records each URL and SHA-256. The offline builder checks those bytes before embedding. A static mirror can replace the URLs during production setup.

## Experience

- Original layered mountain illustration with atmosphere, foreground foliage, and distant birds.
- An actual WebGL2 Quran/rehal/chamber scene with rounded geometry, opening cover, curved page meshes, shadows, floor reflections, light shafts, dust, and a pixel transition into an illustrative studio.
- Source-grounded 4T and ten supporting curriculum groups; vision and mission overlays.
- An on-device composition studio with three palettes and real 1280x800 PNG export.
- Four-part daily journey with corresponding landscape palettes.
- Teacher profiles, documentary gallery, source-index search, FAQ, and on-device WhatsApp draft preparation.

The graphics are illustrative, not a photorealistic scan or a reconstruction of the real campus. Interior ornamental flyleaves are not fabricated Quran verses. There is no autoplay sound. There is no admissions database, booking confirmation, AI chatbot, payment processing, analytics, or automatic message delivery.

## Source organization

```text
index.html                Semantic page and accessible controls
styles/main.css           Cinematic and editorial visual design
src/content.js            Facts, curriculum, people, days, source search index
src/landscape.js           Original Canvas 2D landscape
src/renderer.js            Purpose-built WebGL2 rendering/shaders
src/scenes.js              Quran, rehal, chamber, studio, camera choreography
src/app.js                 Interaction director, gallery, search, draft and PNG tools
assets/manifest.json       Pinned documentary images and checksums
tools/build_offline.py     Standard-library portable exporter
tools/fetch_assets.py      Verified photograph cache download
tests/test_browser.py     Reproducible Playwright regression checks
```

The implementation uses native JavaScript, Canvas 2D and WebGL2, **not Three.js or GSAP**. Fonts use a shared local system stack; different operating systems may select different fallback fonts.

## Verification

See `docs/QA.md` and `docs/test-report.json`. The portable export was rendered and exercised in Chromium 144 using WebGL2/ANGLE SwiftShader on a virtual display. This is an actual browser graphics test, not a hardware-performance, Lighthouse, Safari, or deployed-network test. The visual review included the opening, closed/open/moving book, studio transition, educational sections, day palettes, profiles, gallery and mobile layouts.

For the full regression suite, install Python Playwright and Pillow plus Chromium. Start Xvfb on Linux when needed:

```sh
Xvfb :99 -screen 0 1600x1000x24 -nolisten tcp &
ASSYABAB_TEST_DISPLAY=:99 python3 tests/test_browser.py
```

These are development-only tools. Visitors do not need them.

## Content status

Facts and photographic documentation are based on the owner-supplied `Pesantren Assyabab Profile and Programs.pptx`. See `docs/CONTENT-SOURCES.md`. Confirm roles, contacts, licensing of photographs, admissions, diploma arrangements, fees, quotas and aid criteria with the institution before an official launch. The design mark and editorial language are proposals, not an asserted official identity. Search indexing is disabled intentionally for this presentation build.

Committing these files does not itself enable GitHub Pages or create a Vercel deployment. The static build and offline presentation are independent of any hosting setup.
