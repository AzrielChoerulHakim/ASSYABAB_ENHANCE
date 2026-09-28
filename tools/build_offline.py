#!/usr/bin/env python3
"""Bundle Cahaya into one HTML, including the owner's scroll-video and static fallback frames."""
from pathlib import Path
import argparse, base64, re, mimetypes, json, hashlib
ROOT = Path(__file__).resolve().parents[1]

def build(output=None):
    html = (ROOT / 'index.html').read_text()
    cache = {}
    def local(path):
        p = (ROOT / path).resolve()
        if not p.is_relative_to(ROOT) or not p.is_file():
            raise ValueError(f'Missing/unsafe resource: {path}')
        return p
    def data_uri(path):
        if path not in cache:
            p = local(path)
            mime = mimetypes.guess_type(str(p))[0] or 'application/octet-stream'
            cache[path] = 'data:' + mime + ';base64,' + base64.b64encode(p.read_bytes()).decode()
        return cache[path]
    def verified(path, expected):
        p = local(path)
        if hashlib.sha256(p.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Asset checksum mismatch: {path}')
    photos = json.loads(local('assets/manifest.json').read_text())
    for name, item in photos.items():
        verified('assets/' + name, item['sha256'])
        html = html.replace(item['url'], data_uri('assets/' + name))
    media = json.loads(local('assets/cinema/manifest.json').read_text())
    for name, item in media['files'].items():
        verified('assets/cinema/' + name, item['sha256'])
    html = re.sub(r'<link rel="stylesheet" href="\./([^"]+)">',
                  lambda m: '<style>\n' + local(m[1]).read_text() + '\n</style>', html)
    scripts = []
    def script(m):
        scripts.append(local(m[1]).read_text())
        return ''
    html = re.sub(r'<script defer src="\./([^"]+)"></script>', script, html)
    html = html.replace('</body>', '\n'.join('<script>\n' + s + '\n</script>' for s in scripts) + '\n</body>')
    # Nested media paths and data-src/data-mobile-src/poster are deliberately included.
    html = re.sub(r'\./assets/[a-zA-Z0-9/._-]+', lambda m: data_uri(m[0][2:]), html)
    if re.search(r'(?:src|href|poster)="\./', html):
        raise ValueError('Unbundled resource')
    if output:
        output = Path(output).resolve()
        if output == ROOT / 'index.html':
            raise ValueError('Cannot overwrite source')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(html)
        print(f'Built {output.name}: {len(html.encode()):,} bytes')
    return html

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(ROOT / 'ASSYABAB-CAHAYA.html'))
    build(parser.parse_args().output)
