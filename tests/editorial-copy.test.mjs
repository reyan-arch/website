import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../site/assets/content-updates.js', import.meta.url), 'utf8');

function page(pageName, changes) {
  let mutation, writes = 0;
  const frames = [];
  const parent = { closest: () => null, querySelector: () => null };
  const nodes = changes.map(change => {
    let value = change.from;
    return {
      parentElement: parent,
      get nodeValue() { return value; },
      set nodeValue(next) { value = next; writes++; },
    };
  });
  const field = { value: 'A visitor’s unfinished enquiry' };
  const imageAttributes = new Map([['alt', changes[0].from], ['class', 'existing-photo'], ['src', '/existing.jpg']]);
  const image = { getAttribute: key => imageAttributes.get(key), setAttribute: (key, value) => imageAttributes.set(key, value) };
  const config = { page: pageName, title: 'IRG Media', description: 'Current copy', canonical: 'https://irgmedia.org/'+pageName, editorialCopy: changes };
  const document = {
    title: config.title, body: {}, head: {},
    getElementById: () => ({ textContent: JSON.stringify(config) }),
    querySelector: () => null,
    querySelectorAll: selector => selector === '[alt],[aria-label],[title]' ? [image] : [],
    createTreeWalker: () => {
      let at = 0;
      return { nextNode: () => nodes[at++] || null };
    },
    addEventListener() {},
  };
  vm.runInNewContext(source, {
    document, URL, NodeFilter: { SHOW_TEXT: 4 },
    location: { href: config.canonical, origin: 'https://irgmedia.org', pathname: '/'+pageName },
    requestAnimationFrame: callback => frames.push(callback),
    MutationObserver: class { constructor(callback) { mutation = callback; } observe() {} },
  });
  return {
    nodes, field, imageAttributes,
    writes: () => writes,
    refresh() { mutation(); while (frames.length) frames.shift()(); },
  };
}

test('Resource copy survives Framer restoration without replacing nodes or visitor input', () => {
  const change = { from: 'Placeholder cover. PDF not yet supplied.', to: 'Find the audience fit. Filter for relevance. Brief with clarity.' };
  const site = page('resources', [change]);
  const original = site.nodes[0];
  assert.equal(original.nodeValue, change.to);
  original.nodeValue = change.from;
  site.refresh();
  assert.equal(site.nodes[0], original);
  assert.equal(original.nodeValue, change.to);
  assert.equal(site.field.value, 'A visitor’s unfinished enquiry');
  assert.equal(site.imageAttributes.get('class'), 'existing-photo');
  assert.equal(site.imageAttributes.get('src'), '/existing.jpg');
  assert.equal(site.imageAttributes.get('alt'), change.to);
  const writes = site.writes();
  site.refresh(); site.refresh();
  assert.equal(site.writes(), writes);
});

test('Privacy copy survives restoration while retaining its existing text node', () => {
  const changes = [
    { from: 'Draft: approved legal copy is required before this page can be published.', to: 'IRG Media receives the information you submit to understand your request and respond.' },
  ];
  const site = page('privacy', changes);
  const original = [...site.nodes];
  for (let i = 0; i < changes.length; i++) site.nodes[i].nodeValue = changes[i].from;
  site.refresh();
  site.nodes.forEach((node, index) => {
    assert.equal(node, original[index]);
    assert.equal(node.nodeValue, changes[index].to);
  });
});
