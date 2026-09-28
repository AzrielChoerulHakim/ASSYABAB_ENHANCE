#!/usr/bin/env python3
"""Real Chromium regression for the scroll film, ambience and presentation tools.

ASSYABAB_TEST_URL serves a source build; unset it to test the portable export.
ASSYABAB_TEST_BROWSER may point at any compatible Chrome/Edge executable.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import traceback

from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from build_offline import build

URL = os.environ.get('ASSYABAB_TEST_URL')
OUT = ROOT / 'docs'
SHOTS = OUT / 'screenshots'
SHOTS.mkdir(exist_ok=True, parents=True)
report = {'method': 'Headless Chromium; actual video decode, bidirectional scroll seeking, optional local audio and UI regression. Not a hardware performance or Safari test.',
          'mode': 'served source' if URL else 'portable export', 'checks': {}, 'viewports': [], 'seeks': [], 'errors': []}


def ok(name, condition=True):
    assert condition, name
    report['checks'][name] = True
    print('PASS', name, flush=True)


def browser_options():
    candidates = [os.environ.get('ASSYABAB_TEST_BROWSER'),
                  r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                  r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                  '/usr/bin/chromium', '/usr/bin/chromium-browser',
                  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    executable = next((p for p in candidates if p and Path(p).is_file()), None)
    options = {'headless': os.environ.get('ASSYABAB_TEST_HEADFUL') != '1',
               'args': ['--no-sandbox', '--disable-dev-shm-usage']}
    if executable:
        options['executable_path'] = executable
    return options


def load(page, html):
    page.set_default_timeout(45000)
    if URL:
        page.goto(URL, wait_until='load', timeout=120000)
    else:
        # set_content rewrites a document but keeps window globals; navigate
        # first so reload checks model a real fresh document and audio context.
        page.goto('about:blank')
        page.set_content(html, wait_until='load', timeout=120000)
    page.wait_for_function('window.AssyababDebug && window.AssyababDebug.scene()')


def scroll_film(page, progress):
    page.evaluate('''p => {
        const section = document.querySelector('#cahaya');
        scrollTo({top:section.offsetTop + p * Math.max(1, section.offsetHeight-innerHeight), behavior:'instant'});
    }''', progress)


def wait_frame(page, progress):
    page.wait_for_function('''p => {
        const video = document.querySelector('#cinema-video');
        return video.readyState >= 2 && !video.seeking && Number.isFinite(video.duration)
            && Math.abs(video.currentTime / video.duration-p) < .035;
    }''', arg=progress, timeout=30000)


def frame_signature(page):
    return page.locator('#cinema-video').evaluate('''video => {
        const canvas = document.createElement('canvas'); canvas.width=32; canvas.height=18;
        const context=canvas.getContext('2d'); context.drawImage(video,0,0,32,18);
        const pixels=context.getImageData(0,0,32,18).data;
        return Array.from(pixels).filter((_,i)=>i%4!==3).join(',');
    }''')


def main():
    report['file_hashes'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in [ROOT / 'index.html', *sorted((ROOT / 'src').glob('*.js')), *sorted((ROOT / 'styles').glob('*.css'))]}
    html = None if URL else build()
    if html:
        report['portable_bytes'] = len(html.encode('utf-8'))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(**browser_options())
        report['browser'] = browser.version
        context = browser.new_context(viewport={'width': 1440, 'height': 960}, reduced_motion='reduce', accept_downloads=True)
        page = context.new_page()
        page.on('pageerror', lambda error: report['errors'].append(str(error)))
        requests = []
        page.on('request', lambda request: requests.append(request.url))
        load(page, html)
        ok('video_element_replaces_webgl', page.locator('#cinema-video').count() == 1 and page.locator('#cinema-canvas').count() == 0)
        ok('video_muted_inline_no_autoplay', page.locator('#cinema-video').evaluate('v=>v.muted && v.playsInline && !v.autoplay && v.paused'))
        ok('audio_off_before_consent', page.evaluate('AssyababAmbience.enabled===false && AssyababAmbience.contextState==="uninitialized"'))
        page.evaluate("Promise.all([...document.querySelectorAll('main img')].map(i=>{i.loading='eager';return i.decode()}))")
        ok('all_documentary_images_decode', page.evaluate("[...document.querySelectorAll('main img')].every(i=>i.complete&&i.naturalWidth>0)"))

        # Keyboard focus isolation and public information tools.
        page.locator('.menu-button').click()
        ok('menu_open', page.locator('#chapter-menu').is_visible())
        ok('menu_background_inert', page.locator('main').evaluate('e=>e.inert'))
        ok('menu_sound_controls_inert', page.locator('.ambience-toggle').evaluate('e=>!!e.closest("[inert]")'))
        page.locator('#chapter-menu a').last.focus(); page.keyboard.press('Tab')
        ok('menu_focus_wrap', page.locator('.menu-button').evaluate('e=>e===document.activeElement'))
        page.keyboard.press('Escape'); ok('menu_close', not page.locator('#chapter-menu').is_visible())
        page.keyboard.press('Control+k'); ok('search_shortcut', page.locator('#search-modal').is_visible())
        page.locator('#search-input').fill('asrama'); ok('source_search', page.locator('.search-result').count() == 1)
        page.locator('#search-input').fill('<img src=x onerror=alert(1)>')
        ok('search_literal_input', page.locator('#search-results img').count() == 0 and page.locator('.search-result').count() == 0)
        page.locator('#search-input').fill('kurikulum'); page.locator('.search-result').click()
        page.wait_for_selector('#information-modal[open]')
        ok('curriculum_from_search', page.locator('.curriculum-grid article').count() == 10)
        page.keyboard.press('Escape')
        for i in range(4):
            page.locator(f'[data-program="{i}"] summary').click()
            if page.locator('.program-list details[open]').count() == 0:
                page.locator(f'[data-program="{i}"] summary').click()
            page.wait_for_function('(i)=>document.querySelector("#program-index").textContent.startsWith(String(i+1).padStart(2,"0"))', arg=i)
            ok('program_' + str(i), page.locator('.program-list details[open]').count() == 1)
        pixels = []
        for i in range(4):
            page.locator(f'[data-day="{i}"]').click()
            ok('day_' + str(i), page.evaluate('AssyababDebug.metrics.day') == i)
            pixels.append(page.locator('#day-landscape').evaluate('c=>Array.from(c.getContext("2d").getImageData(50,20,1,1).data).join(",")'))
        ok('distinct_day_palettes', len(set(pixels)) == 4)
        page.keyboard.press('Home'); ok('day_keyboard', page.evaluate('AssyababDebug.metrics.day') == 0)
        page.locator('[data-person="mudir"]').click(); ok('teacher_profile', 'Riyadi' in page.locator('#modal-title').inner_text())
        page.locator('#modal-content [data-open-people]').click(); ok('people_directory', page.locator('.people-list button').count() == 8)
        page.keyboard.press('Escape')
        page.locator('#gallery-next').click(); page.wait_for_function('document.querySelector(".gallery-track").scrollLeft > 0')
        ok('gallery_moves')
        page.locator('#gallery-prev').click(); page.locator('[data-gallery="0"]').click()
        ok('gallery_dialog', page.locator('#photo-modal').is_visible())
        page.keyboard.press('ArrowRight'); ok('gallery_keyboard', 'Lapangan' in page.locator('#lightbox-caption').inner_text())
        page.keyboard.press('Escape'); ok('gallery_returns_focus', page.locator('[data-gallery="0"]').evaluate('e=>e===document.activeElement'))

        # Export and form drafting stay on-device; nothing is sent.
        page.locator('#poster-title').fill('Ilmu untuk kehidupan.'); page.locator('[data-palette="1"]').click()
        with page.expect_download() as download:
            page.locator('#export-poster').click()
        download.value.save_as(str(OUT / 'test-poster.png'))
        ok('poster_png_export', Image.open(OUT / 'test-poster.png').size == (1280, 800))
        page.locator('[data-open-contact="pendaftaran"]').click(); page.locator('#contact-name').fill('   ')
        page.locator('#contact-form [type="submit"]').click(); ok('name_validation', not page.locator('#contact-result').is_visible())
        page.locator('#contact-name').fill('Wali Santri'); page.locator('#contact-message').fill('Bagaimana informasi pendidikan? <b>teks biasa</b>')
        page.locator('#contact-form [type="submit"]').click()
        ok('whatsapp_draft', 'https://wa.me/6285716113466?text=' in page.locator('.contact-link').get_attribute('href'))
        ok('draft_escaped', page.locator('.contact-preview b').count() == 0)
        page.locator('#contact-name').fill('Nama baru'); ok('draft_invalidated', not page.locator('#contact-result').is_visible())
        page.keyboard.press('Escape'); page.locator('[data-open-contact="kunjungan"]').click()
        ok('visit_not_confirmed', 'belum terjadwal' in page.locator('#contact-form').inner_text()); page.keyboard.press('Escape')
        page.locator('.faq details').first.locator('summary').click(); ok('faq', page.locator('.faq details').first.locator('p').is_visible())
        page.locator('[data-open-sources]').click(); ok('source_disclosure', 'Bukan rekonstruksi' in page.locator('#modal-content').inner_text()); page.keyboard.press('Escape')

        # Real Web Audio starts only on a click; stopping suspends processing.
        page.locator('.ambience-toggle').click()
        page.wait_for_function('AssyababAmbience.enabled && AssyababAmbience.contextState==="running"')
        ok('audio_explicit_start', page.locator('.ambience-toggle').get_attribute('aria-pressed') == 'true')
        page.locator('.ambience-settings').click()
        ok('audio_volume_control', page.locator('#ambience-volume').is_visible())
        page.locator('#ambience-volume').fill('20')
        ok('audio_volume_changes', abs(page.evaluate('AssyababAmbience.volume') - .2) < .001)
        page.locator('.ambience-toggle').click()
        page.wait_for_function('!AssyababAmbience.enabled && AssyababAmbience.contextState==="suspended"')
        ok('audio_explicit_stop', page.locator('.ambience-toggle').get_attribute('aria-pressed') == 'false')
        ok('audio_no_errors', page.evaluate('AssyababAmbience.error') is None)
        page.locator('.ambience-settings').click()

        # Actual decode and scroll-driven motion, including reverse and final frame.
        page.emulate_media(reduced_motion='no-preference')
        page.wait_for_function('document.documentElement.classList.contains("js-motion")')
        scroll_film(page, .05)
        page.wait_for_function('''() => {const v=document.querySelector('#cinema-video');return v.readyState>=2 && v.videoWidth>0 && v.duration>0 && AssyababDebug.scene().ready;}''', timeout=60000)
        ok('video_metadata_and_decode')
        report['video'] = page.locator('#cinema-video').evaluate('v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight})')
        signatures = []
        for progress, label in [(.08, 'opening'), (.48, 'curtain'), (.90, 'studio'), (.22, 'reverse'), (1, 'last-frame')]:
            started = time.perf_counter(); scroll_film(page, progress); wait_frame(page, progress)
            report['seeks'].append({'progress': progress, 'settled_ms': round((time.perf_counter()-started)*1000)})
            ok('scroll_seek_' + label)
            signatures.append(frame_signature(page))
            page.screenshot(path=str(SHOTS / ('film-' + label + '.png')), timeout=120000)
        ok('decoded_frames_change', len(set(signatures)) == len(signatures))
        ok('scroll_video_stays_paused', page.locator('#cinema-video').evaluate('v=>v.paused && v.muted'))

        # Responsive containment includes short landscape screens and both media variants.
        for width, height in [(320, 568), (320, 740), (390, 844), (700, 960), (760, 960), (768, 1024), (1024, 768), (1440, 960), (1920, 1080), (844, 390), (667, 375)]:
            page.set_viewport_size({'width': width, 'height': height}); scroll_film(page, .5)
            page.wait_for_timeout(300)
            row = page.evaluate('''() => {
                const rect=selector=>document.querySelector(selector).getBoundingClientRect();
                const video=rect('#cinema-video'), sticky=rect('.cinema-sticky'), caption=rect('.scene-copy.is-active');
                const controls=rect('.cinema-bottom'), skip=rect('.skip-cinema'), sound=rect('.ambience-dock');
                const overlap=(a,b)=>a.left<b.right && a.right>b.left && a.top<b.bottom && a.bottom>b.top;
                return {width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,
                    video:[video.width,video.height],sticky:[sticky.width,sticky.height],
                    captionBottom:caption.bottom,controlsTop:controls.top,
                    captionClear:caption.bottom<=controls.top+1,soundClear:!overlap(skip,sound)};
            }''')
            report['viewports'].append(row)
            ok('viewport_' + str(width) + 'x' + str(height), row['scrollWidth'] <= width + 1 and abs(row['video'][0] - width) < 2 and 100 <= row['video'][1] <= row['sticky'][1] + 2 and row['sticky'][1] <= height + 2)
            ok('caption_clear_' + str(width) + 'x' + str(height), row['captionClear'])
            ok('sound_clear_' + str(width) + 'x' + str(height), row['soundClear'])
        page.set_viewport_size({'width': 390, 'height': 844}); scroll_film(page, .88); wait_frame(page, .88)
        page.screenshot(path=str(SHOTS / 'film-mobile-studio.png'), timeout=120000)
        page.set_viewport_size({'width': 1440, 'height': 960}); scroll_film(page, .35); wait_frame(page, .35)

        page.emulate_media(reduced_motion='reduce')
        page.wait_for_function('document.body.classList.contains("reduced-motion")')
        page.wait_for_timeout(300)
        frozen = page.locator('#cinema-video').evaluate('v=>v.currentTime')
        page.locator('#pendidikan').scroll_into_view_if_needed(); page.wait_for_timeout(500)
        ok('reduced_motion_freezes_video', abs(page.locator('#cinema-video').evaluate('v=>v.currentTime') - frozen) < .04)
        page.locator('[data-shot-jump="2"]').click()
        page.wait_for_function('document.querySelector("#cinema-video").currentTime/document.querySelector("#cinema-video").duration>.8')
        ok('reduced_motion_chapter_navigation')
        page.emulate_media(reduced_motion='no-preference'); page.evaluate('scrollTo({top:0,behavior:"instant"})')
        page.locator('[data-play-film]').click(); ok('film_start', page.locator('[data-play-film]').get_attribute('aria-pressed') == 'true')
        page.keyboard.press('Escape'); ok('film_stop', page.locator('[data-play-film]').get_attribute('aria-pressed') == 'false')

        ok('no_javascript_errors', not report['errors'])
        ok('no_app_errors', not page.evaluate('AssyababDebug.metrics.errors'))
        if not URL:
            ok('portable_no_automatic_network_calls', not [url for url in requests if url.startswith(('http:', 'https:'))])
        # Reloading a page never restores ambient sound without a new gesture.
        load(page, html)
        ok('audio_reload_defaults_off', page.evaluate('!AssyababAmbience.enabled && AssyababAmbience.contextState==="uninitialized"'))
        context.close()

        context = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='no-preference')
        page = context.new_page(); load(page, html); scroll_film(page, .5); wait_frame(page, .5)
        report['mobile_video'] = page.locator('#cinema-video').evaluate('v=>({width:v.videoWidth,height:v.videoHeight})')
        ok('mobile_encode_selected', page.locator('#cinema-video').evaluate('v=>v.src===new URL(v.dataset.mobileSrc,document.baseURI).href && v.videoWidth>0 && v.videoWidth<=960'))
        context.close()

        # Failed video keeps the photographic poster and information interface available.
        context = browser.new_context(viewport={'width': 1280, 'height': 800}, reduced_motion='no-preference')
        page = context.new_page()
        if URL:
            page.route(re.compile(r'\.mp4(?:\?|$)'), lambda route: route.abort())
            load(page, None)
        else:
            broken = re.sub(r'data:video/mp4;base64,[A-Za-z0-9+/=]+', 'data:video/mp4;base64,AA==', html)
            page.set_content(broken, wait_until='load', timeout=120000)
        scroll_film(page, .25)
        page.wait_for_selector('#render-note', state='visible', timeout=60000)
        ok('video_failure_fallback', bool(page.locator('#cinema-video').get_attribute('poster')))
        page.locator('[data-open-contact="pendaftaran"]').click(); ok('fallback_ui', page.locator('#contact-form').is_visible())
        context.close()
        context = browser.new_context(viewport={'width': 390, 'height': 844}, java_script_enabled=False)
        page = context.new_page()
        if URL:
            page.goto(URL, wait_until='load')
        else:
            page.set_content(html, wait_until='load')
        ok('no_js_heading', page.locator('h1').is_visible())
        ok('no_js_program', page.locator('[data-program="0"] summary').is_visible())
        ok('no_js_contact', page.locator('.noscript-message a').get_attribute('href') == 'https://wa.me/6285716113466')
        context.close(); browser.close()
    report['status'] = 'passed'


if __name__ == '__main__':
    try:
        main()
    except Exception:
        report['status'] = 'failed'
        report['failure'] = traceback.format_exc()
        raise
    finally:
        report_file = Path(os.environ.get('ASSYABAB_TEST_REPORT', str(OUT / 'test-report.json')))
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print('ALL CHECKS PASSED', flush=True)
