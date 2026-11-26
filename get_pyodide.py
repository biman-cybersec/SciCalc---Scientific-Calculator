"""Download Pyodide (Python for the browser) into webapp/pyodide/ - needs internet, run once.   python get_pyodide.py

The release already shipped inside this folder is Pyodide 0.27.7 (Python 3.12).  Run this only to restore or change it.
"""
import io
import os
import tarfile
import urllib.request

VERSION = "0.27.7"
URL = f"https://github.com/pyodide/pyodide/releases/download/{VERSION}/pyodide-core-{VERSION}.tar.bz2"
KEEP = ["pyodide.js", "pyodide.asm.js", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json"]
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "webapp", "pyodide")

print("downloading", URL)
data = urllib.request.urlopen(URL, timeout=120).read()
os.makedirs(DEST, exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tar:
    for m in tar.getmembers():
        name = os.path.basename(m.name)
        if m.isfile() and name in KEEP:
            with open(os.path.join(DEST, name), "wb") as fh:
                member = tar.extractfile(m)
                if member is not None:
                    fh.write(member.read())
            print("  saved", name)
print("done. Now run  python build_app.py")
