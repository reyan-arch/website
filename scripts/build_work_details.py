#!/usr/bin/env python3
"""Build Work detail routes and planning guides as readable initial HTML.

The Services export at the content model's baselineCommit is the visual template.
This intentionally reads Git, not an already patched page. Run this generator
before update_existing_site.py so the shared brand/footer patch is applied once.
These static detail routes omit Framer hydration; existing core pages and
their forms keep their original runtime and integrations.
"""

from __future__ import annotations

import html
import json
import re
import subprocess
import argparse
from datetime import date
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_IDS = (
    "holafly", "always-on-program", "campaign-operations",
    "hospitality-travel-brief",
)

# Verified against the existing public Framer CMS and script_main bundle. These
# retain the original anonymous published_site_pageview attribution, without
# loading the React/Framer renderer on the static detail pages.
FRAMER_SITE_ID = "bde49d427364712e55d59e146f2ac4f2ecff748a9a34b74cccc36fb1f43dbc01"
FRAMER_WORK_ROUTE_ID = "HrL2VNaYB"
FRAMER_COLLECTION_IDS = {
    "holafly": "As7xNh2AQ",
    "campaign-operations": "LIUIHpLEA",
    "always-on-program": "yEw8hInBr",
    "hospitality-travel-brief": "YaNDolNkn",
}


def metric_is_public(metric: dict) -> bool:
    """Legacy provenance is not permission to publish a numerical claim.

    All three explicit publication flags must be literal booleans. In particular,
    the earlier approval='existing-publication-record' string cannot pass this
    gate after a client withdraws use of its figures.
    """
    return all(metric.get(flag) is True for flag in ("public", "approved", "approval"))


def require_public_metric(metric: dict) -> dict:
    if not metric_is_public(metric):
        raise ValueError(f'Metric {metric.get("id", "<unknown>")} is not approved for public rendering')
    return metric


def public_text_fields(value, path="page"):
    """Yield only reader-facing copy, excluding IDs, URLs and process counters."""
    copy_fields = {"title", "description", "h1", "primaryIntent", "body", "kicker", "alt", "disclosure", "caption", "label", "columns", "subtitle", "summary", "excerpt"}
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in copy_fields:
                if isinstance(child, str):
                    yield child_path, child
                elif isinstance(child, list):
                    for index, text in enumerate(child):
                        if isinstance(text, str):
                            yield f"{child_path}[{index}]", text
            if isinstance(child, (dict, list)):
                yield from public_text_fields(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from public_text_fields(child, f"{path}[{index}]")


def validate_public_page(page: dict, metrics: dict) -> None:
    """Fail before output if a stale model would republish withdrawn figures."""
    if page.get("published") is not True:
        raise ValueError(f'Page {page.get("id", "<unknown>")} is not approved for publication')

    def inspect_references(value):
        if isinstance(value, dict):
            if value.get("metricId"):
                if page.get("id") == "holafly" and not all(
                    page.get(flag) is True for flag in ("numericPublicationApproved", "numericCasePublicationApproved")
                ):
                    raise ValueError('Holafly numerical claims are not approved for public rendering')
                require_public_metric(metrics[value["metricId"]])
            for child in value.values():
                inspect_references(child)
        elif isinstance(value, list):
            for child in value:
                inspect_references(child)

    inspect_references(page)
    withdrawn_holafly = any(
        metric_id.startswith("holafly-") and not metric_is_public(metric)
        for metric_id, metric in metrics.items()
    )
    holafly_quantities_withheld = withdrawn_holafly or not all(
        page.get(flag) is True for flag in ("numericPublicationApproved", "numericCasePublicationApproved")
    )
    if page.get("id") == "holafly" and holafly_quantities_withheld:
        number_words = r"(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)"
        quantified_unit = re.compile(rf"\b{number_words}[\s-]+(?:hundred|thousand|million|billion|percent|niches|creators|partnerships|views|pieces)\b", re.I)
        for path, text in public_text_fields(page):
            # A calendar year is contextual information, rather than a campaign
            # result. Process step numbers are excluded by public_text_fields.
            without_years = re.sub(r"\b(?:19|20)\d{2}\b", "", text)
            if re.search(r"\d", without_years) or quantified_unit.search(text):
                raise ValueError(f'Withdrawn Holafly quantity in public copy at {path}')


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None]
    start: int
    end: int = 0
    parent: "Node | None" = None
    children: list["Node"] = field(default_factory=list)


