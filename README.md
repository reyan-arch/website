# IRG Media — website

Static mirror of the IRG Media site built in Framer, plus the raw content exported from the Framer project. Deploys to Cloudflare Workers from this repo.

## Layout

| Path | What it is |
|---|---|
| `site/` | The rendered site: one HTML file per page (`index.html`, `services.html`, `work/holafly.html` …), `sitemap.xml`, `robots.txt`. This is what Cloudflare serves. |
| `framer-export/PAGES.md` | Page copy pulled from the Framer canvas (home page; other pages' text is in their HTML). |
| `framer-export/pages/` | One JSON per page: path, draft flag, component instances, text layers. |
| `framer-export/cms/` | CMS collections with fields + items: `Case_Studies.json` (4 items), `Resources.json` (1 item). |
| `framer-export/code/` | Code components / overrides (`.tsx`) from the Framer project. |
| `framer-export/project.json`, `redirects.json`, `locales.json`, `publish_info.json` | Project metadata. |
| `wrangler.jsonc` | Cloudflare config: serves `site/` as static assets via `npx wrangler deploy`. |

## Deploy

Live URL: **https://website.reyan-461.workers.dev**

Cloudflare Workers & Pages project **website** is connected to this repo and deploys automatically:

- **Push to `main` → live** within about a minute. No manual step. Build status shows as a check on the commit in GitHub.
- **Other branches / pull requests** get their own Cloudflare preview URL (shown on the PR). Merge to `main` to go live.
- Deploy command is `npx wrangler deploy`; `wrangler.jsonc` tells it to serve `site/` as static assets. If you restructure the output folder, update `assets.directory` in `wrangler.jsonc`.
- There is no build step. Whatever is committed in `site/` is what gets served.

## Notes for whoever rebuilds this

- Images, fonts and the Framer runtime JS are **not** in this repo. The HTML references them on Framer's CDN (`framerusercontent.com`, `framerstatic.com`), so the mirror renders as-is, but it depends on those URLs staying up. A proper rebuild should pull assets local.
- The HTML is generated output from Framer: heavy inline styles, hashed class names. Treat it as a visual + content reference, not clean source.
- Source of truth for copy and structure: `framer-export/`. CMS content (case studies) lives in `framer-export/cms/`.
- Mirror taken from the Framer staging publish; `<link rel="canonical">` tags still point at the Framer host — replace with the final domain.
