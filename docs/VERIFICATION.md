# Verification / Проверка

**Desktop audit: PASS — 9 PTF files, 670 records, 661 decoded graphics.**

Every file matches its recovered original checksum. PTF files total **3,980,952 bytes**; every individual file is below 768 KiB.

| File | Records | Graphics | Structure + pixels | Source rebuild | PSP hardware |
| --- | ---: | ---: | --- | --- | --- |
| Aero-Vista-Aurora.ptf | 75 | 74 | PASS | PASS | Pending |
| Candy-Glass.ptf | 75 | 74 | PASS | PASS | Pending |
| Eesti-Retro-80-90ndad.ptf | 75 | 74 | PASS | PASS | Pending |
| KP-Aero-Vibrant-Blue.ptf | 75 | 74 | PASS | PASS | Pending |
| Windows_XP_Autumn.ptf | 74 | 73 | PASS | PASS | Pending |
| Winter_Moscow.ptf | 74 | 73 | PASS | PASS | Pending |
| Ocean_Frutiger_Aqua.ptf | 74 | 73 | PASS | PASS | Pending |
| Mac_OS_9_Platinum.ptf | 74 | 73 | PASS | PASS | Pending |
| Mac_OS_X_10_Aqua.ptf | 74 | 73 | PASS | PASS | Pending |

## Fresh audit

- Magic, metadata encoding and lengths, product IDs, declared schema and version.
- Group/record boundaries, native slot IDs, reserved fields and complete file coverage.
- Stored/Deflate payload length, end-of-stream and zero padding.
- BMP24 dimensions and pixel extents.
- P8 swizzle, RGBA8888 palettes, tile alignment and required icon sizes.
- Icon colour limits, white focus glow and transparent vertical focus borders.
- Pixel equality between the Python reader and the unmodified imported PTF Studio parser/GIM reader; a separate JavaScript decoder handles BMP24.
- Pixel equality with every prepared source image.

Both comparisons cover **661 resources**. Only RGB channels under fully transparent pixels are normalised to zero. All visible colours and alpha bytes must match.

## Source rebuilding

All nine themes were rebuilt in a temporary directory and matched the originals byte for byte. The four older builds use supplied indexed PNGs. The newer five redraw icon artwork, re-encode GIM and build their containers from the supplied scripts and final wallpaper inputs.

Successful environment: Python **3.12.14**, Pillow **12.3.0**, NumPy **2.3.5**, Node.js **v24.19.0**. Other graphics-library environments are accepted only if they reproduce the original hashes.

## Evidence

- [Fresh audit JSON](../verification/latest.json), including metadata and per-resource raw/pixel SHA-256.
- [Rebuild results](../verification/rebuild.json) and [command log](../verification/rebuild.log).
- [Restored archive hashes and CRC tests](../verification/restoration.json).
- [Original Vista report](../verification/original/vista/strict-verification.json), [Glass reports](../verification/original/glass), [original five-theme results](../verification/original/classic-five/verification.json).
- [PTF hashes](../SHA256SUMS.txt) and [complete repository file hashes](../FILES_SHA256.txt). The latter excludes itself, caches and the temporary CI output.
- [User's desktop file-list image](../verification/evidence/original-theme-file-list.png), showing requested filenames and approximate sizes.

## Pending

Physical PSP application, display quality and suspend/resume are pending in [hardware-tests.json](../verification/hardware-tests.json). Desktop previews and the file list do not establish hardware results.

The Actions verification command passed locally, and the workflow YAML was checked. Its first remote GitHub run is pending repository publication.

~~~sh
python -m pip install -r requirements.txt
python tools/verify.py --output verification/ci-result.json
python tools/check_package.py
~~~

[Sony resource reference](https://cdn.us.playstation.com/pscomauth/groups/public/documents/webasset/ps_custom_theme-english_pp.pdf) · [PTF Studio](https://github.com/S1implyBlue/PTF-Studio)