class SourceTree(HTMLParser):
    """Retain exact source spans so original navigation/CSS remain intact."""

    VOID = set("area base br col embed hr img input link meta param source track wbr".split())

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.offsets = [0] + [match.end() for match in re.finditer("\n", source)]
        self.nodes: list[Node] = []
        self.stack: list[Node] = []
        self.feed(source)

    def position(self) -> int:
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.position(), parent=self.stack[-1] if self.stack else None)
        if node.parent:
            node.parent.children.append(node)
        self.nodes.append(node)
        if tag in self.VOID:
            node.end = node.start + len(self.get_starttag_text())
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            node = self.stack.pop()
            node.end = node.start + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                self.stack[index].end = self.position() + len(tag) + 3
                del self.stack[index:]
                return

    def raw(self, node: Node) -> str:
        assert node.end > node.start, (node.tag, node.attrs)
        return self.source[node.start:node.end]

    def find(self, **attributes) -> Node:
        return next(node for node in self.nodes if all(node.attrs.get(key) == value for key, value in attributes.items()))


def escape(value) -> str:
    return html.escape(str(value), quote=True)


def action_class(primary: bool) -> str:
    return ' class="irg-update-button"' if primary else ""


def href(value: str) -> str:
    # Sector context now lives inside the existing Services page.
    return {
        "/industries/travel": "/services#travel",
        "/industries/hospitality": "/services#hospitality",
        "/industries/lifestyle": "/services#lifestyle",
        "/services#scope": "/services#campaign-operations",
    }.get(value, value)


def links(items: list[dict], approach_stage: str | None = None) -> str:
    if not items:
        return ""
    return '<div class="irg-detail-links">' + "".join(
        f'<a href="{escape("/approach#" + approach_stage if item["href"] == "/approach" and approach_stage else href(item["href"]))}">{escape(item["label"])} <span aria-hidden="true">↗</span></a>'
        for item in items
    ) + "</div>"


def paragraphs(items: list[str]) -> str:
    return "".join(f"<p>{escape(item)}</p>" for item in items)


def visible_static(fragment: str) -> str:
    # Original footer content starts invisible until Framer's appear animation.
    # Removing that deferred state keeps the copied layout usable without JS.
    def fix_style(match):
        style = match.group(1)
        opacity = re.search(r"(?:^|;)\s*opacity\s*:\s*([\d.]+)(?:;|$)", style)
        if opacity and float(opacity[1]) < .01:
            style = ";".join(
                property for property in style.split(";")
                if property.split(":", 1)[0].strip() not in {"opacity", "transform", "will-change"}
            )
        return f'style="{style}"'

    # All component styles are copied once into <head> below. Keeping the
    # repeated inline copies would let their generic nav rules override the
    # detail-specific disclosure and in-page navigation rules.
    fragment = re.sub(r"<style\b[^>]*>.*?</style>", "", fragment, flags=re.S)
    fragment = re.sub(r'style="([^"]*)"', fix_style, fragment)
    fragment = fragment.replace(' data-framer-page-link-current="true"', "")
    return re.sub(
        r'href="(?:\./)?(index|services|why-irg|approach|work|resources|about|contact|privacy)\.html([#?][^"]*)?"',
        lambda match: f'href="{("/" if match[1] == "index" else "/" + match[1])}{match[2] or ""}"',
        fragment,
    )


def navigation(tree: SourceTree) -> str:
    node = tree.find(**{"data-framer-name": "Navigation Wrapper"})
    source = tree.raw(node).replace('data-framer-name="Navigation Wrapper"', 'data-framer-name="Navigation Wrapper" data-irg-work-navigation="true"', 1)
    controls = [child for child in tree.nodes if child.tag == "button" and child.attrs.get("data-framer-name") == "Open navigation" and node.start < child.start < node.end]
    nav_links = [
        {"label": "Services", "href": "/services"},
        {"label": "Why IRG", "href": "/why-irg"},
        {"label": "Approach", "href": "/approach"},
        {"label": "Work", "href": "/work"},
        {"label": "Resources", "href": "/resources"},
        {"label": "About", "href": "/about"},
        {"label": "Start a project", "href": "/contact"},
    ]
    for control in reversed(controls):
        original = tree.raw(control)
        start = original.index(">") + 1
        lines = original[start:original.rfind("</button>")]
        panel = "".join(f'<a{action_class(item["href"] == "/contact")} href="{escape(item["href"])}">{escape(item["label"])}</a>' for item in nav_links)
        replacement = '<details class="irg-work-nav"><summary class="framer-1be3zl6" aria-label="Open navigation">' + lines + '</summary><div class="irg-work-nav-panel">' + panel + "</div></details>"
        source = source.replace(original, replacement, 1)
    return visible_static(source)


