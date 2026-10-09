# Building and verifying

Canonical released files live in PSP/THEME. The combined builder uses temporary directories and leaves them intact.

## Requirements

Python 3.12, Pillow, NumPy and Node.js 22 are the tested setup. The DejaVu preview fonts and licence are bundled. Verification alone needs Pillow and Node.js.

~~~sh
python -m pip install -r requirements-build.txt
python tools/rebuild.py
~~~

The older four build from prepared indexed PNGs. The newer five redraw icons and encode GIM again. Generated wallpapers are included as final source images; rebuilding needs no image-generation service or original reference screenshots.

[rebuild.json](../verification/rebuild.json) records the successful library versions. Dependency ranges support verification elsewhere; rebuilt output must still match the archived bytes.

| Source directory | Themes | Build entry point |
| --- | --- | --- |
| sources/vista | Aero Vista — Aurora | build_theme.py |
| sources/glass | Candy, Eesti Retro, Vibrant Blue | source/build_themes.py |
| sources/classic-five | XP, Moscow, Ocean, Mac OS 9, Mac OS X | build_assets.py → gim_codec.js → build_ptf.py in source/ |

Source SVGs for Glass, prepared PNGs, GIMs and wallpaper inputs are retained. Optional original rendering/quantising scripts use Sharp and @napi-rs/canvas; the combined commands do not need them.

The historical five-theme verifier expects external LibPSPThemes files, which are not redistributed. The current combined verifier uses the bundled PTF Studio reader.

## Refresh previews and package

~~~sh
python tools/render_previews.py
python tools/verify.py --export-assets
python tools/rebuild.py
python tools/package.py --output ../PSP_9_Themes_GitHub_v1.0.zip
~~~

Rendering reads shipped PTF pixels. Packaging refreshes the all-file checksum list, checks first-party local Markdown links and PNGs, then compares every ZIP member with its local file and tests CRC.

The ZIP includes the entire PSP-PTF-Themes directory and .github configuration. For an intentional theme edit, update the theme version, prepared images, manifest checksum, previews, documentation and change log.
