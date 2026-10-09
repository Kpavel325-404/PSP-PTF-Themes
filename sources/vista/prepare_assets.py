#!/usr/bin/env python3
"""Prepare PSP-native assets from original Windows Vista artwork."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parent
ICONS = ROOT / 'sources/windows/Icons/Windows Vista/ico'
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

CATEGORY = {
    0: ('Default', 'imageres', 115),
    1: ('Settings', 'imageres', 27),
    2: ('Photo', 'imageres', 21),
    3: ('Music', 'imageres', 108),
    4: ('Video', 'imageres', 23),
    5: ('TV', 'imageres', 109),
    6: ('Game', 'imageres', 14),
    7: ('Network', 'imageres', 25),
    8: ('Extras', 'imageres', 115),
}
FIRST = {
    2: ('Memory Stick', 'imageres', 36),
    4: ('UMD', 'imageres', 38),
    6: ('Camera', 'imageres', 46),
    8: ('Game Sharing', 'imageres', 178),
    10: ('Saved Data Utility', 'imageres', 166),
    12: ('UMD Update', 'imageres', 161),
    14: ('Network Update', 'imageres', 184),
    16: ('USB Connection', 'imageres', 36),
    18: ('Video Settings', 'imageres', 189),
    20: ('Photo Settings', 'imageres', 168),
    22: ('System Settings', 'imageres', 114),
    24: ('Theme Settings', 'imageres', 197),
    26: ('Date and Time', 'imageres', 144),
    28: ('Power Save Settings', 'imageres', 119),
    30: ('External Display', 'imageres', 109),
    32: ('Sound Settings', 'imageres', 176),
    34: ('Security Settings', 'imageres', 106),
    36: ('RSS Channel Settings', 'imageres', 117),
    38: ('Network Settings', 'imageres', 179),
    40: ('Online Instruction Manuals', 'imageres', 101),
    42: ('Remote Play', 'imageres', 147),
    44: ('Internet Radio', 'imageres', 108),
    46: ('RSS Channel', 'imageres', 117),
    48: ('Internet Browser', 'shell32', 16744),
    50: ('Internet Search', 'imageres', 177),
    52: ('Account Management', 'imageres', 130),
    54: ('Default and model fallback', 'imageres', 181),
    56: ('Bluetooth Settings', 'imageres', 179),
    58: ('SensMe Channels', 'imageres', 22),
}

entries: list[dict] = []


def icon(dll: str, number: int, size: tuple[int, int], box: tuple[int, int]) -> Image.Image:
    source = ICONS / f'{dll}.dll/ICON{number}_1.ico'
    original = Image.open(source)
    largest = max(original.ico.sizes(), key=lambda s: s[0] * s[1])
    rgba = original.ico.getimage(largest).convert('RGBA')
    bounds = rgba.getchannel('A').getbbox()
    assert bounds, f'Empty original icon: {source}'
    rgba = rgba.crop(bounds)
    factor = min(box[0] / rgba.width, box[1] / rgba.height)
    target = (max(1, round(rgba.width * factor)), max(1, round(rgba.height * factor)))
    # Premultiply before filtering so invisible RGB does not create dark fringes.
    rgba = rgba.convert('RGBa').resize(target, Image.Resampling.LANCZOS).convert('RGBA')
    result = Image.new('RGBA', size, (0, 0, 0, 0))
    result.alpha_composite(rgba, ((size[0] - target[0]) // 2, (size[1] - target[1]) // 2))
    return result


def put(obj: int, sub: int, label: str, image: Image.Image, *, source: str | None = None, focus: bool = False) -> None:
    name = f'{obj}-{sub:02d}.png'
    image.save(ASSETS / name)
    entries.append(dict(obj=obj, sub=sub, label=label, file=name, size=list(image.size), focus=focus, source=source))


def halo(body: Image.Image, size: tuple[int, int]) -> Image.Image:
    alpha = Image.new('L', size)
    alpha.paste(body.getchannel('A'), (8, 8))
    blurred = alpha.filter(ImageFilter.GaussianBlur(2.1))
    a = np.maximum(0, np.asarray(blurred, dtype=float) * .98 - np.asarray(alpha, dtype=float))
    # Transparent + 63 white-alpha levels; the sharp body is never duplicated.
    levels = np.where(a < 3, 0, np.maximum(1, np.rint(a / 255 * 63)))
    a = np.rint(levels * 255 / 63).astype(np.uint8)
    rgba = np.zeros((*a.shape, 4), dtype=np.uint8)
    rgba[a > 0, :3] = 255
    rgba[:, :, 3] = a
    return Image.fromarray(rgba)


def source_url(dll: str, number: int) -> str:
    return f'https://github.com/bartekl1/windows-ui-assets/blob/main/Icons/Windows%20Vista/ico/{dll}.dll/ICON{number}_1.ico'


def main() -> None:
    supplied = ROOT.parent / 'upload/изображение(20261005-180359).png'
    if not supplied.is_file():
        supplied = ROOT / 'sources/Aurora-original.png'
    # The user selected this higher resolution Aurora. The archive source is
    # preserved separately in SOURCES; no AI-generated artwork is introduced.
    original = Image.open(supplied).convert('RGB')
    wallpaper = ImageOps.fit(original, (480, 272), Image.Resampling.LANCZOS, centering=(.5, .45))
    put(1, 0, 'Aurora wallpaper', wallpaper, source='User-supplied Windows Vista Aurora')
    wallpaper.save(ROOT / 'dist/Aero-Vista-Wallpaper.png')
    wallpaper.save(ASSETS / 'wallpaper.bmp')

    for sub, (label, dll, number) in CATEGORY.items():
        put(2, sub, label, icon(dll, number, (64, 48), (44, 40)), source=source_url(dll, number))
    for sub, (label, dll, number) in FIRST.items():
        body = icon(dll, number, (48, 48), (40, 40))
        put(3, sub, label, body, source=source_url(dll, number))
        put(3, sub + 1, label + ' focus', halo(body, (64, 64)), source='Focus derived from matching icon silhouette', focus=True)
    for sub, number in [(0, 114), (2, 106)]:
        body = icon('imageres', number, (32, 32), (26, 26))
        put(4, sub, 'Settings detail', body, source=source_url('imageres', number))
        put(4, sub + 1, 'Settings detail focus', halo(body, (48, 48)), source='Focus derived from matching icon silhouette', focus=True)

    put(0, 0, 'Theme preview icon', icon('imageres', 115, (16, 16), (15, 15)), source=source_url('imageres', 115))
    preview = wallpaper.resize((300, 170), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(preview)
    preview_font = ROOT / 'sources/preview-font.ttf'
    font_path = str(preview_font) if preview_font.is_file() else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    font = ImageFont.truetype(font_path, 21)
    small = ImageFont.truetype(font_path, 10)
    draw.text((20, 20), 'AERO VISTA', font=font, fill=(248, 253, 255), stroke_width=1, stroke_fill=(9, 88, 112))
    draw.text((22, 50), 'Frutiger Aero / Aurora', font=small, fill=(244, 253, 255))
    for n, sub in enumerate([1, 2, 3, 4, 6, 7]):
        image = Image.open(ASSETS / f'2-{sub:02d}.png').convert('RGBA')
        image = image.resize((45, 34), Image.Resampling.LANCZOS)
        preview.paste(image, (15 + n * 44, 93), image)
    put(0, 1, 'Theme preview image', preview)
    preview.save(ASSETS / 'theme-preview.bmp')
    entries.sort(key=lambda e: (e['obj'], e['sub']))
    (ASSETS / 'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2))
    print(json.dumps({'assets': len(entries), 'category_icons': len(CATEGORY), 'first_level_pairs': len(FIRST), 'wallpaper': list(wallpaper.size)}))


if __name__ == '__main__':
    main()
