/* IRG lead capture.
   Copies every successful form submission on the site to the "Website Leads" Google Sheet
   (via a Make webhook), independently of the Framer form backend, then shows a thank-you
   confirmation in the site's brand style.
   Loaded on every page: the site navigates client-side, so the listener lives on document. */
(function () {
  var ENDPOINT = "https://hook.eu2.make.com/2zijd3f6yfwi3d4brzk9gwrlmz2a9mll";
  var FIELDS = ["name", "email", "company", "timing", "project_context"];
  var lastKey = "";

  // Framer forms carry invisible honeypot inputs (some reuse real names like "company").
  function isHidden(el) {
    return el.type === "hidden" || el.tabIndex === -1 || el.getAttribute("aria-hidden") === "true" ||
      !!el.closest('[aria-hidden="true"]') || el.offsetParent === null;
  }


  /* ---------- Thank-you confirmation ---------- */
  var CSS = [
    ".irg-ty{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:center;justify-content:center;padding:16px;background:rgba(10,10,10,.44);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);opacity:0;transition:opacity .35s ease}",
    ".irg-ty.is-in{opacity:1}",
    ".irg-ty__card{position:relative;width:100%;max-width:440px;background:#fff;border-radius:28px;padding:46px 40px 40px;text-align:center;overflow:hidden;box-shadow:0 30px 80px -20px rgba(22,24,26,.5),0 0 0 1px rgba(22,24,26,.05);transform:translateY(26px) scale(.955);opacity:0;transition:transform .7s cubic-bezier(.2,.9,.25,1.12),opacity .4s ease}",
    ".irg-ty.is-in .irg-ty__card{transform:none;opacity:1}",
    ".irg-ty__card:before{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(110% 70% at 0% 0%,rgba(255,49,49,.11),transparent 62%),radial-gradient(110% 70% at 100% 0%,rgba(34,61,254,.12),transparent 62%)}",
    ".irg-ty__mark{position:relative;width:88px;height:88px;margin:0 auto 26px}",
    ".irg-ty__halo{position:absolute;inset:-14px;border-radius:50%;background:linear-gradient(135deg,#ff3131,#223dfe);filter:blur(22px);opacity:0;transform:scale(.6);animation:irgTyHalo 1.5s .25s cubic-bezier(.2,.8,.2,1) forwards}",
    ".irg-ty__disc{position:absolute;inset:0;border-radius:50%;background:#fff}",
    ".irg-ty__svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible}",
    ".irg-ty__ring{fill:none;stroke:url(#irg-ty-g);stroke-width:3;stroke-linecap:round;stroke-dasharray:252;stroke-dashoffset:252;transform:rotate(-90deg);transform-origin:44px 44px;animation:irgTyDraw .85s .2s cubic-bezier(.65,0,.35,1) forwards}",
    ".irg-ty__check{fill:none;stroke:#191c1f;stroke-width:3.5;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:48;stroke-dashoffset:48;animation:irgTyDraw .42s .85s cubic-bezier(.65,0,.35,1) forwards}",
    ".irg-ty__dot{position:absolute;left:50%;top:50%;width:8px;height:8px;margin:-4px;border-radius:50%;opacity:0;animation:irgTyBurst .95s 1s cubic-bezier(.15,.75,.3,1) forwards}",
    ".irg-ty__pill{display:inline-block;margin:0 0 14px;padding:6px 12px;border-radius:999px;background:#f4f4f4;color:#505a63;font:600 11px/1 'BDO Grotesk Variable','Inter',sans-serif;letter-spacing:.12em;text-transform:uppercase}",
    ".irg-ty__title{margin:0 0 10px;color:#191c1f;font:500 30px/1.15 'General Sans','Inter',sans-serif;letter-spacing:-.02em}",
    ".irg-ty__text{margin:0 auto 28px;max-width:330px;color:#505a63;font:400 16px/1.5 'Inter',sans-serif}",
    ".irg-ty__text b{color:#191c1f;font-weight:500;word-break:break-word}",
    ".irg-ty__btn{appearance:none;border:0;cursor:pointer;border-radius:999px;padding:15px 30px;color:#fff;background:linear-gradient(135deg,#ff3131 0%,#223dfe 100%);font:600 13px/1 'BDO Grotesk Variable','Inter',sans-serif;letter-spacing:.1em;text-transform:uppercase;transition:transform .25s ease,box-shadow .25s ease}",
    ".irg-ty__btn:hover{transform:translateY(-2px);box-shadow:0 12px 26px -10px rgba(34,61,254,.65)}",
    ".irg-ty__btn:focus-visible{outline:2px solid #223dfe;outline-offset:3px}",
    ".irg-ty__rise{opacity:0;transform:translateY(12px);animation:irgTyRise .6s cubic-bezier(.2,.8,.2,1) forwards}",
    ".irg-ty__bar{position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,#ff3131,#223dfe);transform-origin:left;animation:irgTyBar 7s 1.2s linear forwards}",
    ".irg-ty__card:hover .irg-ty__bar{animation-play-state:paused}",
    "@keyframes irgTyDraw{to{stroke-dashoffset:0}}",
    "@keyframes irgTyHalo{45%{opacity:.5;transform:scale(1.15)}100%{opacity:.2;transform:scale(1)}}",
    "@keyframes irgTyBurst{0%{opacity:0;transform:rotate(var(--a)) translateX(30px) scale(.3)}25%{opacity:1}100%{opacity:0;transform:rotate(var(--a)) translateX(var(--d)) scale(1)}}",
    "@keyframes irgTyRise{to{opacity:1;transform:none}}",
    "@keyframes irgTyBar{to{transform:scaleX(0)}}",
    "@media (max-width:480px){.irg-ty__card{padding:38px 24px 32px;border-radius:24px}.irg-ty__title{font-size:26px}}",
    "@media (prefers-reduced-motion:reduce){.irg-ty,.irg-ty__card{transition:none}.irg-ty__ring,.irg-ty__check{animation:none;stroke-dashoffset:0}.irg-ty__rise{animation:none;opacity:1;transform:none}.irg-ty__dot,.irg-ty__bar{display:none}.irg-ty__halo{animation:none;opacity:.2;transform:none}}"
  ].join("");

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function showThanks(formName, data) {
    try {
      if (!document.getElementById("irg-ty-css")) {
        var st = el("style"); st.id = "irg-ty-css"; st.textContent = CSS; document.head.appendChild(st);
      }
      var old = document.querySelector(".irg-ty"); if (old) old.remove();
      var first = (data.name || "").split(/\s+/)[0].slice(0, 24);
      var enquiry = /enquiry/i.test(formName);
      var back = document.activeElement;

      var root = el("div", "irg-ty");
      root.setAttribute("role", "dialog");
      root.setAttribute("aria-modal", "true");
      root.setAttribute("aria-labelledby", "irg-ty-title");
      var card = el("div", "irg-ty__card");

      var mark = el("div", "irg-ty__mark");
      mark.appendChild(el("div", "irg-ty__halo"));
      mark.appendChild(el("div", "irg-ty__disc"));
      // Static markup only: no user data goes through innerHTML.
      var svgBox = el("div");
      svgBox.innerHTML = '<svg class="irg-ty__svg" viewBox="0 0 88 88" aria-hidden="true"><defs><linearGradient id="irg-ty-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff3131"/><stop offset="1" stop-color="#223dfe"/></linearGradient></defs><circle class="irg-ty__ring" cx="44" cy="44" r="40"/><path class="irg-ty__check" d="M29 45.5l10.5 10.5L60 34"/></svg>';
      mark.appendChild(svgBox.firstChild);
      var colors = ["#ff3131", "#223dfe", "#8f37b0"];
      for (var i = 0; i < 12; i++) {
        var d = el("span", "irg-ty__dot");
        d.style.setProperty("--a", (i * 30 + 12) + "deg");
        d.style.setProperty("--d", (i % 2 ? 78 : 62) + "px");
        d.style.background = colors[i % 3];
        if (i % 2) { d.style.width = d.style.height = "5px"; d.style.margin = "-2.5px"; }
        d.style.animationDelay = (1 + (i % 3) * 0.04) + "s";
        mark.appendChild(d);
      }
      card.appendChild(mark);

      var pill = el("div", "irg-ty__pill irg-ty__rise", enquiry ? "Enquiry received" : "Request received");
      pill.style.animationDelay = ".45s";
      var title = el("h2", "irg-ty__title irg-ty__rise", first ? "Thank you, " + first + "." : "Thank you.");
      title.id = "irg-ty-title"; title.style.animationDelay = ".55s";
      var text = el("p", "irg-ty__text irg-ty__rise");
      text.style.animationDelay = ".65s";
      text.appendChild(document.createTextNode(enquiry ? "Your enquiry is with the team. We'll reply to " : "Your details are in. We'll be in touch at "));
      text.appendChild(el("b", null, data.email));
      text.appendChild(document.createTextNode(enquiry ? " shortly." : "."));
      var btn = el("button", "irg-ty__btn irg-ty__rise", "Done");
      btn.type = "button"; btn.style.animationDelay = ".75s";
      var bar = el("div", "irg-ty__bar");
      card.appendChild(pill); card.appendChild(title); card.appendChild(text); card.appendChild(btn); card.appendChild(bar);
      root.appendChild(card);

      var closed = false, timer;
      function close() {
        if (closed) return; closed = true;
        clearTimeout(timer);
        document.removeEventListener("keydown", onKey, true);
        root.classList.remove("is-in");
        setTimeout(function () { root.remove(); }, 380);
        try { if (back && back.focus) back.focus({ preventScroll: true }); } catch (e) {}
      }
      function onKey(e) { if (e.key === "Escape") close(); }
      btn.addEventListener("click", close);
      root.addEventListener("click", function (e) { if (e.target === root) close(); });
      bar.addEventListener("animationend", close);
      document.addEventListener("keydown", onKey, true);
      timer = setTimeout(close, 20000); // safety net (also covers reduced-motion, where the bar is hidden)

      document.body.appendChild(root);
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        root.classList.add("is-in");
        try { btn.focus({ preventScroll: true }); } catch (e) {}
      }); });
    } catch (e) { /* never block the form */ }
  }

  document.addEventListener("submit", function (ev) {
    try {
      var form = ev.target;
      if (!form || form.tagName !== "FORM") return;
      var data = {}, bot = false;
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.tagName === "BUTTON") return;
        var v = (el.value || "").trim();
        if (isHidden(el)) { if (v) bot = true; return; }
        if (FIELDS.indexOf(el.name) !== -1 && !(el.name in data)) data[el.name] = v.slice(0, 2000);
      });
      if (bot || !data.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) return;

      var formName = form.getAttribute("data-framer-name") || "Website form";
      var key = formName + "|" + data.email;
      if (key === lastKey) return; // double-click guard
      lastKey = key;
      setTimeout(function () { lastKey = ""; }, 10000);

      var p = new URLSearchParams();
      p.set("form", formName);
      FIELDS.forEach(function (k) { p.set(k, data[k] || ""); });
      p.set("page", location.href.slice(0, 500));
      p.set("referrer", (document.referrer || "").slice(0, 500));
      // sendBeacon survives page navigation; urlencoded body needs no CORS preflight.
      if (!(navigator.sendBeacon && navigator.sendBeacon(ENDPOINT, p))) {
        fetch(ENDPOINT, { method: "POST", body: p, mode: "no-cors", keepalive: true });
      }
      setTimeout(function () { showThanks(formName, data); }, 250);
    } catch (e) { /* never block the form */ }
  }, true);
})();
