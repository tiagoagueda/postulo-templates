# Assets

Every file this plugin ships that is not code or a template, with where it came from and the
licence it is under. A template names a file by its path under `src/postulo_templates/`
(`{% theme_asset "assets/icons/phone.svg" %}`); Postulo writes it into the document, so a
drawn PDF and its preview carry it and nothing is fetched.

A test (`tests/test_assets.py`) fails for a file under `assets/` that is not listed here, for
a font without its licence beside it, and for an icon that sets a colour of its own.

## Icons

All are drawn for this plugin as outlines in `currentColor`, 16 x 16, and are under the
plugin's own licence (AGPL-3.0-or-later). They take their colour from the text around them,
so they print in black and white.

| File | Used by | Source |
| --- | --- | --- |
| `assets/icons/location.svg` | `europass` | Drawn here |
| `assets/icons/phone.svg` | `europass` | Drawn here |
| `assets/icons/email.svg` | `europass` | Drawn here |
| `assets/icons/web.svg` | `europass` | Drawn here |
| `assets/icons/message.svg` | `europass` | Drawn here |
| `assets/icons/identifier.svg` | `europass` | Drawn here |

## Fonts

| File | Used by | Draws | Source | Licence |
| --- | --- | --- | --- | --- |
| `assets/fonts/Arimo-Regular.woff2` | `europass` | Latin, Greek, Cyrillic | Arimo by Steve Matteson, Google Fonts (<https://github.com/googlefonts/arimo>, the `ofl/arimo` directory of <https://github.com/google/fonts>) | SIL Open Font License 1.1, in `assets/fonts/Arimo-OFL.txt` |

The font is the regular weight of the variable font, instanced at weight 400 and subset to
Basic Latin, Latin-1, Latin Extended-A and -B, Latin Extended Additional, Greek, Cyrillic,
general punctuation and the euro sign, then written as WOFF2 (about 44 kB, which every
document drawn in the theme carries). Only the style the theme uses is shipped. The licence
file names no Reserved Font Name, so the subset keeps the name Arimo; the OFL allows
embedding and redistribution, and the licence travels beside the file.

Arimo is metric-compatible with Arial, which the Europass template is set in and which is
not redistributable.
