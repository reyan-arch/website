"""Keep original image panels intact while linking their full bounds."""
import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('home_cards_update', ROOT/'scripts/update_existing_site.py')
update = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update)


class HomeImageCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = subprocess.check_output(['git', 'show', update.BASELINE+':site/index.html'], cwd=ROOT, text=True)
        cls.enhanced = update.image_cards(cls.original)

    def test_native_links_cover_each_responsive_panel_without_changing_copy_or_media(self):
        original_tree, tree = update.Tree(self.original), update.Tree(self.enhanced)
        for card in update.HOME_IMAGE_CARDS:
            originals = [n for n in original_tree.nodes if n.attrs.get('data-framer-name') == card['name']]
            panels = [n for n in tree.nodes if n.attrs.get('data-framer-name') == card['name']]
            self.assertEqual(len(originals), len(panels))
            self.assertGreater(len(panels), 1)
            for before, panel in zip(originals, panels):
                links = [n for n in update.descendants(tree, panel) if n.tag == 'a']
                self.assertEqual(1, len(links))
                link = links[0]
                self.assertIs(link.parent, panel)
                self.assertEqual(card['href'], link.attrs['href'])
                self.assertEqual(card['label'], link.attrs['aria-label'])
                original_body = self.original[before.open_end:before.end-len('</div>')]
                enhanced_body = self.enhanced[panel.open_end:link.start]
                self.assertEqual(original_body, enhanced_body)
        self.assertEqual(self.enhanced, update.image_cards(self.enhanced))

    def test_inline_linking_skips_image_copy_but_preserves_contextual_links_elsewhere(self):
        doc = update.inline_links(self.enhanced, 'index')
        tree = update.Tree(doc)
        for panel in tree.nodes:
            if panel.attrs.get('data-irg-image-card'):
                links = [n for n in update.descendants(tree, panel) if n.tag == 'a']
                self.assertEqual(['irg-image-card-link'], [n.attrs.get('class') for n in links])
        self.assertIn('class="irg-context-link" href="/services#creator-access"', doc)
        self.assertIn('class="irg-context-link" href="/services#campaign-operations"', doc)


if __name__ == '__main__':
    unittest.main()
