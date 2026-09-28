#!/usr/bin/env python3
"""Offline Chromium regression checks for the Veo replacement (no real-device claims)."""
import argparse, importlib.util, json, os, shutil, time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bundle', ROOT/'tools/build_offline.py')
bundle = importlib.util.module_from_spec(spec); spec.loader.exec_module(bundle)
HTML = bundle.build()
OUT = Path(os.environ.get('ASSYABAB_QA_DIR', str(ROOT/'docs/video-qa')))
OUT.mkdir(parents=True, exist_ok=True)
results = []
CAPTURE = os.environ.get("ASSYABAB_SCREENSHOTS") == "1"

def check(name, condition, detail=None):
    results.append({'name': name, 'passed': bool(condition), 'detail': detail})
    print(('PASS' if condition else 'FAIL') + ' ' + name, flush=True)

def scroll(page, progress):
    page.evaluate('p => { const s=document.querySelector("#cahaya"); window.scrollTo({top:s.offsetTop+p*(s.offsetHeight-innerHeight),behavior:"instant"}); }', progress)

def wait_seek(page, progress):
    page.wait_for_function('p => { const v=document.querySelector("video"); return v.readyState>=2 && !v.seeking && Math.abs(v.currentTime-p*(v.duration-1/24))<.085; }', arg=progress, timeout=8000)
    page.wait_for_timeout(70)

def fresh(browser, mobile=False, reduced=False, broken=False, nojs=False, save=False):
    page = browser.new_page(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},
        device_scale_factor=1, is_mobile=mobile, has_touch=mobile,
        reduced_motion='reduce' if reduced else 'no-preference', java_script_enabled=not nojs,
        accept_downloads=True)
    page.set_default_timeout(5000)
    errors=[]; external=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: external.append(r.url) if r.url.startswith(('http:','https:')) else None)
    if save: page.evaluate('Object.defineProperty(navigator, "connection", {value:{saveData:true},configurable:true})')
    html=HTML
    if broken:
        import re
        html=re.sub(r'data-src="data:video/mp4;base64,[^"]+"', 'data-src="data:video/mp4;base64,AAAA"', html)
        html=re.sub(r'data-mobile-src="data:video/mp4;base64,[^"]+"', 'data-mobile-src="data:video/mp4;base64,AAAA"', html)
    page.set_content(html,wait_until='domcontentloaded',timeout=45000)
    return page,errors,external

