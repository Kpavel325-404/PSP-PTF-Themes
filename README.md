# PSP PTF Themes — KP Collection

[Русский](README_RU.md) · [Install](docs/INSTALL_EN.md) · [Verification](docs/VERIFICATION.md) · [Build](docs/BUILD.md) · [Credits](CREDITS.md)

Nine native PSP themes inspired by classic operating systems, Frutiger glass aesthetics and winter scenery. Curated for **Kpavel325-404**.

![All nine themes, rendered from the actual PTF graphics](assets/gallery.png)

**9 original PTF files · 3.80 MiB total · 661 checked graphics · byte-identical source builds**

Desktop verification passed. **Physical PSP testing is pending.** Previews are computer-rendered XMB illustrations with substituted fonts and sample status information.

## Choose a theme

The theme name opens its PTF file. PNG opens the native desktop preview.

| Theme / PTF | Style | Size | Preview |
| --- | --- | ---: | --- |
| [Aero Vista — Aurora](PSP/THEME/Aero-Vista-Aurora.ptf) | Aurora · original Vista icon artwork | 449.9 KiB | [PNG](assets/previews/vista-aurora.png) |
| [Candy Glass](PSP/THEME/Candy-Glass.ptf) | Mint · peach · lavender glass | 460.3 KiB | [PNG](assets/previews/candy-glass.png) |
| [Eesti Retro — 80–90ndad](PSP/THEME/Eesti-Retro-80-90ndad.ptf) | Amber · cassette · Tallinn | 402.4 KiB | [PNG](assets/previews/eesti-retro.png) |
| [KP Aero — Vibrant Blue](PSP/THEME/KP-Aero-Vibrant-Blue.ptf) | Cobalt ribbons · silver · soft glow | 424.9 KiB | [PNG](assets/previews/vibrant-blue.png) |
| [Windows XP — Autumn](PSP/THEME/Windows_XP_Autumn.ptf) | Golden leaves · classic XP colours | 608.9 KiB | [PNG](assets/previews/xp-autumn.png) |
| [Winter Moscow](PSP/THEME/Winter_Moscow.ptf) | Snow · Red Square · frosted blue | 474.5 KiB | [PNG](assets/previews/winter-moscow.png) |
| [Ocean — Frutiger Aqua](PSP/THEME/Ocean_Frutiger_Aqua.ptf) | Water · bubbles · glass city | 559.7 KiB | [PNG](assets/previews/ocean-aqua.png) |
| [Mac OS 9 — Platinum](PSP/THEME/Mac_OS_9_Platinum.ptf) | Classic gray controls · purple Finder pattern | 146.9 KiB | [PNG](assets/previews/mac-os9.png) |
| [Mac OS X 10 — Aqua](PSP/THEME/Mac_OS_X_10_Aqua.ptf) | Early Aqua · blue waves · glossy icons | 360.0 KiB | [PNG](assets/previews/mac-osx.png) |

## Install

Copy PTF files from PSP/THEME to the same folder on your PSP Memory Stick. Apply one through the built-in XMB theme menu. Follow the [short guide](docs/INSTALL_EN.md).

Primary target: **PSP-3000 / system software 6.61**, including an ARK installation. Each file declares the 6.20 resource schema. The [compatibility table](docs/COMPATIBILITY.md) records testing status.

## Included

- Native themes, decoded wallpaper PNGs, individual previews, a gallery and social preview.
- Russian and English documentation, release notes and artwork attribution.
- Source assets and builders for all three original source families.
- Historical reports, a fresh audit, SHA-256 lists and recorded source rebuild results.
- GitHub Actions configuration and issue templates for bugs and physical-console reports.

Repeat the desktop checks with Python 3.12 and Node.js 22:

~~~sh
python -m pip install -r requirements.txt
python tools/verify.py --output verification/ci-result.json
python tools/check_package.py
~~~

## Evidence

[Detailed report](docs/VERIFICATION.md) · [Full audit JSON](verification/latest.json) · [Rebuild results](verification/rebuild.json) · [PTF hashes](SHA256SUMS.txt) · [All-file hashes](FILES_SHA256.txt) · [Hardware result slots](verification/hardware-tests.json)

The Actions commands were run locally. **The first remote GitHub Actions run is pending publication.**

## Attribution

This fan collection contains mixed artwork sources. GPL-3.0 applies to build and verification code; Microsoft artwork, supplied photos, generated images and fonts have separate provenance. See [CREDITS.md](CREDITS.md) and [LICENSE_SCOPE.md](LICENSE_SCOPE.md).

[Publish the prepared directory](docs/PUBLISH_GITHUB.md) · [Contribute or report a test](CONTRIBUTING.md) · [Changelog](CHANGELOG.md)