DETAIL_CSS = """
.irg-work-detail.framer-3BEj8{width:100%;max-width:none;color:#191c1f;font-family:"BDO Grotesk Variable",Arial,sans-serif}
.irg-work-detail p,.irg-work-detail li,.irg-work-detail td,.irg-work-detail th,.irg-work-detail dd,.irg-work-detail dt{font-family:"Inter",Arial,sans-serif;font-size:var(--irg-body);line-height:1.5;margin:0;letter-spacing:var(--irg-type-spacing);font-weight:400;font-variation-settings:"wght" 400;text-wrap:pretty}
.irg-work-detail p+p{margin-top:20px}
.irg-work-detail #detail-title{color:#fff;--framer-text-color:#fff;--framer-font-size:var(--irg-page-title);--framer-font-variation-axes:"wght" 600;--framer-letter-spacing:var(--irg-type-spacing)}
.irg-work-detail h2.framer-text.framer-styles-preset-vl1nhu{color:#191c1f;--framer-text-color:#191c1f;--framer-font-size:var(--irg-section-title);--framer-font-variation-axes:"wght" 600;--framer-letter-spacing:var(--irg-type-spacing)}
.irg-work-detail h3{font-size:var(--irg-card-title);line-height:1.12;font-variation-settings:"wght" 600;letter-spacing:var(--irg-type-spacing);margin:0;text-wrap:balance}
.irg-work-detail :is(h1,h2,h3,p,li){font-feature-settings:"blwf","cv03","cv04","cv09","cv11"}
.irg-work-detail .framer-1cpauo7,.irg-work-detail .framer-1asr0dp{overflow:visible}
.irg-work-detail .framer-17nmvxz{overflow:visible;align-items:flex-start}
.irg-work-detail .framer-i9djt6{color:#d3d3d6;gap:28px}
.irg-detail-kicker{display:inline-flex;align-items:center;min-height:32px;padding:7px 14px;border:1px solid #424245;border-radius:999px;font-size:12px;line-height:1.25;letter-spacing:.055em;color:#eee}
.irg-detail-breadcrumb{display:flex;flex-wrap:wrap;align-items:center;gap:10px;font-size:13px;line-height:1.4;color:#b4b4b8}
.irg-work-detail :is(.irg-detail-breadcrumb,.irg-detail-on-this-page){width:100%!important;height:auto!important;border-radius:0!important;max-height:none!important;overflow:visible!important}
.irg-detail-breadcrumb a{color:inherit;text-decoration:none}
.irg-detail-breadcrumb a:hover{text-decoration:underline}
.irg-detail-actions,.irg-detail-links{display:flex;flex-wrap:wrap;align-items:center;gap:14px 28px}
.irg-detail-actions a{display:inline-flex;align-items:center;justify-content:center;gap:12px;padding:14px 24px;border-radius:999px;background:#fff;color:#171719;text-decoration:none;font-size:16px;line-height:1.2}
.irg-detail-actions a+ a{background:transparent;color:#fff;border:1px solid #67676b}
.irg-work-detail a:focus-visible,.irg-work-nav summary:focus-visible,.irg-work-nav a:focus-visible{outline:3px solid #0037fb;outline-offset:5px}
.irg-detail-on-this-page{display:flex;flex-wrap:wrap;gap:10px 24px;padding-top:12px;border-top:1px solid #424245;width:100%;color:#d3d3d6;font-size:14px;line-height:1.4}
.irg-detail-on-this-page a{color:inherit;text-decoration:none}
.irg-detail-section+.irg-detail-section{border-top:1px solid #e1e1e3}
.irg-detail-section .framer-1asr0dp{gap:40px}
.irg-detail-section-title{max-width:850px}
.irg-detail-section-body{max-width:1000px;width:100%}
.irg-detail-section-body:empty{display:none}
.irg-detail-section-body:not(:empty){padding:28px;background:#f4f4f4;border:0;border-radius:32px}
.irg-detail-links{margin-top:28px}
.irg-detail-links a{font-family:Inter,Arial,sans-serif;font-size:var(--irg-body);line-height:1.5;letter-spacing:var(--irg-type-spacing);color:#191c1f;text-decoration:underline;text-underline-offset:4px}
.irg-detail-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px;width:100%}
.irg-detail-item{display:flex;flex-direction:column;gap:16px;padding:28px;background:#f4f4f4;border:0;border-radius:32px;min-width:0}
.irg-detail-item p{color:#55555d}
.irg-detail-steps{list-style:none;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:32px;width:100%}
.irg-detail-step{padding:28px;background:#f4f4f4;border:0;border-radius:32px;display:flex;flex-direction:column;gap:16px}
.irg-detail-step-number{font-family:"BDO Grotesk Variable",sans-serif;font-size:14px;line-height:1.4;color:#62626c;background:#fff;border:1px solid #dcdce2;border-radius:999px;padding:6px 12px;align-self:flex-start}
.irg-detail-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px;width:100%;margin:0}
.irg-detail-metric{background:#f7f7f8;border:1px solid #e4e4e8;border-radius:24px;padding:28px;display:flex;flex-direction:column;gap:10px}
.irg-detail-metric dd{font-family:"BDO Grotesk Variable",sans-serif;order:-1;font-size:56px;line-height:1;font-variation-settings:"wght" 600;letter-spacing:-.04em}
.irg-detail-metric dt{font-size:18px;line-height:1.45;font-weight:600}
.irg-detail-metric dt small,.irg-detail-metric dt span{display:block;font-weight:400;margin-top:12px}
.irg-detail-metric small,.irg-detail-disclosure,.irg-detail-metric-context{font-size:14px!important;line-height:1.55!important;color:#62626c}
.irg-detail-metric-context{margin-top:12px!important}
.irg-detail-disclosure{max-width:1000px;margin-top:20px!important}
.irg-detail-table-scroll{width:100%;overflow:auto;scroll-margin-top:120px;background:#f7f7f8;border:1px solid #e4e4e8;border-radius:24px;padding:28px}
.irg-detail-table{width:100%;border-collapse:collapse;text-align:left;min-width:620px}
.irg-detail-table caption{text-align:left;font-size:14px;color:#62626c;padding:0 0 16px}
.irg-detail-table th,.irg-detail-table td{padding:20px 20px 20px 0;border-bottom:1px solid #d7d7db;vertical-align:top}
.irg-detail-table thead th{font-size:14px;line-height:1.5;font-weight:600}
.irg-detail-table tbody th{font-weight:600}
.irg-detail-table td small{display:block;font-size:13px;line-height:1.4;color:#62626c}
.irg-detail-creator-layout{display:grid;grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:64px;align-items:start;width:100%}
.irg-detail-campaign-image{margin:0;max-width:430px}
.irg-detail-campaign-image img{width:100%;height:auto;display:block;border-radius:24px}
.irg-detail-campaign-image figcaption{font-size:13px;line-height:1.5;color:#62626c;margin-top:14px}
.irg-detail-creator-items{display:flex;flex-direction:column;gap:32px}
.irg-work-nav{width:44px;height:44px;flex:none;grid-column:2;grid-row:1;justify-self:end;position:relative}
.irg-work-nav summary{list-style:none;border:0;background:transparent}
.irg-work-nav summary::-webkit-details-marker{display:none}
.irg-work-nav-panel{position:absolute;right:-16px;top:calc(100% + 18px);width:min(380px,calc(100vw - 32px));max-height:calc(100dvh - 130px);overflow:auto;background:#fafafa;border:1px solid #ddd;border-radius:24px;padding:16px;box-shadow:0 14px 40px #0002;display:flex;flex-direction:column;gap:2px}
.irg-work-nav-panel a{padding:12px 16px;border-radius:12px;min-height:48px;font-family:"BDO Grotesk Variable",sans-serif;font-size:24px;font-weight:600;font-variation-settings:"wght" 600;line-height:1.3;text-decoration:none;color:#171719}
.irg-work-nav-panel a:hover{background:#ececef}
.irg-work-nav-panel a:last-child{margin-top:6px;background:#171719;color:#fff}
[data-irg-work-navigation] nav{overflow:visible!important;--irg-nav-ink:#fff;background-color:rgba(10,10,10,.94)!important;backdrop-filter:blur(16px)!important;-webkit-backdrop-filter:blur(16px)!important}
[data-irg-work-navigation] nav[data-irg-scrolled="true"]{--irg-nav-ink:#1f1f1f;background-color:rgba(250,250,250,.96)!important;box-shadow:0 4px 20px #0001!important}
[data-irg-work-navigation] nav [data-framer-name="Navigation Links"] :is(a,.framer-text){color:var(--irg-nav-ink)!important}
[data-irg-work-navigation] nav [data-framer-name="Menu line"]{background:var(--irg-nav-ink)!important}
.irg-work-nav[open] summary .framer-1bppvce{transform:translateY(4px) rotate(45deg)}
.irg-work-nav[open] summary .framer-1t8abph{transform:translateY(-4px) rotate(-45deg)}
.irg-detail-skip{position:fixed;left:16px;top:12px;z-index:100;background:#fff;color:#171719;padding:12px 18px;border-radius:12px;transform:translateY(-160%);font-family:"BDO Grotesk Variable",sans-serif}
.irg-detail-skip:focus{transform:translateY(0)}
@media(min-width:1600px){.irg-work-detail .framer-6tdioh{padding-bottom:128px}.irg-work-detail .framer-11dwd3{padding-top:128px;padding-bottom:128px}}
@media(max-width:1199.98px){.irg-work-detail .framer-6tdioh{padding:160px 32px 80px}.irg-work-detail .framer-17nmvxz{flex-direction:column;gap:32px}.irg-work-detail .framer-1oj2673,.irg-work-detail .framer-i9djt6{width:100%;flex:none;max-width:900px}.irg-work-detail .framer-11dwd3{padding:80px 32px}.irg-detail-grid,.irg-detail-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.irg-detail-creator-layout{gap:32px}}
@media(max-width:809.98px){.irg-work-detail .framer-6tdioh{padding:176px 20px 64px}.irg-work-detail .framer-11dwd3{padding:64px 20px}.irg-work-detail .framer-1cpauo7{gap:28px}.irg-detail-grid,.irg-detail-steps,.irg-detail-metrics{grid-template-columns:1fr;gap:20px}.irg-detail-metric dd{font-size:48px}.irg-detail-metric dt{font-size:17px}.irg-detail-creator-layout{grid-template-columns:1fr}.irg-detail-campaign-image{max-width:370px}.irg-detail-section .framer-1asr0dp{gap:28px}.irg-detail-actions{gap:12px}.irg-detail-actions a{padding:14px 20px}.irg-detail-kicker{font-size:11px}.irg-detail-table th,.irg-detail-table td{padding-top:16px;padding-bottom:16px}.irg-detail-item,.irg-detail-step,.irg-detail-metric,.irg-detail-section-body:not(:empty),.irg-detail-table-scroll{padding:24px;border-radius:24px}}
@media(prefers-reduced-motion:reduce){.irg-work-detail *,.irg-work-nav *{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
"""