def desktop(browser):
    page,errors,external=fresh(browser)
    scroll(page,0); wait_seek(page,0)
    check('HTML loads without the legacy renderer',page.evaluate('typeof AssyababCahaya==="undefined" && typeof AssyababRenderer==="undefined" && document.querySelector("#cinema-canvas")===null'))
    check('Video stays paused, muted, inline',page.evaluate('(()=>{const v=document.querySelector("video");return v.paused&&v.muted&&v.playsInline&&!v.autoplay})()'))
    check('Desktop delivery is selected',page.evaluate('AssyababDebug.scene().metrics.source==="desktop"'))
    check('Video duration is 10 seconds',page.evaluate('Math.abs(document.querySelector("video").duration-10)<.05'))
    for p in [0.08,0.34,0.51,0.65,0.94,0.18,0.98,0.04]:
        scroll(page,p);wait_seek(page,p)
        state=page.evaluate('({time:document.querySelector("video").currentTime,shot:document.querySelector("#cahaya").dataset.activeShot})')
        check(f'Scroll seeks to {p:.2f}, including reverse',abs(state['time']-p*(10-1/24))<.085,state)
    scroll(page,.51);wait_seek(page,.51)
    check('Copy disappears during the curtain transition',page.evaluate('Number(getComputedStyle(document.querySelector("#cahaya")).getPropertyValue("--cinema-copy-opacity"))<.05'))
    for i,p in [(2,.87),(0,.02),(1,.34)]:
        page.locator(f'[data-shot-jump="{i}"]').click();wait_seek(page,p)
        check(f'Chapter {i+1} button selects the correct scene',page.locator(f'[data-shot-jump="{i}"]').get_attribute('aria-pressed')=='true')
    before=page.evaluate('AssyababDebug.scene().metrics.seeks');page.wait_for_timeout(600)
    check('An idle page stops issuing seeks',page.evaluate('AssyababDebug.scene().metrics.seeks')==before)
    page.locator('#motion-toggle').click();page.wait_for_timeout(150)
    check('Pause uses stills and preserves chapter position',page.evaluate('AssyababDebug.scene().staticMode && Math.abs(AssyababDebug.metrics.cinemaProgress-.34)<.04'))
    count=page.evaluate('AssyababDebug.scene().metrics.seeks');scroll(page,.88);page.wait_for_timeout(200)
    check('Paused scrolling does not seek the video',page.evaluate('AssyababDebug.scene().metrics.seeks')==count)
    check('Paused creation chapter uses the correct still',page.evaluate('AssyababDebug.scene().posterIndex===2'))
    page.locator('#motion-toggle').click();wait_seek(page,.88)
    check('Resuming returns to scroll-video mode',page.evaluate('!AssyababDebug.scene().staticMode && AssyababDebug.scene().metrics.mode==="ready"'))
    # Existing interactions must stay intact.
    page.locator('.search-open').click();page.locator('#search-input').fill('asrama');page.wait_for_timeout(100)
    check('Search still returns source-index results',page.locator('.search-result').count()>0)
    page.locator('[data-close-search]').click()
    page.locator('[data-open-curriculum]').click()
    check('Curriculum modal still opens',page.locator('#information-modal').evaluate('(e)=>e.open') and page.locator('.curriculum-grid article').count()==10)
    page.locator('[data-close-modal]').click()
    page.locator('[data-day="3"]').click();check('Daily schedule buttons still work',page.evaluate('AssyababDebug.metrics.day===3'))
    page.locator('[data-person="mudir"]').click();check('Teacher profile still opens',page.locator('#modal-title').inner_text().find('Riyadi')>=0);page.locator('[data-close-modal]').click()
    page.locator('[data-gallery="0"]').click();check('Gallery still opens a real photograph',page.locator('#photo-modal').evaluate('(e)=>e.open'));page.locator('.photo-close').click()
    page.locator('[data-open-contact="pendaftaran"]').click();page.locator('#contact-name').fill('Pengujian');page.locator('#contact-message').fill('Informasi pendidikan');page.locator('#contact-form button[type="submit"]').click()
    check('Contact only prepares an unsent WhatsApp draft',page.locator('.contact-link').get_attribute('href').startswith('https://wa.me/') and page.locator('#contact-result').is_visible());page.locator('[data-close-modal]').click()
    page.locator('#poster-title').fill('Ilmu yang menjadi kebaikan.')
    import base64, io
    from PIL import Image
    png=page.locator('#composition').evaluate('(c)=>c.toDataURL("image/png")')
    check('Poster canvas still produces a 1280 x 800 PNG',Image.open(io.BytesIO(base64.b64decode(png.split(",",1)[1]))).size==(1280,800))
    check('Desktop has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
    check('No JavaScript exceptions in desktop workflow',not errors,errors)
    check('Offline export makes no automatic external requests',not external,external)
    page.close()

def mobile(browser):
    page,errors,external=fresh(browser,mobile=True)
    for p,name in [(0,'source'),(.34,'light'),(.87,'creation')]:
        scroll(page,p);wait_seek(page,p)
        if CAPTURE:page.screenshot(path=str(OUT/f'mobile-{name}.png'))
    check('Mobile delivery is selected',page.evaluate('AssyababDebug.scene().metrics.source==="mobile"'))
    check('Portrait shows the entire landscape frame',page.evaluate('(()=>{const m=document.querySelector(".cinema-media").getBoundingClientRect();return Math.abs(m.width/m.height-16/9)<.02&&getComputedStyle(document.querySelector("video")).objectFit==="contain"})()'))
    check('Mobile copy sits below rather than on the video',page.evaluate('document.querySelector(".scene-copy:not([hidden])").getBoundingClientRect().top>document.querySelector(".cinema-media").getBoundingClientRect().bottom'))
    check('Mobile copy and controls do not collide',page.evaluate('document.querySelector(".scene-copy:not([hidden])").getBoundingClientRect().bottom<document.querySelector(".cinema-bottom").getBoundingClientRect().top'))
    for w,h,label in [(360,640,'small'),(844,390,'landscape'),(390,844,'restored')]:
        page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(300);scroll(page,.87);wait_seek(page,.87)
        check(f'{label} viewport has no horizontal overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        check(f'{label} viewport keeps its existing media source',page.evaluate('AssyababDebug.scene().metrics.source==="mobile"'))
        if CAPTURE and label!='restored':page.screenshot(path=str(OUT/f'mobile-{label}.png'))
    page.locator('.menu-button').click();check('Mobile chapter menu still opens',page.locator('.menu-button').get_attribute('aria-expanded')=='true');page.keyboard.press('Escape')
    check('No JavaScript exceptions in mobile workflow',not errors,errors);page.close()

def fallback(browser):
    page,errors,_=fresh(browser,reduced=True)
    scroll(page,.87);page.wait_for_timeout(250)
    check('Reduced-motion does not load a video source',page.evaluate('!document.querySelector("video").getAttribute("src") && AssyababDebug.scene().metrics.mode==="static"'))
    check('Reduced-motion reveals the creation still',page.evaluate('AssyababDebug.scene().posterIndex===2'))
    page.locator('[data-shot-jump="0"]').click();page.wait_for_timeout(120)
    check('Reduced-motion chapter navigation works',page.evaluate('AssyababDebug.scene().posterIndex===0'))
    if CAPTURE:page.screenshot(path=str(OUT/'reduced-motion.png'))
    check('Reduced-motion has no JavaScript exceptions',not errors,errors);page.close()
    page,errors,_=fresh(browser,broken=True)
    scroll(page,.87);page.wait_for_timeout(100);page.evaluate('document.querySelector("video").dispatchEvent(new Event("error"))');page.wait_for_function('AssyababDebug.scene().metrics.mode==="error"');page.wait_for_timeout(100)
    check('Unavailable video falls back to a visible still',page.locator('#cinema-poster').evaluate('(e)=>e.naturalWidth>0') and not page.locator('#cahaya').evaluate('(e)=>e.classList.contains("video-ready")'))
    check('Unavailable video offers retry, not a blank viewport',page.locator('#cinema-retry').is_visible() and page.locator('#render-note').is_visible())
    if CAPTURE:page.screenshot(path=str(OUT/'video-error.png'))
    check('Video failure does not crash the page',not errors,errors);page.close()
    page,errors,_=fresh(browser,save=True)
    scroll(page,.34);page.wait_for_timeout(180)
    check('Save-Data skips video loading',page.evaluate('AssyababDebug.scene().saveData && !document.querySelector("video").getAttribute("src")'))
    page.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['desktop','mobile','fallback','all'],default='all');args=parser.parse_args()
    executable=os.environ.get('ASSYABAB_BROWSER') or shutil.which('chromium')
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox'])
        version=browser.version
        try:
            for name,fn in [('desktop',desktop),('mobile',mobile),('fallback',fallback)]:
                if args.part in ('all',name):fn(browser)
        finally:
            report={'browser':version,'mode':'Chromium offline HTML via set_content; mobile viewports emulated, not physical phones; media-error event injected; live deployment not tested','part':args.part,'checks':results,'passed':sum(x['passed'] for x in results),'failed':sum(not x['passed'] for x in results)}
            (OUT/f'report-{args.part}.json').write_text(json.dumps(report,indent=2)+'\n');browser.close()
    if any(not x['passed'] for x in results):raise SystemExit(1)
