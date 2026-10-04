# Release checks

Validation record updated on 4 October 2026 (Asia/Kolkata) for the incremental update to the existing Framer website. Current Holafly publication restrictions supersede earlier numerical-copy approval. The baseline is `e886e2e836b5aee46cd10c2d00d70f3c1263cadb`. These checks cover the repository and local preview; they do not establish production delivery, search rankings or a site-wide accessibility certification.

## Routes, links and metadata

The current qualitative-copy [link audit](link-audit.json), generated at `2026-10-04T11:53:30.843715+00:00`, records:

| Check | Result |
|---|---|
| Local routes fetched by GET | 13; all returned HTTP 200 at `http://127.0.0.1:4173` |
| Sitemap entries | 12; draft privacy excluded |
| Internal link instances / distinct route connections | 827 / 129 |
| Missing pages, assets, fragments or publication-rule violations | 0 |
| Orphan routes / routes without contextual incoming links | 0 / 0 |
| Maximum navigation depth from home | 2 |
| Warnings | 4 inherited responsive H1 source-count warnings |

These are actual local-preview GET observations, not inferred production status. The audit checks public text, accessible labels, metadata, JSON-LD, enhancement output and Framer handover string values for withdrawn case claims. Framer graph integers are references and are not treated as campaign figures. All current confidentiality checks pass. The private historical source remains unchanged and publication approval is disabled in the ledger.

The subsequent image-card refinement preserves the two original Home photographic panels. Each responsive variant contains one native, full-panel link to its existing Creator Access or Campaign Operations destination; image labels remain white and unlined. Source checks verify unchanged media/copy, idempotence, no nested links and retained contextual links outside the panels. Browser review confirms exact white labels, matching link/panel bounds and no horizontal overflow at desktop and 375px mobile sizes, including after breakpoint hydration. Pointer activation reaches Creator Access; keyboard Enter reaches Campaign Operations. The full-panel links do not extend into adjacent content.

The three Services sector headings now name influencer marketing for travel, hospitality and lifestyle; their concise introductions describe finding influencers for each niche. Home and Services have distinct model-backed titles and descriptions. Organization/WebSite use the consistent IRG Media identity and IRG alias; three Service nodes describe the existing sector anchors, with the same organization as provider. This is standard crawlable content and entity markup, not a ranking guarantee or special AI-search submission. All existing links are retained. The additional 18-reference review is documented in [benchmark-research.md](benchmark-research.md). The existing six Home FAQ questions now contain concise source-readable answers and 11 contextual links, with matching semantic Question/Answer records. Original outer frames and non-FAQ content are preserved.

The retained baseline has responsive H1 source variants on Home, Contact, Resources and Work. Source counts alone do not prove visible duplicates or post-hydration accessibility. Remote CDN assets and external destinations are outside the local source audit. Browser hydration and the signed-in hosting build remain separate checks.

## Preservation and current content permission

The original named sections, body-media references and source frame are retained on the core routes. The home Resource section and Resources body/form remain protected, apart from authorised brand, footer-credit and subsequent CTA presentation updates. The latest user request explicitly includes the Resource Send enquiry button: only its casing, styling and interaction presentation change. The existing Home Explore the resource CTA also receives the shared button presentation without changing its protected raw section HTML. Resource content, fields, delivery and fulfilment remain excluded from this update.

The latest user direction withdraws Holafly numerical results from the public website. Public copy now describes creator selection, continuous sourcing, advance planning, refreshed briefs and repeat collaboration. It includes no quantified result, reporting-period comparison, creator metric or spelled-out programme count. Titles, descriptions, structured data and responsive variants follow the same qualitative scope.

Historical evidence in `framer-export/cms/Case_Studies.json` stays unchanged. The metric ledger is retained for provenance with every publication/approval flag set to `false`; historical reproduction checks are superseded by public-confidentiality checks. No withdrawn values are repeated in this document or the refreshed audit report. The latest public-copy and handover-string checks pass.

The qualitative case retains the existing results, measurement, market-context and creative-example anchors. Campaign operations, always-on programme and hospitality/travel pages remain clearly labelled illustrative methodology examples. No client-result claims are attached to those examples.

The existing privacy draft remains `noindex,follow` pending approved wording. Sector planning content does not imply offices, unverified city results or unconfirmed service capabilities.

## Brand and contrast

The logo is native SVG using the supplied screenshot's sampled red `#ff3436`, blue `#0037fb` and ink `#191c1f`. The three-figure geometry follows the existing IRG People Mark. Header/footer variants retain vector wordmark paths. Following the user's final direction, logo backing tiles were removed: dark variants retain the original ink fill with no background tile or outline around the center figure, as requested in the subsequent logo review. The favicon and regenerated Apple touch icon are transparent. The social preview retains its full paper-colored design canvas without a separate logo backing block.