def metric_context(metric: dict) -> str:
    details = [metric["period"]]
    if metric.get("baseline"):
        details.append("Baseline: " + metric["baseline"])
    return " · ".join(details)


def metric_card(metric: dict) -> str:
    require_public_metric(metric)
    return f'<div class="irg-detail-metric" data-metric-id="{escape(metric["id"])}"><dt>{escape(metric["label"])}<small>{escape(metric["unit"])}</small><span class="irg-detail-metric-context">{escape(metric_context(metric))}</span></dt><dd>{escape(metric["display"])}</dd></div>'


def item_markup(item: dict, metrics: dict) -> str:
    context = ""
    if item.get("metricId"):
        metric = require_public_metric(metrics[item["metricId"]])
        context = f'<p class="irg-detail-metric-context">{escape(metric_context(metric))}. {escape(metric["caveat"])}</p>'
    return f'<article class="irg-detail-item"><h3>{escape(item["title"])}</h3><p>{escape(item["body"])}</p>{context}</article>'


def campaign_figure(page: dict) -> str:
    image = page["image"]
    return '<figure class="irg-detail-campaign-image"><img src="/assets/holafly-vineyards.webp" width="506" height="900" loading="lazy" decoding="async" alt="' + escape(image["alt"]) + '"><figcaption>Holafly programme · Existing campaign still.</figcaption></figure>'


