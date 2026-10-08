# Site typography and layout review — 8 October 2026

Reviewed every published route at 1440 × 1000 (laptop), 1024 × 900 (tablet),
and 390 × 844 (phone), scrolling through the original animated sections before
capturing the layouts. Additional 360 × 800 checks covered Home, Services,
About, Contact, Resources and the campaign brief guide.

## Shared typography

The original Services presets are the reference for the inner pages:

| Role | Laptop | Tablet | Phone |
| --- | --- | --- | --- |
| Page title | 64 px | 48 px | 38 px |
| Section title | 44 px | 36 px | 30 px |
| Card title | 24 px | 22 px | 20 px |
| Reading copy | 17 px | 17 px | 16 px |

Headings use BDO Grotesk and reading copy uses Inter. Home retains its larger
editorial scale, with consistent 60 / 42 / 34 px section headings. Its photo
hero, smaller FAQ titles, form titles, labels and button labels retain their
distinct roles. The existing wide-screen presets remain responsive above
1600 px.

## Corrected inconsistencies

- Alternate Approach and About heading presets now match the original
  Services scale, line height and letter spacing.
- All eight guide and Work detail routes share the inner-page title/body
  presets, gray cards, inset spacing and corner treatment.
- Home section gutters now align at each breakpoint. Fixed inline heading
  sizes, deliverable titles and the Source/Run/Scale typography are consistent.
- The four About principle titles align to one fixed-width number column.
- Shared related cards, booking copy, resource reading text, form field fonts
  and sector labels use the appropriate common font and size.
- Phone and tablet partner cards and sector cards share responsive insets and
  image heights. Sector spacing scales down on phones; double spacing after
  proof labels has been removed. Reading paragraphs use natural line wrapping.
- Home Selected work has three equal laptop columns and a 40 px heading-to-card
  gap, without the extra carousel-control row and fourth-card bleed. The native
  phone rail still scrolls and all original destinations remain available.
- Guide/Work mobile menu labels match the original menu's 22 px type and left
  alignment, including the open menu's white background and dark wordmark.
- Work cards, their destination pages and the sector references now use
  finished campaign-planning copy. Drafting notes such as "Format example",
  "No client named" and future publication instructions have been removed.
  The guides remain clearly identified as planning guides and claim no client
  results. All existing image-card links remain intact.

## Route coverage

Home; Services (all four markets, other sectors and planning references);
Approach; Why IRG; Work; About; Contact; Resources; Privacy;
campaign operations, always-on programme and hospitality Work details;
Guides; agency selection, campaign brief, measurement and content rights guides.

Checked the six expanded Home FAQs, all fourteen expanded sector disclosures,
and the original/static mobile navigation. No page-wide horizontal overflow
was found at the reviewed widths. The decorative gradient numerals' visible
glyph overhang was inspected in context; their containing cards do not clip it.

The content, photographic layout, original forms, Calendly destination and
interlinks remain in place. The excluded blank resource content/download flow
and withdrawn Holafly publication state are preserved.

Validation: 20 Python tests, 13 JavaScript tests, source-preservation and route
audit (17 routes, 1,137 internal links, zero errors), and clean diff whitespace.
Browser measurements and screenshots are saved in the task's `outputs/layout-audit`
folder; they are not included in the public site assets.
