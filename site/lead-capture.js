/* IRG lead capture.
   Copies every successful form submission on the site to the "Website Leads" Google Sheet
   (via a Make webhook), independently of the Framer form backend.
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
    } catch (e) { /* never block the form */ }
  }, true);
})();
