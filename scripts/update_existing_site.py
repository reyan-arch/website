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
HOME_FAQ = json.loads((ROOT / 'content/home-faq.json').read_text())['items']
IMAGE_LINKS = json.loads((ROOT / 'content/image-links.json').read_text())
CONTACT_BOOKING = (ROOT / 'content/contact-booking.html').read_text()
BOOKING_JUMP = '<a class="irg-update-button irg-booking-jump" href="#book-a-call"><span>Book a discovery call</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v16m-6-6 6 6 6-6"/></svg></a>'
BASELINE = MODEL['baselineCommit']
ORIGIN = 'https://irgmedia.org'
CORE = ['index', 'services', 'approach', 'why-irg', 'work', 'about', 'contact', 'resources', 'privacy']

# The source CMS stays immutable. Public cards/cache receive current approved copy.
HOLAFLY_PAGE = next(page for page in MODEL['pages'] if page['path'] == '/work/holafly')
CASE_STUDY = {
    'path': '/work/holafly',
    'published': HOLAFLY_PAGE['published'],
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

# Publish finished descriptions of the operating guides. The archival CMS is
# unchanged; these same scalar replacements also update Framer's handover data.
WORK_CARD_COPY = [
    {'from':'Format example. How IRG operates a campaign once the roster is set. No client named.', 'to':'Briefing, creator coordination, approvals and delivery, managed in one connected flow.'},
    {'from':'Format example. How an always-on program would be framed for lifestyle brands.', 'to':'Retain creator context, refine each brief and carry learning into the next lifestyle campaign.'},
    {'from':'Format example. A travel and hospitality brief showing how a published case will sit on this rail. Not a named brand.', 'to':'Plan travel and hospitality campaigns around the audience, the experience and the practical details.'},
    {'from':'Briefs, approvals, and delivery in one run', 'to':'From brief to delivery'},
    {'from':'A retained creator rhythm, not a one-off burst', 'to':'Build an ongoing creator programme'},
    {'from':'A hospitality stay, told through the right creators', 'to':'Plan a travel or hospitality campaign'},
    {'from':'Reference still: a working conversation. Format example, not a client campaign.', 'to':'A working conversation about campaign delivery'},
    {'from':'Reference still: people reviewing creative work. Format example, not a client campaign.', 'to':'People reviewing creative work'},
    {'from':'Reference still: a creator photographing a city. Format example, not a client campaign.', 'to':'A creator photographing a city'},
    {'from':'Labelled format example. Not a client case or verified result.', 'to':'A planning guide to IRG’s creator campaign approach.'},
    {'from':'Format example', 'to':'Planning guide'},
]
CASE_SCALARS.update({item['from']:item['to'] for item in WORK_CARD_COPY})

COPY_REPLACEMENTS = {
    'index': [{'from':'Explore our Holafly case study and examples of how we work.','to':'Explore how IRG connects creator briefs, campaign delivery and ongoing programmes.'}, {'from': 'We find the right creators for travel, hospitality and lifestyle brands, run the work with you, and keep the learning so next month is stronger than this one.', 'to': 'IRG Media is an influencer marketing agency for travel, hospitality, entertainment and lifestyle brands. We find the right creators, run the work with your team, and carry the learning into the next campaign.'}],
    'work': [{'from':'A Holafly case study, alongside labelled examples of how we work.','to':'Explore IRG’s approach to creator briefs, campaign delivery and ongoing programmes.'}],
    'services': [
        {'from': 'IRG connects creator access, campaign operations and performance learning in one operating model.', 'to': 'Connect creator access, campaign operations and performance learning in one operating model.'},
        {'from': 'For travel, hospitality and lifestyle brands, the work starts with context: who needs to care, what makes the experience distinctive and what the campaign needs to achieve. We turn that context into creator decisions, coordinated delivery and a useful next step.', 'to': 'For travel, hospitality, entertainment and lifestyle brands: define the audience, the distinctive experience and the campaign goal. Use that context to choose creators, coordinate delivery and plan the next step.'}
    ]
}

for _page in ('index','work'):
    COPY_REPLACEMENTS[_page].extend(WORK_CARD_COPY)

for _page in ('about', 'approach', 'why-irg', 'work', 'contact'):
    COPY_REPLACEMENTS.setdefault(_page, []).append({'from': 'travel, hospitality and lifestyle', 'to': 'travel, hospitality, entertainment and lifestyle'})

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

def faq_html():
    items = []
    for item in HOME_FAQ:
        answer = escape(item['answer'])
        for link in item['links']:
            label = escape(link['label'])
            if answer.count(label) != 1:
                raise ValueError('FAQ link must match one answer phrase: '+link['label'])
            answer = answer.replace(label, '<a href="'+escape(link['href'], quote=True)+'">'+label+'</a>', 1)
        items.append('<details class="irg-faq-item" data-irg-faq-key="'+escape(item['key'], quote=True)+'"><summary><h3>'+escape(item['question'])+'</h3><span class="irg-faq-icon" aria-hidden="true"></span></summary><p>'+answer+'</p></details>')
    return ''.join(items)

def home_faq(doc):
    tree = Tree(doc)
    lists = [node for node in tree.nodes if node.attrs.get('data-framer-name') == 'FAQ List']
    if not lists:
        raise ValueError('Original Home FAQ List is missing')
    expected = [item['question'] for item in HOME_FAQ]
    changes = []
    for node in lists:
        questions = [plain(doc[child.open_end:child.end-len('</h3>')]) for child in descendants(tree, node) if child.tag == 'h3']
        if questions != expected:
            raise ValueError('Original Home FAQ questions changed')
        changes.append((node.open_end, node.end-len('</'+node.tag+'>'), faq_html()))
    for start, end, value in reversed(changes):
        doc = doc[:start]+value+doc[end:]
    return doc

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

def withdrawn_case_content(doc):
    """Keep React-owned frames, but unpublish this case's cards and CMS markers."""
    if CASE_STUDY['published']: return doc
    tree = Tree(doc)
    changes = {}
    hidden = set()
    for node in tree.nodes:
        if node.attrs.get('data-slug') == 'holafly' and 'data-story-cms-item' in node.attrs:
            opening = doc[node.start:node.open_end]
            opening = re.sub(r'\sdata-story-cms-item(?:="[^"]*")?', '', opening)
            opening = re.sub(r'data-button-link="[^"]*"', 'data-button-link="/work"', opening)
            changes[node.start] = (node.open_end, opening[:-1]+' hidden data-irg-withdrawn="true">')
        if node.tag != 'a' or not case_route(node.attrs.get('href', '')): continue
        opening = re.sub(r'href="[^"]*"', 'href="/work"', doc[node.start:node.open_end])
        changes[node.start] = (node.open_end, opening)
        card = node
        while card:
            if 'sc-card' in card.attrs.get('class', '').split() or card.attrs.get('data-framer-name') == 'Case Study':
                hidden.add(card)
                break
            card = card.parent
    for card in hidden:
        end, opening = changes.get(card.start, (card.open_end, doc[card.start:card.open_end]))
        changes[card.start] = (end, opening[:-1]+' hidden data-irg-withdrawn="true">')
    for start, (end, value) in sorted(changes.items(), reverse=True): doc = doc[:start]+value+doc[end:]
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
    'index': [('travel', '/services#travel'), ('hospitality', '/services#hospitality'), ('entertainment', '/services#entertainment'), ('lifestyle', '/services#lifestyle'), ('Creator relationships', '/services#creator-access'), ('connected delivery', '/services#campaign-operations'), ('learning that carries', '/approach#learn'), ('always-on creator programme', '/work/always-on-program'), ('campaign operations', '/work/campaign-operations'), ('always-on planning', '/work/always-on-program')],
    'services': [('travel', '/services#travel'), ('hospitality', '/services#hospitality'), ('entertainment', '/services#entertainment'), ('lifestyle', '/services#lifestyle'), ('one operating model', '/approach'), ('selection criteria', '/approach#assemble'), ('campaign plan', '/approach#run'), ('available content and campaign signals', '/services#performance-learning'), ('next creator selection and brief', '/work/always-on-program')],
    'approach': [('creator recommendations', '/services#creator-access'), ('creator selection', '/services#creator-access'), ('creator coordination', '/services#campaign-operations'), ('performance review', '/services#performance-learning'), ('available evidence', '/services#performance-learning'), ('the next campaign', '/work/always-on-program')],
    'why-irg': [('creator context', '/services#creator-access'), ('shared record', '/work/campaign-operations'), ('next brief', '/work/always-on-program'), ('available evidence', '/services#performance-learning'), ('in-house team', '/about')],
    'about': [('creator judgment', '/services#creator-access'), ('campaign ownership', '/services#campaign-operations'), ('retained learning', '/services#performance-learning'), ('travel', '/services#travel'), ('hospitality', '/services#hospitality'), ('entertainment', '/services#entertainment'), ('lifestyle', '/services#lifestyle'), ('selection rationale', '/approach#assemble')],
    'work': [('UK, Australia, California and Saudi Arabia', '/services#travel'), ('continuous sourcing', '/services#creator-access'), ('stronger briefs', '/approach#frame'), ('repeat partnerships', '/work/always-on-program')],
    'contact': [('market', '/services#target-markets'), ('operating challenge', '/approach#run'), ('shape a brief', '/approach#frame')]
}

