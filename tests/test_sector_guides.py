"""Guard discovery, source/rendered semantics and reuse of the existing page frame."""
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('guide_updates', ROOT/'scripts/update_existing_site.py')
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)


class SectorGuideTests(unittest.TestCase):
    def test_guide_semantics_match_visible_content(self):
        for page in update.MODEL['pages']:
            if page['type'] != 'guide':
                continue
            with self.subTest(page=page['id']):
                source=(ROOT/'site'/(page['slug']+'.html')).read_text()
                tree=update.Tree(source)
                graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',source,re.S)[1])['@graph']
                article=next(n for n in graph if n['@type']=='Article')
                h1=next(n for n in tree.nodes if n.tag=='h1')
                self.assertEqual(update.plain(source[h1.open_end:h1.end-5]),article['headline'])
                self.assertIn('By IRG Media',source)
                self.assertIn('datetime="'+article['datePublished']+'"',source)
                self.assertEqual(article['author']['@id'],'https://irgmedia.org/#organization')
                self.assertEqual(article['mainEntityOfPage']['@id'],page['canonicalUrl']+'#webpage')
                crumbs=next(n for n in graph if n['@type']=='BreadcrumbList')['itemListElement']
                self.assertEqual([x['item'] for x in crumbs],['https://irgmedia.org/','https://irgmedia.org/guides',page['canonicalUrl']])
                for citation in article.get('citation',[]):
                    self.assertTrue(any(n.tag=='a' and n.attrs.get('href')==citation for n in tree.nodes))
                self.assertNotIn('data-irg-work-pageview',source)
                self.assertEqual(1,source.count('>Skip to content</a>'))

    def test_guides_reuse_existing_styles_and_have_discovery_links(self):
        old=(ROOT/'site/work/campaign-operations.html').read_text()
        old_css=re.search(r'<style data-irg-work-detail-css>(.*?)</style>',old,re.S)[1]
        old_stylesheets=re.findall(r'<link rel="stylesheet" href="([^"]+)"',old)
        home=(ROOT/'site/index.html').read_text()
        self.assertIn('href="/guides"',home)
        hub=(ROOT/'site/guides.html').read_text()
        for page in update.MODEL['pages']:
            if page['type'] not in ('guide','guide-hub'):continue
            source=(ROOT/'site'/(page['slug']+'.html')).read_text()
            self.assertEqual(old_css,re.search(r'<style data-irg-work-detail-css>(.*?)</style>',source,re.S)[1])
            self.assertEqual(old_stylesheets,re.findall(r'<link rel="stylesheet" href="([^"]+)"',source))
            if page['type']=='guide':self.assertIn('href="'+page['path']+'"',hub)

    def test_entertainment_scope_is_consistent_and_uses_existing_card(self):
        source=(ROOT/'site/services.html').read_text()
        tree=update.Tree(source)
        sector=next(n for n in tree.nodes if n.attrs.get('id')=='entertainment')
        contents=source[sector.start:sector.end]
        self.assertIn('class="irg-market-card"',contents)
        self.assertIn('class="irg-market-card__copy"',contents)
        self.assertIn('IRG Media runs creator campaigns for entertainment brands.',contents)
        page=next(p for p in update.MODEL['pages'] if p['path']=='/services')
        graph=json.loads(update.schema(page))['@graph']
        service=next(n for n in graph if n.get('@id')=='https://irgmedia.org/services#entertainment')
        self.assertIn(service['description'],update.plain(contents))
        self.assertEqual(service['provider']['@id'],'https://irgmedia.org/#organization')
        home=next(p for p in update.MODEL['pages'] if p['path']=='/')
        faq=json.loads(update.schema(home))['@graph'][2]['mainEntity']
        self.assertTrue(any('entertainment' in q['acceptedAnswer']['text'] for q in faq))

    def test_partial_edits_have_whole_paragraph_hydration_matches(self):
        for name in ('about','approach','why-irg','work','contact'):
            source=(ROOT/'site'/(name+'.html')).read_text()
            config=json.loads(re.search(r'<script id="irg-page-enhancements" type="application/json">(.*?)</script>',source,re.S)[1])
            for item in config['replacements']:
                if item['from']=='travel, hospitality and lifestyle':continue
                if 'travel, hospitality and lifestyle' in item['from']:
                    self.assertIn('travel, hospitality, entertainment and lifestyle',item['to'])


if __name__ == '__main__':unittest.main()
