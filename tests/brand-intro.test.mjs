import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../site/assets/brand-updates.js', import.meta.url), 'utf8');
const styles = readFileSync(new URL('../site/assets/brand-updates.css', import.meta.url), 'utf8');

// A small DOM stand-in exercises actual navigation and lifetime decisions.
function page(options = {}) {
  const settings = { path: '/', navigation: 'reload', hash: '', scroll: 0, reduced: false, hidden: false, loaded: true, ...options };
  const timers = new Map(), frames = [], windowEvents = new Map(), documentEvents = new Map();
  let clock = 0, nextTimer = 0;
  const listen = events => (name, callback) => events.set(name, [...(events.get(name) || []), callback]);
  const fire = (events, name) => { for (const callback of events.get(name) || []) callback({}); };
  function element(tagName) {
    const events = new Map();
    return {
      tagName: tagName.toUpperCase(), style: {}, dataset: {}, attributes: {}, children: [],
      complete: settings.loaded, naturalWidth: settings.loaded ? 88 : 0,
      addEventListener: listen(events),
      setAttribute(name, value) { this.attributes[name] = value; },
      append(child) { child.parent = this; this.children.push(child); },
      remove() { this.parent.children = this.parent.children.filter(child => child !== this); },
      fire(name) { fire(events, name); },
    };
  }
  const body = element('body'), html = element('html');
  body.style.overflow = 'auto'; body.style.paddingRight = '0px'; html.style.scrollbarGutter = 'auto';
  const motion = { matches: settings.reduced, addEventListener: listen(new Map()) };
  const window = {
    location: { pathname: settings.path, hash: settings.hash }, scrollY: settings.scroll,
    matchMedia: () => motion, addEventListener: listen(windowEvents),
    setTimeout(callback, delay) { timers.set(++nextTimer, { callback, delay }); return nextTimer; },
    clearTimeout(id) { timers.delete(id); }, requestAnimationFrame(callback) { frames.push(callback); },
  };
  const document = {
    body, documentElement: html, hidden: settings.hidden,
    querySelector: () => null,
    querySelectorAll: selector => selector.startsWith('a.framer-N1V3k') ? settings.controls || [] : [],
    createTreeWalker(control) {
      const nodes = [];
      function visit(node) {
        if (node.children) node.children.forEach(visit);
        else if (typeof node.textContent === 'string') nodes.push(node);
      }
      visit(control);
      return { nextNode: () => nodes.shift() || null };
    },
    createElement: element, addEventListener: listen(documentEvents),
  };
  const performance = { now: () => clock };
  if (settings.navigation !== undefined) performance.getEntriesByType = () => settings.navigation === null ? [] : [{ type: settings.navigation }];
  vm.runInNewContext(source, { window, document, performance, NodeFilter: { SHOW_TEXT: 4 }, MutationObserver: class { observe() {} } });
  return {
    window, document, body, timers,
    intro: () => body.children.find(child => child.dataset.irgBrandIntro),
    clock(value) { clock = value; },
    navigate(path) { window.location.pathname = path; fire(windowEvents, 'popstate'); while (frames.length) frames.shift()(); },
    interact(name) { fire(documentEvents, name); },
  };
}

test('Only home reloads show the loader; normal visits and unavailable navigation information skip it', () => {
  for (const path of ['/', '/index.html']) assert.ok(page({ path }).intro());
  for (const options of [
    { navigation: 'navigate' }, { navigation: 'back_forward' }, { navigation: null }, { navigation: undefined },
    { path: '/services' }, { path: '/work/holafly' }, { hash: '#content' },
    { scroll: 1 }, { reduced: true }, { hidden: true },
  ]) assert.equal(page(options).intro(), undefined, JSON.stringify(options));
});

test('Navigating to home never replays the loader, even if the document initially reloaded', () => {
  const otherPage = page({ path: '/services' });
  otherPage.navigate('/');
  assert.equal(otherPage.intro(), undefined);
  const home = page();
  home.navigate('/services');
  assert.equal(home.intro(), undefined);
  home.navigate('/');
  assert.equal(home.intro(), undefined);
});

test('Identical crisp logo layers activate together and clear within the existing cap without scroll locks', () => {
  const browser = page(), intro = browser.intro(), logo = intro.children[0];
  assert.equal(intro.attributes.role, 'status');
  assert.equal(intro.attributes['aria-label'], 'Loading IRG Media');
  assert.equal(logo.attributes['aria-hidden'], 'true');
  assert.equal(intro.dataset.active, 'true');
  assert.deepEqual(logo.children.map(image => image.src), ['/assets/irg-lockup.svg', '/assets/irg-lockup.svg']);
  for (const image of logo.children) {
    assert.equal(image.width / image.height, 88 / 28);
    assert.equal(image.alt, '');
  }
  assert.equal(browser.body.style.overflow, 'auto');
  assert.equal(browser.body.style.paddingRight, '0px');
  const timer = [...browser.timers.values()][0];
  assert.equal(timer.delay, 1200);
  timer.callback();
  assert.equal(browser.intro(), undefined);
  assert.equal(browser.timers.size, 0);
  assert.match(styles, /@keyframes irg-brand-reveal\{from\{clip-path:inset\(0 100% 0 0\)\}to\{clip-path:inset\(0 0 0 0\)\}\}/);
  assert.match(styles, /\.irg-brand-intro-base\{filter:grayscale\(1\);opacity:\.18\}/);
});

test('Unavailable or slow assets remain hidden, and user interaction dismisses a visible loader', () => {
  const waiting = page({ loaded: false }), intro = waiting.intro(), images = intro.children[0].children;
  assert.equal(intro.dataset.active, undefined);
  images[0].complete = true; images[0].naturalWidth = 88; images[0].fire('load');
  assert.equal(intro.dataset.active, undefined);
  waiting.clock(400);
  images[1].complete = true; images[1].naturalWidth = 88; images[1].fire('load');
  assert.equal(intro.dataset.active, undefined);
  images[1].fire('error');
  assert.equal(waiting.intro(), undefined);
  for (const event of ['pointerdown', 'keydown']) {
    const browser = page();
    browser.interact(event);
    assert.equal(browser.intro(), undefined);
  }
});

test('CTA labels use title case while preserving their existing wrappers and icon nodes', () => {
  const project = { textContent: ' START A PROJECT ' }, enquiry = { textContent: 'SEND ENQUIRY' };
  const icon = { textContent: '↗' }, unrelated = { textContent: 'DOWNLOAD RESOURCE' };
  const wrapper = { children: [project] };
  const controls = [{ children: [wrapper, icon] }, { children: [enquiry] }, { children: [unrelated] }];
  const browser = page({ navigation: 'navigate', controls });
  assert.equal(project.textContent, ' Start a project ');
  assert.equal(enquiry.textContent, 'Send enquiry');
  assert.equal(controls[0].children[0], wrapper);
  assert.equal(controls[0].children[1], icon);
  assert.equal(icon.textContent, '↗');
  assert.equal(unrelated.textContent, 'DOWNLOAD RESOURCE');
  browser.navigate('/services');
  assert.equal(project.textContent, ' Start a project ');
});