def render_section(section: dict, page: dict, metrics: dict) -> str:
    validate_public_page(page, metrics)
    contents = '<div class="irg-detail-section-body">' + paragraphs(section.get("body", [])) + "</div>"
    has_campaign_image = section["id"] == "creator-examples" and page["id"] == "holafly"
    if has_campaign_image:
        items = "".join(item_markup(item, metrics) for item in section.get("items", []))
        contents = '<div class="irg-detail-creator-layout">' + campaign_figure(page) + '<div class="irg-detail-creator-items">' + contents + items + "</div></div>"
    if section.get("stats"):
        contents += '<dl class="irg-detail-metrics">' + "".join(metric_card(metrics[item["metricId"]]) for item in section["stats"]) + "</dl>"
    if section.get("steps"):
        contents += '<ol class="irg-detail-steps">' + "".join(
            f'<li class="irg-detail-step"><span class="irg-detail-step-number" aria-hidden="true">{escape(step["number"])}</span><h3>{escape(step["title"])}</h3><p>{escape(step["body"])}</p></li>'
            for step in section["steps"]
        ) + "</ol>"
    if section.get("items") and not has_campaign_image:
        items = "".join(item_markup(item, metrics) for item in section["items"])
        contents += '<div class="irg-detail-grid">' + items + "</div>"
    if section["kind"] == "table":
        headers = "".join(f'<th scope="col">{escape(column)}</th>' for column in section["columns"])
        rows = []
        for row in section["rows"]:
            cells = []
            for cell in row["cells"]:
                metric = require_public_metric(metrics[cell["metricId"]])
                cells.append(f'<td data-metric-id="{escape(metric["id"])}">{escape(metric["display"])}</td>')
            rows.append(f'<tr><th scope="row">{escape(row["label"])}</th>{"".join(cells)}</tr>')
        table_label = section.get("title", "Approved results")
        caption = f'<caption>{escape(section["caption"])}</caption>' if section.get("caption") else ""
        contents += '<div class="irg-detail-table-scroll" tabindex="0" role="region" aria-label="' + escape(table_label) + '"><table class="irg-detail-table">' + caption + '<thead><tr>' + headers + '</tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>"
    stage = "run" if page["id"] == "campaign-operations" else "frame"
    section_links = list(section.get("links", []))
    if page["id"] == "always-on-program" and section["id"] == "cycle":
        section_links += [
            {"label": "Frame the next brief", "href": "/approach#frame"},
            {"label": "Coordinate delivery", "href": "/approach#run"},
            {"label": "Record the learning", "href": "/approach#learn"},
        ]
    if page["id"] == "hospitality-travel-brief" and section["id"] == "brief-context":
        section_links += [{"label": "Frame the audience and objective", "href": "/approach#frame"}]
    if page["id"] == "holafly" and section["id"] == "measurement":
        section_links += [{"label": "Carry evidence into the next brief", "href": "/approach#learn"}]
    contents += links(section_links, approach_stage=stage)
    if section.get("disclosure"):
        contents += f'<p class="irg-detail-disclosure">{escape(section["disclosure"])}</p>'
    has_markets_section = any(item["id"] == "markets" for item in page["sections"])
    markets_alias = '<span id="markets" aria-hidden="true"></span>' if page["id"] == "holafly" and section["id"] == "results" and not has_markets_section else ""
    return f'<section id="{escape(section["id"])}" class="framer-11dwd3 irg-detail-section" aria-labelledby="{escape(section["id"])}-heading">{markets_alias}<div class="framer-1asr0dp"><div class="framer-roardh irg-detail-section-title"><h2 id="{escape(section["id"])}-heading" class="framer-text framer-styles-preset-vl1nhu">{escape(section["title"])}</h2></div>{contents}</div></section>'


