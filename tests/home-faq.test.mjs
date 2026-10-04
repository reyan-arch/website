import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../site/assets/content-updates.js', import.meta.url), 'utf8');
const items = JSON.parse(readFileSync(new URL('../content/home-faq.json', import.meta.url), 'utf8')).items;
const faqHtml = items.map(item => `<details data-irg-faq-key="${item.key}"></details>`).join('');

// Exercise refresh and native toggle state with a bounded DOM stand-in.
function page({ native = false } = {}) {
  const events = new Map(), frames = [];
  let mutations, writes = 0;
  const list = {
    items: [],
    querySelector() { return this.items[0] || null; },
    querySelectorAll() { return this.items; },
    set innerHTML(html) {
      writes++;
      this.items = [...html.matchAll(/data-irg-faq-key="([^"]+)"/g)].map(match => ({
        dataset: { irgFaqKey: match[1] }, open: false,
        matches: () => true, closest: () => list,
      }));
    },
  };
  if (native) { list.innerHTML = faqHtml; writes = 0; }
  const config = { page: 'index', title: 'IRG Media', description: 'Verified scope', canonical: 'https://irgmedia.org/', faqHtml };
  const document = {
    title: config.title, body: {}, head: {},
    getElementById: () => ({ textContent: JSON.stringify(config) }),
    querySelector: () => null,
    querySelectorAll: selector => selector === '[data-framer-name="FAQ List"]' ? [list] : [],
    addEventListener: (name, callback) => events.set(name, callback),
  };
  vm.runInNewContext(source, {
    document, URL, location: { href: config.canonical, origin: 'https://irgmedia.org', pathname: '/' },
    requestAnimationFrame: callback => frames.push(callback),
    MutationObserver: class { constructor(callback) { mutations = callback; } observe() {} },
  });
  const refresh = () => { mutations(); while (frames.length) frames.shift()(); };
  return {
    list, refresh, writes: () => writes,
    toggle(key, open) { const item = list.items.find(item => item.dataset.irgFaqKey === key); item.open = open; events.get('toggle')({ target: item }); },
    hydrate() { list.items = []; refresh(); },
  };
}

test('SSR native questions remain untouched through unrelated refreshes', () => {
  const site = page({ native: true });
  const first = site.list.items[0];
  site.toggle(items[0].key, true);
  for (let i = 0; i < 4; i++) site.refresh();
  assert.equal(site.writes(), 0);
  assert.equal(site.list.items[0], first);
  assert.equal(first.open, true);
});

test('Framer replacement restores both open and subsequently closed user states', () => {
  const site = page();
  assert.equal(site.writes(), 1);
  assert.equal(site.list.items.length, 6);
  site.toggle(items[2].key, true);
  site.hydrate();
  assert.equal(site.list.items[2].open, true);
  site.toggle(items[2].key, false);
  site.hydrate();
  assert.equal(site.list.items[2].open, false);
  site.refresh();
  assert.equal(site.writes(), 3);
});
