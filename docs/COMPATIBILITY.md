# Compatibility / Совместимость

| Environment | Intended use | Physical test evidence |
| --- | --- | --- |
| PSP-3000 / FW 6.61 | Primary target | Pending |
| PSP-3000 / 6.61 with ARK | Primary target; normal XMB theme menu | Pending |
| PSP-1000 / 2000 / Go / Street | Model-dependent PTF menu coverage | Not tested |
| Other firmware releases | Declared resource schema is 6.20 | Not tested |

All files are PTF v1. They define supported XMB icons, focus graphics, wallpaper and theme colour. Menu visibility depends on model and region; TV or model-specific items may be absent.

The ordinary PTF mechanism uses the system theme settings. An active CTF theme or CXMB plugin can affect the displayed interface; resolve that configuration if it conflicts with applying a PTF.

The original slot sets are preserved. The four older themes have nine category resources, including slot 0; the newer five have eight category resources. All nine themes contain 29 first-level body/focus pairs and two second-level pairs.

Wallpapers are 480 × 272; PTF selection images are 300 × 170. Desktop preview fonts and sample status text differ from a live console.

Record real-console observations in [hardware-tests.json](../verification/hardware-tests.json), using the [hardware report template](../.github/ISSUE_TEMPLATE/hardware-test.md).

[Sony format reference](https://cdn.us.playstation.com/pscomauth/groups/public/documents/webasset/ps_custom_theme-english_pp.pdf)