def hero(page: dict) -> str:
    data = page["hero"]
    parent_path, parent_label = ("/guides", "Guides") if page["type"] == "guide" else ("/", "Home") if page["type"] == "guide-hub" else ("/work", "Work")
    parent_crumb = '<a href="' + parent_path + '">' + parent_label + '</a><span aria-hidden="true">/</span>' if parent_path != "/" else ""
    byline = '<p>By IRG Media · Published <time datetime="' + page["publishedAt"] + '">' + escape(date.fromisoformat(page['publishedAt']).strftime('%-d %B %Y')) + '</time></p>' if page["type"] in ("guide", "guide-hub") else ""
    actions = "".join(f'<a{action_class(key == "primary")} href="{escape(href(data[key]["href"]))}">{escape(data[key]["label"])} <span aria-hidden="true">↗</span></a>' for key in ["primary", "secondary"])
    anchors = [(section["id"], section["title"].rstrip(".")) for section in page["sections"] if section["id"] not in ["disclosure", "limits"]]
    if page["id"] == "holafly":
        anchors = [(target, label) for target, label in anchors if target in {"results", "measurement", "creator-examples"}]
    on_page = "".join(f'<a href="#{escape(target)}">{escape(label)}</a>' for target, label in anchors)
    return '<section class="framer-6tdioh" data-framer-name="IRG opening dark" aria-labelledby="detail-title"><div class="framer-1cpauo7"><nav class="irg-detail-breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span aria-hidden="true">/</span>' + parent_crumb + '<span aria-current="page">' + escape("Holafly" if page["id"] == "holafly" else page["title"].split(" | ")[0]) + '</span></nav><span class="irg-detail-kicker">' + escape(data["kicker"]) + '</span><div class="framer-17nmvxz"><div class="framer-1oj2673"><div class="framer-i1uytd"><h1 id="detail-title" class="framer-text framer-styles-preset-15zio5j">' + escape(page["h1"]) + '</h1></div></div><div class="framer-i9djt6"><p>' + escape(data["body"]) + '</p>' + byline + '<div class="irg-detail-actions">' + actions + '</div></div></div><nav class="irg-detail-on-this-page" aria-label="On this page">' + on_page + "</nav></div></section>"


