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

def table_rows(doc):
    """Preserve column order so a valid number in the wrong column cannot pass."""
    return [[doc.text_of(c) for c in n.children if c.tag in {'th','td'}]
            for n in doc.nodes if n.tag == 'tr']

def check_public_case(model, docs, commit, errors):
    """Check the immutable CMS evidence, model and rendered case independently."""
    rel = 'framer-export/cms/Case_Studies.json'
    raw = baseline_source(commit, rel)
    cms = json.loads(raw)
    fields = {f['id']:f['name'] for f in cms['fields']}
    case = next(i for i in cms['items'] if i['slug'] == 'holafly')
    values = {fields.get(k,k):v.get('value') for k,v in case['fieldData'].items()}
    unchanged = raw == (ROOT/rel).read_text()
    if not unchanged: errors.append({'type':'case-evidence-source-modified','source':rel})
    before_table = table_rows(Document(values['Results']))
    public = docs['/work/holafly']
    after_table = table_rows(public)
    same_table = before_table == after_table
    if not same_table: errors.append({'type':'public-case-market-table-changed','expected':before_table,'actual':after_table})
    metric_nodes = [n for n in public.nodes if 'irg-detail-metric' in n.attrs.get('class','').split()]
    metrics = {m['id']:m for m in model['metrics']}
    snapshot_ids = ['holafly-organic-views','holafly-reported-reach','holafly-partnerships','holafly-content-pieces','holafly-cost-reduction','holafly-monthly-view-growth']
    public_checks = {}
    for ident in snapshot_ids:
        record = metrics[ident]
        tokens = [record['display'], record['unit'], record['period']]
        if record['baseline']: tokens.append(record['baseline'])
        matched = any(all(token in public.text_of(n) for token in tokens) for n in metric_nodes)
        public_checks[ident] = {'passed':matched,'requiredValueUnitPeriodBaseline':tokens}
        if not matched: errors.append({'type':'public-case-snapshot-metric','metricId':ident,'expectedTokens':tokens})
    # Twelve August cells use distinct view-target and planned-cost baselines.
    market_checks = {}
    for row in before_table[1:]:
        market = row[0].lower().replace(' ','-')
        for suffix,display,unit,baseline in zip(['views','target','cost'],row[1:],['organic views','comparison with view target','cost below planned cost'],[None,'Market view target','Planned cost']):
            ident = 'holafly-august-'+market+'-'+suffix
            record = metrics.get(ident,{})
            valid = all(record.get(k)==v for k,v in {'display':display,'unit':unit,'period':'August 2026','baseline':baseline}.items())
            market_checks[ident] = {'passed':valid,'sourceDisplay':display,'baseline':baseline}
            if not valid: errors.append({'type':'market-metric-definition','metricId':ident})
    public_text = public.text_of(next(n for n in public.nodes if n.attrs.get('id')=='content'))
    provenance_tokens = ['IRG-reported results','underlying reports','independent audit','Reported reach is kept separate from organic views','programme-level platform mix is not established']
    provenance_visible = all(t.lower() in public_text.lower() for t in provenance_tokens)
    if not provenance_visible: errors.append({'type':'public-case-provenance-caveat-missing'})
    creator_checks = {}
    for ident,display,unit,period,baseline in [('holafly-vineyards-views','998K','views','Within January–August 2026; individual date not supplied',None),('holafly-obaydfox-views','1.01M','views','Within January–August 2026; individual date not supplied',None),('holafly-ben-reid-views','450K → 3M+','views','July 2026','Approximately 450K average views on previous content')]:
        record = metrics.get(ident,{})
        valid = all(record.get(k)==v for k,v in {'display':display,'unit':unit,'period':period,'baseline':baseline}.items())
        creator_checks[ident] = {'passed':valid,'sourceDisplay':display,'period':period,'baseline':baseline}
        if not valid: errors.append({'type':'creator-example-metric-definition','metricId':ident})
    all_provenance = all(m.get('sourceRefs')==['holafly-cms','holafly-reports'] and m.get('caveat') and m.get('independentlyAudited') is False for m in metrics.values())
    if not all_provenance or len(metrics)!=21: errors.append({'type':'all-case-metric-provenance','metricCount':len(metrics),'passed':all_provenance})
    examples = {}
    for route in ['/work/campaign-operations','/work/always-on-program','/work/hospitality-travel-brief']:
        text = docs[route].text_of(next(n for n in docs[route].nodes if n.attrs.get('id')=='content'))
        lowered = text.lower()
        labelled = 'illustrative' in lowered and any(t in lowered for t in ['no client results','no results are claimed','not a client programme or verified performance result'])
        examples[route] = {'illustrativeLabelAndNoClientResultsVisible':labelled}
        if not labelled: errors.append({'type':'methodology-example-not-labelled','route':route})
    return {'immutableCmsSource':rel,'sourceSha256':hashlib.sha256(raw.encode()).hexdigest(),'cmsUnchanged':unchanged,'publicMarketTableExactlyMatchesCms':same_table,'snapshotMetrics':public_checks,'augustMarketMetrics':market_checks,'creatorMetrics':creator_checks,'all21MetricsHaveSourceAndUnauditedCaveat':all_provenance,'publicMeasurementCaveatsVisible':provenance_visible,'methodologyLabels':examples}

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
        for value in re.findall(r'url\(\s*[\'\"]?([^\)\'\"]+)',css.read_text()):
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
            normalize=lambda text:text.replace('by agr.studio','by leadscorer.co')
            same_text=normalize(before.text_of(before_body))==normalize(after.text_of(after_body))
            same_forms=before.forms()==after.forms()
            preservation[route].update({'bodyTextPreservedExceptCredit':same_text,'formsPreserved':same_forms,'baselineForms':before.forms(),'updatedForms':after.forms()})
            if not same_text or not same_forms:errors.append({'type':'resource-body-or-form-modified','bodyText':same_text,'forms':same_forms})
    # Exact metric/provenance checks retain distinctions, periods and baselines.
    metrics={m['id']:m for m in model['metrics']};sources={s['id']:s for s in model['sources']}
    checks={}
    for ident,display,period,baseline in [('holafly-organic-views','84.3M','January–August 2026',None),('holafly-reported-reach','78.8M','January–August 2026',None),('holafly-partnerships','161','January–August 2026',None),('holafly-content-pieces','920+','January–August 2026',None),('holafly-cost-reduction','56%','By July 2026','Programme start'),('holafly-monthly-view-growth','169%','April–July 2026','April 2026 monthly organic views')]:
        record=metrics.get(ident,{})
        passed=record.get('display')==display and record.get('period')==period and record.get('baseline')==baseline and record.get('sourceRefs')==['holafly-cms','holafly-reports'] and bool(record.get('caveat')) and record.get('independentlyAudited') is False
        checks[ident]={'passed':passed,'display':record.get('display'),'period':record.get('period'),'baseline':record.get('baseline'),'independentlyAudited':record.get('independentlyAudited')}
        if not passed:errors.append({'type':'metric-provenance-or-definition','metricId':ident})
    source=sources.get('holafly-cms',{})
    if source.get('baselineCommit')!=commit or commit not in source.get('immutableUrl',''):errors.append({'type':'case-source-not-immutable-baseline'})
    public_case_checks=check_public_case(model,docs,commit,errors)
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
