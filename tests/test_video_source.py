#!/usr/bin/env python3
"""Portable export contracts: lazy media remains available without a server."""
import base64
from html.parser import HTMLParser
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build_offline


class MediaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.video = {}

    def handle_starttag(self, tag, attrs):
        if tag == 'video':
            self.video = dict(attrs)


class PortableMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        for directory in ['assets', 'styles', 'src']:
            (self.root / directory).mkdir()
        self.files = {
            'cahaya-scroll.mp4': b'desktop video fixture\x00\xff',
            'cahaya-scroll-mobile.mp4': b'mobile video fixture\x00\xfe',
            'cahaya-poster.jpg': b'poster fixture\x00\xfd',
        }
        for name, payload in self.files.items():
            (self.root / 'assets' / name).write_bytes(payload)
        (self.root / 'assets/manifest.json').write_text('{}', encoding='utf-8')
        (self.root / 'styles/main.css').write_text('video { object-fit: cover; }', encoding='utf-8')
        (self.root / 'src/video.js').write_text('window.caption = "Mengaji → berkarya";', encoding='utf-8')
        (self.root / 'index.html').write_text('''<!doctype html><html><head>
<meta charset="utf-8"><link rel="stylesheet" href="./styles/main.css">
<script defer src="./src/video.js"></script></head><body>
<h1>Mengaji → berkarya</h1>
<video preload="none" data-src="./assets/cahaya-scroll.mp4"
 data-mobile-src="./assets/cahaya-scroll-mobile.mp4" poster="./assets/cahaya-poster.jpg"></video>
</body></html>''', encoding='utf-8')
        patcher = patch.object(build_offline, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_lazy_video_variants_and_poster_survive_portable_export(self):
        output = self.root / 'output/presentation.html'
        exported = build_offline.build(output)
        self.assertEqual(exported, output.read_text(encoding='utf-8'))
        self.assertIn('Mengaji → berkarya', exported)
        self.assertIn('window.caption', exported)
        self.assertIn('object-fit: cover', exported)
        self.assertNotIn('./assets/', exported)
        self.assertNotIn('<script defer src=', exported)
        self.assertNotIn('<link rel="stylesheet"', exported)
        parsed = MediaParser()
        parsed.feed(exported)
        for attr, name, mime in [
            ('data-src', 'cahaya-scroll.mp4', 'video/mp4'),
            ('data-mobile-src', 'cahaya-scroll-mobile.mp4', 'video/mp4'),
            ('poster', 'cahaya-poster.jpg', 'image/jpeg'),
        ]:
            with self.subTest(attribute=attr):
                header, encoded = parsed.video[attr].split(',', 1)
                self.assertEqual(header, f'data:{mime};base64')
                self.assertEqual(base64.b64decode(encoded), self.files[name])

    def test_missing_video_does_not_silently_create_broken_export(self):
        (self.root / 'assets/cahaya-scroll-mobile.mp4').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing/unsafe resource: assets/cahaya-scroll-mobile.mp4'):
            build_offline.build()

    def test_export_cannot_overwrite_source_document(self):
        source = self.root / 'index.html'
        original = source.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Cannot overwrite source'):
            build_offline.build(source)
        self.assertEqual(source.read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
