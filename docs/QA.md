# Render, inspect, correct, test

## What was actually exercised

The self-contained export was rendered inside Chromium 144.0.7559.96 using Playwright, WebGL2 and ANGLE SwiftShader on Xvfb. All shaders ran in the browser; this is not a substitution of pre-rendered screenshots for interactive 3D. Browser navigation to network URLs was unavailable in the execution environment, so tests used `page.set_content` on the portable HTML. No hosted-site test is claimed.

The regression report records the exact SHA-256 of every HTML/CSS/JavaScript source file. Its checks cover image decoding, menu focus isolation and keyboard wrap, search and literal input handling, all four program panels, day palettes and keyboard controls, teacher directory, gallery/lightbox focus return, actual 1280x800 PNG output, validated WhatsApp drafts, stale-draft invalidation, visit disclaimers, FAQ and source disclosure.

Eight viewport widths were checked: **320, 390, 700, 760, 768, 1024, 1440 and 1920 pixels**. Six animation progress values were rendered and checked for GL errors. Graphics-context loss/restoration, unavailable-GPU fallback, film start/stop, system reduced-motion changes, and essential no-JavaScript content were tested. No JavaScript errors or automatic network calls were observed in the tested portable-export sequence.

## Visual iterations

1. Inspected the first landscape and cinematic frames. Replaced the overly striped mountain shading with subtle granular layers and near-ridge canopy detail.
2. Rebalanced room lighting and reduced visual noise from dust/orbital lines. Shifted the Quran framing so its title does not obscure the book; pulled the studio camera back to separate the monitor from the large editorial heading.
3. Inspected actual closed-book, moving-page, open-book and studio frames. Inspected editorial, daily palette, teacher, gallery, ending and narrow-screen layouts. Corrected an off-screen skip-link positioning issue and checked the final source again.
4. Corrected a degenerate zero-length tube segment in geometry generation, then recompiled and rendered all cinematic stages. Rechecked keyboard focus and context restoration rather than declaring success after an initial screenshot. A stricter two-dimensional viewport check caught a stale WebGL canvas height when both viewport dimensions changed; a ResizeObserver now tracks settled container dimensions and the complete suite was rerun.

Screenshots in the delivered source archive show the rendered design. `tools/render_check.py` regenerates four core screenshots with the same browser setup. `tests/test_browser.py` writes `test-report.json` and saves a real poster export.

## Limits

This is a presentation build, not a guarantee of visual approval. SwiftShader is software rendering, so these results do **not** measure laptop GPU frame rate, battery use, Core Web Vitals, Lighthouse, real mobile devices, Safari/iOS, Firefox, or all assistive technologies. Hosting, external photograph delivery, the YouTube video and WhatsApp service were not end-to-end tested. Fullscreen depends on browser permission and support.

The ordinary website loads pinned documentary image URLs. The tested portable version embeds them. Fallback typography may vary across operating systems. No administrative backend, enrollment/payment system, automatic messaging, or appointment booking is claimed.
