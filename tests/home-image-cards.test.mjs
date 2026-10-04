import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../site/assets/content-updates.js', import.meta.url), 'utf8');
const cards = [
  { name: 'Old Model', href: '/services#creator-access', label: 'Creator relationships — explore creator access', text: 'Creator relationships' },
  { name: 'IRG Model', href: '/services#campaign-operations', label: 'Connected delivery — explore campaign operations', text: 'Connected delivery' },
];

// A bounded DOM stand-in runs the actual enhancement through hydration changes.
function element(tagName, attrs = {}) {
  const node = {
    tagName: tagName.toUpperCase(), attrs: { ...attrs }, children: [], parentElement: null,
    className: attrs.class || '', href: attrs.href || '',
    hasAttribute(name) { return name in this.attrs; },
    setAttribute(name, value) { this.attrs[name] = value; },
    getAttribute(name) { return this.attrs[name]; },
    append(child) { child.parentElement = this; this.children.push(child); },
    replaceWith(...children) {
      const parent = this.parentElement;
      const index = parent.children.indexOf(this);
      children.forEach(child => { child.parentElement = parent; });
      parent.children.splice(index, 1, ...children);
      this.parentElement = null;
    },
    matches(selector) {
      if (selector === '[data-irg-image-card]') return this.hasAttribute('data-irg-image-card');
      const match = selector.match(/^(a|p)(?:\.([\w-]+))?$/);
      return !!match && this.tagName === match[1].toUpperCase() && (!match[2] || this.className.split(' ').includes(match[2]));
    },
    closest(selector) {
      for (let current = this; current; current = current.parentElement) {
        if (selector.split(',').some(part => current.matches?.(part))) return current;
      }
      return null;
    },
    querySelectorAll(selector) {
      const found = [];
      function visit(parent) {
        for (const child of parent.children || []) {
          if (child.matches?.(selector)) found.push(child);
          visit(child);
        }
      }
      visit(this);
      return found;
    },
    querySelector(selector) { return this.querySelectorAll(selector)[0] || null; },
    get childNodes() { return this.children; },
    get textContent() { return this.children.map(child => child.textContent).join(''); },
  };
  return node;
}

function panel(card, unrelated = false) {
  const node = element('div', { 'data-framer-name': card.name });
  const caption = element('p');
  const text = { textContent: card.text };
  const link = element('a', {
    class: unrelated ? 'original-link' : 'irg-context-link',
    href: unrelated ? '/contact' : card.href,
  });
  link.append(text);
  caption.append(link);
  node.append(caption);
  return node;
}

function page({ unrelated = false } = {}) {
  let panels = cards.flatMap(card => [panel(card, unrelated), panel(card, unrelated)]);
  let mutation;
  const frames = [];
  const config = {
    page: 'index', title: 'IRG Media', description: 'Verified scope', canonical: 'https://irgmedia.org/',
    imageCards: cards.map(({ name, href, label }) => ({ name, href, label })),
    inlineLinks: cards.map(card => ({ phrase: card.text, href: card.href })),
  };
  const document = {
    title: config.title, body: {}, head: {},
    getElementById: () => ({ textContent: JSON.stringify(config) }),
    querySelector: () => null,
    querySelectorAll(selector) {
      const match = selector.match(/^\[data-framer-name="([^"]+)"\]$/);
      if (match) return panels.filter(node => node.attrs['data-framer-name'] === match[1]);
      if (selector === 'p') return panels.flatMap(node => node.querySelectorAll('p'));
      return [];
    },
    createElement: element,
    addEventListener() {},
    createTreeWalker() { throw new Error('Image captions must remain outside generic inline linking'); },
  };
  vm.runInNewContext(source, {
    document, URL, location: { href: config.canonical, origin: 'https://irgmedia.org', pathname: '/' },
    requestAnimationFrame: callback => frames.push(callback),
    MutationObserver: class { constructor(callback) { mutation = callback; } observe() {} },
  });
  function refresh() {
    mutation();
    while (frames.length) frames.shift()();
  }
  return {
    panels: () => panels,
    refresh,
    hydrate() { panels = cards.flatMap(card => [panel(card, unrelated), panel(card, unrelated)]); refresh(); },
  };
}

test('Repeated Framer replacement restores one native card link per responsive panel', () => {
  const site = page();
  for (let cycle = 0; cycle < 4; cycle++) {
    if (cycle) site.hydrate();
    for (const node of site.panels()) {
      const card = cards.find(card => card.name === node.attrs['data-framer-name']);
      const links = node.querySelectorAll('a');
      assert.equal(links.length, 1);
      const link = links[0];
      assert.equal(link.className, 'irg-image-card-link');
      assert.equal(link.href, card.href);
      assert.equal(link.getAttribute('aria-label'), card.label);
      assert.equal(link.parentElement, node);
      assert.equal(link.querySelectorAll('a').length, 0);
      assert.equal(node.textContent, card.text);
      site.refresh();
      site.refresh();
      assert.equal(node.querySelectorAll('a').length, 1);
      assert.equal(node.querySelector('a'), link);
    }
  }
});

test('An unrelated original anchor is retained without adding an overlay or nested anchor', () => {
  const site = page({ unrelated: true });
  for (let cycle = 0; cycle < 3; cycle++) {
    if (cycle) site.hydrate();
    for (const node of site.panels()) {
      const original = node.querySelector('a');
      site.refresh();
      assert.equal(node.querySelectorAll('a').length, 1);
      assert.equal(node.querySelector('a'), original);
      assert.equal(original.className, 'original-link');
      assert.equal(original.href, '/contact');
      assert.equal(original.querySelectorAll('a').length, 0);
      assert.equal(node.querySelector('a.irg-image-card-link'), null);
    }
  }
});
