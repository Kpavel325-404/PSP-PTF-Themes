CLASSIC FIVE — SOURCE BUILD

From sources/classic-five:
  python -m pip install Pillow numpy
  python source/build_assets.py
  node source/gim_codec.js
  python source/build_ptf.py

Final wallpaper inputs: assets/<theme>/wallpaper_source.*
Preview fonts/notices: vendor/fonts
Original visual reference screenshots are not required or redistributed.

The collection-root tools/rebuild.py builds all nine in temporary directories.
The current combined verifier is tools/verify.py.
Historical verify_ptf.py expects the unbundled external LibPSPThemes files.
See collection LICENSE_SCOPE.md for code and artwork scopes.
