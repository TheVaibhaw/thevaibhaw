#!/usr/bin/env python3
"""Preview the README locally, laid out like the GitHub profile page.

    python3 scripts/preview.py            # then open http://localhost:8000

The page is rebuilt on every refresh, so edit README.md / re-run forge.py and reload.
The skyline normally lives on the `output` branch, so a local copy is built at startup.
"""
import http.server
import os
import re
import socketserver
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".preview")
USER = "thevaibhaw"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>{user} — local profile preview</title>
<style>
body{{margin:0;background:#0d1117;color:#e6edf3;font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
a{{color:#4493f8;text-decoration:none}} a:hover{{text-decoration:underline}}
.top{{height:64px;background:#010409;border-bottom:1px solid #30363d;display:flex;align-items:center;padding:0 24px;gap:12px}}
.top b{{font-size:15px}} .tag{{margin-left:auto;font-size:12px;color:#7d8590;border:1px solid #30363d;border-radius:20px;padding:2px 10px}}
.wrap{{max-width:1280px;margin:24px auto;padding:0 24px;display:flex;gap:24px}}
.side{{width:296px;flex:none}} .side img{{width:296px;height:296px;border-radius:50%;border:1px solid #30363d}}
.side h1{{margin:16px 0 0;font-size:24px;line-height:1.25}} .side h1 span{{display:block;font-size:20px;font-weight:300;color:#7d8590}}
.side p{{color:#e6edf3}} .btn{{display:block;text-align:center;background:#21262d;border:1px solid #30363d;border-radius:6px;padding:5px;color:#e6edf3;font-weight:500}}
.main{{flex:1;min-width:0}}
.box{{border:1px solid #30363d;border-radius:6px;padding:24px}}
.box .hd{{font-size:12px;color:#e6edf3;margin-bottom:16px}} .box .hd span{{color:#7d8590}}
.md img{{max-width:100%;box-sizing:content-box;background:transparent}} .md p{{margin:0 0 16px}}
.md code{{background:#6e768166;border-radius:6px;padding:.2em .4em;font-size:85%}}
@media (max-width:900px){{.wrap{{flex-direction:column}} .side img{{width:120px;height:120px}}}}
</style></head><body>
<div class="top"><b>GitHub</b> <span style="color:#7d8590">/ {user}</span><span class="tag">LOCAL PREVIEW — not pushed</span></div>
<div class="wrap"><aside class="side">
<img src="https://github.com/{user}.png" alt="">
<h1>Vaibhaw Kumar<span>{user}</span></h1>
<p>Full Stack Developer · WordPress · WooCommerce · BigCommerce</p>
<a class="btn" href="#">Follow</a>
</aside><main class="main"><div class="box"><div class="hd">{user} <span>/</span> README<span>.md</span></div>
<article class="md">{readme}</article></div></main></div></body></html>"""


def build_skyline():
    out = os.path.join(CACHE, "skyline-light.svg")
    print("building local skyline ...")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "skyline.py"), USER, out], check=False)


def render():
    readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    readme = readme.replace(f"https://raw.githubusercontent.com/{USER}/{USER}/output/skyline-light.svg", "/.preview/skyline-light.svg")
    readme = re.sub(r"<!--.*?-->", "", readme, flags=re.S)
    # GitHub serves repo-relative images; the local server does the same from ROOT
    readme = re.sub(r'src="(?!https?:|/)', 'src="/', readme)
    return PAGE.format(user=USER, readme=readme).encode()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = render()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


def main():
    os.makedirs(CACHE, exist_ok=True)
    build_skyline()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as srv:
        print(f"\n  profile preview  ->  http://localhost:{PORT}\n  (Ctrl+C to stop, refresh the page after edits)\n")
        srv.serve_forever()


if __name__ == "__main__":
    main()
