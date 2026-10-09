"""Deterministic native PTF v1 writer with P8 swizzled GIM graphics.

Original KP builder; dimensions and PTF slot IDs follow Sony's 6.20 schema.
"""
from collections import OrderedDict
import io
import struct
import zlib
from PIL import Image

MAX_THEME_BYTES = 768 * 1024


def pixel_data(image):
    method = getattr(image, 'get_flattened_data', None)
    return method() if method else image.getdata()


def align(value, n=4):
    return (value + n - 1) // n * n


def block(kind, size, next_offset):
    return struct.pack('<HHIII', kind, 0, size, next_offset, 16)


def image_block(kind, fmt, order, width, height, bpp, pixels, level_type):
    info = bytearray(64)
    struct.pack_into('<H', info, 0, 0x30)
    struct.pack_into('<8H', info, 4, fmt, order, width, height, bpp, 16, 8, 2)
    struct.pack_into('<4I', info, 24, 0x30, 0x40, 0x40 + len(pixels), 0)
    struct.pack_into('<4H', info, 40, level_type, 1, 3, 1)
    struct.pack_into('<I', info, 48, 0x40)
    size = 16 + len(info) + len(pixels)
    return block(kind, size, size) + info + pixels


def encode_gim(image):
    image = image.convert('RGBA')
    colors = OrderedDict([((0, 0, 0, 0), 0)])
    indices = bytearray()
    for rgba in pixel_data(image):
        rgba = rgba if rgba[3] else (0, 0, 0, 0)
        if rgba not in colors:
            colors[rgba] = len(colors)
        if len(colors) > 256:
            raise ValueError('Indexed icon exceeds 256 RGBA entries')
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
    pal = image_block(5, 3, 0, 256, 1, 32, bytes(palette), 2)
    pix = image_block(4, 5, 1, w, h, 8, bytes(swizzled), 1)
    author = b'\0\0Oct 07 2026\n\0KP Native Theme Collection 1.0\0'
    author += bytes(align(len(author)) - len(author))
    file_info = block(0xFF, 16 + len(author), 16 + len(author)) + author
    picture_size = 16 + len(pal) + len(pix)
    root_size = 16 + picture_size + len(file_info)
    return (b'MIG.00.1PSP\0\0\0\0\0' + block(2, root_size, 16)
            + block(3, picture_size, 16) + pal + pix + file_info), len(colors)


def encode_bitmap(image):
    buf = io.BytesIO()
    image.convert('RGB').save(buf, format='BMP')
    data = buf.getvalue()
    assert data[:2] == b'BM' and struct.unpack_from('<H', data, 28)[0] == 24
    assert struct.unpack_from('<I', data, 30)[0] == 0
    return data


def record(sub, file_type, raw, color=False):
    packed = raw if color else zlib.compress(raw, 9)
    compression = 2
    if not color and align(len(packed)) >= len(raw):
        packed, compression = raw, 0
    padded = packed + bytes(align(len(packed)) - len(packed))
    header = bytearray(32)
    struct.pack_into('<4H2I', header, 0, sub, 0, file_type, compression, len(padded), len(raw))
    return bytes(header) + padded


def theme_bytes(config, objects):
    header = bytearray(0x120)
    header[:8] = b'\0PTF\0\1\0\0'
    for offset, limit, value in [(8, 128, config['title']), (136, 48, config['product_id']),
                                 (184, 8, '6.20'), (192, 8, config['version'])]:
        encoded = value.encode('utf-8')
        assert len(encoded) < limit and b'\0' not in encoded
        header[offset:offset + len(encoded)] = encoded
    struct.pack_into('<I', header, 200, 8)
    segments = []
    offset = len(header)
    assert list(sorted(objects)) == [0, 1, 2, 3, 4]
    for pointer, (obj, entries) in enumerate(sorted(objects.items())):
        entries = sorted(entries)
        assert len({sub for sub, _ in entries}) == len(entries)
        data = b''.join(item for _, item in entries)
        object_header = bytearray(32)
        struct.pack_into('<HHII', object_header, 0, obj, len(entries), len(data), offset + 32)
        struct.pack_into('<I', header, 0x100 + pointer * 4, offset)
        segments.extend([bytes(object_header), data])
        offset += 32 + len(data)
    result = bytes(header) + b''.join(segments)
    assert len(result) == offset and len(result) <= MAX_THEME_BYTES
    return result
