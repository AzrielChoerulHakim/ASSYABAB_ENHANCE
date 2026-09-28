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
report = {'method': 'Headless Chromium; actual video decode, bidirectional scroll seeking, landscape pixels, SVG/CSS atmosphere, optional local audio and UI regression. Not a hardware performance or Safari test.',
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


def canvas_signature(page, selector):
    """Hash actual canvas pixels, unaffected by overlaid captions or the clock."""
    return page.locator(selector).evaluate('''canvas => {
        const pixels=canvas.getContext('2d').getImageData(0,0,canvas.width,canvas.height).data;
        let hash=2166136261;
        for(let i=0;i<pixels.length;i++) hash=Math.imul(hash^pixels[i],16777619);
        return hash>>>0;
    }''')


def check_landscape_pixels(page):
    """Exercise the real renderer deterministically, without screen timing noise."""
    result = page.evaluate('''() => {
        const canvas=document.createElement('canvas');
        canvas.style.cssText='position:fixed;left:-10000px;top:0;width:640px;height:360px;visibility:hidden;pointer-events:none';
        document.body.append(canvas);
        const scene=new AssyababLandscape(canvas,813), context=canvas.getContext('2d');
        const capture=(x,y,w,h)=>context.getImageData(Math.floor(x*canvas.width),Math.floor(y*canvas.height),Math.floor(w*canvas.width),Math.floor(h*canvas.height)).data;
        const changed=(a,b)=>{let count=0;for(let i=0;i<a.length;i+=4)if(Math.abs(a[i]-b[i])+Math.abs(a[i+1]-b[i+1])+Math.abs(a[i+2]-b[i+2])>2)count++;return count;};
        try {
            scene.wind=-.8; scene.render(1);
            const skyA=capture(.58,.02,.4,.45),grassA=capture(0,.85,1,.15),mistA=capture(.15,.56,.7,.18);
            scene.wind=.8; scene.render(9);
            const daylight={upperChangedPixels:changed(skyA,capture(.58,.02,.4,.45)),
                grassChangedPixels:changed(grassA,capture(0,.85,1,.15)),
                mistChangedPixels:changed(mistA,capture(.15,.56,.7,.18)),diagnostics:{...scene.diagnostics}};
            scene.still=true; scene.render(10);
            const frozen=capture(0,0,1,1);
            scene.wind=-1;scene.pointer=[1,-1];scene.zoom=.8;scene.render(40);
            const stillChangedPixels=changed(frozen,capture(0,0,1,1));
            scene.still=false;scene.pointer=[0,0];scene.zoom=0;scene.wind=0;scene.setDay(3);scene.render(3);
            const nightA=capture(.18,.68,.7,.24),reflectionA=capture(.18,.92,.7,.08);
            scene.render(17);
            const night={changedPixels:changed(nightA,capture(.18,.68,.7,.24)),
                reflectionChangedPixels:changed(reflectionA,capture(.18,.92,.7,.08)),diagnostics:{...scene.diagnostics}};
            return {daylight,night,stillChangedPixels};
        } finally {scene.dispose();canvas.remove();}
    }''')
    report['nature_pixels'] = result
    day = result['daylight']; night = result['night']
    ok('sunlight_and_cloud_pixels_animate', day['upperChangedPixels'] > 20 and day['diagnostics']['sunlightShafts'] > 0 and day['diagnostics']['thinClouds'] > 0)
    ok('wind_grass_pixels_respond', day['grassChangedPixels'] > 20 and day['diagnostics']['grassBlades'] > 0)
    ok('wind_mist_pixels_respond', day['mistChangedPixels'] > 20)
    ok('night_firefly_pixels_animate', night['changedPixels'] > 20 and night['diagnostics']['fireflies'] > 0)
    ok('night_reflection_pixels_animate', night['reflectionChangedPixels'] > 20 and night['diagnostics']['reflections'] > 0)
    ok('landscape_still_freezes_all_pixels', result['stillChangedPixels'] == 0)


def nature_style_snapshot(page):
    return page.evaluate('''() => ({
        wordmark:getComputedStyle(document.querySelector('.hero-wordmark')).translate,
        mist:getComputedStyle(document.querySelector('.atmosphere-mist-front')).transform,
        orbit:getComputedStyle(document.querySelector('.atmosphere-geometry-orbit')).transform,
        strokes:[...document.querySelectorAll('.atmosphere-geometry-stroke')].map(e=>getComputedStyle(e).strokeDashoffset),
        leaves:[...document.querySelectorAll('.ambience-layer')].map(e=>getComputedStyle(e).transform)
    })''')


def check_nature_experience(page):
    check_landscape_pixels(page)
    page.emulate_media(reduced_motion='no-preference')
    page.evaluate('scrollTo({top:0,behavior:"instant"})')
    page.wait_for_timeout(2200)  # Let the existing opening title animation settle.
    ok('nature_layers_noninteractive', page.evaluate('''[...document.querySelectorAll('.atmosphere-decoration')].length===3 &&
        [...document.querySelectorAll('.atmosphere-decoration')].every(e=>e.getAttribute('aria-hidden')==='true' && getComputedStyle(e).pointerEvents==='none' && !e.querySelector('a,button,input,[tabindex]'))'''))
    before = nature_style_snapshot(page)
    entry_before = page.locator('.atmosphere-entry-fog').evaluate('e=>Number(getComputedStyle(e).opacity)')
    page.evaluate('scrollTo({top:document.querySelector("#beranda").offsetHeight*.35,behavior:"instant"})')
    page.wait_for_function('AssyababDebug.nature().wind>.005 && AssyababAtmosphereDebug.wind>0 && new DOMMatrixReadOnly(getComputedStyle(document.querySelector(".ambience-hero")).transform).m41>0')
    down = page.evaluate('''() => {const d=AssyababDebug.nature(),land=AssyababDebug.landscapes();return {
        wind:d.wind,heroWind:land.hero.wind,dailyWind:land.daily.wind,atmosphereWind:d.atmosphere.wind,
        leafX:new DOMMatrixReadOnly(getComputedStyle(document.querySelector('.ambience-hero')).transform).m41};}''')
    ok('shared_scroll_wind_reaches_landscapes_and_leaves', down['wind'] > 0 and abs(down['heroWind']-down['wind']) < .001 and abs(down['dailyWind']-down['wind']) < .001 and down['atmosphereWind'] > 0 and abs(down['atmosphereWind']-down['wind']) < .2 and down['leafX'] > 0)
    after = nature_style_snapshot(page)
    ok('wordmark_depth_moves_with_scroll', before['wordmark'] != after['wordmark'] and page.locator('.hero-wordmark').evaluate('e=>getComputedStyle(e).textShadow!=="none"'))
    ok('foreground_wordmark_mist_moves', before['mist'] != after['mist'])
    page.evaluate('scrollTo({top:document.querySelector("#beranda").offsetHeight*.10,behavior:"instant"})')
    page.wait_for_function('AssyababDebug.nature().wind<-.005 && new DOMMatrixReadOnly(getComputedStyle(document.querySelector(".ambience-hero")).transform).m41<0')
    ok('shared_wind_reverses_with_scroll', page.locator('.ambience-hero').evaluate('e=>new DOMMatrixReadOnly(getComputedStyle(e).transform).m41<0'))

    page.evaluate('scrollTo({top:document.querySelector("#cahaya").offsetTop-innerHeight*.4,behavior:"instant"})')
    page.wait_for_timeout(150)
    ok('entry_fog_reveals_at_chapter_boundary', page.locator('.atmosphere-entry-fog').evaluate('e=>Number(getComputedStyle(e).opacity)') > entry_before + .1)
    page.locator('#tentang').scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    haze = page.locator('.atmosphere-light-haze').evaluate('e=>({opacity:Number(getComputedStyle(e).opacity),transform:getComputedStyle(e).transform,background:getComputedStyle(e).backgroundImage})')
    page.wait_for_timeout(350)
    ok('exit_light_haze_animates', haze['opacity'] > 0 and 'gradient' in haze['background'] and haze['transform'] != page.locator('.atmosphere-light-haze').evaluate('e=>getComputedStyle(e).transform'))

    # Enter, complete and retrace the actual SVG line drawing; rotation uses the shared clock.
    page.evaluate('''() => {const art=document.querySelector('.program-art');scrollTo({top:scrollY+art.getBoundingClientRect().top-innerHeight*.94,behavior:'instant'});}''')
    page.wait_for_timeout(200)
    starting_strokes = page.locator('.atmosphere-geometry-stroke').evaluate_all('els=>els.map(e=>parseFloat(getComputedStyle(e).strokeDashoffset))')
    page.evaluate('''() => {const art=document.querySelector('.program-art');scrollTo({top:scrollY+art.getBoundingClientRect().top-innerHeight*.22,behavior:'instant'});}''')
    page.wait_for_timeout(200)
    full_strokes = page.locator('.atmosphere-geometry-stroke').evaluate_all('els=>els.map(e=>parseFloat(getComputedStyle(e).strokeDashoffset))')
    ok('geometry_lines_draw_on_entry', len(full_strokes) >= 4 and sum(starting_strokes) > sum(full_strokes) + 100 and max(full_strokes) < 1)
    rotation = page.locator('.atmosphere-geometry-orbit').evaluate('e=>getComputedStyle(e).transform')
    page.wait_for_timeout(450)
    ok('geometry_rotates_on_shared_clock', rotation != page.locator('.atmosphere-geometry-orbit').evaluate('e=>getComputedStyle(e).transform'))
    page.evaluate('''() => {const art=document.querySelector('.program-art');scrollTo({top:scrollY+art.getBoundingClientRect().top-innerHeight*.75,behavior:'instant'});}''')
    page.wait_for_timeout(200)
    ok('geometry_retraces_on_reverse_scroll', sum(page.locator('.atmosphere-geometry-stroke').evaluate_all('els=>els.map(e=>parseFloat(getComputedStyle(e).strokeDashoffset))')) > sum(full_strokes) + 100)

    page.locator('[data-day="3"]').click()
    page.wait_for_timeout(350)
    night_before = canvas_signature(page, '#day-landscape')
    page.wait_for_timeout(550)
    ok('night_animation_integrated_in_visible_canvas', night_before != canvas_signature(page, '#day-landscape') and page.evaluate('AssyababDebug.nature().daily.fireflies>0 && AssyababDebug.nature().daily.reflections>0'))
    page.screenshot(path=str(SHOTS / 'nature-night.png'), timeout=120000)

    # Real controls freeze both the canvas pixels and SVG/CSS decorations.
    page.locator('#motion-toggle').click(); page.wait_for_function('AssyababDebug.nature().quiet')
    page.wait_for_timeout(300)
    frozen_canvas = canvas_signature(page, '#day-landscape'); frozen_style = nature_style_snapshot(page)
    page.mouse.move(100, 120); page.wait_for_timeout(550)
    ok('manual_pause_freezes_nature_pixels', frozen_canvas == canvas_signature(page, '#day-landscape'))
    ok('manual_pause_freezes_nature_styles', frozen_style == nature_style_snapshot(page))
    ok('manual_pause_zeroes_scroll_wind', page.evaluate('AssyababDebug.nature().wind===0 && AssyababAtmosphereDebug.wind===0'))
    page.locator('#motion-toggle').click(); page.wait_for_function('!AssyababDebug.nature().quiet')
    page.emulate_media(reduced_motion='reduce'); page.wait_for_function('AssyababDebug.nature().quiet')
    page.wait_for_timeout(350)
    frozen_canvas = canvas_signature(page, '#day-landscape'); frozen_style = nature_style_snapshot(page)
    page.wait_for_timeout(550)
    ok('reduced_motion_freezes_nature_pixels', frozen_canvas == canvas_signature(page, '#day-landscape'))
    ok('reduced_motion_freezes_nature_styles', frozen_style == nature_style_snapshot(page))
    ok('reduced_motion_full_geometry_and_hidden_mist', page.evaluate('''[...document.querySelectorAll('.atmosphere-geometry-stroke')].every(e=>parseFloat(getComputedStyle(e).strokeDashoffset)===0) && [...document.querySelectorAll('.atmosphere-decoration')].every(e=>getComputedStyle(e).display==='none'||getComputedStyle(e).visibility==='hidden')'''))
    page.locator('[data-day="0"]').click()
    page.emulate_media(reduced_motion='no-preference'); page.wait_for_function('!AssyababDebug.nature().quiet')


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

        check_nature_experience(page)

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
            if (width, height) in [(320, 740), (390, 844)]:
                page.evaluate('scrollTo({top:0,behavior:"instant"})'); page.wait_for_timeout(300)
                hero = page.evaluate('''() => {
                    const button=document.querySelector('[data-play-film]'),a=button.getBoundingClientRect(),b=document.querySelector('.ambience-dock').getBoundingClientRect();
                    const visible=a.top>=0&&a.bottom<=innerHeight;
                    const overlap=a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top;
                    const hit=visible ? document.elementFromPoint((a.left+a.right)/2,(a.top+a.bottom)/2)?.closest('[data-play-film]')===button : true;
                    return {visible,overlap,hit};
                }''')
                ok('mobile_hero_cta_clear_' + str(width), not hero['visible'] or not hero['overlap'])
                ok('mobile_hero_cta_not_intercepted_' + str(width), hero['hit'])
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