The local BDO Grotesk binary preserves the original Framer asset byte-for-byte, SHA-256 `40ddb4a8fbd717aea3c8bb4d0113d45f03218730228ef9400bdb6fdec98125d7`. Its embedded license and the [official BDO project](https://github.com/LCTipografi/BDO-Grotesk) were reviewed for SIL OFL 1.1 redistribution. Inter is also supplied with its [official OFL](https://github.com/rsms/inter). Copyright notices and complete license files are retained in `site/assets/`.

The user's latest direction requires the exact logo fills for red, blue and black text, including dark contexts. The [brand ledger](../content/brand.json) records raw foreground/background pairs using WCAG relative luminance and distinguishes normal- and large-text thresholds in [WCAG 2.2 SC 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html). It does not claim every raw pair passes. Small red labels use ink support surfaces. The user subsequently rejected white backgrounds and outlines on blue text; blue text now uses the plain exact fill and native link decoration. Blue on dark surfaces has the documented low-contrast raw pair below; this is not a site-wide AA claim.

| Text / surface | Measured ratio, displayed rounded |
|---|---|
| Ink / white; ink / paper | 17.11:1; 15.56:1 |
| Exact red / white; exact red / paper | 3.62:1; 3.29:1 (large text only) |
| Blue / white; blue / paper | 7.14:1; 6.50:1 |
| White / action red; white / blue; white / ink | 5.30:1; 7.14:1; 17.11:1 |
| Exact red / ink (small-label support) | 4.72:1 |
| Exact blue / ink (unsupported raw pair) | 2.40:1 (fails normal and large text) |
| Exact blue / paper (raw reference pair) | 6.50:1 |

For `linear-gradient(120deg,#d1212b 0%,#853064 48%,#0037fb 100%)`, piecewise sRGB interpolation was sampled at all 1001 positions `t=i/1000`, including the three stops. White-text contrast has a measured minimum of **5.298363301552297:1** at the red start, and every sampled position exceeds 4.5:1. The calculation uses the sRGB transfer-function breakpoint 0.04045, luminance weights 0.2126/0.7152/0.0722, and `(Llighter+0.05)/(Ldarker+0.05)`. These token and gradient checks do not measure every possible overlay on photography, antialiasing or a browser's alternative gradient interpolation space.

## Local behavior and implementation checks

- Browser review at 1440×900 and 375×812 checked the retained photographic hero and layout, clear vector identity, refined buttons and absence of horizontal overflow in the inspected views. These are desktop-browser viewport checks, not physical-device tests.
- The core mobile navigation opens/closes and Escape dismissal was verified in the browser. The native Work-detail menu passed its final 375×812 recheck: Escape closes it and restores focus to the `Open navigation` summary. Its visible links use 24px BDO text and at least 55px height; that view has no horizontal overflow.
- The refreshed Services additions were checked at 1440×900 and 375×812. The opening uses a bounded paper card with the original 44px desktop/30px mobile section-heading preset, 40px card inset and 32px corners. Each sector separates the narrative and practical brief into paper cards; research has its own full-width card. Sector chapter headings use 26px desktop/24px mobile BDO, with a smaller subheading hierarchy. Outer spacing is 64px with the existing responsive gutters. A further 894px check confirms the sector navigation no longer inherits Framer’s clipped rounded navigation container. Neither inspected viewport has horizontal overflow; sector deep links position their content below the navigation. All six expandable checklists remain; the first opens successfully on mobile.
- All 20 original gradient controls and 12 static Work CTAs share the scoped presentation rules: 48px minimum height, 16px corners, 14px BDO sentence-case labels, restrained hover gradient movement/lift, press reset, focus outline and disabled/reduced-motion handling. Resource keyboard focus was verified with an exact-blue outline; no form was submitted.
- The shortened Services opening retains its operating-model and Travel/Hospitality/Lifestyle links after hydration. Home's carousel and Work's featured card show qualitative Holafly copy after hydration; Work's original metric slots now describe creator fit, delivery and learning. The footer retains the direct leadscorer.co backlink.
- Five publication regression tests passed using synthetic data: explicit metric permissions, page-level permissions, prohibited metric components, stale numerical copy before generation, and allowed qualitative process copy.
- The introduction reveals the identical sharp SVG from left to right over a faint grayscale copy. Only an explicit homepage refresh shows it; normal visits, history restoration, navigation and other routes skip it. It has a source-enforced 1.2-second maximum, no scroll lock and no pointer-event gate. Unavailable or slow images never activate the overlay. Reduced motion, hash/deep entry, restored scroll and hidden documents skip it; interaction dismisses it. Five Node behavior tests cover navigation gating, lifetime, image failure and CTA label preservation. Reduced motion was not tested using operating-system emulation.
- The preview server injects an early capture-phase submit guard into local HTML and serves all responses with `Cache-Control: no-store`. Isolated server and simulated submit checks confirm no preview submission is forwarded to the original handlers; production assets are unchanged.
- Four Node lead-capture tests passed: unchanged Project enquiry recipient/field names without timer-based success, preserved excluded Resource confirmation timing, honeypot rejection and invalid-email rejection. Tests use simulated/intercepted delivery; no live enquiry was submitted.
- The current rerun passed the five homepage-reveal/CTA behavior tests, five publication tests, three FAQ source/preservation regressions, two FAQ hydration-state regressions, shipped enhancement JavaScript syntax and Python compilation. Browser checks confirm six visible native questions, successful pointer and keyboard toggling, matching 20px desktop/18px mobile typography and no overflow at the inspected viewports. Card corner arrows now use 18px exact-blue SVGs with rounded strokes and reduced-motion-aware hover handling. All 13 HTML routes reproduce identically after regeneration. The earlier unchanged lead-capture checks remain recorded above. A final Wrangler deployment dry-run passed after the transparent-logo changes and read all 36 served asset files. A dry-run does not publish the website.

The existing Make/Sheet recipient is unchanged. Beacon/no-cors delivery remains best effort and cannot establish receipt in the browser. Contact feedback relies on Framer's delivery feedback; Resource confirmation behavior remains the original excluded flow. Live form delivery and resource fulfilment were not tested. The prior releases were subsequently published through the existing GitHub/Cloudflare integration; their production checks are recorded below. The current Calendly/image release still requires its own successful hosting check. No Lighthouse score, field-performance result or ranking improvement is claimed.

## Calendly and linked photography

The supplied Discovery Call embed is now an additive section at `/contact#book-a-call`. Start a project actions point directly to that section. The original Project enquiry form panel is byte-for-byte preserved by the scheduling helper, and the existing email links remain available. Contact alone loads Calendly’s official asynchronous widget script, with one widget/iframe and a separate-window fallback. Browser review confirms the actual Reyan Gada / Discovery Call / 30 min calendar and available dates render. No date, booking or enquiry was submitted.

Public photographs now have native destinations mapped to their context: creator access, campaign operations, performance learning, sector briefs, methodology, work or booking. Multi-image compositions and repeated galleries share one image-area link; existing Work/carousel links retain their destinations. Source regressions cover more than 200 photo instances, unchanged image nodes, no nested anchors and idempotence. The protected Resource section source remains intact; its existing photo receives an additive runtime link.

Inspected Home image panels have matching photo/link bounds, white captions, a 3px lift and an image scale of 1.018 on hover. Linked galleries pause while hovered or keyboard-focused. Motion respects reduced-motion preferences, and keyboard links have visible focus. Browser checks confirm all rendered Home photographs have destinations and the Start a project button reaches the booking anchor.

A responsive Framer ownership error was also fixed: headline colouring retains the original React text nodes instead of replacing them. Contact remained rendered while switching 942→1440→375→942 widths, with exactly one booking iframe and no horizontal overflow at the inspected widths. Sixteen Python source/preservation/publication regressions and thirteen Node behaviour tests passed, as did JavaScript syntax checks and the local route audit.

## Hosting diagnosis

The signed-in IRG Cloudflare dashboard confirms the **website** Worker is connected to **reyan-arch/website**, with `main` as the production branch and `irgmedia.org` attached for Production and Preview. The failed branch build's actual log identifies a missing top-level `previews` block required by its `npx wrangler preview` command. The documented empty block was added without changing asset paths or production deployment settings; a Wrangler deployment dry-run passes.

Cloudflare build `248fee90-307e-46fe-9e36-be0bf10c9ad9` succeeds for commit `033ebbd34d2320d745eed37c5b6d54aa4590cc4a`. The log confirms static asset upload and returns the [branch preview](https://codex-irg-brand-and-enterprise-update.irgmedia.org) and unique deployment URL. Browser checks of hosted Services and Holafly confirm the shortened copy, sector anchors, original frame, correct canonical, and absence of case metric components/results tables. Hosted desktop and mobile Services views have no horizontal overflow. No hosted forms were submitted. This confirms a branch Preview deployment, not publication to the production apex.

The [README](../README.md#rollback) records rollback by reverting the update/merge commit on `main`. Existing repository hosting automation may deploy a subsequent push or merge independently of these local checks.

The earlier production releases are merged in [PR #1](https://github.com/reyan-arch/website/pull/1) and [PR #2](https://github.com/reyan-arch/website/pull/2). Their respective production merge commits are `9b49ba471263475a2e6c8e5daeb258a2cbf286e7` and `6c01b4b61e56261e4a01a7c54f6ca3f007e82ef6`, with successful Workers Builds checks. Calendly and the broader photo interactions belong to the subsequent release and must be verified independently before reporting them live.
