# Third-party components

Application code, embedded translation resources and fonts came from the user's ZIP. No new license for that application code is asserted here.

Exact versions, npm source URLs, verified package SHA-512 integrity and bundle SHA-256 hashes are recorded in [vendor/manifest.json](vendor/manifest.json). Refresh with `python3 tools/vendor.py`. License files shipped by the packages are retained in `vendor/`.

| Package | Version | License |
|---|---|---|
| xlsx | 0.18.5 | Apache-2.0 |
| html-docx-js | 0.3.1 | MIT |
| jszip | 3.10.1 | MIT or GPL-3.0-or-later; MIT use applies here |
| @cantoo/pdf-lib | 2.11.1 | MIT |
| @pdf-lib/fontkit | 1.1.1 | MIT; published README/package.json retained, package omits a separate LICENSE |
| pdfjs-dist | 3.11.174 | Apache-2.0 |
| diff | 5.2.0 | BSD-3-Clause |
| docx-preview | 0.3.3 | Apache-2.0 |

The HTML embeds Be Vietnam Pro and Tinos fonts under SIL Open Font License 1.1. The original reduced Tinos fonts have been replaced with complete upstream Regular/Bold fonts so arrows have actual glyph outlines. Pinned upstream URLs and SHA-256 checksums are in `vendor/pdf-fonts.json`; reproduce with `python3 tools/update_pdf_fonts.py`. License notices are retained in `vendor/bevietnampro-OFL.txt` and `vendor/tinos-OFL.txt`; Tinos identifies the 2026 Tinos Project Authors. PDF.js may fetch auxiliary assets from its pinned CDN when needed.
