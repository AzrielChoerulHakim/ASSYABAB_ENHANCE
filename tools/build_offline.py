#!/usr/bin/env python3
"""Bundle the source website into a single portable HTML. No network dependencies."""
from pathlib import Path
import argparse, base64, re, mimetypes, json, hashlib
ROOT=Path(__file__).resolve().parents[1]
def build(output=None):
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    def local(path):
        p=(ROOT/path).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():raise ValueError(f'Missing/unsafe resource: {path}')
        return p
    html=re.sub(r'<link rel="stylesheet" href="\./([^"]+)">',lambda m:'<style>\n'+local(m[1]).read_text(encoding='utf-8')+'\n</style>',html)
    scripts=[]
    def script(m):
        scripts.append(local(m[1]).read_text(encoding='utf-8'))
        return ''
    html=re.sub(r'<script defer src="\./([^"]+)"></script>',script,html)
    html=html.replace('</body>','\n'.join('<script>\n'+s+'\n</script>' for s in scripts)+'\n</body>')
    def asset(m):
        f=local(m[0][2:]);mime=mimetypes.guess_type(str(f))[0] or 'application/octet-stream'
        return 'data:'+mime+';base64,'+base64.b64encode(f.read_bytes()).decode()
    html=re.sub(r'\./assets/[a-zA-Z0-9._-]+',asset,html)
    manifest=json.loads((ROOT/'assets/manifest.json').read_text(encoding='utf-8'))
    for name,item in manifest.items():
        f=ROOT/'assets'/name
        if not f.is_file():raise ValueError('Run python3 tools/fetch_assets.py before the portable export.')
        data=f.read_bytes()
        if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError(f'Asset checksum mismatch: {name}')
        html=html.replace(item['url'],'data:image/avif;base64,'+base64.b64encode(data).decode())
    if re.search(r'(?:src|href)="\./',html):raise ValueError('Unbundled resource')
    if output:
        output=Path(output).resolve()
        if output==ROOT/'index.html':raise ValueError('Cannot overwrite source')
        output.parent.mkdir(parents=True,exist_ok=True);output.write_text(html,encoding='utf-8')
        print(f'Built {output.name}: {len(html.encode()):,} bytes')
    return html
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',default=str(ROOT/'ASSYABAB-CAHAYA.html'))
    build(a.parse_args().output)
