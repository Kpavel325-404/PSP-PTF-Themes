#!/usr/bin/env python3
"""Verify shipped file checksums, first-party Markdown links and PNG assets.
SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
import hashlib
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def check():
    checksum_files = ['SHA256SUMS.txt', 'FILES_SHA256.txt']
    count = 0
    for name in checksum_files:
        lines = (ROOT / name).read_text().splitlines()
        if not lines:
            raise ValueError('Empty checksum manifest: ' + name)
        seen = set()
        for line in lines:
            digest, separator, relative = line.partition('  ')
            path = (ROOT / relative).resolve()
            if not separator or not re.fullmatch('[a-f0-9]{64}', digest) or relative in seen or not path.is_relative_to(ROOT):
                raise ValueError('Invalid checksum entry: ' + line)
            seen.add(relative)
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError('Checksum mismatch: ' + relative)
            count += 1
    # Imported third-party READMEs describe their original repositories. Audit
    # only the first-party documentation and issue templates shipped here.
    documents = list(ROOT.glob('*.md')) + list((ROOT / 'docs').rglob('*.md')) + list((ROOT / '.github').rglob('*.md')) + list((ROOT / 'verification/evidence').glob('*.md'))
    links = 0
    for document in documents:
        text = document.read_text()
        text = re.sub(r'```.*?```', '', text, flags=re.S)
        for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
            target = target.split('#', 1)[0]
            if not target or '://' in target or target.startswith(('mailto:', 'data:')):
                continue
            path = (document.parent / target).resolve()
            if not path.is_relative_to(ROOT) or not path.exists():
                raise ValueError(f'Broken local Markdown link: {document.relative_to(ROOT)} -> {target}')
            links += 1
    images = 0
    for path in (ROOT / 'assets').rglob('*.png'):
        with Image.open(path) as image:
            image.verify()
        images += 1
    for folder in ['previews', 'wallpapers']:
        for path in (ROOT / 'assets' / folder).glob('*.png'):
            with Image.open(path) as image:
                if image.size != (480, 272):
                    raise ValueError('Not a native PSP image: ' + str(path))
    social = ROOT / 'assets/social-preview.png'
    with Image.open(social) as image:
        if image.size != (1280, 640) or social.stat().st_size >= 1_000_000:
            raise ValueError('Social preview size/weight')
    print(f'PASS: {count} checksum entries, {links} local documentation links, {images} PNG assets.')
    return dict(checksum_entries=count, local_documentation_links=links, png_assets=images, status='PASS')


if __name__ == '__main__':
    check()
