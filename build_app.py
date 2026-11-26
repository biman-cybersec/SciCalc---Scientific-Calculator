"""Build the web app:  python build_app.py

 1. webapp/scicalc.zip   the calculator package (scicalc/ up to api.py, without selftest/app/tests) that the browser unpacks into Pyodide
 2. webapp/assets.js     the list of files the service worker saves for offline use + a version number
Run it again after changing anything in scicalc/ or webapp/ (the version changes, so installed copies update).
"""
import hashlib
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "webapp")
PYO = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]


def build_zip():
    out = os.path.join(WEB, "scicalc.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for d, dirs, files in os.walk(os.path.join(ROOT, "scicalc")):
            dirs[:] = sorted(x for x in dirs if x not in ("tests", "__pycache__"))
            for f in sorted(files):
                if f.endswith(".py") and f not in ("selftest.py", "app.py"):      # the test runner and command line are not needed in the browser
                    p = os.path.join(d, f)
                    info = zipfile.ZipInfo(os.path.relpath(p, ROOT).replace(os.sep, "/"), (2020, 1, 1, 0, 0, 0))   # fixed date: same input, same zip
                    info.compress_type = zipfile.ZIP_DEFLATED
                    z.writestr(info, open(p, "rb").read())
    return out


def main():
    missing = [f for f in PYO if not os.path.exists(os.path.join(WEB, "pyodide", f))]
    if missing:
        print("Missing Pyodide files:", ", ".join(missing), "\nRun  python get_pyodide.py  once (needs internet).")
        return 1
    build_zip()
    files = ["index.html", "style.css", "app.js", "credits.js", "engine.js", "py-worker.js", "manifest.webmanifest", "scicalc.zip"]
    files += sorted("icons/" + f for f in os.listdir(os.path.join(WEB, "icons")))
    files += ["pyodide/" + f for f in PYO]
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode())
        h.update(open(os.path.join(WEB, f), "rb").read())
    version = h.hexdigest()[:12]
    with open(os.path.join(WEB, "assets.js"), "w", encoding="utf-8") as fh:
        fh.write("/* written by build_app.py - do not edit */\nself.ASSET_VERSION = %s;\nself.ASSETS = %s;\n" % (json.dumps(version), json.dumps(["./"] + files, indent=1)))
    size = sum(os.path.getsize(os.path.join(WEB, f)) for f in files) / 1e6
    print(f"built webapp/  version {version}  {len(files)} files  {size:.1f} MB (what a device stores for offline use)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
