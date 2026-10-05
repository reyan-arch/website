#!/usr/bin/env python3
"""Audit the actual retained IRG static routes without submitting forms.

File-backed validity and optional local HTTP GET observations are separate fields.
Baseline comparisons inspect source HTML; they do not certify post-hydration UI.
"""
from collections import Counter, deque
from datetime import datetime, timezone
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urljoin, unquote
from urllib.request import Request, urlopen
import argparse
import csv
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ORIGIN = 'https://irgmedia.org'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
CORE = {'/':'index','/services':'services','/approach':'approach','/why-irg':'why-irg','/work':'work','/about':'about','/contact':'contact','/resources':'resources','/privacy':'privacy'}

class Node:
    def __init__(self, tag, attrs, start, open_end, parent):
        self.tag, self.attrs, self.start, self.open_end = tag, dict(attrs), start, open_end
        self.end, self.parent, self.children, self.text = open_end, parent, [], []

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source, self.nodes, self.stack = source, [], []
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.feed(source)
        self.ids = Counter(n.attrs['id'] for n in self.nodes if n.attrs.get('id'))
        self.title = self.text_of(next((n for n in self.nodes if n.tag == 'title'), None))
        self.canonicals = [n.attrs.get('href','') for n in self.nodes if n.tag == 'link' and 'canonical' in n.attrs.get('rel','').split()]
        self.descriptions = [n.attrs.get('content','') for n in self.nodes if n.tag == 'meta' and n.attrs.get('name') == 'description']
        self.robots = [n.attrs.get('content','') for n in self.nodes if n.tag == 'meta' and n.attrs.get('name') == 'robots']
    def pos(self):
        row, col = self.getpos(); return self.lines[row-1] + col
    def handle_starttag(self, tag, attrs):
        start = self.pos(); n = Node(tag, attrs, start, start + len(self.get_starttag_text()), self.stack[-1] if self.stack else None)
        self.nodes.append(n)
        if n.parent: n.parent.children.append(n)
        if tag not in VOID: self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if self.stack and self.stack[-1].tag == tag: self.stack.pop()
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i].tag == tag:
                self.stack[i].end = self.pos() + len('</'+tag+'>'); del self.stack[i:]; break
    def handle_data(self, value):
        if not self.stack: return
        # Scripts/styles are not public body text; keep their raw text for JSON parsing.
        if self.stack[-1].tag in {'script','style'}: self.stack[-1].text.append(value); return
        if any(n.tag in {'script','style','svg'} for n in self.stack): return
        for n in self.stack: n.text.append(value)
    @staticmethod
    def text_of(node): return re.sub(r'\s+',' ',' '.join(node.text)).strip() if node else ''
    def raw(self,node): return self.source[node.start:node.end]
    def named_sections(self): return Counter(n.attrs.get('data-framer-name','') for n in self.nodes if n.tag == 'section')
    def media(self):
        return Counter(n.attrs['src'] for n in self.nodes if n.tag in {'img','video','source'} and n.attrs.get('src') and any(a.tag=='body' for a in ancestors(n)))
    def forms(self):
        records=[]
        for n in self.nodes:
            if n.tag != 'form': continue
            fields=[{'name':f.attrs.get('name'),'type':f.attrs.get('type',f.tag),'required':'required' in f.attrs} for f in self.nodes if f.tag in {'input','textarea','select'} and n in ancestors(f)]
            records.append({'label':n.attrs.get('data-framer-name'),'action':n.attrs.get('action'),'method':n.attrs.get('method','get'),'fields':fields})
        return records

def ancestors(node):
    result=[]; n=node.parent
    while n: result.append(n); n=n.parent
    return result

def route_for_file(path):
    rel=path.relative_to(SITE).as_posix()
    return '/' if rel=='index.html' else '/'+rel.removesuffix('.html')

