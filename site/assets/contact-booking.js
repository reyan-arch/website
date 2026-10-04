/* The supplied inline embed, kept intact through Contact's Framer hydration. */
(() => {
  const tag = document.getElementById('irg-page-enhancements');
  if (!tag) return;
  const config = JSON.parse(tag.textContent);
  if (config.page !== 'contact' || !config.bookingHtml) return;
  let ready = document.readyState === 'complete';
  let loading = false;
  let failed = false;
  let entryPending = location.hash === '#book-a-call';
  const watchedFrames = new WeakSet();
  const alignEntry = () => {
    if (entryPending && location.hash === '#book-a-call') requestAnimationFrame(() => document.getElementById('book-a-call')?.scrollIntoView({block:'start',behavior:'instant'}));
  };
  let observedMain;
  const entryObserver = new ResizeObserver(alignEntry);
  // Hydration can change the original form's height after an anchor entry.
  // Finish that entry when the calendar loads, unless the visitor has moved on.
  for (const event of ['wheel','pointerdown','touchstart','keydown']) document.addEventListener(event, () => {entryPending = false;}, {passive:true});
  window.addEventListener('resize', () => {entryPending = false;});
  document.addEventListener('click', event => {
    const anchor = event.target.closest('a[href]');
    if (!anchor) return;
    const target = new URL(anchor.href,location.href);
    if (target.origin === location.origin && target.pathname === location.pathname && target.hash === '#book-a-call') entryPending = true;
  });
  const watchFrame = frame => {
    if (!frame || watchedFrames.has(frame)) return;
    watchedFrames.add(frame);
    frame.addEventListener('load', () => {
      alignEntry();
    }, {once:true});
  };
  const initialize = () => {
    const widget = document.querySelector('#book-a-call .calendly-inline-widget');
    if (!widget || !ready || failed) return;
    const frame = widget.querySelector('iframe');
    if (frame) {
      if (frame.title !== 'Book an IRG Media discovery call') frame.title = 'Book an IRG Media discovery call';
      watchFrame(frame);
      return;
    }
    if (window.Calendly?.initInlineWidget) {
      window.Calendly.initInlineWidget({url:widget.dataset.url,parentElement:widget});
      const created = widget.querySelector('iframe');
      if (created) {created.title = 'Book an IRG Media discovery call';watchFrame(created);}
      return;
    }
    if (loading) return;
    loading = true;
    const script = document.createElement('script');
    script.id = 'irg-calendly-script';
    script.type = 'text/javascript';
    script.src = 'https://assets.calendly.com/assets/external/widget.js';
    script.async = true;
    script.onload = initialize;
    script.onerror = () => { failed = true; };
    document.head.append(script);
  };
  const patch = () => {
    const main = document.querySelector('main[data-framer-name="IRG opening dark"]');
    if (main && main !== observedMain) {entryObserver.disconnect();entryObserver.observe(main);observedMain = main;}
    if (main && !document.getElementById('book-a-call')) {
      const fragment = document.createElement('template');
      fragment.innerHTML = config.bookingHtml;
      main.after(fragment.content.cloneNode(true));
      if (location.hash === '#book-a-call') requestAnimationFrame(() => document.getElementById('book-a-call')?.scrollIntoView({block:'start',behavior:'instant'}));
    }
    const utility = document.querySelector('[data-framer-name="Contact utility"]');
    if (utility && !utility.querySelector('.irg-booking-jump')) {
      const fragment = document.createElement('template');
      fragment.innerHTML = config.bookingJumpHtml;
      const email = utility.querySelector('[data-framer-name="Direct contact"]');
      if (email) email.before(fragment.content.cloneNode(true));
      else utility.append(fragment.content.cloneNode(true));
    }
    initialize();
  };
  // Load the provider after parsing, so its standard auto-loader sees one widget.
  if (!ready) {
    document.addEventListener('DOMContentLoaded', () => {ready = true;patch();}, {once:true});
  } else {
    patch();
  }
  let scheduled = false;
  new MutationObserver(() => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => {scheduled = false;patch();});
  }).observe(document.body, {childList:true,subtree:true});
})();