HOME_IMAGE_CARDS = [
    {'name': 'Old Model', 'href': '/services#creator-access', 'label': 'Creator relationships — explore creator access'},
    {'name': 'IRG Model', 'href': '/services#campaign-operations', 'label': 'Connected delivery — explore campaign operations'}
]

def image_cards(doc):
    # Retain Framer's original image/copy frame; a native link covers its bounds.
    tree = Tree(doc)
    changes = []
    for card in HOME_IMAGE_CARDS:
        panels = [node for node in tree.nodes if node.attrs.get('data-framer-name') == card['name']]
        if not panels:
            raise ValueError('Original Home image panel missing: '+card['name'])
        for panel in panels:
            if panel.attrs.get('data-irg-image-card'):
                continue
            if any(node.tag == 'a' for node in descendants(tree, panel)):
                raise ValueError('Home image panel already contains a link: '+card['name'])
            opening = doc[panel.start:panel.open_end]
            changes.append((panel.start, panel.open_end, opening[:-1]+' data-irg-image-card="true">'))
            link = '<a class="irg-image-card-link" href="'+escape(card['href'], quote=True)+'" aria-label="'+escape(card['label'], quote=True)+'"></a>'
            end = panel.end-len('</'+panel.tag+'>')
            changes.append((end, end, link))
    for start, end, value in sorted(changes, reverse=True):
        doc = doc[:start]+value+doc[end:]
    return doc

