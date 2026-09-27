#!/usr/bin/env python3
"""Actual Chromium/WebGL2 regression. Local inline export; no hosted-network claims."""
import sys,os,json,time,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from build_offline import build
os.environ['DISPLAY']=os.environ.get('ASSYABAB_TEST_DISPLAY',':99')
OUT=ROOT/'docs';SHOTS=OUT/'screenshots';SHOTS.mkdir(exist_ok=True,parents=True)
report={'method':'Chromium rendering inline portable export; WebGL2 with ANGLE SwiftShader on Xvfb; not hardware performance or hosted site test','checks':{},'viewports':[],'errors':[]}
def ok(name,condition=True):
 assert condition,name
 report['checks'][name]=True;print('PASS',name,flush=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--disable-dev-shm-usage'])
 report['browser']=b.version
 c=b.new_context(viewport={'width':1440,'height':960},reduced_motion='reduce',accept_downloads=True)
 page=c.new_page();page.set_default_timeout(45000);page.on('pageerror',lambda e:report['errors'].append(str(e)))
 requests=[];page.on('request',lambda r:requests.append(r.url))
 html=build();page.set_content(html,wait_until='load',timeout=120000)
 print('INIT',page.evaluate('window.AssyababDebug?.metrics'),report['errors'],flush=True)
 page.wait_for_function('window.AssyababDebug && window.AssyababDebug.metrics.webgl')
 ok('actual_webgl2',page.evaluate('AssyababDebug.metrics.webgl'))
 report['gpu']=page.evaluate('(()=>{let g=AssyababDebug.scene().renderer.gl;return {version:g.getParameter(g.VERSION),renderer:g.getParameter(g.getExtension("WEBGL_debug_renderer_info").UNMASKED_RENDERER_WEBGL)}})()')
 page.evaluate("Promise.all([...document.querySelectorAll('main img')].map(i=>{i.loading='eager';return i.decode()}))")
 ok('all_documentary_images_decode',page.evaluate("[...document.querySelectorAll('main img')].every(i=>i.complete&&i.naturalWidth>0)"))
 # Native menu focus trap and focus isolation.
 page.locator('.menu-button').click();ok('menu_open',page.locator('#chapter-menu').is_visible());ok('menu_background_inert',page.locator('main').evaluate('e=>e.inert'))
 page.locator('#chapter-menu a').last.focus();page.keyboard.press('Tab');ok('menu_focus_wrap',page.locator('.menu-button').evaluate('e=>e===document.activeElement'))
 page.keyboard.press('Escape');ok('menu_close',not page.locator('#chapter-menu').is_visible())
 # Search, zero-result and literal input; keyboard shortcut.
 page.keyboard.press('Control+k');ok('search_shortcut',page.locator('#search-modal').is_visible());page.locator('#search-input').fill('asrama');ok('source_search',page.locator('.search-result').count()==1)
 page.locator('#search-input').fill('<img src=x onerror=alert(1)>');ok('search_literal_input',page.locator('#search-results img').count()==0 and page.locator('.search-result').count()==0)
 page.locator('#search-input').fill('kurikulum');page.locator('.search-result').click();page.wait_for_selector('#information-modal[open]');ok('curriculum_from_search',page.locator('.curriculum-grid article').count()==10)
 page.keyboard.press('Escape')
 for i in range(4):
  page.locator(f'[data-program="{i}"] summary').click()
  if page.locator('.program-list details[open]').count()==0:page.locator(f'[data-program="{i}"] summary').click()
  page.wait_for_function('(i)=>document.querySelector("#program-index").textContent.startsWith(String(i+1).padStart(2,"0"))',arg=i)
  ok('program_'+str(i),page.locator('.program-list details[open]').count()==1)
 # Day theme changes actual canvas pixels, not just button label.
 pixel=[]
 for i in range(4):
  page.locator(f'[data-day="{i}"]').click();ok('day_'+str(i),page.evaluate('AssyababDebug.metrics.day')==i)
  pixel.append(page.locator('#day-landscape').evaluate('c=>Array.from(c.getContext("2d").getImageData(50,20,1,1).data).join(",")'))
 ok('distinct_day_palettes',len(set(pixel))==4);page.keyboard.press('Home');ok('day_keyboard',page.evaluate('AssyababDebug.metrics.day')==0)
 page.locator('[data-person="mudir"]').click();ok('teacher_profile','Riyadi' in page.locator('#modal-title').inner_text());page.locator('#modal-content [data-open-people]').click();ok('people_directory',page.locator('.people-list button').count()==8);page.keyboard.press('Escape')
 page.locator('#gallery-next').click();page.wait_for_timeout(100);ok('gallery_moves',page.locator('.gallery-track').evaluate('e=>e.scrollLeft')>0)
 page.locator('#gallery-prev').click();page.wait_for_timeout(100);page.locator('[data-gallery="0"]').click();ok('gallery_dialog',page.locator('#photo-modal').is_visible());page.keyboard.press('ArrowRight');ok('gallery_keyboard','Lapangan' in page.locator('#lightbox-caption').inner_text());page.keyboard.press('Escape');ok('gallery_returns_focus',page.locator('[data-gallery="0"]').evaluate('e=>e===document.activeElement'))
 # Local poster output is a real file with the advertised dimensions.
 page.locator('#poster-title').fill('Ilmu untuk kehidupan.');page.locator('[data-palette="1"]').click()
 with page.expect_download() as download:page.locator('#export-poster').click()
 file=download.value;file.save_as(str(OUT/'test-poster.png'))
 from PIL import Image
 ok('poster_png_export',Image.open(OUT/'test-poster.png').size==(1280,800))
 # Preview only: no enrollment submission or WhatsApp network request is performed.
 page.locator('[data-open-contact="pendaftaran"]').click();page.locator('#contact-name').fill('   ');page.locator('#contact-form [type="submit"]').click();ok('name_validation',not page.locator('#contact-result').is_visible())
 page.locator('#contact-name').fill('Wali Santri');page.locator('#contact-message').fill('Bagaimana informasi pendidikan? <b>teks biasa</b>');page.locator('#contact-form [type="submit"]').click()
 ok('whatsapp_draft','https://wa.me/6285716113466?text=' in page.locator('.contact-link').get_attribute('href'));ok('draft_escaped',page.locator('.contact-preview b').count()==0)
 page.locator('#contact-name').fill('Nama baru');ok('draft_invalidated',not page.locator('#contact-result').is_visible());page.keyboard.press('Escape')
 page.locator('[data-open-contact="kunjungan"]').click();ok('visit_not_confirmed','belum terjadwal' in page.locator('#contact-form').inner_text());page.keyboard.press('Escape')
 page.locator('.faq details').first.locator('summary').click();ok('faq',page.locator('.faq details').first.locator('p').is_visible())
 page.locator('[data-open-sources]').click();ok('source_disclosure','Bukan rekonstruksi' in page.locator('#modal-content').inner_text());page.keyboard.press('Escape')
 # Resize real WebGL resources. UI visible/overflow checks at each viewport.
 for width in [320,390,700,760,768,1024,1440,1920]:
  page.set_viewport_size({'width':width,'height':960 if width>760 else 844});page.evaluate('scrollTo({top:0,behavior:"instant"})');page.wait_for_function('document.querySelector("#cinema-canvas").width===Math.round(innerWidth*Math.min(devicePixelRatio,1.5)) && document.querySelector("#cinema-canvas").height===Math.round(innerHeight*Math.min(devicePixelRatio,1.5))', timeout=30000)
  row=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,webgl:AssyababDebug.metrics.webgl,canvas:[document.querySelector("#cinema-canvas").width,document.querySelector("#cinema-canvas").height]})')
  ok('viewport_'+str(width),row['scrollWidth']<=width and row['webgl'] and row['canvas']==[width,960 if width>760 else 844]);report['viewports'].append(row)
 page.set_viewport_size({'width':1440,'height':960});page.wait_for_timeout(750)
 # Sample the actual animated book and transition progress, check GL state.
 for pos in [.03,.25,.48,.73,.84,.96]:
  page.evaluate('(p)=>scrollTo({top:document.querySelector("#cahaya").offsetTop+p*(document.querySelector("#cahaya").offsetHeight-innerHeight),behavior:"instant"})',pos);page.wait_for_timeout(120)
  page.evaluate('(p)=>AssyababDebug.renderAt(p)',pos)
  ok('scene_'+str(pos),page.evaluate('AssyababDebug.scene().renderer.gl.getError()')==0)
  if pos==.25:page.screenshot(path=str(SHOTS/'05-pages-moving.png'),timeout=120000)
 # Trigger context loss and actual restoration.
 page.evaluate('window.testLost=AssyababDebug.scene().renderer.gl.getExtension("WEBGL_lose_context");testLost.loseContext()')
 page.wait_for_function('!AssyababDebug.metrics.webgl');ok('context_loss_fallback',page.locator('#render-note').is_visible())
 page.wait_for_timeout(150);page.evaluate('testLost.restoreContext()');page.wait_for_function('AssyababDebug.metrics.webgl',timeout=120000);ok('context_restored',page.locator('#cinema-canvas').evaluate('e=>e.width>0&&e.height>0'))
 # Motion works, can be stopped, and is paused automatically with system preferences.
 page.evaluate('scrollTo({top:0,behavior:"instant"})');page.emulate_media(reduced_motion='no-preference');page.wait_for_function('document.documentElement.classList.contains("js-motion")',timeout=15000)
 ok('motion_enabled',page.locator('html').evaluate('e=>e.classList.contains("js-motion")'))
 page.locator('[data-play-film]').click();page.wait_for_timeout(150);ok('film_start',page.locator('[data-play-film]').get_attribute('aria-pressed')=='true');page.keyboard.press('Escape');ok('film_stop',page.locator('[data-play-film]').get_attribute('aria-pressed')=='false')
 page.emulate_media(reduced_motion='reduce');page.wait_for_function('document.body.classList.contains("reduced-motion")');ok('reduced_motion',page.locator('body').evaluate('e=>e.classList.contains("reduced-motion")'))
 ok('no_javascript_errors',not report['errors']);ok('no_automatic_network_calls',not requests)
 c.close()
 # Force unavailable GPU to verify graceful fallback without suppressing arbitrary errors.
 c=b.new_context(viewport={'width':1280,'height':800},reduced_motion='reduce');page=c.new_page()
 fallback=html.replace("if(new URLSearchParams(location.search).get('graphics')==='off')",'if(true)')
 page.set_content(fallback,wait_until='load',timeout=120000);ok('gpu_unavailable_fallback',not page.evaluate('AssyababDebug.metrics.webgl') and page.locator('#render-note').evaluate('e=>!e.hidden'))
 page.locator('[data-open-contact="pendaftaran"]').click();ok('fallback_ui',page.locator('#contact-form').is_visible());c.close()
 c=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False);page=c.new_page();page.set_content(html,wait_until='load')
 ok('no_js_heading',page.locator('h1').is_visible());ok('no_js_program',page.locator('[data-program="0"] summary').is_visible());ok('no_js_contact',page.locator('.noscript-message a').get_attribute('href')=='https://wa.me/6285716113466');c.close();b.close()
report['portable_bytes']=len(html.encode());report['file_hashes']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'index.html',*sorted((ROOT/'src').glob('*.js')),ROOT/'styles/main.css']}
(OUT/'test-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print('ALL CHECKS PASSED',flush=True)
