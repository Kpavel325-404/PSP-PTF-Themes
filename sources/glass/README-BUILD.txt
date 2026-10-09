SOURCE BUILD

For installation, only PSP/THEME/*.ptf is needed.

Build from already-prepared indexed resources:
  python -m pip install Pillow
  python source/build_themes.py

Optional full asset preparation (modern Node.js required):
  npm install sharp @napi-rs/canvas
  node source/prepare_assets.js
  node source/quantize_assets.js
  python source/build_themes.py

Independent verification and desktop previews:
  node source/verify_themes.js
  python source/validate_themes.py
  node source/render_themes.js

Paths are relative to this Source directory. No Sony executable, PSP SDK,
network connection or custom firmware plugin is needed for building.
PTF Studio source and adapters use GPL-3.0; see source/vendor/PTF-Studio-LICENSE.txt.
The original collection build scripts are also provided under GPL-3.0.
Generated wallpaper prompt specifications and original vector sources are
included so the collection can be edited and rebuilt.
