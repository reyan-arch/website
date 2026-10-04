"""Public photos have real destinations without replacing original assets."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('image_link_update', ROOT/'scripts/update_existing_site.py')
update = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update)


class LinkedImagesTests(unittest.TestCase):
    def test_every_public_photo_has_a_native_destination(self):
        checked = 0
        for path in (ROOT/'site').rglob('*.html'):
            doc = path.read_text(); tree = update.Tree(doc)
            for image in [node for node in tree.nodes if node.tag == 'img']:
                ancestors=[]; parent=image.parent
                while parent:
                    ancestors.append(parent); parent=parent.parent
                if any(node.attrs.get('data-framer-name') in ('Work CMS source','Resources CTA') for node in ancestors): continue
                anchor=next((node for node in ancestors if node.tag == 'a' and node.attrs.get('href')), None)
                if not anchor:
                    frame=next((node for node in ancestors if node.attrs.get('data-irg-media-frame')), None)
                    self.assertIsNotNone(frame, str(path)+' / '+str(image.attrs.get('alt')))
                    links=[node for node in update.descendants(tree,frame) if node.tag == 'a' and any(cls in node.attrs.get('class','').split() for cls in ('irg-media-link','irg-image-card-link'))]
                    self.assertEqual(1,len(links))
                    anchor=links[0]
                    self.assertTrue(anchor.attrs.get('aria-label'))
                self.assertTrue(anchor.attrs.get('href'))
                checked += 1
        self.assertGreater(checked, 200)

    def test_links_are_not_nested_and_photo_nodes_are_not_rewritten(self):
        for path in (ROOT/'site').rglob('*.html'):
            doc=path.read_text(); tree=update.Tree(doc)
            for node in tree.nodes:
                if node.tag == 'a':
                    parent=node.parent
                    while parent:
                        self.assertNotEqual('a',parent.tag,str(path)+' / '+str(node.attrs.get('href')))
                        parent=parent.parent
            before=[doc[node.start:node.open_end] for node in tree.nodes if node.tag == 'img']
            again=update.linked_images(doc,path.stem)
            after=[again[node.start:node.open_end] for node in update.Tree(again).nodes if node.tag == 'img']
            self.assertEqual(before,after)
            self.assertEqual(doc,again)


if __name__ == '__main__':
    unittest.main()