def resolve(value, source_route):
    parts=urlsplit(urljoin(ORIGIN+source_route,value))
    if parts.scheme not in {'http','https'}: return {'kind':'special','value':value}
    if parts.netloc.lower() not in {'irgmedia.org','www.irgmedia.org'}: return {'kind':'external','value':value}
    path=unquote(parts.path)
    if path == '/index.html': route='/'
    elif path.endswith('.html'): route=path[:-5].rstrip('/') or '/'
    else: route=path.rstrip('/') or '/'
    candidate=SITE/path.lstrip('/')
    if path=='/': candidate=SITE/'index.html'
    elif not path.endswith('.html') and not candidate.is_file(): candidate=SITE/(path.lstrip('/')+'.html')
    return {'kind':'internal','value':value,'path':path,'route':route,'fragment':unquote(parts.fragment),'file':candidate,'legacyVariant':path.endswith('.html'),'canonicalTarget':ORIGIN+route,'nonPreferredHost':parts.netloc.lower()!='irgmedia.org'}

def link_kind(node):
    chain=[node]+ancestors(node)
    if any(n.tag in {'nav','footer'} or 'navigation' in n.attrs.get('data-framer-name','').lower() for n in chain): return 'navigation'
    if any('irg-related' in n.attrs.get('class','') for n in chain): return 'related'
    return 'contextual'

def http_observation(url):
    try:
        with urlopen(Request(url,headers={'User-Agent':'IRG-Local-Release-Audit/1.0'}),timeout=5) as response:
            body=response.read()
            return {'status':response.status,'finalUrl':response.url,'contentType':response.headers.get('Content-Type'),'bytes':len(body)}
    except Exception as exc: return {'status':getattr(exc,'code',None),'error':str(exc)}

def baseline_source(commit, rel):
    return subprocess.check_output(['git','show',commit+':'+rel],cwd=ROOT).decode()

def string_surfaces(value, skip_matching_inputs=False):
    """Return public output strings; runtime match inputs are implementation rules."""
    if isinstance(value,dict):
        return [s for k,v in value.items() if not (skip_matching_inputs and k=='from') for s in string_surfaces(v,skip_matching_inputs)]
    if isinstance(value,list):return [s for v in value for s in string_surfaces(v,skip_matching_inputs)]
    if isinstance(value,(str,int,float)):return [str(value)]
    return []

def public_surfaces(doc):
    body=next((n for n in doc.nodes if n.tag=='body'),next((n for n in doc.nodes if n.parent is None and n.tag=='section'),None))
    text=[doc.title,doc.text_of(body)]
    for n in doc.nodes:
        for key in ['alt','aria-label','title']:
            if n.attrs.get(key):text.append(n.attrs[key])
        if n.tag=='meta' and n.attrs.get('content'):text.append(n.attrs['content'])
        if n.tag=='script' and n.attrs.get('type') in {'application/ld+json','application/json'}:
            try:text += string_surfaces(json.loads(''.join(n.text)),n.attrs.get('id')=='irg-page-enhancements')
            except json.JSONDecodeError:pass  # General schema validation reports invalid JSON separately.
        if n.tag=='script' and (n.attrs.get('type')=='framer/handover' or n.attrs.get('id')=='__framer__handoverData'):
            def graph_strings(value):
                if isinstance(value,str):return [value]
                if isinstance(value,list):return [s for v in value for s in graph_strings(v)]
                if isinstance(value,dict):return [s for v in value.values() for s in graph_strings(v)]
                return []  # Framer graph integers are reference indices, not campaign figures.
            try:text += graph_strings(json.loads(''.join(n.text)))
            except json.JSONDecodeError:pass
    return text

