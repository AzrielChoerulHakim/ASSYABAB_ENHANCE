from pathlib import Path
from playwright.sync_api import sync_playwright
import json, mimetypes, os
ROOT=Path(__file__).resolve().parents[1]
os.environ['DISPLAY']=':99'
OUT=ROOT/'docs/screenshots';OUT.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1440,'height':960},device_scale_factor=1,reduced_motion='reduce')
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 from build_offline import build
 page.set_content(build(),wait_until='load')
 page.wait_for_timeout(100)
 page.screenshot(path=str(OUT/'01-landscape.png'),timeout=120000)
 print('metrics',page.evaluate('AssyababDebug.metrics'),'errors',errors,flush=True)

 for progress,name in [(0.05,'02-closed'),(.48,'03-open'),(.95,'04-studio')]:
  page.evaluate('(p)=>scrollTo({top:document.querySelector("#cahaya").offsetTop+p*(document.querySelector("#cahaya").offsetHeight-innerHeight),behavior:"instant"})',progress)
  page.wait_for_timeout(500)
  page.evaluate('(p)=>AssyababDebug.renderAt(p)',progress)
  page.screenshot(path=str(OUT/(name+'.png')),timeout=120000)
  print(name,page.evaluate('AssyababDebug.scene()?.metrics'),flush=True)
 print('errors',errors)
 b.close()
