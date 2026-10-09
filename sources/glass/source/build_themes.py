#!/usr/bin/env python3
"""Build the three installable themes from prepared native-size artwork."""
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image
from ptf_codec import encode_bitmap, encode_gim, record, theme_bytes, pixel_data, MAX_THEME_BYTES

ROOT = Path(__file__).resolve().parent.parent


def main():
    (ROOT / 'dist').mkdir(exist_ok=True)
    reports = []
    for config in json.loads((ROOT / 'themes.json').read_text()):
        assets = ROOT / 'themes' / config['slug'] / 'assets'
        out = ROOT / 'verification' / config['slug']
        out.mkdir(parents=True, exist_ok=True)
        entries = json.loads((assets / 'manifest.json').read_text())
        objects, stats = {}, []
        for entry in entries:
            obj, sub = entry['obj'], entry['sub']
            is_bitmap = obj == 1 or (obj == 0 and sub == 1)
            source = assets / entry['file'] if is_bitmap else assets / 'indexed' / entry['file']
            image = Image.open(source)
            assert list(image.size) == entry['size']
            if is_bitmap:
                raw, palette_count, file_type = encode_bitmap(image), None, 4
            else:
                raw, palette_count = encode_gim(image)
                file_type = 5
                if entry['focus']:
                    assert palette_count <= 64
                    assert all(a == 0 or (r, g, b) == (255, 255, 255)
                               for r, g, b, a in pixel_data(image.convert('RGBA')))
            packed = record(sub, file_type, raw)
            objects.setdefault(obj, []).append((sub, packed))
            stats.append(dict(obj=obj, sub=sub, label=entry['label'], size=entry['size'],
                              palette=palette_count, raw_bytes=len(raw), record_bytes=len(packed)))
        assert len(stats) == 74
        objects[0].append((2, record(2, 5, struct.pack('<I', config['theme_color']), color=True)))
        data = theme_bytes(config, objects)
        dest = ROOT / 'dist' / config['file']
        dest.write_bytes(data)
        report = dict(title=config['title'], file=config['file'], product_id=config['product_id'],
                      version=config['version'], firmware_schema='6.20',
                      theme_color=config['theme_color'], size_bytes=len(data),
                      maximum_bytes=MAX_THEME_BYTES, graphic_assets=len(stats),
                      records=len(stats) + 1, sha256=hashlib.sha256(data).hexdigest(), assets=stats)
        (out / 'build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
        reports.append({k:v for k,v in report.items() if k != 'assets'})
    print(json.dumps(reports, ensure_ascii=False))


if __name__ == '__main__':
    main()
