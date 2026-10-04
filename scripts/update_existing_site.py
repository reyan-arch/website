#!/usr/bin/env python3
"""Apply bounded additions to the existing Framer mirror, keeping its visual frame.

Core documents always start from the recorded baseline, so this is idempotent.
Work detail generators must run first. Source files and assets remain committed.
"""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
import hashlib
import json
import re
import subprocess
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
MODEL = json.loads((ROOT / 'content/site.json').read_text())
BASELINE = MODEL['baselineCommit']
ORIGIN = 'https://irgmedia.org'
CORE = ['index', 'services', 'approach', 'why-irg', 'work', 'about', 'contact', 'resources', 'privacy']

# The source CMS stays immutable. Public cards/cache receive current approved copy.
HOLAFLY_PAGE = next(page for page in MODEL['pages'] if page['path'] == '/work/holafly')
CASE_STUDY = {
    'path': '/work/holafly',
    'headline': HOLAFLY_PAGE['h1'],
    'focus': [
        {'value': 'Fit', 'label': 'Creator relevance'},
        {'value': 'Delivery', 'label': 'Briefs and coordination'},
        {'value': 'Learning', 'label': 'Next-campaign decisions'}
    ]
}
CASE_PROCESS = 'Continuous sourcing, advance planning, refreshed creative briefs and repeat collaboration connected in an always-on creator programme.'

def cms_text(value):
    # This export stores some Unicode escapes literally inside its JSON values.
    return re.sub(r'\\u([0-9a-fA-F]{4})', lambda match: chr(int(match[1], 16)), value)

def case_scalar_replacements():
    cms = json.loads((ROOT / 'framer-export/cms/Case_Studies.json').read_text())
    fields = {field['name']: field['id'] for field in cms['fields']}
    source = next(item for item in cms['items'] if item['slug'] == 'holafly')['fieldData']
    replacements = {
        'Outcome Headline': CASE_STUDY['headline'],
        'Verified Metrics': CASE_PROCESS,
        'SEO Title': HOLAFLY_PAGE['title'],
        'SEO Description': HOLAFLY_PAGE['description']
    }
    for index, focus in enumerate(CASE_STUDY['focus'], 1):
        replacements['Metric '+str(index)+' Value'] = focus['value']
        replacements['Metric '+str(index)+' Label'] = focus['label']
    return {cms_text(source[fields[name]]['value']): current for name, current in replacements.items()}

CASE_SCALARS = case_scalar_replacements()

COPY_REPLACEMENTS = {
    'index': [{'from': 'We find the right creators for travel, hospitality and lifestyle brands, run the work with you, and keep the learning so next month is stronger than this one.', 'to': 'IRG Media is an influencer marketing agency for travel, hospitality and lifestyle brands. We find the right creators, run the work with your team, and carry the learning into the next campaign.'}],
    'services': [
        {'from': 'IRG connects creator access, campaign operations and performance learning in one operating model.', 'to': 'Connect creator access, campaign operations and performance learning in one operating model.'},
        {'from': 'For travel, hospitality and lifestyle brands, the work starts with context: who needs to care, what makes the experience distinctive and what the campaign needs to achieve. We turn that context into creator decisions, coordinated delivery and a useful next step.', 'to': 'For travel, hospitality and lifestyle brands: define the audience, the distinctive experience and the campaign goal. Use that context to choose creators, coordinate delivery and plan the next step.'}
    ]
}

class Node:
    def __init__(self, tag, attrs, start, open_end, parent=None):
        self.tag, self.attrs, self.start, self.open_end = tag, dict(attrs), start, open_end
        self.end = open_end
        self.parent = parent
        self.children = []

class Tree(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.lines = [0] + [m.end() for m in re.finditer('\n', source)]
        self.nodes, self.stack = [], []
        self.feed(source)
    def pos(self):
        row, col = self.getpos()
        return self.lines[row-1] + col
    def handle_starttag(self, tag, attrs):
        start = self.pos()
        node = Node(tag, attrs, start, start+len(self.get_starttag_text()), self.stack[-1] if self.stack else None)
        self.nodes.append(node)
        if node.parent: node.parent.children.append(node)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:
            self.stack.append(node)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1].tag == tag: self.stack.pop()
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i].tag == tag:
                self.stack[i].end = self.pos()+len('</'+tag+'>')
                del self.stack[i:]
                break

