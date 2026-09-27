#!/usr/bin/env python3
"""Fetch documentary images pinned to a source commit, verifying every checksum.
The ordinary website loads these public images directly. This utility is only
needed to recreate the fully offline presentation. Never modifies the source repo.
"""
from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
for name,item in json.loads((ROOT/'assets/manifest.json').read_text()).items():
    target=ROOT/'assets'/name
    if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:
        print('Verified',name);continue
    req=Request(item['url'],headers={'User-Agent':'Assyabab-Portable-Builder'})
    with urlopen(req,timeout=30) as r:data=r.read(5_000_000)
    if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError(f'Checksum failed: {name}')
    target.write_bytes(data);print('Fetched and verified',name)
