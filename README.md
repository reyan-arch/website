# IRG Media — website

Static mirror of the existing IRG Media site built in Framer, with bounded brand, content and search improvements. The original core layouts, photo hero, responsive navigation and form integrations are preserved. Deploys to Cloudflare Workers from **reyan-arch/website**.

## Layout

| Path | What it is |
|---|---|
| `site/` | The rendered site: one HTML file per page (`index.html`, `services.html`, `work/campaign-operations.html` …), `sitemap.xml`, `robots.txt`. This is what Cloudflare serves. |
| `framer-export/PAGES.md` | Page copy pulled from the Framer canvas (home page; other pages' text is in their HTML). |
| `framer-export/pages/` | One JSON per page: path, draft flag, component instances, text layers. |
| `framer-export/cms/` | CMS collections with fields + items: `Case_Studies.json` (4 items), `Resources.json` (1 item). |
| `framer-export/code/` | Code components / overrides (`.tsx`) from the Framer project. |
| `framer-export/project.json`, `redirects.json`, `locales.json`, `publish_info.json` | Project metadata. |
| `wrangler.jsonc` | Cloudflare config: serves `site/` as static assets via `npx wrangler deploy`. |
| `content/site.json` | Editable copy, historical metric ledger with publication gates, immutable source references and contextual relationships. |
| `content/contact-booking.html` / `content/image-links.json` | Additive Contact scheduling and contextual native destinations for existing photos. |
| `content/services-markets.html` | Travel, Hospitality and Lifestyle scroll sections inside Services, including sourced planning references. |
| `site/assets/` | Local vector identity, favicon, fonts and scoped enhancement styles/scripts. Font licenses are included. |
| `scripts/` | Repeatable bounded updates, initial Work detail HTML, local preview and audit. |
| `docs/` | Source review, benchmark research, route/link reports and release checks. |

## Edit and preview

Run the detail generator before the shared patch. Both read the recorded baseline commit, preserving the core Framer frame. Do not regenerate from a different Framer export without reviewing the baseline and preservation checks.

```sh
python3 scripts/build_work_details.py
python3 scripts/update_existing_site.py
python3 scripts/audit_site.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/lead-capture.test.mjs tests/brand-intro.test.mjs tests/home-faq.test.mjs tests/home-image-cards.test.mjs
python3 scripts/preview.py
```

Open http://127.0.0.1:4173. This visual preview never forwards form submissions. Use `--base-url http://127.0.0.1:4173` on the audit for GET-only HTTP observations. The production service remains the existing static Cloudflare asset deployment; there is no new backend or mandatory production build step.

Core pages keep their original Framer runtime. Four existing Work detail routes now include substantive initial HTML, reuse the original Services frame, preserve anonymous pageview attribution, and use a native mobile menu. Shared navigation uses ordinary browser navigation so each route loads its own published HTML and metadata. Brand/context additions are reapplied after core Framer hydration. The original six Home FAQ questions use native disclosure controls with initial-HTML answers; `content/home-faq.json` supplies both those answers and their semantic schema, with open state preserved through hydration.

Text uses the exact logo red `#ff3436`, blue `#0037fb` and ink `#191c1f`, with ink surfaces for small red labels. Blue text has no added white backing or outline. Public photography uses native image-area links to contextual destinations, restored after hydration. Multi-image compositions share one link. The Home photographic Creator Relationships and Connected Delivery panels retain white labels. Linked images have a gentle zoom; full-panel/native image cards also lift, with keyboard focus and reduced-motion support. Shared CTA styling includes hover, press, keyboard focus and reduced-motion handling. The left-to-right logo reveal runs only on an explicit homepage refresh.

The Services market overview and sector headers follow the immediately preceding How We Partner gradient/photo card, including its responsive proportions, fonts, insets and heading scale. All existing market guidance and interlinks are retained. Travel, Hospitality and Lifestyle are Services anchors (`#travel`, `#hospitality`, `#lifestyle`), not separate market pages. US locations are planning context; no offices or unverified city results are claimed.

The Holafly detail page is temporarily unpublished at the owner’s request. Its original URL, trailing-slash variant and `.html` variant redirect to Work with HTTP 302. The sitemap and public links exclude it, and its featured cards/CMS markers stay hidden through Framer hydration. Historical source and the private metric ledger are retained for restoration; numerical publication remains blocked. All public contact links, copy and Organization email markup use `alex@irgmedia.org`.

## Deploy

Live domain: **https://irgmedia.org**. The signed-in IRG Cloudflare dashboard confirms this domain is attached to the **website** Worker. Its production Workers URL is **https://website.reyan-461.workers.dev**.

Cloudflare Workers & Pages project **website** is connected to this repo and deploys automatically:

- **Push to `main` → production deployment** through the existing integration. Verify its successful build before reporting the update live. Build status shows as a check on the commit in GitHub.
- **Other branches / pull requests** get their own Cloudflare preview URL (shown on the PR). Merge to `main` to go live.
- Production deploy command is `npx wrangler deploy`; preview branches use `npx wrangler preview`. The top-level `previews` block enables the latter. `wrangler.jsonc` tells both to serve `site/` as static assets. If you restructure the output folder, update `assets.directory` in `wrangler.jsonc`.
- There is no build step. Whatever is committed in `site/` is what gets served.

Review previews appear on the corresponding pull request after its Workers Builds check passes. The existing site is published at [irgmedia.org](https://irgmedia.org); each subsequent release requires a successful production build before being described as live.

## Discovery-call scheduling

Start a project actions open `/contact#book-a-call`. The supplied Calendly event is embedded below the original Contact form in the existing dark layout. Only Contact loads the official `assets.calendly.com` widget script; its scoped helper restores a single widget after Framer hydration. A native link opens the same booking page if an embed is blocked. Scheduling does not forward enquiry fields, replace the enquiry form or change its delivery integration.

## Lead capture (do not remove)

The existing Make route copies form submissions to the **Website Leads** Google Sheet (owned by reyan@irgmedia.org). Its beacon/no-cors delivery is best effort and does not provide a delivery acknowledgement to the browser.

- `site/lead-capture.js` listens for form submits on every page and posts the fields to a Make webhook, which appends a row to the sheet.
- Each HTML page loads it with `<script defer src="/lead-capture.js"></script>` just before `</head>`. Any new or rebuilt page needs that tag.
- It reads the visible inputs named `name`, `email`, `company`, `timing`, `project_context`, plus the form's `data-framer-name` as the form label. Keep those names (or update `FIELDS` in the script) if you rebuild the forms.
- Hidden honeypot inputs are respected: if a bot fills one, nothing is sent.
- Forms covered today: "Resource download form" on `/resources` and "Project enquiry" on `/contact`.
- Project enquiries now use Framer's delivery feedback; a 250 ms timer no longer claims receipt. The excluded Resource download flow retains its original behaviour. No live enquiries were sent during validation.

## Notes for whoever rebuilds this

- Most original images and the core Framer runtime remain on Framer's CDN (`framerusercontent.com`, `framerstatic.com`). The new logo, fonts, favicon, social preview and existing Holafly campaign still are local assets.
- The HTML is generated output from Framer: heavy inline styles, hashed class names. Treat it as a visual + content reference, not clean source.
- Original source copy/structure and CMS publication records remain in `framer-export/`; reviewed additions and exact metric provenance are in `content/`.
- Canonicals and sitemap use `https://irgmedia.org`. The existing draft privacy text stays available with `noindex,follow` pending approved policy wording. The unfinished Resource section, content and download setup are explicitly excluded from this update.
- Footer attribution is `by leadscorer.co`, linking directly to `https://leadscorer.co/` on all routes.

## Rollback

Revert the update commit or merge commit on `main` to restore the prior asset snapshot. A preview branch does not publish to `irgmedia.org`; merging/pushing to `main` triggers the existing Cloudflare production deployment. Preserve the resource and recipient-routing checks when reviewing future edits.
