"""Scheduling is additive and confined to the existing Contact destination."""
import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('contact_booking_update', ROOT/'scripts/update_existing_site.py')
update = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(update)


class ContactBookingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = subprocess.check_output(['git', 'show', update.BASELINE+':site/contact.html'], cwd=ROOT, text=True)
        cls.enhanced = update.contact_booking(cls.original)

    def test_enquiry_form_panel_is_preserved_byte_for_byte(self):
        panels = []
        for doc in (self.original, self.enhanced):
            node = next(n for n in update.Tree(doc).nodes if n.attrs.get('data-framer-name') == 'Project enquiry form panel')
            panels.append(doc[node.start:node.end])
        self.assertEqual(panels[0], panels[1])

    def test_one_source_widget_and_native_jump_with_the_supplied_destination(self):
        tree = update.Tree(self.enhanced)
        widgets = [n for n in tree.nodes if n.attrs.get('class') == 'calendly-inline-widget']
        self.assertEqual(1, len(widgets))
        self.assertEqual('https://calendly.com/irgmediareyan/discovery-call', widgets[0].attrs['data-url'])
        self.assertEqual('min-width:320px;height:700px;', widgets[0].attrs['style'])
        self.assertEqual(1, len([n for n in tree.nodes if n.attrs.get('id') == 'book-a-call']))
        jump = next(n for n in tree.nodes if 'irg-booking-jump' in n.attrs.get('class', '').split())
        self.assertEqual('#book-a-call', jump.attrs['href'])
        self.assertEqual(self.enhanced, update.contact_booking(self.enhanced))

    def test_provider_integration_is_loaded_only_on_contact(self):
        for path in (ROOT/'site').rglob('*.html'):
            scripts = [n.attrs.get('src') for n in update.Tree(path.read_text()).nodes if n.tag == 'script']
            if path.name == 'contact.html':
                self.assertEqual(1, scripts.count('/assets/contact-booking.js'))
            else:
                self.assertNotIn('/assets/contact-booking.js', scripts)

    def test_start_a_project_actions_open_scheduling_on_existing_contact_page(self):
        actions = 0
        for path in (ROOT/'site').rglob('*.html'):
            doc=path.read_text()
            for node in update.Tree(doc).nodes:
                if node.tag == 'a' and update.plain(doc[node.start:node.end]).lower() == 'start a project':
                    self.assertEqual('/contact#book-a-call',node.attrs.get('href'))
                    actions += 1
        self.assertGreater(actions, 20)


if __name__ == '__main__':
    unittest.main()
