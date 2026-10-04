/* Identity-only enhancement for the existing Framer pages. */
(() => {
  "use strict";
  if (window.__irgBrandUpdates) return;
  window.__irgBrandUpdates = true;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  let intro = null;
  let introTimeout = 0;
  let pending = false;
  let currentPath = window.location.pathname;
  const existingLegacy = !!document.querySelector('[data-irg-preloader="true"]');
  const previous = {
    overflow: existingLegacy ? "" : document.body.style.overflow,
    padding: existingLegacy ? "" : document.body.style.paddingRight,
    gutter: existingLegacy ? "" : document.documentElement.style.scrollbarGutter,
  };

  function dismissIntro() {
    window.clearTimeout(introTimeout);
    if (intro) intro.remove();
    intro = null;
  }

  function showIntro() {
    dismissIntro();
    // Only an explicit home-page refresh gets the identity reveal. A normal
    // visit, history restoration or Framer navigation must remain immediate.
    if (!["/", "/index.html"].includes(window.location.pathname)) return;
    const navigation = performance.getEntriesByType?.("navigation")[0];
    if (navigation?.type !== "reload" || reduced.matches || document.hidden || window.location.hash || window.scrollY > 0) return;
    const started = performance.now();
    const overlay = document.createElement("div");
    overlay.className = "irg-brand-intro";
    overlay.dataset.irgBrandIntro = "true";
    overlay.setAttribute("role", "status");
    overlay.setAttribute("aria-label", "Loading IRG Media");
    const logo = document.createElement("div");
    logo.className = "irg-brand-intro-logo";
    logo.setAttribute("aria-hidden", "true");
    const images = ["base", "reveal"].map(layer => {
      const image = document.createElement("img");
      image.className = "irg-brand-intro-" + layer;
      image.src = "/assets/irg-lockup.svg";
      image.alt = "";
      image.width = 88;
      image.height = 28;
      image.decoding = "sync";
      image.fetchPriority = "high";
      logo.append(image);
      return image;
    });
    overlay.append(logo);
    intro = overlay;
    document.body.append(overlay);
    // An unavailable/slow asset never leaves a blank loading screen.
    const activate = () => {
      if (intro !== overlay || performance.now() - started > 350) return;
      if (!images.every(image => image.complete && image.naturalWidth)) return;
      overlay.dataset.active = "true";
    };
    for (const image of images) {
      image.addEventListener("load", activate, { once: true });
      image.addEventListener("error", () => { if (intro === overlay) dismissIntro(); }, { once: true });
    }
    activate();
    introTimeout = window.setTimeout(dismissIntro, 1200);
  }

  function releaseLegacyLock() {
    if (!document.querySelector('[data-irg-preloader="true"]')) return;
    // The mobile menu keeps its own scroll behavior.
    if (document.querySelector('nav [data-framer-name="Close navigation"]')) return;
    const body = document.body;
    const html = document.documentElement;
    if (body.style.overflow === "hidden" && body.style.overflow !== previous.overflow) body.style.overflow = previous.overflow;
    if (body.style.paddingRight !== previous.padding) body.style.paddingRight = previous.padding;
    if (html.style.scrollbarGutter === "stable" && html.style.scrollbarGutter !== previous.gutter) html.style.scrollbarGutter = previous.gutter;
  }

  const headingEmphasis = [
    ["Real performance.", "red"], ["Scaled year on year.", "blue"],
    ["creator fit", "red"], ["campaign impact", "blue"],
    ["Clear roles.", "red"], ["Confident decisions.", "blue"],
    ["next one", "red"], ["smarter.", "blue"],
    ["your team.", "red"], ["the work.", "blue"],
    ["needs", "red"], ["change.", "blue"],
    ["Work,", "red"], ["context.", "blue"],
    ["Privacy", "red"], ["policy", "blue"],
  ];

  function usesLightText(element) {
    const channels = getComputedStyle(element).color.match(/[\d.]+/g);
    return !!channels && channels.slice(0, 3).every(channel => Number(channel) > 190);
  }

  function hasDarkSurface(element) {
    for (let current = element; current; current = current.parentElement) {
      const style = getComputedStyle(current);
      const channels = style.backgroundColor.match(/[\d.]+/g)?.map(Number);
      if (channels && (channels.length < 4 || channels[3] > .85)) {
        const linear = channels.slice(0, 3).map(channel => {
          const value = channel / 255;
          return value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4;
        });
        return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2] < .2;
      }
      if (style.backgroundImage !== 'none') return usesLightText(current);
    }
    return false;
  }

  function markReadingInk() {
    for (const text of document.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,td,th,label,input,textarea,select,a')) {
      if (text.closest('nav,.irg-brand-intro') || text.dataset.irgReadingInk) continue;
      const channels = getComputedStyle(text).color.match(/[\d.]+/g)?.slice(0, 3).map(Number);
      if (!channels || Math.max(...channels) >= 220 || Math.max(...channels) - Math.min(...channels) >= 30) continue;
      // Normalize neutral reading text only on a pale surface. Existing white
      // text on dark cards, gradients and photography keeps its original fill.
      if (!hasDarkSurface(text)) text.dataset.irgReadingInk = 'true';
    }
  }

  const headingCopies = new WeakMap();
  function colorHeading(heading) {
    let text = heading.textContent;
    if (heading.dataset.irgColoredText === text && heading.querySelector('[data-irg-brand-tone]')) return;
    // React retains references to its text nodes across responsive updates.
    // Keep those nodes in their original parent instead of replacing them.
    for (const copy of headingCopies.get(heading) || []) {
      if (copy.node.isConnected && copy.node.textContent === '') copy.node.textContent = copy.text;
      copy.visual.remove();
    }
    headingCopies.delete(heading);
    text = heading.textContent;
    const ranges = [];
    for (const [phrase, tone] of headingEmphasis) {
      const start = text.toLowerCase().indexOf(phrase.toLowerCase());
      if (start >= 0) ranges.push({ start, end: start + phrase.length, tone });
    }
    if (!ranges.length) return;
    const inverse = usesLightText(heading);
    // Framer's character spans and text-node identities remain intact.
    for (const span of heading.querySelectorAll('[data-irg-brand-tone]')) span.removeAttribute('data-irg-brand-tone');
    const walker = document.createTreeWalker(heading, NodeFilter.SHOW_TEXT);
    const nodes = []; let node; let offset = 0;
    while ((node = walker.nextNode())) {
      nodes.push({ node, start: offset, end: offset + node.textContent.length });
      offset += node.textContent.length;
    }
    const copies = [];
    for (const entry of nodes) {
      const intersecting = ranges.filter(range => range.start < entry.end && range.end > entry.start);
      if (!intersecting.length) continue;
      const cuts = new Set([0, entry.node.textContent.length]);
      for (const range of intersecting) {
        cuts.add(Math.max(0, range.start - entry.start));
        cuts.add(Math.min(entry.node.textContent.length, range.end - entry.start));
      }
      const stops = [...cuts].sort((a, b) => a - b);
      const fragments = [];
      for (let i = 0; i < stops.length - 1; i++) {
        const start = stops[i], end = stops[i + 1];
        if (start === end) continue;
        const range = intersecting.find(item => entry.start + start >= item.start && entry.start + end <= item.end);
        fragments.push({ text: entry.node.textContent.slice(start, end), tone: range && ((inverse ? "inverse-" : "") + range.tone) });
      }
      if (fragments.length === 1 && fragments[0].tone && entry.node.parentElement.tagName === 'SPAN') {
        entry.node.parentElement.dataset.irgBrandTone = fragments[0].tone;
      } else {
        const fragment = document.createElement('span');
        fragment.dataset.irgColorCopy = 'true';
        for (const part of fragments) {
          if (!part.tone) fragment.append(document.createTextNode(part.text));
          else {
            const span = document.createElement('span');
            span.dataset.irgColorFragment = "true";
            span.dataset.irgBrandTone = part.tone;
            span.textContent = part.text;
            fragment.append(span);
          }
        }
        const original = entry.node.textContent;
        entry.node.textContent = '';
        entry.node.after(fragment);
        copies.push({node:entry.node,text:original,visual:fragment});
      }
    }
    headingCopies.set(heading, copies);
    heading.dataset.irgColoredText = text;
  }

  function colorType() {
    markReadingInk();
    for (const heading of document.querySelectorAll('h1')) colorHeading(heading);
    // Exact existing section-pill construction, not arbitrary code components.
    for (const pill of document.querySelectorAll('[data-code-component-plugin-id="api"]>div')) {
      if (pill.style.height !== '32px' || pill.style.minWidth !== 'max-content' || !pill.querySelector('svg')) continue;
      if (!pill.dataset.irgBrandPill) pill.dataset.irgBrandPill = 'true';
      const label = pill.lastElementChild;
      if (label && label.tagName === 'SPAN' && !label.querySelector('svg')) {
        const tone = usesLightText(pill) ? 'inverse-red' : 'red';
        if (label.dataset.irgBrandTone !== tone) label.dataset.irgBrandTone = tone;
      }
    }
    for (const link of document.querySelectorAll('a.irg-context-link,.irg-detail-links a')) {
      const tone = (usesLightText(link.parentElement) || hasDarkSurface(link.parentElement)) ? 'inverse' : 'default';
      if (link.dataset.irgLinkTone !== tone) link.dataset.irgLinkTone = tone;
    }
    for (const kicker of document.querySelectorAll('.irg-detail-kicker')) {
      const tone = (kicker.closest('.irg-work-detail .framer-6tdioh') || usesLightText(kicker.parentElement)) ? 'inverse-red' : 'red';
      if (kicker.dataset.irgBrandTone !== tone) kicker.dataset.irgBrandTone = tone;
    }
    for (const number of document.querySelectorAll('.irg-detail-metric strong,.irg-detail-metric dd,.irg-detail-step-number')) {
      const base = number.classList.contains('irg-detail-step-number') ? 'red' : 'blue';
      const tone = (usesLightText(number.parentElement) ? 'inverse-' : '') + base;
      if (number.dataset.irgBrandTone !== tone) number.dataset.irgBrandTone = tone;
    }
  }

  function normalizeButtonLabels() {
    const labels = new Map([["START A PROJECT", "Start a project"], ["SEND ENQUIRY", "Send enquiry"], ["SEE HOW IRG WORKS", "See how IRG works"], ["EXPLORE OUR WORK", "Explore our work"], ["DISCUSS YOUR CAMPAIGN", "Discuss your campaign"], ["EXPLORE THE RESOURCE", "Explore the resource"]]);
    const controls = document.querySelectorAll('a.framer-N1V3k[data-framer-name="Primary"],a[data-framer-name="Framework CTA wrap"],a[data-framer-name="IRG CTA Button"],a[data-framer-name="Partner CTA Button"],a[data-framer-name="See How IRG Works Button"],form[data-framer-name="Project enquiry"] button[type="submit"],form[data-framer-name="Resource download form"] button[type="submit"],.irg-detail-actions a,.irg-update-button');
    for (const control of controls) {
      const walker = document.createTreeWalker(control, NodeFilter.SHOW_TEXT);
      let node;
      while ((node = walker.nextNode())) {
        const original = node.textContent;
        const trimmed = original.trim();
        const label = labels.get(trimmed.toUpperCase());
        if (label && trimmed !== label) node.textContent = original.replace(trimmed, label);
      }
    }
  }

  function refresh() {
    pending = false;
    releaseLegacyLock();
    for (const logo of document.querySelectorAll('a[data-framer-name="IRG Logo"]')) {
      if (!logo.hasAttribute("aria-label")) logo.setAttribute("aria-label", "IRG Media home");
    }
    colorType();
    normalizeButtonLabels();
    if (currentPath !== window.location.pathname) {
      currentPath = window.location.pathname;
      dismissIntro();
    }
  }

  function scheduleRefresh() {
    if (pending) return;
    pending = true;
    window.requestAnimationFrame(refresh);
  }

  // Child-list observation handles Framer hydration/navigation. It does not observe
  // animation styles, and accessibility attributes are written only when absent.
  const treeObserver = new MutationObserver(scheduleRefresh);
  treeObserver.observe(document.body, { childList: true, characterData: true, subtree: true });
  // Only the two elements the old preloader locks are observed for style changes.
  const lockObserver = new MutationObserver(releaseLegacyLock);
  lockObserver.observe(document.body, { attributes: true, attributeFilter: ["style"] });
  lockObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["style"] });
  reduced.addEventListener("change", () => { if (reduced.matches) dismissIntro(); });
  document.addEventListener("visibilitychange", () => { if (document.hidden) dismissIntro(); });
  document.addEventListener("pointerdown", dismissIntro, { passive: true });
  document.addEventListener("keydown", dismissIntro);
  window.addEventListener("scroll", dismissIntro, { passive: true });
  window.addEventListener("pagehide", dismissIntro);
  window.addEventListener("popstate", scheduleRefresh);
  window.addEventListener("pageshow", scheduleRefresh);
  refresh();
  showIntro();
})();
