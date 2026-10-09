#!/usr/bin/env python3
"""Audit the shipped themes and compare two readers with prepared source images.

SPDX-License-Identifier: GPL-3.0-only
The verification report describes desktop checks, not a PSP hardware test.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 768 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def u16(data, offset):
    return struct.unpack_from('<H', data, offset)[0]


def u32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def canonical(image):
    pixels = bytearray(image.convert('RGBA').tobytes())
    for offset in range(0, len(pixels), 4):
        if not pixels[offset + 3]:
            pixels[offset:offset + 3] = bytes(3)
    return bytes(pixels)


def fixed_string(data, offset, size):
    field = data[offset:offset + size]
    require(0 in field, 'Metadata is not NUL-terminated')
    text, padding = field.split(b'\0', 1)
    require(not any(padding), 'Nonzero metadata padding')
    return text.decode('utf-8')


def decode_gim(data, expected_size):
    require(data[:16] == b'MIG.00.1PSP\0\0\0\0\0', 'Bad GIM magic')
    require(len(data) >= 48 and u16(data, 16) == 2, 'Missing GIM root')
    require(u32(data, 20) == len(data) - 16, 'GIM root length')
    blocks, position, image_info, palette = [], 16, None, None
    picture_length = None
    while position < len(data):
        require(position % 4 == 0 and position + 16 <= len(data), 'GIM block boundary')
        kind, reserved, size, step, start = struct.unpack_from('<HHIII', data, position)
        require(reserved == 0 and start == 16, 'GIM reserved/header fields')
        require(size >= 16 and position + size <= len(data), 'GIM block length')
        require(step >= 16 and position + step <= len(data), 'GIM next block')
        blocks.append(kind)
        if kind in (2, 3):
            require(step == 16, 'GIM container traversal')
            if kind == 3:
                picture_length = size
        else:
            require(step == size, 'GIM leaf traversal')
        if kind in (4, 5):
            info = position + 16
            require(size >= 80, 'GIM image info boundary')
            fmt, order, width, height, bits = struct.unpack_from('<5H', data, info + 4)
            require(u16(data, info) == 0x30 and u16(data, info + 2) == 0, 'GIM image header')
            require((u16(data, info + 14), u16(data, info + 16)) == (16, 8), 'GIM tile alignment')
            index, begin, end = struct.unpack_from('<3I', data, info + 24)
            require(index == 48 and begin == 64 and u32(data, info + index) == begin, 'GIM frame offset')
            require(info + end == position + size, 'GIM frame length')
            frame = data[info + begin:info + end]
            if kind == 5:
                require((fmt, order, width, height, bits) == (3, 0, 256, 1, 32), 'GIM RGBA8888 CLUT')
                require(len(frame) == 1024, 'GIM CLUT length')
                palette = frame
            else:
                require((fmt, order, bits) == (5, 1, 8), 'GIM P8 swizzled image')
                require((width, height) == expected_size, 'GIM image dimensions')
                stride = (width + 15) // 16 * 16
                rows = (height + 7) // 8 * 8
                require(len(frame) == stride * rows, 'GIM image data length')
                image_info = (width, height, stride, rows, frame)
        position += step
    require(position == len(data) and blocks == [2, 3, 5, 4, 255], 'GIM block sequence')
    require(palette is not None and image_info is not None, 'Missing GIM pixels/palette')
    require(picture_length == 16 + (80 + 1024) + (80 + len(image_info[4])), 'GIM picture boundary')
    width, height, stride, rows, frame = image_info
    pixels, position = bytearray(width * height * 4), 0
    for tile_y in range(0, rows, 8):
        for tile_x in range(0, stride, 16):
            for y in range(8):
                for x in range(16):
                    index = frame[position]
                    position += 1
                    px, py = tile_x + x, tile_y + y
                    if px < width and py < height:
                        offset = (py * width + px) * 4
                        pixels[offset:offset + 4] = palette[index * 4:index * 4 + 4]
    return Image.frombytes('RGBA', (width, height), bytes(pixels))


def image_size(group, sub):
    if group == 0:
        return (16, 16) if sub == 0 else (300, 170)
    if group == 1:
        return (480, 272)
    if group == 2:
        return (64, 48)
    if group == 3:
        return (64, 64) if sub % 2 else (48, 48)
    return (48, 48) if sub % 2 else (32, 32)


def parse_ptf(data):
    require(288 <= len(data) <= LIMIT and len(data) % 4 == 0, 'PTF size/alignment')
    require(data[:8] == b'\0PTF\0\1\0\0', 'PTF v1 magic')
    metadata = dict(title=fixed_string(data, 8, 128), product_id=fixed_string(data, 136, 48),
                    schema_version=fixed_string(data, 184, 8), version=fixed_string(data, 192, 8))
    require(re.fullmatch(r'[A-Za-z0-9_-]{1,47}', metadata['product_id']), 'Product ID format')
    require(metadata['schema_version'] == '6.20', 'Unexpected firmware resource schema')
    require(re.fullmatch(r'\d{1,2}(?:\.\d{1,2}){0,2}', metadata['version']), 'Theme version format')
    require(u32(data, 200) == 8 and not any(data[204:256]), 'PTF reserved fields')
    offsets = struct.unpack_from('<8I', data, 256)
    require(all(offsets[:5]) and not any(offsets[5:]), 'PTF group pointers')
    images, resources, slots = {}, [], {}
    previous_end, maximum_icon_colors, maximum_focus_colors = 288, 0, 0
    for group, offset in enumerate(offsets[:5]):
        require(offset == previous_end and offset + 32 <= len(data), 'PTF group boundary')
        ident, count, length, position = struct.unpack_from('<HHII', data, offset)
        require(ident == group and position == offset + 32 and not any(data[offset + 12:offset + 32]), 'PTF group header')
        end = position + length
        require(end <= len(data), 'PTF group extent')
        identifiers = []
        for _ in range(count):
            require(position % 4 == 0 and position + 32 <= end, 'PTF record boundary')
            sub, zero, kind, compression, size, raw_size = struct.unpack_from('<4H2I', data, position)
            require(zero == 0 and not any(data[position + 16:position + 32]), 'PTF record reserved fields')
            require(size % 4 == 0 and position + 32 + size <= end, 'PTF record extent')
            require(0 < raw_size <= 2 * 1024 * 1024, 'PTF resource size bound')
            require(compression in (0, 2), 'Unexpected PTF compression')
            packed = data[position + 32:position + 32 + size]
            if compression == 2 and size < raw_size:
                stream = zlib.decompressobj()
                raw = stream.decompress(packed, raw_size + 1)
                require(stream.eof and not stream.unconsumed_tail, 'PTF Deflate EOF/size')
                require(len(stream.unused_data) <= 3 and not any(stream.unused_data), 'PTF Deflate padding')
            else:
                require(compression == 0 or (group, sub) == (0, 2), 'Unexpected stored resource')
                raw = packed[:raw_size]
                require(len(packed[raw_size:]) <= 3 and not any(packed[raw_size:]), 'PTF stored padding')
            require(len(raw) == raw_size and sub not in identifiers, 'PTF resource length/duplicate ID')
            identifiers.append(sub)
            resource = dict(group=group, sub=sub, file_type=kind, compression=compression,
                            raw_bytes=raw_size, raw_sha256=hashlib.sha256(raw).hexdigest())
            if (group, sub) == (0, 2):
                require((kind, compression, size, raw_size) == (5, 2, 4, 4), 'PTF theme colour record')
                metadata['theme_color'] = u32(raw, 0)
                require(0 <= metadata['theme_color'] <= 12, 'PTF theme colour range')
            else:
                required = image_size(group, sub)
                if group == 1 or (group, sub) == (0, 1):
                    require(kind == 4 and len(raw) >= 54 and raw[:2] == b'BM', 'BMP24 resource')
                    require(u32(raw, 2) == len(raw) and u32(raw, 10) == 54 and u32(raw, 14) == 40, 'BMP header/size')
                    require(u16(raw, 26) == 1 and u16(raw, 28) == 24 and u32(raw, 30) == 0, 'BMP24 format')
                    image = Image.open(io.BytesIO(raw)).convert('RGBA')
                    require(image.size == required, 'BMP dimensions')
                    stride = (required[0] * 3 + 3) // 4 * 4
                    require(len(raw) == 54 + stride * required[1], 'BMP pixel extent')
                else:
                    require(kind == 5, 'GIM resource type')
                    image = decode_gim(raw, required)
                    rgba = canonical(image)
                    unique = set(rgba[index:index + 4] for index in range(0, len(rgba), 4))
                    require(len(unique) <= 256, 'Icon palette limit')
                    maximum_icon_colors = max(maximum_icon_colors, len(unique))
                    require(image.getchannel('A').getextrema()[1] > 40, 'Blank icon')
                    if group in (3, 4) and sub % 2:
                        require(len(unique) <= 64, 'Focus palette limit')
                        require(all(pixel[3] == 0 or pixel[:3] == b'\xff\xff\xff' for pixel in unique), 'Focus must glow white')
                        alpha = image.getchannel('A')
                        require(alpha.crop((0, 0, image.width, 2)).getextrema()[1] == 0 and
                                alpha.crop((0, image.height - 2, image.width, image.height)).getextrema()[1] == 0,
                                'Focus clipped at image border')
                        maximum_focus_colors = max(maximum_focus_colors, len(unique))
                images[(group, sub)] = image
                resource.update(width=image.width, height=image.height,
                                rgba_sha256=hashlib.sha256(canonical(image)).hexdigest())
            resources.append(resource)
            position += 32 + size
        require(position == end and identifiers == sorted(identifiers), 'PTF group record order/extent')
        slots[group], previous_end = identifiers, end
    require(previous_end == len(data), 'PTF trailing bytes')
    require(slots[0] == [0, 1, 2] and slots[1] == [0] and slots[3] == list(range(2, 60)) and slots[4] == list(range(4)), 'PTF native slot IDs')
    require(slots[2] in (list(range(9)), list(range(1, 9))), 'PTF category slot IDs')
    require(len(images) in (73, 74), 'PTF graphics count')
    metadata.update(records=len(resources), graphics=len(images), max_icon_colors=maximum_icon_colors,
                    max_focus_colors=maximum_focus_colors)
    return metadata, images, resources


def verify(output, export_assets=False):
    themes = json.loads((ROOT / 'themes.json').read_text())
    require(len(themes) == 9 and len({theme['file'] for theme in themes}) == 9, 'Expected nine distinct themes')
    require({p.name for p in (ROOT / 'PSP/THEME').glob('*.ptf')} == {t['file'] for t in themes}, 'Unexpected/missing PTF files')
    reports = []
    with tempfile.TemporaryDirectory(prefix='ptf-independent-') as temporary:
        subprocess.run(['node', str(ROOT / 'tools/verify_independent.cjs'), str(Path(temporary))], check=True, cwd=ROOT)
        for theme in themes:
            path = ROOT / 'PSP/THEME' / theme['file']
            data = path.read_bytes()
            require(len(data) == theme['bytes'] and hashlib.sha256(data).hexdigest() == theme['sha256'], 'Shipped PTF differs from its original checksum: ' + theme['file'])
            metadata, images, resources = parse_ptf(data)
            require(metadata['title'] == theme['ptf_title'] and metadata['product_id'] == theme['product_id'] and metadata['version'] == theme['theme_version'], 'Theme metadata differs from manifest')
            require(set(theme['prepared_images']) == {f'{g}:{s}' for g, s in images}, 'Prepared source image map differs')
            independent = json.loads((Path(temporary) / theme['slug'] / 'reader.json').read_text())
            require(independent['graphics'] == len(images) and independent['metadata']['title'] == metadata['title'] and
                    independent['metadata']['productId'] == metadata['product_id'] and independent['metadata']['color'] == metadata['theme_color'], 'Independent reader metadata mismatch')
            for (group, sub), image in images.items():
                pixels = canonical(image)
                target = (Path(temporary) / theme['slug'] / f'{group}_{sub}.rgba').read_bytes()
                require(pixels == target, f'Independent reader pixel mismatch: {theme["file"]} {group}:{sub}')
                prepared_path = (ROOT / theme['prepared_images'][f'{group}:{sub}']).resolve()
                require(prepared_path.is_relative_to(ROOT), 'Prepared image path escapes repository')
                with Image.open(prepared_path) as prepared:
                    require(image.size == prepared.size and pixels == canonical(prepared), f'Prepared source pixel mismatch: {theme["file"]} {group}:{sub}')
            if export_assets:
                for directory in ['assets/wallpapers', 'assets/icons', 'assets/selection-previews']:
                    (ROOT / directory).mkdir(parents=True, exist_ok=True)
                images[(1, 0)].convert('RGB').save(ROOT / 'assets/wallpapers' / (theme['slug'] + '.png'))
                images[(0, 0)].save(ROOT / 'assets/icons' / (theme['slug'] + '.png'))
                images[(0, 1)].convert('RGB').save(ROOT / 'assets/selection-previews' / (theme['slug'] + '.png'))
            report = dict(file=theme['file'], slug=theme['slug'], status='PASS', bytes=len(data), sha256=theme['sha256'],
                          metadata=metadata, normalized_rgba_matches=len(images), prepared_source_matches=len(images),
                          hardware_test='NOT_RUN', resources=resources)
            reports.append(report)
            print(f'PASS {theme["file"]}: {len(images)} graphics / original SHA-256', flush=True)
    result = dict(schema_version=1, verified_at=datetime.now(timezone.utc).isoformat(), status='PASS',
                  theme_count=len(reports), graphic_resources=sum(t['metadata']['graphics'] for t in reports),
                  total_ptf_bytes=sum(t['bytes'] for t in reports), hardware_test='NOT_RUN',
                  normalization='Only RGB channels of fully transparent pixels are set to zero.',
                  independent_reader='Unmodified PTF Studio parser and GIM decoder; separate JavaScript BMP24 decoder.',
                  themes=reports)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(f'PASS: {len(reports)} themes, {result["graphic_resources"]} graphics. Hardware: NOT_RUN.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'verification/latest.json')
    parser.add_argument('--export-assets', action='store_true')
    args = parser.parse_args()
    verify(args.output, args.export_assets)
