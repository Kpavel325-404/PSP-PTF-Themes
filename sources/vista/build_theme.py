#!/usr/bin/env python3
"""Build a standard PTF v1 with native, swizzled P8 GIM icon resources."""
from __future__ import annotations

from collections import OrderedDict
import hashlib
import io
import json
from pathlib import Path
import struct
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
DIST = ROOT / 'dist'
TITLE = 'Aero Vista - Aurora'
PRODUCT = 'KP_AERO_VISTA_AURORA'
VERSION = '1.0'
COLOR = 7  # Fixed turquoise; do not inherit October's orange colour.


def pixel_data(image: Image.Image):
    """Support both established and newer Pillow releases."""
    method = getattr(image, 'get_flattened_data', None)
    return method() if method else image.getdata()


def align(value: int, n: int = 4) -> int:
    return (value + n - 1) // n * n


def block(kind: int, size: int, next_offset: int) -> bytes:
    return struct.pack('<HHIII', kind, 0, size, next_offset, 16)


def image_block(kind: int, format_id: int, order: int, width: int, height: int,
                bpp: int, pixels: bytes, level_type: int) -> bytes:
    info = bytearray(64)
    struct.pack_into('<H', info, 0, 0x30)
    struct.pack_into('<8H', info, 4, format_id, order, width, height, bpp, 16, 8, 2)
    struct.pack_into('<4I', info, 24, 0x30, 0x40, 0x40 + len(pixels), 0)
    struct.pack_into('<4H', info, 40, level_type, 1, 3, 1)
    struct.pack_into('<I', info, 48, 0x40)
    size = 16 + len(info) + len(pixels)
    return block(kind, size, size) + info + pixels


def gim(image: Image.Image) -> tuple[bytes, int]:
    image = image.convert('RGBA')
    colors: OrderedDict[tuple[int, int, int, int], int] = OrderedDict()
    colors[(0, 0, 0, 0)] = 0
    indices = bytearray()
    for rgba in pixel_data(image):
        rgba = rgba if rgba[3] else (0, 0, 0, 0)
        if rgba not in colors:
            colors[rgba] = len(colors)
        assert len(colors) <= 256, f'Icon has {len(colors)} palette colours'
        indices.append(colors[rgba])
    palette = bytearray(1024)
    for rgba, index in colors.items():
        palette[index * 4:index * 4 + 4] = bytes(rgba)
    w, h = image.size
    swizzled = bytearray()
    for ty in range(0, align(h, 8), 8):
        for tx in range(0, align(w, 16), 16):
            for y in range(8):
                for x in range(16):
                    sx, sy = tx + x, ty + y
                    swizzled.append(indices[sy * w + sx] if sx < w and sy < h else 0)
    palette_block = image_block(5, 3, 0, 256, 1, 32, bytes(palette), 2)
    pixels_block = image_block(4, 5, 1, w, h, 8, bytes(swizzled), 1)
    author = b'\0\0Oct 05 2026\n\0Aero Vista Theme Builder 1.0\0'
    author += b'\0' * (align(len(author)) - len(author))
    file_info = block(0xFF, 16 + len(author), 16 + len(author)) + author
    picture_size = 16 + len(palette_block) + len(pixels_block)
    root_size = 16 + picture_size + len(file_info)
    header = b'MIG.00.1PSP\0\0\0\0\0'
    return header + block(2, root_size, 16) + block(3, picture_size, 16) + palette_block + pixels_block + file_info, len(colors)


def bitmap(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.convert('RGB').save(buf, format='BMP')
    data = buf.getvalue()
    assert data[:2] == b'BM' and struct.unpack_from('<H', data, 28)[0] == 24
    return data


def record(sub: int, file_type: int, raw: bytes, *, color: bool = False) -> bytes:
    packed = raw if color else zlib.compress(raw, 9)
    compression = 2
    if not color and align(len(packed)) >= len(raw):
        packed = raw
        compression = 0
    padded = packed + bytes(align(len(packed)) - len(packed))
    header = bytearray(32)
    struct.pack_into('<4H2I', header, 0, sub, 0, file_type, compression, len(padded), len(raw))
    return bytes(header) + padded


def build() -> None:
    DIST.mkdir(exist_ok=True)
    (ROOT / 'build').mkdir(exist_ok=True)
    manifest = json.loads((ASSETS / 'manifest.json').read_text())
    objects: dict[int, list[tuple[int, bytes]]] = {}
    statistics = []
    for entry in manifest:
        obj, sub = entry['obj'], entry['sub']
        is_bitmap = obj == 1 or (obj == 0 and sub == 1)
        source = ASSETS / entry['file'] if is_bitmap else ASSETS / 'indexed' / entry['file']
        image = Image.open(source)
        assert list(image.size) == entry['size']
        if is_bitmap:
            raw, palette_count, file_type = bitmap(image), None, 4
        else:
            raw, palette_count = gim(image)
            file_type = 5
            (ROOT / 'build' / f'{obj}-{sub:02d}.gim').write_bytes(raw)
            if entry['focus']:
                assert palette_count <= 64
                assert all(a == 0 or (r, g, b) == (255, 255, 255) for r, g, b, a in pixel_data(image.convert('RGBA')))
        packed_record = record(sub, file_type, raw)
        objects.setdefault(obj, []).append((sub, packed_record))
        statistics.append(dict(obj=obj, sub=sub, label=entry['label'], width=image.width,
                               height=image.height, palette=palette_count,
                               raw_bytes=len(raw), record_bytes=len(packed_record), source=entry['source']))
    objects[0].append((2, record(2, 5, struct.pack('<I', COLOR), color=True)))

    header = bytearray(0x120)
    header[:8] = b'\0PTF\0\1\0\0'
    for offset, limit, value in [(8, 128, TITLE), (136, 48, PRODUCT), (184, 8, '6.20'), (192, 8, VERSION)]:
        encoded = value.encode('utf-8')
        assert len(encoded) < limit
        header[offset:offset + len(encoded)] = encoded
    struct.pack_into('<I', header, 200, 8)
    segments = []
    offset = len(header)
    for pointer, (obj, entries) in enumerate(sorted(objects.items())):
        entries.sort()
        assert len({sub for sub, _ in entries}) == len(entries)
        data = b''.join(item for _, item in entries)
        object_header = bytearray(32)
        struct.pack_into('<HHII', object_header, 0, obj, len(entries), len(data), offset + 32)
        struct.pack_into('<I', header, 0x100 + pointer * 4, offset)
        segments.extend([bytes(object_header), data])
        offset += 32 + len(data)
    result = bytes(header) + b''.join(segments)
    assert len(result) == offset and len(result) <= 768 * 1024
    dest = DIST / 'Aero-Vista-Aurora.ptf'
    dest.write_bytes(result)
    report = dict(title=TITLE, product_id=PRODUCT, version=VERSION, firmware_schema='6.20',
                  theme_color=COLOR, size_bytes=len(result), maximum_bytes=768 * 1024,
                  graphic_assets=len(statistics), records=len(statistics) + 1,
                  sha256=hashlib.sha256(result).hexdigest(), assets=statistics)
    (ROOT / 'build/build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != 'assets'}))


if __name__ == '__main__':
    build()
