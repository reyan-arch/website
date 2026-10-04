# Release checks

Validation record updated on 4 October 2026 (Asia/Kolkata) for the incremental update to the existing Framer website. Current Holafly publication restrictions supersede earlier numerical-copy approval. The baseline is `e886e2e836b5aee46cd10c2d00d70f3c1263cadb`. These checks cover the repository and local preview; they do not establish production delivery, search rankings or a site-wide accessibility certification.

## Routes, links and metadata

The current qualitative-copy [link audit](link-audit.json), generated at `2026-10-04T06:30:31.006187+00:00`, records:

| Check | Result |
|---|---|
| Local routes fetched by GET | 13; all returned HTTP 200 at `http://127.0.0.1:4173` |
| Sitemap entries | 12; draft privacy excluded |
| Internal link instances / distinct route connections | 721 / 129 |
| Missing pages, assets, fragments or publication-rule violations | 0 |
| Orphan routes / routes without contextual incoming links | 0 / 0 |
| Maximum navigation depth from home | 2 |
| Warnings | 4 inherited responsive H1 source-count warnings |

These are actual local-preview GET observations, not inferred production status. The audit checks public text, accessible labels, metadata, JSON-LD, enhancement output and Framer handover string values for withdrawn case claims. Framer graph integers are references and are not treated as campaign figures. All current confidentiality checks pass. The private historical source remains unchanged and publication approval is disabled in the ledger.

The retained baseline has responsive H1 source variants on Home, Contact, Resources and Work. Source counts alone do not prove visible duplicates or post-hydration accessibility. Remote CDN assets and external destinations are outside the local source audit. Browser hydration and the signed-in hosting build remain separate checks.

## Preservation and current content permission

The original named sections, body-media references and source frame are retained on the core routes. The home Resource section and Resources body/form remain protected, apart from authorised brand and footer-credit updates. Resource content and fulfilment remain excluded from this update.

The latest user direction withdraws Holafly numerical results from the public website. Public copy now describes creator selection, continuous sourcing, advance planning, refreshed briefs and repeat collaboration. It includes no quantified result, reporting-period comparison, creator metric or spelled-out programme count. Titles, descriptions, structured data and responsive variants follow the same qualitative scope.

Historical evidence in `framer-export/cms/Case_Studies.json` stays unchanged. The metric ledger is retained for provenance with every publication/approval flag set to `false`; historical reproduction checks are superseded by public-confidentiality checks. No withdrawn values are repeated in this document or the refreshed audit report. The latest public-copy and handover-string checks pass.

The qualitative case retains the existing results, measurement, market-context and creative-example anchors. Campaign operations, always-on programme and hospitality/travel pages remain clearly labelled illustrative methodology examples. No client-result claims are attached to those examples.

The existing privacy draft remains `noindex,follow` pending approved wording. Sector planning content does not imply offices, unverified city results or unconfirmed service capabilities.

## Brand and contrast

The logo is native SVG using the supplied screenshot's sampled red `#ff3436`, blue `#0037fb` and ink `#191c1f`. The three-figure geometry follows the existing IRG People Mark. Header/footer variants retain vector wordmark paths. Following the user's final direction, logo backing tiles were removed: dark variants retain the original ink fill with a fine paper-colored outline behind the center figure. The favicon and regenerated Apple touch icon are transparent. The social preview retains its full paper-colored design canvas without a separate logo backing block.

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
- The refreshed Services additions were checked at 1440×900 and 375×812. Desktop sections use the original 96px/40px spacing, 44px heading preset and 32px paper-card frame. Research panels span the full 1280px inner grid. Mobile sections use 64px/20px spacing and 30px headings. Neither inspected viewport has horizontal overflow; sector deep links position their content below the navigation. All six expandable checklists remain; the first opens successfully on mobile.
- The shortened Services opening retains its operating-model and Travel/Hospitality/Lifestyle links after hydration. Home's carousel and Work's featured card show qualitative Holafly copy after hydration; Work's original metric slots now describe creator fit, delivery and learning. The footer retains the direct leadscorer.co backlink.
- Five publication regression tests passed using synthetic data: explicit metric permissions, page-level permissions, prohibited metric components, stale numerical copy before generation, and allowed qualitative process copy.
- The introduction uses a clear SVG with a source-enforced 1.2-second maximum, no scroll lock and no pointer-event gate. Source review confirms skips for reduced-motion preference, hash/deep entry and other stated conditions. Reduced motion was not tested using operating-system emulation.
- The preview server injects an early capture-phase submit guard into local HTML and serves all responses with `Cache-Control: no-store`. Isolated server and simulated submit checks confirm no preview submission is forwarded to the original handlers; production assets are unchanged.
- Four Node lead-capture tests passed: unchanged Project enquiry recipient/field names without timer-based success, preserved excluded Resource confirmation timing, honeypot rejection and invalid-email rejection. Tests use simulated/intercepted delivery; no live enquiry was submitted.
- The final rerun passed syntax checks for all three shipped JavaScript files, Python script compilation and all four Node tests. A final Wrangler deployment dry-run passed after the transparent-logo changes and read all 36 served asset files. A dry-run does not publish the website.

The existing Make/Sheet recipient is unchanged. Beacon/no-cors delivery remains best effort and cannot establish receipt in the browser. Contact feedback relies on Framer's delivery feedback; Resource confirmation behavior remains the original excluded flow. Live form delivery and resource fulfilment were not tested. No production deployment was performed as part of these checks, and no Lighthouse score, field-performance result or ranking improvement is claimed.

## Hosting diagnosis

The signed-in IRG Cloudflare dashboard confirms the **website** Worker is connected to **reyan-arch/website**, with `main` as the production branch and `irgmedia.org` attached for Production and Preview. The failed branch build's actual log identifies a missing top-level `previews` block required by its `npx wrangler preview` command. The documented empty block was added without changing asset paths or production deployment settings; a Wrangler deployment dry-run passes. A successful build of the new commit is still required to establish hosted preview availability.

The [README](../README.md#rollback) records rollback by reverting the update/merge commit on `main`. Existing repository hosting automation may deploy a subsequent push or merge independently of these local checks.
