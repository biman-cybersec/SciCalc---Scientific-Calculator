/* Web Worker: loads Pyodide (Python in WebAssembly) from this folder, unpacks scicalc.zip and answers calls.
   Nothing is downloaded from the internet: pyodide/ and scicalc.zip are files of this app. */
"use strict";

importScripts("pyodide/pyodide.js");

let dispatch = null;
const queue = [];

function say(text) { self.postMessage({ type: "progress", text: text }); }

async function boot() {
  say("Loading Python…");
  const pyodide = await loadPyodide({ indexURL: new URL("pyodide/", self.location.href).href });
  say("Loading the calculator code…");
  const resp = await fetch("scicalc.zip");
  if (!resp.ok) throw new Error("scicalc.zip not found (run build_app.py)");
  const buf = await resp.arrayBuffer();
  pyodide.unpackArchive(buf, "zip", { extractDir: "/app" });
  say("Starting the engine…");
  pyodide.runPython("import sys\nif '/app' not in sys.path: sys.path.insert(0, '/app')\nimport scicalc.api as _scicalc_api");
  dispatch = pyodide.pyimport("scicalc.api").dispatch;
  self.postMessage({ type: "ready" });
  while (queue.length) handle(queue.shift());
}

function handle(m) {
  let out;
  try {
    out = JSON.parse(dispatch(m.method, m.payload));
  } catch (err) {
    out = { ok: false, error: "Math ERROR", detail: String(err), pos: null };
  }
  self.postMessage({ type: "result", id: m.id, data: out });
}

self.onmessage = function (ev) {
  const m = ev.data;
  if (m.type !== "call") return;
  if (dispatch) handle(m); else queue.push(m);
};

boot().catch(function (err) { self.postMessage({ type: "fatal", text: String(err && err.message || err) }); });
