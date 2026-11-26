"""Run the app on your own computer:   python serve.py          then open  http://localhost:8000

   python serve.py 9000         another port
   python serve.py --test       also answers /api/<method> with the real Python engine, for index.html?engine=server
                                (used to test the screen without Pyodide)

Only needs Python.  localhost counts as a secure address, so the browser lets you install the app and use it offline.
For other devices, put the webapp/ folder on any HTTPS web host (see README.txt): that is what makes phones installable.
"""
import http.server
import mimetypes
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "webapp")
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("text/javascript", ".js")
TEST = "--test" in sys.argv
if TEST:
    sys.path.insert(0, ROOT)
    from scicalc.api import dispatch as api_dispatch
else:
    api_dispatch = None


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=WEB, **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_POST(self):
        if not (TEST and self.path.startswith("/api/")):
            self.send_error(404)
            return
        n = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(n).decode("utf-8") if n else "[]"
        out = api_dispatch(self.path[5:], body).encode("utf-8")  # pyright: ignore[reportOptionalCall]
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, format, *args):
        if "--quiet" not in sys.argv:
            super().log_message(format, *args)


def main():
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    port = int(nums[0]) if nums else 8000
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"SciCalc is running at  http://localhost:{port}   (Ctrl+C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