def linked_images(doc, name):
    """Give public photography a relevant native link without moving its nodes."""
    tree = Tree(doc)
    attrs, overlays = {}, {}
    def mark(node, key, value='true'):
        if key not in node.attrs: attrs.setdefault(node.start, (node, {}))[1][key] = value
    for image in [node for node in tree.nodes if node.tag == 'img']:
        ancestors=[]; parent=image.parent
        while parent:
            ancestors.append(parent); parent=parent.parent
        # CMS handover thumbnails are hidden metadata, rather than public photos.
        if any(node.attrs.get('data-framer-name') == 'Work CMS source' for node in ancestors): continue
        # Resource text/delivery stays protected; its photo link is added at runtime.
        if any(node.attrs.get('data-framer-name') == 'Resources CTA' for node in ancestors): continue
        anchor=next((node for node in ancestors if node.tag=='a' and node.attrs.get('href')), None)
        if anchor:
            mark(anchor,'data-irg-media-hover'); continue
        frame=None; destination=None
        carousel=next((node for node in ancestors if 'sc-card' in node.attrs.get('class','').split()),None)
        if carousel:
            action=next((node for node in descendants(tree,carousel) if node.tag=='a' and 'sc-link' in node.attrs.get('class','').split()),None)
            if action:
                frame=image.parent; destination={'href':action.attrs['href'],'label':action.attrs.get('aria-label','Explore this work example')}
        if not frame:
            for node in ancestors:
                rule=next((rule for rule in IMAGE_LINKS['rules'] if node.attrs.get('data-framer-name') in rule['names']),None)
                if rule:
                    frame=node; destination=rule; break
        if not frame:
            frame=next((node for node in ancestors if node.attrs.get('data-framer-name')),image.parent)
            destination=IMAGE_LINKS['defaults'].get(name)
        if not frame or not destination: raise ValueError('Unmapped public image on '+name)
        mark(frame,'data-irg-media-frame')
        if destination.get('gallery'): mark(frame,'data-irg-media-gallery')
        current=[node for node in descendants(tree,frame) if node.tag=='a' and any(cls in node.attrs.get('class','').split() for cls in ('irg-media-link','irg-image-card-link'))]
        if current or frame.start in overlays: continue
        link='<a class="irg-media-link" href="'+escape(destination['href'],quote=True)+'" aria-label="'+escape(destination['label'],quote=True)+'"></a>'
        overlays[frame.start]=(frame.end-len('</'+frame.tag+'>'),link)
    changes=[]
    for node, values in attrs.values():
        opening=doc[node.start:node.open_end]
        extra=''.join(' '+key+'="'+escape(value,quote=True)+'"' for key,value in values.items())
        changes.append((node.start,node.open_end,opening[:-1]+extra+'>'))
    changes.extend((end,end,link) for end,link in overlays.values())
    for start,end,value in sorted(changes,reverse=True): doc=doc[:start]+value+doc[end:]
    return doc

