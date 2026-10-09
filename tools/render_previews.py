#!/usr/bin/env python3
"""Render a consistent desktop XMB illustration from actual decoded PTF pixels.

SPDX-License-Identifier: GPL-3.0-only
These PNGs are visual previews, not photographs or screenshots of a PSP.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from verify import parse_ptf

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / 'sources/classic-five/vendor/fonts/DejaVuSans.ttf'
BOLD = ROOT / 'sources/classic-five/vendor/fonts/DejaVuSans-Bold.ttf'


def font(size, bold=False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def label(image, position, text, size=11, alpha=255, anchor=None):
    x, y = position
    shadow = Image.new('RGBA', image.size)
    ImageDraw.Draw(shadow).text((x + 1, y + 1), text, font=font(size), fill=(0, 0, 0, alpha * 3 // 4), anchor=anchor)
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(.6)))
    ImageDraw.Draw(image).text(position, text, font=font(size), fill=(250, 252, 255, alpha), anchor=anchor)


def xmb(theme):
    _, images, _ = parse_ptf((ROOT / 'PSP/THEME' / theme['file']).read_bytes())
    target = images[(1, 0)].copy().convert('RGBA')
    for sub, center in {4:-54, 5:28, 6:110, 7:192, 8:274}.items():
        icon = images[(2, sub)].copy()
        if sub != 6:
            icon.putalpha(icon.getchannel('A').point(lambda value:round(value * .56)))
        target.alpha_composite(icon, (center - 32, 48))
    label(target, (110, 103), 'Game', anchor='mt')
    for sub, center, opacity in [(4, 12, .32), (2, 201, .5)]:
        icon = images[(3, sub)].copy()
        icon.putalpha(icon.getchannel('A').point(lambda value:round(value * opacity)))
        target.alpha_composite(icon, (86, center - 24))
    target.alpha_composite(images[(3, 11)], (78, 105))
    target.alpha_composite(images[(3, 10)], (86, 113))
    label(target, (146, 131), 'Saved Data Utility', 12)
    label(target, (146, 195), 'Memory Stick', 10, 170)
    label(target, (403, 13), '09/10  14:14', 10, anchor='rt')
    draw = ImageDraw.Draw(target)
    draw.rounded_rectangle((418, 12, 439, 21), radius=1, outline=(250, 253, 255, 230))
    draw.rectangle((440, 15, 441, 18), fill=(250, 253, 255, 230))
    draw.rectangle((421, 15, 434, 18), fill=(250, 253, 255, 215))
    label(target, (12, 253), 'Desktop preview', 8, 180)
    return target.convert('RGB')


def backdrop(size):
    image = Image.new('RGB', size)
    draw = ImageDraw.Draw(image)
    width, height = size
    for y in range(height):
        blend = y / max(1, height - 1)
        color = tuple(round(a * (1 - blend) + b * blend) for a, b in zip((15, 27, 47), (5, 10, 20)))
        draw.line((0, y, width, y), fill=color)
    return image


def main():
    themes = json.loads((ROOT / 'themes.json').read_text())
    previews = []
    destination = ROOT / 'assets/previews'
    destination.mkdir(exist_ok=True)
    for theme in themes:
        preview = xmb(theme)
        preview.save(destination / (theme['slug'] + '.png'))
        previews.append(preview)
    gallery = backdrop((1680, 1480))
    draw = ImageDraw.Draw(gallery)
    draw.text((40, 30), 'PSP / PTF THEMES', font=font(54, True), fill='#f4f8ff')
    draw.text((42, 103), 'Kpavel325-404 · Retro desktops, glass and winter scenes', font=font(21), fill='#a5b9d0')
    pills = [(40, 234, '9 THEMES', '#78d6ff'), (290, 340, '661 IMAGES CHECKED', '#80e1b5'),
             (646, 348, 'DESKTOP CHECKS: PASS', '#80e1b5'), (1010, 628, 'PSP HARDWARE TEST: PENDING', '#e6bd80')]
    for x, width, text, color in pills:
        draw.rounded_rectangle((x, 150, x + width, 190), radius=12, fill='#14233a', outline='#263b56')
        draw.text((x + 16, 160), text, font=font(15, True), fill=color)
    for index, (theme, preview) in enumerate(zip(themes, previews)):
        x, y = 40 + (index % 3) * 540, 220 + (index // 3) * 396
        draw.rounded_rectangle((x, y, x + 520, y + 374), radius=16, fill='#111c2e', outline='#2a3a50', width=1)
        draw.rounded_rectangle((x + 20, y + 17, x + 54, y + 21), radius=2, fill=theme['accent'])
        draw.text((x + 20, y + 32), theme['title'], font=font(21, True), fill='#f2f6ff')
        draw.text((x + 20, y + 63), theme['description'], font=font(12), fill='#a4b4c8')
        gallery.paste(preview, (x + 20, y + 86))
    draw.text((40, 1412), 'Native 480 × 272 artwork · Standard PTF v1 · Target: PSP-3000 / FW 6.61', font=font(19), fill='#cad7e8')
    draw.text((40, 1445), 'Computer-rendered XMB illustrations. Fonts and live status on a PSP may differ.', font=font(16), fill='#8095b0')
    gallery.save(ROOT / 'assets/gallery.png')
    social = backdrop((1280, 640))
    draw = ImageDraw.Draw(social)
    draw.text((48, 54), 'Kpavel325-404 / PSP', font=font(19, True), fill='#80d6ff')
    draw.text((46, 173), 'Nine themes.', font=font(52, True), fill='#f7faff')
    draw.text((46, 239), 'One handheld.', font=font(48, True), fill='#f7faff')
    draw.text((48, 331), 'Retro desktops · Glass · Winter', font=font(22), fill='#aac1db')
    draw.rounded_rectangle((48, 397, 534, 448), radius=12, fill='#152840', outline='#31506c')
    draw.text((66, 411), 'Native PTF / 480 × 272 / 3.80 MiB', font=font(17, True), fill='#a9e2ff')
    draw.text((48, 544), 'Desktop verified · Hardware testing pending', font=font(16), fill='#e6bd80')
    for index, preview in enumerate(previews):
        x, y = 650 + (index % 3) * 200, 145 + (index // 3) * 121
        social.paste(preview.resize((190, 108), Image.Resampling.LANCZOS), (x, y))
        draw.rectangle((x, y, x + 189, y + 107), outline='#41617b')
    social.save(ROOT / 'assets/social-preview.png')
    print('Rendered nine native previews, gallery and social preview.')


if __name__ == '__main__':
    main()