def plain(value):
    return unescape(re.sub('<[^>]+>', '', value)).strip()

def case_route(href):
    return urlparse(href).path.strip('/').removesuffix('.html') == CASE_STUDY['path'].strip('/')

def descendants(tree, parent):
    for node in tree.nodes:
        ancestor = node.parent
        while ancestor:
            if ancestor is parent:
                yield node
                break
            ancestor = ancestor.parent

def case_cards(doc, name):
    if name not in ('index', 'work'): return doc
    tree = Tree(doc)
    changes = {}
    def text(node, value):
        changes[(node.open_end, node.end-len('</'+node.tag+'>'))] = escape(value)
    for node in tree.nodes:
        if 'data-story-cms-item' in node.attrs and node.attrs.get('data-slug') == 'holafly':
            opening = doc[node.start:node.open_end]
            updated = re.sub(r'data-card-title="[^"]*"', 'data-card-title="'+escape(CASE_STUDY['headline'], quote=True)+'"', opening)
            changes[(node.start, node.open_end)] = updated
    for link in tree.nodes:
        if link.tag != 'a' or not case_route(link.attrs.get('href', '')): continue
        if name == 'index':
            card = link.parent
            while card and 'sc-card' not in card.attrs.get('class', '').split(): card = card.parent
            if not card: continue
            for node in descendants(tree, card):
                if node.tag == 'h3' and 'sc-lead' in node.attrs.get('class', '').split(): text(node, CASE_STUDY['headline'])
            opening = doc[link.start:link.open_end]
            if 'aria-label' in link.attrs:
                updated = re.sub(r'aria-label="[^"]*"', 'aria-label="'+escape('See work: '+CASE_STUDY['headline'], quote=True)+'"', opening)
                changes[(link.start, link.open_end)] = updated
        elif link.attrs.get('data-framer-name') == 'Case Study':
            for node in descendants(tree, link):
                if node.tag == 'h2': text(node, CASE_STUDY['headline'])
                for index, focus in enumerate(CASE_STUDY['focus'], 1):
                    if node.attrs.get('data-framer-name') == 'Metric '+str(index):
                        paragraphs = [child for child in descendants(tree, node) if child.tag == 'p']
                        if len(paragraphs) != 2: raise ValueError('Unexpected Holafly metric card structure')
                        text(paragraphs[0], focus['value']); text(paragraphs[1], focus['label'])
    for (start, end), value in sorted(changes.items(), reverse=True): doc = doc[:start]+value+doc[end:]
    return doc

