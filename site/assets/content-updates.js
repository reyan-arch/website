/* Keep bounded, crawlable additions after Framer's existing client hydration. */
(() => {
  const tag = document.getElementById('irg-page-enhancements');
  if (!tag) return;
  const config = JSON.parse(tag.textContent);
  const excluded = 'nav,footer,form,[data-framer-name="Resources CTA"],[data-irg-addition],.irg-markets,[data-framer-name="FAQ List"]';
  const faqOpen = new Map();
  // Native toggle does not bubble; capture records the user's state before hydration.
  document.addEventListener('toggle', event => {
    const item = event.target;
    if (item.matches?.('details[data-irg-faq-key]') && item.closest('[data-framer-name="FAQ List"]')) {
      faqOpen.set(item.dataset.irgFaqKey, item.open);
    }
  }, true);
  const patchFaq = () => {
    if (!config.faqHtml) return;
    for (const list of document.querySelectorAll('[data-framer-name="FAQ List"]')) {
      if (list.querySelector('details[data-irg-faq-key]')) continue;
      list.innerHTML = config.faqHtml;
      for (const item of list.querySelectorAll('details[data-irg-faq-key]')) {
        item.open = faqOpen.get(item.dataset.irgFaqKey) || false;
      }
    }
  };
  const setText = (element, value) => {
    if (element && element.textContent !== value) element.textContent = value;
  };
  const patchCaseStudy = () => {
    const study = config.caseStudy;
    if (!study) return;
    for (const marker of document.querySelectorAll('[data-story-cms-item][data-slug="holafly"]')) {
      if (marker.getAttribute('data-card-title') !== study.headline) marker.setAttribute('data-card-title', study.headline);
    }
    for (const link of document.querySelectorAll('.sc-card a[href],a[data-framer-name="Case Study"][href]')) {
      const path = new URL(link.href, location.href).pathname.replace(/\.html$/, '').replace(/\/$/, '');
      if (path !== study.path) continue;
      const homeCard = link.closest('.sc-card');
      if (homeCard) {
        setText(homeCard.querySelector('h3.sc-lead'), study.headline);
        const label = `See work: ${study.headline}`;
        if (link.hasAttribute('aria-label') && link.getAttribute('aria-label') !== label) link.setAttribute('aria-label', label);
      } else {
        setText(link.querySelector('h2'), study.headline);
        study.focus.forEach((focus, index) => {
          const metric = link.querySelector(`[data-framer-name="Case metrics"] [data-framer-name="Metric ${index + 1}"]`);
          const paragraphs = metric?.querySelectorAll('p');
          if (paragraphs?.length === 2) {
            setText(paragraphs[0], focus.value);
            setText(paragraphs[1], focus.label);
          }
        });
      }
    }
  };
  const patch = () => {
    if (document.title !== config.title) document.title = config.title;
    for (const [key, value] of [['description',config.description],['robots',config.robots]]) {
      const meta = document.querySelector(`meta[name="${key}"]`);
      if (meta && meta.content !== value) meta.content = value;
    }
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical && canonical.href !== config.canonical) canonical.href = config.canonical;
    for (const a of document.querySelectorAll('a[href*="agr.studio"]')) {
      a.href = 'https://leadscorer.co/';
      for (const text of a.querySelectorAll('p,span')) if (text.textContent.trim() === 'by agr.studio') text.textContent = 'by leadscorer.co';
      if (a.textContent.trim() === 'by agr.studio') a.textContent = 'by leadscorer.co';
    }
    // Existing responsive hero retains its visuals and gets a readable heading name.
    for (const heading of document.querySelectorAll('h1,h2,h3')) {
      if ([...heading.querySelectorAll('span[style]')].some(span => /display\s*:\s*inline-block/.test(span.getAttribute('style') || ''))) {
        if (!heading.hasAttribute('aria-label')) heading.setAttribute('aria-label', heading.textContent.trim());
        for (const span of heading.children) if (span.tagName === 'SPAN' && !span.hasAttribute('aria-hidden')) span.setAttribute('aria-hidden','true');
      }
    }
    if (config.page === 'resources' || config.page === 'privacy') return;
    patchFaq();
    patchCaseStudy();
    if (config.page === 'services') {
      const outputs = document.querySelector('[data-framer-name="Services / tangible outputs"]');
      if (outputs && !outputs.id) outputs.id = 'evaluation';
    }
    for (const p of document.querySelectorAll('p')) {
      if (!p.closest(excluded)) for (const item of config.replacements || []) if (p.textContent.trim() === item.from) p.textContent = item.to;
      if (p.closest(excluded) || p.querySelector('a')) continue;
      // Split text nodes only: existing nested marks, links and animation are retained.
      for (const item of config.inlineLinks || []) {
        const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
        const textNodes = []; let node;
        while ((node = walker.nextNode())) if (!node.parentElement.closest('a')) textNodes.push(node);
        for (const text of textNodes) {
          const at = text.textContent.toLowerCase().indexOf(item.phrase.toLowerCase());
          if (at < 0) continue;
          const before = text.textContent[at - 1], after = text.textContent[at + item.phrase.length];
          if ((before && /\w/.test(before)) || (after && /\w/.test(after))) continue;
          const link = document.createElement('a'); link.href = item.href; link.className = 'irg-context-link';
          const match = text.splitText(at); match.splitText(item.phrase.length);
          link.textContent = match.textContent; match.replaceWith(link); break;
        }
      }
    }
    const footer = document.querySelector('footer');
    if (footer && config.additionHtml && !document.querySelector('[data-irg-addition="related"]')) {
      let container = footer;
      while (container.parentElement && (container.parentElement.classList.contains('ssr-variant') || [...container.parentElement.classList].some(c => c.endsWith('-container')))) container = container.parentElement;
      const fragment = document.createElement('template'); fragment.innerHTML = config.additionHtml;
      container.before(fragment.content.cloneNode(true));
      const id = decodeURIComponent(location.hash.slice(1));
      if (id && document.getElementById(id)?.closest('.irg-markets,[data-irg-addition]')) requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({block:'start',behavior:'instant'}));
    }
  };
  // Each exported route loads its own initial HTML and enhancement manifest.
  // Let browser-native navigation run instead of Framer's client router.
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href]');
    if (!anchor || anchor.hasAttribute('download') || anchor.target === '_blank' || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = new URL(anchor.href,location.href);
    if (target.origin === location.origin && target.pathname !== location.pathname) event.stopPropagation();
  },true);
  patch();
  let scheduled = false;
  const observer = new MutationObserver(() => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; patch(); });
  });
  observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-card-title'] });
  observer.observe(document.head, { childList: true, subtree: true });
})();
