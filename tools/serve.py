#!/usr/bin/env python3
"""Local dev server for the C3S viewer.

Serves docs/ and lets the in-page "save region defaults → file" button write the
current calibration sliders straight into docs/index.html (the REGION_CAL block).
Tune a region's pan/zoom in the browser, click save, then commit & push — the
values you set become the defaults everyone sees on GitHub Pages.

Usage:
    python3 tools/serve.py            # http://localhost:8000
    python3 tools/serve.py 8080       # custom port

The save button only appears when the page is opened from localhost. The deployed
GitHub Pages site never calls this API and stays a pure static page (no backend).
"""
import json
import re
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
INDEX = DOCS / "index.html"


def fmt(v: float) -> str:
    """Compact number: round to 4 dp and drop trailing zeros (0.30 -> 0.3, 4.0 -> 4)."""
    s = f"{round(float(v), 4):.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def obj(cal: dict) -> str:
    return f'{{x:{fmt(cal["x"])},y:{fmt(cal["y"])},z:{fmt(cal["z"])}}}'


def patch_region(region: str, sk: dict, fc: dict) -> None:
    """Replace the single-line REGION_CAL entry for `region` in index.html.

    Scoped to the `const REGION_CAL={ ... };` block so it can't touch the
    identically-keyed lines in AREAS or COUNTRY.
    """
    text = INDEX.read_text()
    block = re.compile(r'(const REGION_CAL=\{)(.*?)(\n\};)', re.S)
    bm = block.search(text)
    if not bm:
        raise ValueError("could not find the REGION_CAL block")

    new_obj = f"{{sk:{obj(sk)}, fc:{obj(fc)}}}"
    # match:  <indent>"Region":<pad>{ ... }<optional comma>  on its own line
    pat = re.compile(r'(?m)^(\s*"' + re.escape(region) + r'":\s*)\{.*\}(,?)\s*$')
    new_inner, n = pat.subn(lambda m: f"{m.group(1)}{new_obj}{m.group(2) or ','}", bm.group(2))
    if n != 1:
        raise ValueError(f"expected exactly 1 REGION_CAL line for {region!r}, found {n}")
    INDEX.write_text(text[:bm.start()] + bm.group(1) + new_inner + bm.group(3) + text[bm.end():])


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DOCS), **kwargs)

    def do_POST(self):
        if self.path != "/api/save-calibration":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            patch_region(body["region"], body["sk"], body["fc"])
            payload = json.dumps({"ok": True, "region": body["region"]}).encode()
            code = 200
            print(f"saved {body['region']}: sk={body['sk']} fc={body['fc']}")
        except Exception as e:  # surface the reason to the browser
            payload = json.dumps({"ok": False, "error": str(e)}).encode()
            code = 500
            print(f"save error: {e}", file=sys.stderr)
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"C3S viewer → http://localhost:{port}   (writes {INDEX})")
    try:
        HTTPServer(("127.0.0.1", port), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
