# Release checks

Validation recorded on 4 October 2026 (Asia/Kolkata) for the incremental update to the existing Framer website. The baseline is `e886e2e836b5aee46cd10c2d00d70f3c1263cadb`. These checks cover the repository and local preview; they do not establish production delivery, search rankings or a site-wide accessibility certification.

## Routes, links and metadata

The final [link audit](link-audit.json), generated at `2026-10-03T19:07:40.290579+00:00`, records:

| Check | Result |
|---|---|
| Local routes fetched by GET | 13; all returned HTTP 200 at `http://127.0.0.1:4173` |
| Sitemap entries | 12; the draft privacy route is excluded |
| Internal link instances / distinct route edges | 717 / 129 |
| Missing local pages, assets or fragment targets | 0 audit errors |
| Orphan routes / routes without contextual incoming links | 0 / 0 |
| Maximum navigation depth from home | 2 |
| Warnings | 4 inherited responsive H1 source-count warnings |

The warnings concern `/` (4 source H1 variants), `/contact` (3), `/resources` (3) and `/work` (3). Those counts match the original source. Source counts alone do not prove visible duplicate headings or post-hydration accessibility. The report also checks unique page titles/descriptions, canonicals, sitemap eligibility and local fragment targets. Its HTTP observations are local-preview responses, not inferred production status. External destinations and remote CDN assets were not fetched by this audit.

## Preservation and content provenance

- The audit retains each original named section, body-media reference and source frame on the nine core routes. This is a source comparison; browser rendering was checked separately.
- The home Resource section passes `protectedResourceSectionExact: true`. `/resources` retains its two original sections, body text apart from the authorized footer credit, and the original form label, method, field names, input types and required flags. Its resource content and fulfilment flow remain excluded from this update.
- The immutable `framer-export/cms/Case_Studies.json` source matches SHA-256 `fc6bfb8d4bb8970b6f42c89c6101ab8bb4405a59ab77b6ae1df8c34f91bbfcf7`. The public August market table exactly matches that source.
- All 21 Holafly metric records retain their source and unaudited caveat. Six snapshot values, twelve August market values and three creator examples pass their source-preservation checks. Required period, unit and available baseline text is retained. These checks establish faithful reproduction, not independent verification of campaign performance.
- Campaign operations, always-on programme and hospitality/travel detail pages visibly identify themselves as illustrative methodology examples and do not claim client results.

| Snapshot metric | Preserved value and context |
|---|---|
| Organic views | 84.3M; January–August 2026 |
| Reported reach | 78.8M; January–August 2026 |
| Creator partnerships | 161; January–August 2026 |
| Content pieces | 920+; January–August 2026 |
| Cost per thousand reached reduction | 56%; by July 2026, versus programme start |
| Monthly organic view increase | 169%; April–July 2026, versus April 2026 monthly organic views |

The existing privacy draft remains `noindex,follow` pending approved policy wording. Sector planning content does not imply new offices, unverified city results or unconfirmed service capabilities.

## Brand and contrast

The logo is native SVG using the supplied screenshot's sampled red `#ff3436`, blue `#0037fb` and ink `#191c1f`. The three-figure geometry follows the existing IRG People Mark. Header/footer variants retain vector wordmark paths; dark variants place the original colors on a white backing tile. Favicon, Apple touch icon and social preview are derived from those assets.

The local BDO Grotesk binary preserves the original Framer asset byte-for-byte, SHA-256 `40ddb4a8fbd717aea3c8bb4d0113d45f03218730228ef9400bdb6fdec98125d7`. Its embedded license and the [official BDO project](https://github.com/LCTipografi/BDO-Grotesk) were reviewed for SIL OFL 1.1 redistribution. Inter is also supplied with its [official OFL](https://github.com/rsms/inter). Copyright notices and complete license files are retained in `site/assets/`.

All 14 documented foreground/background pairs were recomputed from the exact hexadecimal values in [brand.json](../content/brand.json) using WCAG relative luminance. Each exceeds the unrounded 4.5:1 threshold for ordinary text in [WCAG 2.2 SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).

| Text / surface | Measured ratio, displayed rounded |
|---|---|
| Ink / white; ink / paper | 17.11:1; 15.56:1 |
| Muted / white; muted / paper | 7.04:1; 6.40:1 |
| Deep red / white; deep red / paper | 5.62:1; 5.11:1 |
| Blue / white; blue / paper | 7.14:1; 6.50:1 |
| White / action red; white / blue; white / ink | 5.30:1; 7.14:1; 17.11:1 |
| Inverse red / ink; inverse blue / ink; inverse muted / ink | 6.66:1; 7.39:1; 10.47:1 |

For `linear-gradient(120deg,#d1212b 0%,#853064 48%,#0037fb 100%)`, piecewise sRGB interpolation was sampled at all 1001 positions `t=i/1000`, including the three stops. White-text contrast has a measured minimum of **5.298363301552297:1** at the red start, and every sampled position exceeds 4.5:1. The calculation uses the sRGB transfer-function breakpoint 0.04045, luminance weights 0.2126/0.7152/0.0722, and `(Llighter+0.05)/(Ldarker+0.05)`. These token and gradient checks do not measure every possible overlay on photography, antialiasing or a browser's alternative gradient interpolation space.

## Local behavior and implementation checks

- Browser review at 1440×900 and 375×812 checked the retained photographic hero and layout, clear vector identity, refined buttons and absence of horizontal overflow in the inspected views. These are desktop-browser viewport checks, not physical-device tests.
- The core mobile navigation opens/closes and Escape dismissal was verified in the browser. The native Work-detail menu passed its final 375×812 recheck: Escape closes it and restores focus to the `Open navigation` summary. Its visible links use 24px BDO text and at least 55px height; that view has no horizontal overflow.
- On the desktop Services page, each sector's research block is a 1360px direct child of its sector layout after reload. Six FAQ accordion entries are present; the first was toggled successfully in the browser.
- The introduction uses a clear SVG with a source-enforced 1.2-second maximum, no scroll lock and no pointer-event gate. Source review confirms skips for reduced-motion preference, hash/deep entry and other stated conditions. Reduced motion was not tested using operating-system emulation.
- The preview server injects an early capture-phase submit guard into local HTML and serves all responses with `Cache-Control: no-store`. Isolated server and simulated submit checks confirm no preview submission is forwarded to the original handlers; production assets are unchanged.
- Four Node lead-capture tests passed: unchanged Project enquiry recipient/field names without timer-based success, preserved excluded Resource confirmation timing, honeypot rejection and invalid-email rejection. Tests use simulated/intercepted delivery; no live enquiry was submitted.
- The final rerun passed syntax checks for all three shipped JavaScript files, Python script compilation and all four Node tests. A Wrangler deployment dry-run also passed earlier in this validation session; it was not rerun after the last asset-only changes. A dry-run does not publish the website.

The existing Make/Sheet recipient is unchanged. Beacon/no-cors delivery remains best effort and cannot establish receipt in the browser. Contact feedback relies on Framer's delivery feedback; Resource confirmation behavior remains the original excluded flow. Live form delivery and resource fulfilment were not tested. No production deployment was performed as part of these checks, and no Lighthouse score, field-performance result or ranking improvement is claimed.

The [README](../README.md#rollback) records rollback by reverting the update/merge commit on `main`. Existing repository hosting automation may deploy a subsequent push or merge independently of these local checks.
