#!/usr/bin/env python3
"""Save actual video/landscape screenshots using the regression browser setup."""
import importlib.util
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('assyabab_regression', ROOT / 'tests/test_browser.py')
test = importlib.util.module_from_spec(spec)
spec.loader.exec_module(test)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(**test.browser_options())
    page = browser.new_page(viewport={'width': 1440, 'height': 960}, device_scale_factor=1, reduced_motion='reduce')
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    html = None if test.URL else test.build()
    test.load(page, html)
    page.screenshot(path=str(test.SHOTS / '01-landscape.png'), timeout=120000)
    page.emulate_media(reduced_motion='no-preference')
    for progress, label in [(.08, '02-quran'), (.48, '03-curtain'), (.90, '04-studio')]:
        test.scroll_film(page, progress)
        test.wait_frame(page, progress)
        page.screenshot(path=str(test.SHOTS / (label + '.png')), timeout=120000)
        print(label, page.locator('#cinema-video').evaluate('v=>({time:v.currentTime,duration:v.duration,width:v.videoWidth})'), flush=True)
    print('metrics', page.evaluate('AssyababDebug.metrics'), 'errors', errors, flush=True)
    assert not errors, errors
    browser.close()
