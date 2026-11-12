from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html = (root / "index.html").read_text(encoding="utf-8")
library = root / "vendor" / "jszip.min.js"
license_file = root / "vendor" / "JSZip-LICENSE.txt"

assert library.is_file(), "Local JSZip bundle is missing"
assert license_file.is_file(), "JSZip license is missing"
assert "JSZip v3.10.1" in library.read_text(encoding="utf-8")[:200]
assert './vendor/jszip.min.js' in html, "Demo must load its local JSZip bundle"
assert "corsProxy" not in html, "Third-party CORS proxy selector must not return"
assert "allorigins.win" not in html and "corsproxy.io" not in html
assert "credentials: 'omit'" in html, "Direct requests must omit credentials"
assert "new AbortController()" in html, "The operator must be able to cancel requests"

remote_scripts = re.findall(r'<script[^>]+src=["\'](https?://[^"\']+)', html, re.IGNORECASE)
assert not remote_scripts, f"Unexpected remote JavaScript dependencies: {remote_scripts}"

site = root / "site"
(site / "vendor").mkdir(parents=True, exist_ok=True)
(site / "index.html").write_text(html, encoding="utf-8")
(site / "vendor" / "jszip.min.js").write_bytes(library.read_bytes())

print("Static demo validation passed; site/ contains only the browser demo and local JSZip.")
