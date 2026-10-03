/* Keep bounded, crawlable additions after Framer's existing client hydration. */
(() => {
  const tag = document.getElementById('irg-page-enhancements');
  if (!tag) return;
  const config = JSON.parse(tag.textContent);
  const excluded = 'nav,footer,form,[data-framer-name="Resources CTA"],[data-irg-addition],.irg-markets';
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
      if (heading.querySelector('span[style*="display:inline-block"]')) {
        if (!heading.hasAttribute('aria-label')) heading.setAttribute('aria-label', heading.textContent.trim());
        for (const span of heading.children) if (span.tagName === 'SPAN' && !span.hasAttribute('aria-hidden')) span.setAttribute('aria-hidden','true');
      }
    }
    if (config.page === 'resources' || config.page === 'privacy') return;
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
  observer.observe(document.body, { childList: true, subtree: true });
  observer.observe(document.head, { childList: true, subtree: true });
})();