def analytics(page_id: str) -> str:
    # Same Framer queue event, route ID, collection ID and site ID as the public
    # renderer. Query/hash/referrer are intentionally omitted to keep these
    # restored detail pageviews free of arbitrary user-supplied values.
    return '<script data-irg-work-pageview>window.__framer_events=window.__framer_events||[];window.__framer_events.push(["published_site_pageview",{framerSiteId:' + json.dumps(FRAMER_SITE_ID) + ',version:2,routePath:"/work/:ExKkw5wwc",collectionItemId:' + json.dumps(FRAMER_COLLECTION_IDS[page_id]) + ',framerLocale:"en-US",webPageId:' + json.dumps(FRAMER_WORK_ROUTE_ID) + ',referrer:null,url:window.location.origin+window.location.pathname,hostname:window.location.hostname||null,pathname:window.location.pathname||null,hash:null,search:null,timezone:Intl.DateTimeFormat().resolvedOptions().timeZone,locale:Intl.DateTimeFormat().resolvedOptions().locale},"eager"]);</script><script async src="https://events.framer.com/script?v=2" data-fid="' + FRAMER_SITE_ID + '" data-no-nt></script>'


STATIC_NAV_SCRIPT = """<script data-irg-work-navigation-script>
(() => {
  const wrapper = document.querySelector('[data-irg-work-navigation]');
  if (!wrapper) return;
  const navs = [...wrapper.querySelectorAll('nav')];
  let scheduled = false;
  const refresh = () => {
    scheduled = false;
    const scrolled = window.scrollY > 40 ? 'true' : 'false';
    for (const nav of navs) if (nav.dataset.irgScrolled !== scrolled) nav.dataset.irgScrolled = scrolled;
  };
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(refresh); }
  }, {passive:true});
  window.addEventListener('pageshow', refresh);
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || event.defaultPrevented) return;
    const menu = wrapper.querySelector('details[open]');
    if (menu) {
      event.preventDefault();
      menu.open = false;
      menu.querySelector('summary')?.focus();
    }
  });
  refresh();
})();
</script>"""


