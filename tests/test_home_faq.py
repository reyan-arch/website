"""Check crawlable answers against the original Home and matching semantic data."""
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('home_faq_update', ROOT/'scripts/update_existing_site.py')
update = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update)


class HomeFaqTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = subprocess.check_output(['git', 'show', update.BASELINE+':site/index.html'], cwd=ROOT, text=True)
        cls.enhanced = update.home_faq(cls.baseline)

    def test_original_questions_and_outer_frames_are_preserved(self):
        original_tree, enhanced_tree = update.Tree(self.baseline), update.Tree(self.enhanced)
        original = [node for node in original_tree.nodes if node.attrs.get('data-framer-name') == 'FAQ List']
        enhanced = [node for node in enhanced_tree.nodes if node.attrs.get('data-framer-name') == 'FAQ List']
        self.assertEqual(len(original), len(enhanced))
        for before, after in zip(original, enhanced):
            self.assertEqual(self.baseline[before.start:before.open_end], self.enhanced[after.start:after.open_end])
            before_questions = [update.plain(self.baseline[n.open_end:n.end-len('</h3>')]) for n in update.descendants(original_tree, before) if n.tag == 'h3']
            after_questions = [update.plain(self.enhanced[n.open_end:n.end-len('</h3>')]) for n in update.descendants(enhanced_tree, after) if n.tag == 'h3']
            self.assertEqual(before_questions, after_questions)
            self.assertEqual(6, len([n for n in update.descendants(enhanced_tree, after) if n.tag == 'details']))
        self.assertEqual(update.home_faq(self.enhanced), self.enhanced)

    def test_all_answers_are_source_available_and_match_schema(self):
        home = next(page for page in update.MODEL['pages'] if page['path'] == '/')
        graph = json.loads(update.schema(home))['@graph']
        webpage = next(node for node in graph if node['@id'].endswith('#webpage'))
        self.assertEqual(['WebPage', 'FAQPage'], webpage['@type'])
        tree = update.Tree(update.faq_html())
        answers = [update.plain(update.faq_html()[node.open_end:node.end-len('</p>')]) for node in tree.nodes if node.tag == 'p']
        self.assertEqual([item['answer'] for item in update.HOME_FAQ], answers)
        self.assertEqual(answers, [question['acceptedAnswer']['text'] for question in webpage['mainEntity']])
        for item in update.HOME_FAQ:
            self.assertTrue(25 <= len(item['answer'].split()) <= 45)
            for link in item['links']:
                self.assertIn('href="'+link['href']+'"', update.faq_html())

    def test_content_outside_faq_including_resource_block_is_untouched(self):
        def mask_faq(source):
            tree = update.Tree(source)
            ranges = [(node.open_end, node.end-len('</'+node.tag+'>')) for node in tree.nodes if node.attrs.get('data-framer-name') == 'FAQ List']
            for start, end in reversed(ranges):
                source = source[:start]+'FAQ CONTENT'+source[end:]
            return source
        self.assertEqual(mask_faq(self.baseline), mask_faq(self.enhanced))


if __name__ == '__main__':
    unittest.main()