def withdrawn_patterns(metrics):
    """Use private source fingerprints without repeating confidential values in reports."""
    patterns=[]
    for metric in metrics:
        for token in re.findall(r'\d+(?:\.\d+)?[MK%+]?',metric.get('display','')):
            patterns.append(('withdrawn-metric:'+metric['id'],re.compile(r'(?<![\w.])'+re.escape(token)+r'(?![\w.])',re.I)))
            if token.endswith(('M','K')):
                scale='million' if token.endswith('M') else 'thousand'
                patterns.append(('spelled-unit:'+metric['id'],re.compile(r'(?<![\w.])'+re.escape(token[:-1])+r'\s+'+scale+r'\b',re.I)))
    patterns += [
        ('case-count-in-words',re.compile(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten)(?:\s+(?:reported|creator|organic|million|thousand)){0,3}\s+(?:niches|markets|views|partnerships|reels?)\b',re.I)),
        ('case-reporting-period',re.compile(r'\b(?:January\s*(?:[–—-]|to)\s*August|April\s*(?:[–—-]|to)\s*July|(?:January|April|August|July|June)\s+20\d{2})\b',re.I)),
        ('spelled-case-quantity',re.compile(r'\b(?:eighty[- ]four|seventy[- ]eight|one hundred(?: and)? sixty[- ]one|nine hundred(?: and)? twenty)\b',re.I)),
    ]
    return patterns

def css_urls(source):
    """Consume complete quoted URLs before examining any apparent nested url()."""
    pattern=re.compile(r'''url\(\s*(?:"((?:\\.|[^"\\])*)"|'((?:\\.|[^'\\])*)'|([^\s)]+))\s*\)''',re.I)
    return [next(group for group in match.groups() if group is not None) for match in pattern.finditer(source)]

def check_public_case(model,docs,commit,errors):
    """Enforce current qualitative publication permission, preserving historical evidence."""
    rel='framer-export/cms/Case_Studies.json';raw=baseline_source(commit,rel)
    unchanged=raw==(ROOT/rel).read_text()
    if not unchanged:errors.append({'type':'case-evidence-source-modified','source':rel})
    metrics=model['metrics'];patterns=withdrawn_patterns(metrics)
    ledger_private=bool(metrics) and all(all(m.get(k) is False for k in ['public','approved','approval','published']) for m in metrics)
    if not ledger_private:errors.append({'type':'withdrawn-metric-ledger-publication-gate'})
    public_checks={}
    for route,doc in docs.items():
        findings=sorted({label for text in public_surfaces(doc) for label,pattern in patterns if pattern.search(text)})
        metric_nodes=[n for n in doc.nodes if n.attrs.get('data-metric-id') or 'irg-detail-metric' in n.attrs.get('class','').split()]
        public_checks[route]={'withdrawnNumericClaimsAbsent':not findings,'metricComponentsAbsent':not metric_nodes}
        if findings:errors.append({'type':'withdrawn-holafly-public-copy','route':route,'matchedPrivateFingerprints':findings})
        if metric_nodes:errors.append({'type':'withdrawn-public-metric-component','route':route,'count':len(metric_nodes)})
    model_findings=[]
    for key in ['pages','searchIntentMap']:
        for text in string_surfaces(model[key]):
            model_findings += [label for label,pattern in patterns if pattern.search(text)]
    def has_metric_reference(value):
        if isinstance(value,dict):return bool(set(value)&{'stats','metricId','reportingWindow'}) or any(has_metric_reference(v) for v in value.values())
        if isinstance(value,list):return any(has_metric_reference(v) for v in value)
        return False
    clean_model=not model_findings and not has_metric_reference(model['pages'])
    if not clean_model:errors.append({'type':'withdrawn-metric-public-model-reference','matchedPrivateFingerprints':sorted(set(model_findings))})
    case_page=next(p for p in model['pages'] if p['id']=='holafly')
    case=docs.get('/work/holafly')
    qualitative=anchors=None
    withdrawn=case_page.get('published') is False and case_page.get('indexable') is False
    if withdrawn:
        if case:errors.append({'type':'withdrawn-case-route-still-served'})
        for route,doc in docs.items():
            stale=[n for n in doc.nodes if n.tag=='a' and resolve(n.attrs.get('href',''),route).get('route')=='/work/holafly']
            if stale:errors.append({'type':'withdrawn-case-link','route':route,'count':len(stale)})
    elif case:
        body=case.text_of(next(n for n in case.nodes if n.attrs.get('id')=='content')).lower()
        qualitative=all(word in body for word in ['holafly','sourcing','planning','brief','collaboration'])
        anchors=all(case.ids.get(i)==1 for i in ['content','markets','results','measurement'])
        if not qualitative:errors.append({'type':'qualitative-client-process-missing'})
        if not anchors:errors.append({'type':'qualitative-case-required-anchor'})
        if any(n.tag=='table' for n in case.nodes):errors.append({'type':'withdrawn-case-result-table-present'})
    else:errors.append({'type':'published-case-route-missing'})
    examples={}
    for route in ['/work/campaign-operations','/work/always-on-program','/work/hospitality-travel-brief']:
        text=docs[route].text_of(next(n for n in docs[route].nodes if n.attrs.get('id')=='content')).lower()
        labelled='illustrative' in text and any(t in text for t in ['no client results','no results are claimed','not a client programme or verified performance result'])
        examples[route]={'illustrativeLabelAndNoClientResultsVisible':labelled}
        if not labelled:errors.append({'type':'methodology-example-not-labelled','route':route})
    return {'immutableCmsSource':rel,'sourceSha256':hashlib.sha256(raw.encode()).hexdigest(),'cmsUnchanged':unchanged,'historicalMetricLedgerNonPublicAndUnapproved':ledger_private,'publicModelHasNoMetricReferencesOrClaims':clean_model,'publicRoutes':public_checks,'caseTemporarilyWithdrawn':withdrawn,'caseRouteAbsent':case is None,'qualitativeClientProcessPresent':qualitative,'requiredCaseAnchorsPreserved':anchors,'methodologyLabels':examples,'scope':'Visible initial HTML, accessible text, metadata, JSON-LD and current enhancement output values. Historical private values are not repeated in this report. Browser hydration is checked separately.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--base-url',help='Optional local preview origin, for GET-only route observations.');args=parser.parse_args()
    if args.base_url and urlsplit(args.base_url).hostname not in {'localhost','127.0.0.1','::1'}: parser.error('--base-url must be a loopback preview; no production requests are made')
    model=json.loads((ROOT/'content/site.json').read_text());commit=model['baselineCommit']
    files=sorted(SITE.rglob('*.html'));docs={route_for_file(f):Document(f.read_text()) for f in files}
    sitemap=ET.fromstring((SITE/'sitemap.xml').read_text());sitemap_urls=[e.text for e in sitemap.iter() if e.tag.endswith('loc')]
    rows=[];errors=[];warnings=[];route_records=[];edges={r:set() for r in docs};context_incoming={r:set() for r in docs};http={}
    for route,doc in docs.items():
        expected=ORIGIN+route
        if doc.canonicals != [expected]: errors.append({'type':'canonical','route':route,'actual':doc.canonicals,'expected':expected})
        if not doc.title:errors.append({'type':'missing-title','route':route})
        if len(doc.descriptions)!=1 or not doc.descriptions[0]:errors.append({'type':'description','route':route,'values':doc.descriptions})
        schemas=[]
        for n in doc.nodes:
            if n.tag=='script' and n.attrs.get('type')=='application/ld+json':
                try:schemas.append(json.loads(''.join(n.text)))
                except json.JSONDecodeError as exc:errors.append({'type':'invalid-schema-json','route':route,'error':str(exc)})
        if not schemas:errors.append({'type':'missing-schema','route':route})
        schema_types=[]
        for schema in schemas:
            graph=schema.get('@graph',[schema])
            schema_types += [n.get('@type') for n in graph if isinstance(n,dict)]
        h1count=sum(n.tag=='h1' for n in doc.nodes)
        if h1count!=1:warnings.append({'type':'source-h1-count','route':route,'count':h1count,'note':'Responsive/animated original variants require browser accessibility-tree review; source count alone is not proof of a visible duplicate.'})
        duplicates={i:count for i,count in doc.ids.items() if count>1}
        if duplicates:warnings.append({'type':'duplicate-source-ids','route':route,'count':len(duplicates),'ids':duplicates,'note':'Original responsive variants may duplicate SVG/component identifiers. New fragment IDs are checked separately.'})
        robots=','.join(doc.robots);indexable='noindex' not in robots
        if indexable and expected not in sitemap_urls:errors.append({'type':'indexable-route-absent-sitemap','route':route})
        if not indexable and expected in sitemap_urls:errors.append({'type':'noindex-route-in-sitemap','route':route})
        route_records.append({'path':route,'file':str((SITE/('index.html' if route=='/' else route.lstrip('/')+'.html')).relative_to(ROOT)),'title':doc.title,'description':doc.descriptions[0] if doc.descriptions else None,'canonical':doc.canonicals,'robots':doc.robots,'indexable':indexable,'h1SourceCount':h1count,'schemaTypes':schema_types,'sourceIds':len(doc.ids),'duplicateSourceIds':duplicates})
        for n in doc.nodes:
            if n.tag=='a' and n.attrs.get('href'):
                href=n.attrs['href'];r=resolve(href,route)
                if r['kind']!='internal':continue
                target_doc=docs.get(r['route']);file_exists=r['file'].is_file();frag_valid=not r['fragment'] or bool(target_doc and r['fragment'] in target_doc.ids)
                if file_exists and r['route'] in docs:
                    edges[route].add(r['route'])
                    if link_kind(n)!='navigation' and r['route']!=route:context_incoming[r['route']].add(route)
                row={'sourceUrl':expected,'targetUrl':urljoin(expected,href),'anchor':doc.text_of(n) or n.attrs.get('aria-label') or '(image/icon link)','relationship':link_kind(n),'sourceSection':next((p.attrs.get('id') or p.attrs.get('data-framer-name') for p in ancestors(n) if p.tag=='section'),None),'targetRoute':r['route'],'canonicalTarget':r['canonicalTarget'],'fragment':r['fragment'],'fileExists':file_exists,'fragmentExists':frag_valid,'legacyHtmlVariant':r['legacyVariant'],'nonPreferredHost':r['nonPreferredHost'],'httpStatus':None,'validationMethod':'Committed-file lookup; fragment IDs parsed from source HTML. HTTP status is not inferred.'}
                rows.append(row)
                if not file_exists:errors.append({'type':'broken-internal-link','source':route,'href':href,'resolvedFile':str(r['file'])})
                elif not frag_valid:errors.append({'type':'missing-fragment','source':route,'href':href,'target':r['route'],'fragment':r['fragment']})
            values=[]
            if n.tag in {'img','script','source','video','iframe'} and n.attrs.get('src'):values.append(n.attrs['src'])
            if n.tag=='video' and n.attrs.get('poster'):values.append(n.attrs['poster'])
            if n.tag=='link' and set(n.attrs.get('rel','').split()) & {'stylesheet','preload','icon','apple-touch-icon','modulepreload'} and n.attrs.get('href'):values.append(n.attrs['href'])
            if n.attrs.get('srcset'):values += [x.strip().split()[0] for x in n.attrs['srcset'].split(',') if x.strip()]
            for value in values:
                if value.startswith('data:'):continue
                r=resolve(value,route)
                if r['kind']=='internal' and not r['file'].is_file():errors.append({'type':'missing-local-asset','source':route,'reference':value,'resolvedFile':str(r['file'])})
        if args.base_url:
            http[route]=http_observation(args.base_url.rstrip('/')+route)
            if http[route].get('status')!=200:errors.append({'type':'local-http-route','route':route,'observation':http[route]})
    # Relative asset references in committed CSS, excluding remote URLs and SVG fragment paint servers.
    for css in SITE.rglob('*.css'):
        for value in css_urls(css.read_text()):
            value=value.strip()
            if value.startswith(('data:','#','http:','https:','//')):continue
            target=SITE/value.lstrip('/') if value.startswith('/') else css.parent/value.split('?')[0].split('#')[0]
            if not target.is_file():errors.append({'type':'missing-css-asset','source':str(css.relative_to(ROOT)),'reference':value,'resolvedFile':str(target)})
    for key in ['title','description']:
        vals=Counter((r[key] or '') for r in route_records)
        repeated={v:c for v,c in vals.items() if v and c>1}
        if repeated:errors.append({'type':'duplicate-'+key,'values':repeated})
    for url in sitemap_urls:
        path=urlsplit(url).path.rstrip('/') or '/'
        if path not in docs:errors.append({'type':'sitemap-missing-route','url':url})
    distances={'/':0};q=deque(['/'])
    while q:
        r=q.popleft()
        for target in sorted(edges.get(r,[])):
            if target not in distances:distances[target]=distances[r]+1;q.append(target)
    orphans=sorted(set(docs)-set(distances));context_orphans=sorted(r for r in docs if r!='/' and not context_incoming[r])
    if orphans:errors.append({'type':'unreachable-routes-from-home','routes':orphans})
    # Compare the retained core page frame and protected Resources content against Git.
    preservation={}
    for route,name in CORE.items():
        if route not in docs:continue
        before=Document(baseline_source(commit,'site/'+name+'.html'));after=docs[route]
        named_missing=dict(before.named_sections()-after.named_sections())
        media_missing=dict(before.media()-after.media())
        preservation[route]={'originalSectionCount':sum(n.tag=='section' for n in before.nodes),'updatedSectionCount':sum(n.tag=='section' for n in after.nodes),'missingOriginalNamedSections':named_missing,'missingOriginalBodyMedia':media_missing,'sourceFrameRetained':not named_missing and not media_missing,'uiVerification':'Source structure/media comparison only. Browser rendering and hydration are separately verified.'}
        preservation[route]['originalH1SourceCount']=sum(n.tag=='h1' for n in before.nodes)
        if named_missing or media_missing:errors.append({'type':'core-source-frame-changed','route':route,'missingSections':named_missing,'missingMedia':media_missing})
        if route=='/':
            before_resource=next((n for n in before.nodes if n.tag=='section' and n.attrs.get('data-framer-name')=='Resources CTA'),None)
            after_resource=next((n for n in after.nodes if n.tag=='section' and n.attrs.get('data-framer-name')=='Resources CTA'),None)
            same=bool(before_resource and after_resource and before.raw(before_resource)==after.raw(after_resource))
            preservation[route]['protectedResourceSectionExact']=same
            if not same:errors.append({'type':'home-resource-section-modified'})
        if route=='/resources':
            before_body=next(n for n in before.nodes if n.tag=='body');after_body=next(n for n in after.nodes if n.tag=='body')
            # Latest user UI request permits these exact cosmetic labels; the
            # resource copy, workflow and protected Home block remain unchanged.
            cosmetic_changes={'by agr.studio':'by leadscorer.co','START A PROJECT':'Start a project','SEND ENQUIRY':'Send enquiry','reyan@irgmedia.org':model['site']['email']}
            def normalize(text):
                for old,new in cosmetic_changes.items():text=text.replace(old,new)
                return text
            same_text=normalize(before.text_of(before_body))==normalize(after.text_of(after_body))
            same_forms=before.forms()==after.forms()
            preservation[route].update({'bodyTextPreservedExceptApprovedCosmetics':same_text,'authorisedCosmeticTextChanges':cosmetic_changes,'cosmeticAuthorityNote':'Latest user styling instruction authorises only these label-case changes alongside the previously authorised footer credit. The 5 October user request additionally authorises the public contact email change. Form fields/actions and the exact Home Resource block receive no additional exemption.','formsPreserved':same_forms,'baselineForms':before.forms(),'updatedForms':after.forms()})
            if not same_text or not same_forms:errors.append({'type':'resource-body-or-form-modified','bodyText':same_text,'forms':same_forms})
    # Historical values stay private; current publication permission takes precedence.
    metrics={m['id']:m for m in model['metrics']};sources={s['id']:s for s in model['sources']}
    checks={ident:{'passed':all(m.get(k) is False for k in ['public','approved','approval','published']) and m.get('sourceRefs')==['holafly-cms','holafly-reports'] and m.get('independentlyAudited') is False,'public':m.get('public'),'approved':m.get('approved'),'approval':m.get('approval'),'published':m.get('published')} for ident,m in metrics.items()}
    if not all(c['passed'] for c in checks.values()):errors.append({'type':'historical-metric-publication-restriction'})
    source=sources.get('holafly-cms',{})
    if source.get('baselineCommit')!=commit or commit not in source.get('immutableUrl',''):errors.append({'type':'case-source-not-immutable-baseline'})
    public_case_checks=check_public_case(model,docs,commit,errors)
    for route,doc in docs.items():
        if re.search(r'(?:reyan|alex)@irgmedia\.org',doc.source,re.I):errors.append({'type':'stale-public-contact-email','route':route})
        if model['site']['email'] not in doc.source:errors.append({'type':'current-public-contact-email-missing','route':route})
    model_published={p['path'] for p in model['pages'] if p['published']}
    if model_published!=set(docs):errors.append({'type':'model-published-route-mismatch','missingPublicFiles':sorted(model_published-set(docs)),'unregisteredFiles':sorted(set(docs)-model_published)})
    cancelled=[p['path'] for p in model['pages'] if p['id'] in {'industries','travel','hospitality'} and (p['published'] or p['indexable'])]
    if cancelled:errors.append({'type':'cancelled-route-still-published-in-model','routes':cancelled})
    sector=Document((ROOT/'content/services-markets.html').read_text());sector_ids=['target-markets','travel','hospitality','lifestyle']
    if any(docs['/services'].ids[i]!=1 for i in sector_ids):errors.append({'type':'sector-fragment-count','counts':{i:docs['/services'].ids[i] for i in sector_ids}})
    sector_root=next(n for n in sector.nodes if n.attrs.get('id')=='target-markets')
    inserted_root=next((n for n in docs['/services'].nodes if n.attrs.get('id')=='target-markets'),None)
    sector_current=bool(inserted_root and sector.raw(sector_root).strip()==docs['/services'].raw(inserted_root).strip())
    if not sector_current:errors.append({'type':'sector-fragment-not-current','expectedSource':'content/services-markets.html','target':'site/services.html#target-markets'})
    if any(n.attrs.get('href','').startswith('/industries') for n in docs['/services'].nodes if n.tag=='a'):errors.append({'type':'cancelled-industry-link-public'})
    if args.base_url:
        for row in rows: row['httpStatus']=http.get(row['targetRoute'],{}).get('status')
    report={'generatedAt':datetime.now(timezone.utc).isoformat(),'scope':'Actual retained IRG static documents; read-only source and optional loopback GET audit. No forms submitted.','baselineCommit':commit,'summary':{'routes':len(docs),'sitemapEntries':len(sitemap_urls),'internalLinkInstances':len(rows),'uniqueRouteEdges':sum(len(v) for v in edges.values()),'errors':len(errors),'warnings':len(warnings),'orphanRoutes':orphans,'routesWithoutContextualIncoming':context_orphans,'maximumNavigationDepth':max(distances.values())},'routes':[dict(r,depthFromHome=distances.get(r['path']),contextualIncoming=sorted(context_incoming[r['path']])) for r in route_records],'preservation':preservation,'metricChecks':checks,'publicCaseChecks':public_case_checks,'links':rows,'errors':errors,'warnings':warnings,'localHttp':http,'limitations':['Remote CDN assets/external reference destinations not fetched by this audit.','No live form submission, resource fulfilment or production HTTP behaviour tested.','Source HTML checks do not establish post-hydration accessibility, visible layout or field performance.','Original responsive H1/SVG-ID repetitions are warnings requiring browser review, not proof of new visual defects.']}
    (ROOT/'docs').mkdir(exist_ok=True);(ROOT/'docs/link-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with (ROOT/'docs/link-audit.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['sourceUrl','targetUrl'],lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps(report['summary'],indent=2))
    if errors: print(json.dumps(errors[:25],ensure_ascii=False,indent=2))
    raise SystemExit(1 if errors else 0)

if __name__=='__main__':main()