def case_handover(doc):
    pattern = r'(<script\b[^>]*\bid="__framer__handoverData"[^>]*>)(.*?)(</script>)'
    def replace(match):
        graph = json.loads(match[2])
        if not isinstance(graph, list): raise ValueError('Expected Framer handover reference array')
        def visit(value):
            if isinstance(value, str): return CASE_SCALARS.get(value, value)
            if isinstance(value, list): return [visit(item) for item in value]
            if isinstance(value, dict): return {key: visit(item) for key, item in value.items()}
            return value
        # Keep array positions, object keys and every integer reference unchanged.
        return match[1]+json.dumps(visit(graph), ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')+match[3]
    return re.sub(pattern, replace, doc, flags=re.S)

LINKS = {
    'index': [('travel', '/services#travel'), ('hospitality', '/services#hospitality'), ('lifestyle', '/services#lifestyle'), ('Creator relationships', '/services#creator-access'), ('connected delivery', '/services#campaign-operations'), ('learning that carries', '/approach#learn'), ('always-on creator programme', '/work/holafly'), ('campaign operations', '/work/campaign-operations'), ('always-on planning', '/work/always-on-program')],
    'services': [('travel', '/services#travel'), ('hospitality', '/services#hospitality'), ('lifestyle', '/services#lifestyle'), ('one operating model', '/approach'), ('selection criteria', '/approach#assemble'), ('campaign plan', '/approach#run'), ('available content and campaign signals', '/work/holafly#measurement'), ('next creator selection and brief', '/work/always-on-program')],
    'approach': [('creator recommendations', '/services#creator-access'), ('creator selection', '/services#creator-access'), ('creator coordination', '/services#campaign-operations'), ('performance review', '/services#performance-learning'), ('available evidence', '/work/holafly#measurement'), ('the next campaign', '/work/always-on-program')],
    'why-irg': [('creator context', '/services#creator-access'), ('shared record', '/work/campaign-operations'), ('next brief', '/work/always-on-program'), ('available evidence', '/work/holafly#measurement'), ('in-house team', '/about')],
    'about': [('creator judgment', '/services#creator-access'), ('campaign ownership', '/services#campaign-operations'), ('retained learning', '/services#performance-learning'), ('travel', '/services#travel'), ('hospitality', '/services#hospitality'), ('lifestyle', '/services#lifestyle'), ('selection rationale', '/approach#assemble')],
    'work': [('UK, Australia, California and Saudi Arabia', '/work/holafly#markets'), ('continuous sourcing', '/services#creator-access'), ('stronger briefs', '/approach#frame'), ('repeat partnerships', '/work/always-on-program')],
    'contact': [('market', '/services#target-markets'), ('operating challenge', '/approach#run'), ('shape a brief', '/approach#frame')]
}

RELATED = {
    'index': [('/services#target-markets','Travel, hospitality or lifestyle?','Find the relevant brief and service scope.'),('/work/holafly','Explore the Holafly programme','Read how creator sourcing, briefs and repeat collaboration connect.'),('/approach','Inspect the operating model','See the roles, inputs and outputs at each stage.')],
    'services': [('/work/holafly','See the service in practice','Explore the creator programme and connected delivery process.'),('/approach','Inspect how delivery works','Frame, Assemble, Run and Learn with your team.'),('/contact','Discuss your campaign','Bring the market, audience and operating challenge.')],
    'approach': [('/services#campaign-operations','Define the service scope','Connect the operating stages to deliverables.'),('/work/campaign-operations','Explore a delivery example','A clearly labelled campaign operations methodology example.'),('/work/holafly#measurement','Understand the reporting scope','Keep the programme process and reporting boundaries clear.')],
    'why-irg': [('/work/always-on-program','Inspect always-on planning','See how a methodology example carries learning forward.'),('/work/holafly','Read the client programme','Explore sourcing, advance planning and refreshed creative briefs.'),('/services','Define your scope','Understand where IRG supports your team.')],
    'about': [('/approach','See the working relationship','Clear roles and decision points across the campaign.'),('/services#target-markets','Find your category','Travel, hospitality and lifestyle require different briefs.'),('/work','Review work and methodology','Client evidence and planning examples clearly labelled.')],
    'work': [('/services#target-markets','Find your market context','Travel, hospitality and lifestyle sections.'),('/services#performance-learning','Inspect performance learning','See the inputs, evidence and next-step deliverable.'),('/contact','Start with your brief','Discuss the audience and business objective.')],
    'contact': [('/services#target-markets','Explore your market','Review the category questions before sending context.'),('/approach','Understand the next steps','See responsibilities from Frame through Learn.'),('/work/holafly','Review a client programme','Inspect creator selection, briefs and repeat collaboration.')]
}

def related_html(name):
    entries = RELATED.get(name)
    if not entries: return ''
    return '<section class="irg-related" data-irg-addition="related" aria-labelledby="irg-related-title"><div class="irg-related-inner"><p class="irg-eyebrow">Connected context</p><h2 id="irg-related-title">Your next useful step.</h2><div class="irg-related-grid">'+''.join('<a href="'+escape(url)+'"><strong>'+escape(title)+'</strong><span>'+escape(desc)+'</span><span class="irg-related-arrow" aria-hidden="true">↗</span></a>' for url,title,desc in entries)+'</div></div></section>'

def inline_links(doc, name):
    tree = Tree(doc)
    changes = []
    for node in tree.nodes:
        if node.tag != 'p': continue
        parent = node
        excluded = False
        while parent:
            if parent.tag in ['nav','footer','form'] or parent.attrs.get('data-framer-name') == 'Resources CTA': excluded = True
            parent = parent.parent
        raw = doc[node.start:node.end]
        if excluded or '<a ' in raw: continue
        for phrase, href in LINKS.get(name, []):
            # Plain text only. Do not split letter animation markup or existing links.
            raw = re.sub(r'(?<!\w)('+re.escape(phrase)+r')(?!\w)', lambda m:'<a class="irg-context-link" href="'+href+'">'+m.group(1)+'</a>', raw, count=1, flags=re.I)
        if raw != doc[node.start:node.end]: changes.append((node.start,node.end,raw))
    for start,end,value in reversed(changes): doc=doc[:start]+value+doc[end:]
    return doc

def schema(page):
    path=page['path']; name=page['title']
    org={'@type':'Organization','@id':ORIGIN+'/#organization','name':'IRG Media','url':ORIGIN+'/','logo':ORIGIN+'/assets/irg-lockup.svg','email':'reyan@irgmedia.org','description':'Influencer marketing for travel, hospitality and lifestyle brands.'}
    graph=[org,{'@type':'WebSite','@id':ORIGIN+'/#website','name':'IRG Media','url':ORIGIN+'/','publisher':{'@id':org['@id']}},{'@type':'WebPage','@id':ORIGIN+path+'#webpage','name':name,'description':page['description'],'url':ORIGIN+path,'isPartOf':{'@id':ORIGIN+'/#website'}}]
    if path=='/services':
        for ident,title in [('creator-access','Creator access'),('campaign-operations','Campaign operations'),('performance-learning','Performance learning')]:
            graph.append({'@type':'Service','@id':ORIGIN+path+'#'+ident,'name':title,'serviceType':'Influencer marketing','url':ORIGIN+path+'#'+ident,'provider':{'@id':org['@id']}})
    if path!='/':
        chain=[('/', 'Home')]
        if path.startswith('/work/'): chain.append(('/work','Work'))
        chain.append((path,page.get('navTitle',name.split('|')[0].strip())))
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':label,'item':ORIGIN+url} for i,(url,label) in enumerate(chain)]})
    return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')

def meta(doc, attr, key, value):
    pattern=r'<meta\b(?=[^>]*\b'+attr+r'=[\"\"]'+re.escape(key)+r'[\"\"])[^>]*>'
    tag='<meta '+attr+'="'+key+'" content="'+escape(value,quote=True)+'">'
    if re.search(pattern,doc,re.I): return re.sub(pattern,lambda _:tag,doc,flags=re.I)
    return doc.replace('</head>',tag+'\n</head>',1)

def patch(doc,name,page):
    for item in COPY_REPLACEMENTS.get(name, []):
        doc = doc.replace(item['from'], item['to'])
    if name in ('index', 'work'):
        doc = case_handover(case_cards(doc, name))
    # Metadata/identity changes do not alter the existing Framer page structure.
    doc=re.sub(r'<title>.*?</title>',lambda _: '<title>'+escape(page['title'])+'</title>',doc,count=1,flags=re.S)
    for attr,key,value in [('name','description',page['description']),('property','og:title',page['title']),('property','og:description',page['description']),('property','og:url',ORIGIN+page['path']),('property','og:site_name','IRG Media'),('property','og:image',ORIGIN+'/assets/social-preview.png'),('name','twitter:title',page['title']),('name','twitter:description',page['description']),('name','twitter:image',ORIGIN+'/assets/social-preview.png'),('name','theme-color','#191c1f'),('name','robots','noindex,follow' if name=='privacy' else 'index,follow,max-image-preview:large')]:
        doc=meta(doc,attr,key,value)
    doc=re.sub(r'<link\b(?=[^>]*\brel="(?:icon|apple-touch-icon)")[^>]*>','',doc,flags=re.I)
    doc=re.sub(r'<link\b(?=[^>]*\brel="canonical")[^>]*>',lambda _:'<link rel="canonical" href="'+ORIGIN+page['path']+'">',doc,flags=re.I)
    doc=doc.replace('https://agr.studio/', 'https://leadscorer.co/').replace('https://agr.studio','https://leadscorer.co/').replace('by agr.studio','by leadscorer.co')
    if name not in ['resources','privacy']:
        doc=inline_links(doc,name)
        # Letter-by-letter visual spans retain their design, with a readable label.
        doc=re.sub(r'(<h[1-6]\b)([^>]*>)(.*?)(</h[1-6]>)',lambda m:m.group(1)+' aria-label="'+escape(plain(m.group(3)),quote=True)+'"'+m.group(2)+m.group(3)+m.group(4) if 'display:inline-block;opacity:' in m.group(3) else m.group(0),doc,flags=re.S)
    if name=='services':
        doc=doc.replace('data-framer-name="Services / tangible outputs"','data-framer-name="Services / tangible outputs" id="evaluation"',1)
    additions=related_html(name)
    if name=='services' and (ROOT/'content/services-markets.html').exists(): additions=(ROOT/'content/services-markets.html').read_text()+additions
    if additions:
        tree=Tree(doc)
        # Insert before the common footer container, preserving all responsive variants.
        footer=next((n for n in tree.nodes if n.tag=='footer'),None)
        if footer:
            container=footer
            while container.parent and container.parent.attrs.get('id')!='main' and not container.parent.attrs.get('data-framer-page-link') and container.parent.tag not in ['main','body']:
                if 'ssr-variant' in container.parent.attrs.get('class','') or container.parent.attrs.get('class','').endswith('-container'): container=container.parent
                else: break
            doc=doc[:container.start]+additions+doc[container.start:]
        else: doc=doc.replace('</main>',additions+'</main>',1)
    replacements=COPY_REPLACEMENTS.get(name, [])
    config={'page':name,'path':page['path'],'title':page['title'],'description':page['description'],'canonical':ORIGIN+page['path'],'robots':'noindex,follow' if name=='privacy' else 'index,follow,max-image-preview:large','replacements':replacements,'inlineLinks':[{'phrase':p,'href':h} for p,h in LINKS.get(name,[])],'additionHtml':additions}
    if name in ('index', 'work'): config['caseStudy'] = CASE_STUDY
    head='''<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="stylesheet" href="/assets/brand-updates.css"><link rel="stylesheet" href="/assets/content-updates.css"><script defer src="/assets/brand-updates.js"></script><script defer src="/assets/content-updates.js"></script>'''
    if name=='services':head+='<link rel="stylesheet" href="/assets/markets.css">'
    head+='<script id="irg-page-enhancements" type="application/json">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    # Replace any prior generic schema with the grounded graph.
    doc=re.sub(r'<script\b[^>]*type="application/ld\+json"[^>]*>.*?</script>','',doc,flags=re.S|re.I)
    head+='<script type="application/ld+json">'+schema(page)+'</script>'
    doc=doc.replace('</head>',head+'\n</head>',1)
    if name not in ['resources','privacy']:
        target='#main' if name in CORE else '#content'
        doc=re.sub(r'(<body\b[^>]*>)',lambda m:m.group(1)+'<a class="irg-skip-link" href="'+target+'">Skip to content</a>',doc,count=1)
    head, tail = doc.split('</head>',1)
    return re.sub(r'(?m)^[ \t]+$', '', head)+'</head>'+tail

def build():
    pages={p['path']:p for p in MODEL['pages'] if p['path'] in ['/' if n=='index' else '/'+n for n in CORE] or p['path'].startswith('/work/')}
    pages['/']['title']='IRG Media | Influencer Marketing Agency for Travel, Hospitality & Lifestyle'
    pages['/']['description']='IRG Media connects creator selection, campaign operations and performance learning for travel, hospitality and lifestyle brands. Explore the creator programme and operating model.'
    for name in CORE:
        path='/' if name=='index' else '/'+name
        doc=subprocess.check_output(['git','show',BASELINE+':site/'+name+'.html'],cwd=ROOT).decode()
        (SITE/(name+'.html')).write_text(patch(doc,name,pages[path]))
    for file in sorted((SITE/'work').glob('*.html')):
        path='/work/'+file.stem
        if path in pages:
            doc=file.read_text()
            # Detail generators supply a fresh unpatched source before this command.
            if 'id="irg-page-enhancements"' not in doc:
                file.write_text(patch(doc,file.stem,pages[path]))
    routes=[p for p in pages.values() if p.get('indexable') and p.get('published')]
    (SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+escape(ORIGIN+p['path'])+'</loc></url>\n' for p in routes)+'</urlset>\n')
    (SITE/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: https://irgmedia.org/sitemap.xml\n')
    (ROOT/'docs/route-map.json').write_text(json.dumps([{'path':p['path'],'title':p['title'],'type':p['type'],'indexable':p.get('indexable')} for p in pages.values()],indent=2)+'\n')
    print('Applied edits to original Framer layouts; '+str(len(pages))+' existing routes.')

if __name__=='__main__':build()
