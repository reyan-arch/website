#!/usr/bin/env python3
"""Local static preview with form submissions disabled.

Production keeps the site's existing Framer and Make form integrations. This
preview injects its submit blocker before the original scripts, preserving their
UI while preventing local review from submitting a form to those services.
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from io import BytesIO
from pathlib import Path
from urllib.parse import urlsplit
import os
import re

SITE = Path(__file__).resolve().parents[1] / 'site'

PREVIEW_GUARD = b'''<script data-irg-local-preview>
(() => {
  if (window.__irgLocalPreviewFormsBlocked) return;
  window.__irgLocalPreviewFormsBlocked = true;
  window.addEventListener('submit', event => {
    event.preventDefault();
    event.stopImmediatePropagation();
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    let status = form.nextElementSibling;
    if (!status || !status.hasAttribute('data-irg-preview-form-status')) {
      status = document.createElement('p');
      status.setAttribute('data-irg-preview-form-status', '');
      status.setAttribute('role', 'status');
      status.setAttribute('aria-live', 'polite');
      status.style.cssText = 'font:16px/1.5 Inter,Arial,sans-serif;color:#191c1f;background:#fff;border:1px solid #d9d9df;border-radius:14px;padding:14px 18px;margin:12px 0;max-width:640px;';
      form.insertAdjacentElement('afterend', status);
    }
    status.textContent = 'Local preview only: this form has not been sent. Use the live website to submit it.';
  }, {capture:true});
})();
</script>'''


def inject_preview_guard(document):
    """Insert before page scripts without changing the production file."""
    opening_head = re.search(br'<head\b[^>]*>', document, flags=re.I)
    if opening_head:
        position = opening_head.end()
        return document[:position] + PREVIEW_GUARD + document[position:]
    # HTML fragments without a head still receive the blocker before any script.
    return PREVIEW_GUARD + document


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def translate_path(self, request_path):
        path = urlsplit(request_path).path
        if path != '/' and not Path(path).suffix:
            candidate = super().translate_path(path + '.html')
            if Path(candidate).is_file():
                return candidate
        return super().translate_path(request_path)

    def end_headers(self):
        # Includes files, redirects, error pages and rejected POST requests.
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def send_head(self):
        path = Path(self.translate_path(self.path))
        if path.is_dir():
            if not urlsplit(self.path).path.endswith('/'):
                return super().send_head()
            for index in ('index.html', 'index.htm'):
                if (path / index).is_file():
                    path = path / index
                    break
        if path.is_file() and self.guess_type(str(path)) == 'text/html':
            try:
                document = inject_preview_guard(path.read_bytes())
            except OSError:
                self.send_error(404, 'File not found')
                return None
            # HTML is always read fresh, including conditional requests. The
            # returned length covers the injected script for both GET and HEAD.
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(document)))
            self.end_headers()
            return BytesIO(document)
        return super().send_head()

    def do_POST(self):
        self.send_response(503)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok":false,"message":"This visual preview does not send enquiries. Please use email or the live site."}')


if __name__ == '__main__':
    port = int(os.environ.get('IRG_PREVIEW_PORT', '4173'))
    print(f'IRG preview: http://127.0.0.1:{port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()
