#!/usr/bin/env python3
"""Audit actual PTF boundaries and compare every pixel to an independent decode."""
import hashlib
import io
import json
from pathlib import Path
import struct
import zlib
from PIL import Image

ROOT = Path(__file__).resolve().parent
data = (ROOT / 'dist/Aero-Vista-Aurora.ptf').read_bytes()
manifest = json.loads((ROOT / 'assets/manifest.json').read_text())
expected = {(e['obj'], e['sub']): e for e in manifest}
u16 = lambda buf, pos: struct.unpack_from('<H', buf, pos)[0]
u32 = lambda buf, pos: struct.unpack_from('<I', buf, pos)[0]

assert data[:8] == b'\0PTF\0\1\0\0'
assert len(data) <= 768 * 1024
assert u32(data, 200) == 8
offsets = [u32(data, p) for p in range(0x100, 0x120, 4)]
assert offsets[0] == 0x120
assert all(offsets[:5]) and offsets[5:] == [0, 0, 0]
slots = {}
graphics = []
max_palette = max_focus_palette = 0

for group, off in enumerate(offsets[:5]):
    assert off % 4 == 0 and u16(data, off) == group
    count, length, start = u16(data, off + 2), u32(data, off + 4), u32(data, off + 8)
    assert start == off + 32
    end = start + length
    assert end == (offsets[group + 1] if group < 4 else len(data))
    assert data[off + 12:off + 32] == bytes(20)
    pos, seen = start, []
    for _ in range(count):
        assert pos % 4 == 0 and pos + 32 <= end
        sub, kind, comp = u16(data, pos), u16(data, pos + 4), u16(data, pos + 6)
        size, raw_size = u32(data, pos + 8), u32(data, pos + 12)
        assert u16(data, pos + 2) == 0 and data[pos + 16:pos + 32] == bytes(16)
        assert size % 4 == 0 and pos + 32 + size <= end
        packed = data[pos + 32:pos + 32 + size]
        if comp == 2 and size < raw_size:
            stream = zlib.decompressobj()
            raw = stream.decompress(packed) + stream.flush()
            assert stream.eof and len(stream.unused_data) <= 3
            assert not any(stream.unused_data)
        else:
            assert comp == 0 or (group, sub) == (0, 2)
            raw = packed[:raw_size]
            assert len(packed[raw_size:]) <= 3 and not any(packed[raw_size:])
        assert len(raw) == raw_size
        assert sub not in seen
        seen.append(sub)
        if (group, sub) == (0, 2):
            assert kind == 5 and comp == 2 and size == raw_size == 4
            assert u32(raw, 0) == 7
        else:
            entry = expected[(group, sub)]
            if kind == 4:
                assert raw[:2] == b'BM'
                assert u32(raw, 2) == len(raw)
                assert u16(raw, 26) == 1 and u16(raw, 28) == 24
                assert u32(raw, 30) == 0
                decoded = Image.open(io.BytesIO(raw))
                assert list(decoded.size) == entry['size']
            else:
                assert kind == 5 and raw[:16] == b'MIG.00.1PSP\0\0\0\0\0'
                assert u16(raw, 16) == 2 and u32(raw, 20) == len(raw) - 16
                assert u32(raw, 24) == 16 and u32(raw, 28) == 16
                assert u16(raw, 32) == 3 and u32(raw, 40) == 16
                blocks, p = {}, 48
                while p < len(raw):
                    assert p % 4 == 0 and p + 16 <= len(raw)
                    block_type, block_size, step = u16(raw, p), u32(raw, p + 4), u32(raw, p + 8)
                    assert p + block_size <= len(raw) and step == block_size and step > 0
                    assert u16(raw, p + 2) == 0 and u32(raw, p + 12) == 16
                    blocks[block_type] = (p, block_size)
                    p += step
                assert p == len(raw) and set(blocks) == {4, 5, 255}
                for block_type in (4, 5):
                    block_start, block_size = blocks[block_type]
                    info = block_start + 16
                    assert u16(raw, info) == 0x30
                    fmt, order = u16(raw, info + 4), u16(raw, info + 6)
                    width, height, bpp = u16(raw, info + 8), u16(raw, info + 10), u16(raw, info + 12)
                    assert (u16(raw, info + 14), u16(raw, info + 16)) == (16, 8)
                    assert u32(raw, info + 24) == 0x30
                    assert u32(raw, info + 28) == 0x40
                    assert u32(raw, info + 32) == block_size - 16
                    assert u32(raw, info + 48) == 0x40
                    if block_type == 5:
                        assert (fmt, order, width, height, bpp) == (3, 0, 256, 1, 32)
                        assert block_size == 16 + 64 + 1024
                    else:
                        assert (fmt, order, bpp) == (5, 1, 8)
                        assert [width, height] == entry['size']
                        pixel_bytes = ((width + 15) // 16 * 16) * ((height + 7) // 8 * 8)
                        assert block_size == 16 + 64 + pixel_bytes
                assert u32(raw, 36) == 16 + blocks[4][1] + blocks[5][1]

            source = ROOT / 'assets' / ('' if kind == 4 else 'indexed') / entry['file']
            pixels = bytearray(Image.open(source).convert('RGBA').tobytes())
            for index in range(0, len(pixels), 4):
                if pixels[index + 3] == 0:
                    pixels[index:index + 3] = b'\0\0\0'
            independently_decoded = (ROOT / 'build/decoded' / (entry['file'] + '.rgba')).read_bytes()
            assert independently_decoded == bytes(pixels), f"Pixel mismatch: {group}:{sub}"
            unique = set(bytes(pixels[index:index + 4]) for index in range(0, len(pixels), 4))
            if kind == 5:
                assert len(unique) <= 256
                max_palette = max(max_palette, len(unique))
            if entry['focus']:
                assert len(unique) <= 64
                assert all(pixel[3] == 0 or pixel[:3] == b'\xff\xff\xff' for pixel in unique)
                max_focus_palette = max(max_focus_palette, len(unique))
            graphics.append((group, sub))
        pos += 32 + size
    assert pos == end and seen == sorted(seen)
    slots[group] = seen

assert slots == {0: [0, 1, 2], 1: [0], 2: list(range(9)), 3: list(range(2, 60)), 4: list(range(4))}
assert set(graphics) == set(expected) and len(graphics) == 74
report = dict(result='PASS', size_bytes=len(data), maximum_bytes=768 * 1024,
              groups=5, records=sum(map(len, slots.values())), graphic_resources=len(graphics),
              exact_rgba_roundtrips=len(graphics), maximum_icon_colors=max_palette,
              maximum_focus_colors=max_focus_palette,
              checks=['PTF/group/record boundaries', 'native slot IDs', 'zlib EOF and padding',
                      'BMP24 dimensions', 'P8 swizzle and RGBA8888 CLUT',
                      'white focus palette', 'exact pixels from independent decoder'],
              sha256=hashlib.sha256(data).hexdigest())
(ROOT / 'build/strict-verification.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report))