RELATED = {
    'index': [('/services#target-markets','Travel, hospitality or entertainment?','Find the relevant brief and service scope.'),('/guides','Plan your creator campaign','Guides to agency selection, briefs, measurement and content rights.'),('/approach','Inspect the operating model','See the roles, inputs and outputs at each stage.')],
    'services': [('/guides','Explore campaign planning guides','Build the brief, define measurement and agree content use.'),('/approach','Inspect how delivery works','Frame, Assemble, Run and Learn with your team.'),('/contact','Discuss your campaign','Bring the market, audience and operating challenge.')],
    'approach': [('/services#campaign-operations','Define the service scope','Connect the operating stages to deliverables.'),('/guides/influencer-campaign-brief','Build the working brief','Turn the objective and audience into creator decisions.'),('/services#performance-learning','Understand the reporting scope','Keep the programme process and reporting boundaries clear.')],
    'why-irg': [('/work/always-on-program','Inspect always-on planning','See how a methodology example carries learning forward.'),('/services#creator-access','Explore creator selection','Understand sourcing, audience relevance and shortlist rationale.'),('/guides/choosing-an-influencer-marketing-agency','Compare agency fit','Evaluate the scope, responsibilities and evidence you need.')],
    'about': [('/approach','See the working relationship','Clear roles and decision points across the campaign.'),('/services#target-markets','Find your category','Travel, hospitality, entertainment and lifestyle require different briefs.'),('/guides','Read the campaign guides','Practical planning from IRG Media, connected to our service scope.')],
    'work': [('/services#target-markets','Find your market context','Travel, hospitality, entertainment and lifestyle sections.'),('/guides/influencer-campaign-measurement','Plan campaign measurement','Connect the objective, data and next decision.'),('/contact','Start with your brief','Discuss the audience and business objective.')],
    'contact': [('/services#target-markets','Explore your market','Review the category questions before sending context.'),('/approach','Understand the next steps','See responsibilities from Frame through Learn.'),('/work','Explore campaign planning','Creator briefs, campaign delivery and ongoing programmes.')]
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
            if parent.tag in ['a','nav','footer','form'] or parent.attrs.get('data-framer-name') in ('Resources CTA', 'Full-image card / protected copy') or parent.attrs.get('data-irg-image-card') or parent.attrs.get('data-irg-media-frame'): excluded = True
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
    site=MODEL['site']; org_id=site.get('entityId',ORIGIN+'/#organization'); website_id=site.get('websiteId',ORIGIN+'/#website')
    org={'@type':'Organization','@id':org_id,'name':site['name'],'url':ORIGIN+'/','logo':ORIGIN+'/assets/irg-lockup.svg','email':site['email'],'description':site['descriptor']}
    website={'@type':'WebSite','@id':website_id,'name':site['name'],'url':ORIGIN+'/','inLanguage':site['language'],'publisher':{'@id':org_id}}
    if site.get('alternateNames'):
        org['alternateName']=site['alternateNames']; website['alternateName']=site['alternateNames']
    graph=[org,website,{'@type':'WebPage','@id':ORIGIN+path+'#webpage','name':name,'description':page['description'],'url':ORIGIN+path,'inLanguage':site['language'],'isPartOf':{'@id':website_id},'publisher':{'@id':org_id}}]
    if path=='/':
        graph[2]['@type']=['WebPage','FAQPage']
        graph[2]['mainEntity']=[{'@type':'Question','name':item['question'],'acceptedAnswer':{'@type':'Answer','text':item['answer']}} for item in HOME_FAQ]
    if page['type'] in ('guide','guide-hub'):
        graph[2]['datePublished']=page['publishedAt']
        graph[2]['dateModified']=page['reviewedAt']
        if page['type']=='guide':
            article_id=ORIGIN+path+'#article'
            graph[2]['mainEntity']={'@id':article_id}
            citations=list(dict.fromkeys(link['href'] for section in page['sections'] for link in section.get('links',[]) if link['href'].startswith('https://')))
            article={'@type':'Article','@id':article_id,'headline':page['h1'],'description':page['description'],'url':ORIGIN+path,'mainEntityOfPage':{'@id':ORIGIN+path+'#webpage'},'author':{'@id':org_id},'publisher':{'@id':org_id},'inLanguage':site['language'],'datePublished':page['publishedAt'],'dateModified':page['reviewedAt'],'articleSection':'Influencer marketing planning','about':{'@id':ORIGIN+'/services#webpage'}}
            if citations: article['citation']=citations
            graph.append(article)
        else:
            graph[2]['@type']='CollectionPage'
            graph[2]['mainEntity']={'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':ORIGIN+p['path'],'name':p['navTitle']} for i,p in enumerate(p for p in MODEL['pages'] if p.get('published') and p['type']=='guide')]}
    if path=='/services':
        for ident,title in [('creator-access','Creator access'),('campaign-operations','Campaign operations'),('performance-learning','Performance learning')]:
            graph.append({'@type':'Service','@id':ORIGIN+path+'#'+ident,'name':title,'serviceType':'Influencer marketing','url':ORIGIN+path+'#'+ident,'provider':{'@id':org['@id']}})
        sectors=next(section for section in page['sections'] if section['id']=='target-markets')
        for sector in sectors['items']:
            graph.append({'@type':'Service','@id':ORIGIN+path+'#'+sector['id'],'name':sector['title'],'description':sector['body'],'serviceType':sector['serviceType'],'url':ORIGIN+path+'#'+sector['id'],'provider':{'@id':org_id},'audience':{'@type':'BusinessAudience','audienceType':sector['industryName']+' brands'}})
    if path!='/':
        chain=[('/', 'Home')]
        if path.startswith('/work/'): chain.append(('/work','Work'))
        if path.startswith('/guides/'): chain.append(('/guides','Guides'))
        chain.append((path,page.get('navTitle',name.split('|')[0].strip())))
        graph.append({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':i+1,'name':label,'item':ORIGIN+url} for i,(url,label) in enumerate(chain)]})
    return json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')

def meta(doc, attr, key, value):
    pattern=r'<meta\b(?=[^>]*\b'+attr+r'=[\"\"]'+re.escape(key)+r'[\"\"])[^>]*>'
    tag='<meta '+attr+'="'+key+'" content="'+escape(value,quote=True)+'">'
    if re.search(pattern,doc,re.I): return re.sub(pattern,lambda _:tag,doc,flags=re.I)
    return doc.replace('</head>',tag+'\n</head>',1)

def contact_booking(doc):
    tree = Tree(doc)
    main = next((node for node in tree.nodes if node.tag == 'main' and node.attrs.get('data-framer-name') == 'IRG opening dark'), None)
    direct = next((node for node in tree.nodes if node.attrs.get('data-framer-name') == 'Direct contact'), None)
    if not main or not direct:
        raise ValueError('Original Contact booking insertion points are missing')
    if any(node.attrs.get('id') == 'book-a-call' for node in tree.nodes):
        return doc
    # Add scheduling without replacing or relocating the original enquiry form.
    for start, end, value in sorted([(main.end, main.end, CONTACT_BOOKING), (direct.start, direct.start, BOOKING_JUMP)], reverse=True):
        doc = doc[:start]+value+doc[end:]
    return doc

def booking_destinations(doc):
    """Start a project opens scheduling; other Contact links retain their intent."""
    changes=[]
    for node in Tree(doc).nodes:
        if node.tag != 'a' or plain(doc[node.start:node.end]).lower() != 'start a project': continue
        if node.attrs.get('href') not in ('contact.html','./contact','/contact','./contact#book-a-call','/contact#book-a-call','mailto:reyan@irgmedia.org','mailto:'+MODEL['site']['email']): continue
        opening=doc[node.start:node.open_end]
        changes.append((node.start,node.open_end,re.sub(r'href="[^"]*"','href="/contact#book-a-call"',opening,count=1)))
    for start,end,value in sorted(changes,reverse=True): doc=doc[:start]+value+doc[end:]
    return doc

def patch(doc,name,page):
    # A stable page marker scopes the shared layout presets without touching
    # Framer-owned content or its responsive component variants.
    doc = re.sub(r'<html\b', lambda _: '<html data-irg-page="'+escape(name)+'"', doc, count=1)
    replacements=list(COPY_REPLACEMENTS.get(name, []))
    # Hydration restores complete paragraphs. Expand partial editorial changes
    # into exact source-paragraph matches so initial and hydrated copy agree.
    tree=Tree(doc)
    for node in tree.nodes:
        if node.tag != 'p': continue
        original=plain(doc[node.open_end:node.end-len('</p>')])
        changed=original
        for item in COPY_REPLACEMENTS.get(name, []):
            changed=changed.replace(item['from'], item['to'])
        if changed != original and not any(item['from']==original for item in replacements):
            replacements.append({'from':original,'to':changed})
    # Presentation-only casing; the words, destinations and submit behavior stay intact.
    doc = doc.replace('START A PROJECT', 'Start a project').replace('SEND ENQUIRY', 'Send enquiry')
    for item in COPY_REPLACEMENTS.get(name, []):
        doc = doc.replace(item['from'], item['to'])
    if name in ('index', 'work'):
        doc = case_handover(case_cards(doc, name))
    if name=='index':
        doc = home_faq(doc)
        doc = image_cards(doc)
    doc = booking_destinations(doc)
    doc = linked_images(doc, name)
    doc = withdrawn_case_content(doc)
    for previous_email in ("reyan@irgmedia.org", "alex@irgmedia.org"):
        doc = doc.replace(previous_email, MODEL["site"]["email"])
    # Metadata/identity changes do not alter the existing Framer page structure.
    doc=re.sub(r'<title>.*?</title>',lambda _: '<title>'+escape(page['title'])+'</title>',doc,count=1,flags=re.S)
    for attr,key,value in [('name','description',page['description']),('property','og:title',page['title']),('property','og:description',page['description']),('property','og:url',ORIGIN+page['path']),('property','og:site_name','IRG Media'),('property','og:image',ORIGIN+'/assets/social-preview.png'),('name','twitter:title',page['title']),('name','twitter:description',page['description']),('name','twitter:image',ORIGIN+'/assets/social-preview.png'),('name','theme-color','#191c1f'),('name','robots','noindex,follow' if name=='privacy' else 'index,follow,max-image-preview:large')]:
        doc=meta(doc,attr,key,value)
    if page['type']=='guide':
        doc=meta(doc,'property','og:type','article')
        doc=meta(doc,'property','article:published_time',page['publishedAt'])
        doc=meta(doc,'property','article:modified_time',page['reviewedAt'])
    doc=re.sub(r'<link\b(?=[^>]*\brel="(?:icon|apple-touch-icon)")[^>]*>','',doc,flags=re.I)
    doc=re.sub(r'<link\b(?=[^>]*\brel="canonical")[^>]*>',lambda _:'<link rel="canonical" href="'+ORIGIN+page['path']+'">',doc,flags=re.I)
    doc=doc.replace('https://agr.studio/', 'https://leadscorer.co/').replace('https://agr.studio','https://leadscorer.co/').replace('by agr.studio','by leadscorer.co')
    if name not in ['resources','privacy']:
        doc=inline_links(doc,name)
        # Letter-by-letter visual spans retain their design, with a readable label.
        doc=re.sub(r'(<h[1-6]\b)([^>]*>)(.*?)(</h[1-6]>)',lambda m:m.group(1)+' aria-label="'+escape(plain(m.group(3)),quote=True)+'"'+m.group(2)+m.group(3)+m.group(4) if 'display:inline-block;opacity:' in m.group(3) else m.group(0),doc,flags=re.S)
    if name=='services':
        doc=doc.replace('data-framer-name="Services / tangible outputs"','data-framer-name="Services / tangible outputs" id="evaluation"',1)
    if name=='contact':
        doc=contact_booking(doc)
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
    config={'page':name,'path':page['path'],'title':page['title'],'description':page['description'],'canonical':ORIGIN+page['path'],'robots':'noindex,follow' if name=='privacy' else 'index,follow,max-image-preview:large','replacements':replacements,'inlineLinks':[{'phrase':p,'href':h} for p,h in LINKS.get(name,[])],'additionHtml':additions,'contactEmail':MODEL['site']['email'],'withdrawnPaths':[] if CASE_STUDY['published'] else [CASE_STUDY['path']]}
    if name in ('index', 'work'): config['caseStudy'] = CASE_STUDY
    if name=='index':
        config['faqHtml'] = faq_html()
        config['imageCards'] = HOME_IMAGE_CARDS
    if name=='contact':
        config['bookingHtml'] = CONTACT_BOOKING
        config['bookingJumpHtml'] = BOOKING_JUMP
    config['mediaRules'] = IMAGE_LINKS['rules']
    config['mediaDefault'] = IMAGE_LINKS['defaults'].get(name)
    head='''<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg"><link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"><link rel="stylesheet" href="/assets/brand-updates.css"><link rel="stylesheet" href="/assets/content-updates.css"><script defer src="/assets/brand-updates.js"></script><script defer src="/assets/content-updates.js"></script>'''
    if name=='services':head+='<link rel="stylesheet" href="/assets/markets.css">'
    if name=='index':head+='<link rel="stylesheet" href="/assets/faq.css">'
    if name=='contact':head+='<link rel="stylesheet" href="/assets/contact-booking.css"><script defer src="/assets/contact-booking.js"></script>'
    head+='<link rel="stylesheet" href="/assets/layout-consistency.css">'
    head+='<script id="irg-page-enhancements" type="application/json">'+json.dumps(config,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    # Replace any prior generic schema with the grounded graph.
    doc=re.sub(r'<script\b[^>]*type="application/ld\+json"[^>]*>.*?</script>','',doc,flags=re.S|re.I)
    head+='<script type="application/ld+json">'+schema(page)+'</script>'
    doc=doc.replace('</head>',head+'\n</head>',1)
    if name not in ['resources','privacy']:
        target='#main' if name in CORE else '#content'
        if 'class="irg-detail-skip"' not in doc:
            doc=re.sub(r'(<body\b[^>]*>)',lambda m:m.group(1)+'<a class="irg-skip-link" href="'+target+'">Skip to content</a>',doc,count=1)
    head, tail = doc.split('</head>',1)
    return re.sub(r'(?m)^[ \t]+$', '', head)+'</head>'+tail

def build():
    pages={p['path']:p for p in MODEL['pages'] if p.get('published') and (p['path'] in ['/' if n=='index' else '/'+n for n in CORE] or p['path'].startswith('/work/') or p['type'] in ('guide','guide-hub'))}
    for name in CORE:
        path='/' if name=='index' else '/'+name
        doc=subprocess.check_output(['git','show',BASELINE+':site/'+name+'.html'],cwd=ROOT).decode()
        (SITE/(name+'.html')).write_text(patch(doc,name,pages[path]))
    for path, page in pages.items():
        if path in ['/' if n=='index' else '/'+n for n in CORE]: continue
        file=SITE/(path.lstrip('/')+'.html')
        if path in pages:
            doc=file.read_text()
            # Detail generators supply a fresh unpatched source before this command.
            if 'id="irg-page-enhancements"' not in doc:
                file.write_text(patch(doc,file.stem,pages[path]))
    routes=[p for p in pages.values() if p.get('indexable') and p.get('published')]
    (SITE/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('<url><loc>'+escape(ORIGIN+p['path'])+'</loc>'+('<lastmod>'+escape(p['modifiedAt'])+'</lastmod>' if p.get('modifiedAt') else '')+'</url>\n' for p in routes)+'</urlset>\n')
    (SITE/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: https://irgmedia.org/sitemap.xml\n')
    (ROOT/'docs/route-map.json').write_text(json.dumps([{'path':p['path'],'title':p['title'],'type':p['type'],'indexable':p.get('indexable')} for p in pages.values()],indent=2)+'\n')
    print('Applied edits to original Framer layouts; '+str(len(pages))+' published routes.')

if __name__=='__main__':build()