def main(check_only: bool = False) -> None:
    model = json.loads((ROOT / "content/site.json").read_text())
    metrics = {metric["id"]: metric for metric in model["metrics"]}
    pages = {page["id"]: page for page in model["pages"]}
    page_ids = (*PAGE_IDS, *(page["id"] for page in model["pages"] if page.get("type") in ("guide", "guide-hub")))
    # Check every planned output before writing any page, including all copy
    # later reused in <title>, Open Graph, Twitter and structured data.
    for page_id in page_ids:
        if pages[page_id].get("published", True):
            validate_public_page(pages[page_id], metrics)
    if check_only:
        print("Work-detail publication gates passed; no files generated.")
        return
    baseline = model["baselineCommit"]
    original = subprocess.check_output(["git", "show", f"{baseline}:site/services.html"], cwd=ROOT, text=True)
    tree = SourceTree(original)
    styles = []
    for node in tree.nodes:
        if node.tag == "style":
            raw = tree.raw(node)
            # Framer's custom component style children use escaped attribute
            # selectors in the exported HTML. Restore valid CSS text here.
            opening_end = raw.index(">") + 1
            raw = raw[:opening_end] + html.unescape(raw[opening_end:raw.rfind("</style>")]) + "</style>"
            if raw not in styles:
                styles.append(raw)
    icons = "".join(tree.raw(node) for node in tree.nodes if node.tag == "link" and node.attrs.get("rel") == "icon")
    header = navigation(tree)
    footer = visible_static(tree.raw(tree.find(**{"class": "framer-1di1fr4-container"})))
    svg_defs = tree.raw(tree.find(id="svg-templates"))
    for page_id in page_ids:
        page = pages[page_id]
        if not page.get("published", True):
            (ROOT / "site" / (page["slug"] + ".html")).unlink(missing_ok=True)
            continue
        name = "Holafly" if page_id == "holafly" else page["title"].split(" | ")[0]
        schema = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "WebPage", "@id": page["canonicalUrl"] + "#webpage", "url": page["canonicalUrl"], "name": page["title"], "description": page["description"], "inLanguage": "en", "isPartOf": {"@id": model["site"]["origin"] + "/#website"}},
                {"@type": "BreadcrumbList", "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": model["site"]["origin"] + "/"},
                    {"@type": "ListItem", "position": 2, "name": "Work", "item": model["site"]["origin"] + "/work"},
                    {"@type": "ListItem", "position": 3, "name": name, "item": page["canonicalUrl"]},
                ]},
            ],
        }
        og_image = '<meta property="og:image" content="https://irgmedia.org/assets/holafly-vineyards.webp"><meta property="og:image:alt" content="' + escape(page["image"]["alt"]) + '">' if page_id == "holafly" else ""
        head = f'<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(page["title"])}</title><meta name="description" content="{escape(page["description"])}"><link rel="canonical" href="{escape(page["canonicalUrl"])}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(page["title"])}"><meta property="og:description" content="{escape(page["description"])}"><meta property="og:url" content="{escape(page["canonicalUrl"])}"><meta property="og:site_name" content="IRG Media"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(page["title"])}"><meta name="twitter:description" content="{escape(page["description"])}">{og_image}{icons}'
        contents = hero(page) + "".join(render_section(section, page, metrics) for section in page["sections"])
        document = '<!doctype html>\n<html lang="en" dir="ltr"><head>' + head + "\n" + "\n".join(styles) + '\n<style data-irg-work-detail-css>' + DETAIL_CSS + '</style>\n<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c") + '</script></head><body><a class="irg-detail-skip" href="#content">Skip to content</a>' + (analytics(page_id) if page_id in FRAMER_COLLECTION_IDS else '') + '<div class="framer-ETJuL framer-1j9cupc" data-layout-template="true" style="min-height:100vh;width:auto">' + header + '<main id="content" tabindex="-1" class="irg-work-detail framer-3BEj8 framer-DItOg framer-DjMis framer-LNkJV framer-JKIuJ framer-6KOV1 framer-HPd1a framer-14cxuu0">' + contents + '</main>' + footer + '</div>' + svg_defs + STATIC_NAV_SCRIPT + "</body></html>\n"
        destination = ROOT / "site" / (page["slug"] + ".html")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(document)
        print(f"Built {destination.relative_to(ROOT)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-publication", action="store_true", help="Check public claim permissions without generating HTML")
    main(check_only=parser.parse_args().check_publication)
