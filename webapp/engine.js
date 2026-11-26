/* The bridge between the screen and the Python calculator engine.

   Normal mode : the engine runs inside the browser (Pyodide = Python compiled to WebAssembly) in a Web Worker,
                 so the screen never freezes and everything works offline.
   Test mode   : open  index.html?engine=server  and the same calls go to serve.py, which runs the real engine
                 in ordinary Python (used for testing the screen without Pyodide).

   Every call is  engine.call("evaluate", "2+3")  ->  Promise of plain data.  The list of methods is the Engine
   class in scicalc/api.py.
*/
(function () {
  "use strict";

  const params = new URLSearchParams(location.search);
  const SERVER_MODE = params.get("engine") === "server";
  const CALL_TIMEOUT_MS = 20000;          // a calculation that takes longer is stopped (the engine restarts)

  function Engine() {
    this.worker = null;
    this.pending = new Map();
    this.nextId = 1;
    this.onProgress = function () {};
    this.restoreState = null;            // function returning the last saved session text (or null)
    this.ready = null;
  }

  Engine.prototype.start = function (onProgress) {
    if (onProgress) this.onProgress = onProgress;
    if (SERVER_MODE) {
      this.ready = Promise.resolve();
      return this.ready;
    }
    this.ready = this._startWorker();
    return this.ready;
  };

  Engine.prototype._startWorker = function () {
    const self = this;
    return new Promise(function (resolve, reject) {
      let worker;
      try {
        worker = new Worker("py-worker.js");
      } catch (err) {
        reject(err);
        return;
      }
      self.worker = worker;
      worker.onmessage = function (ev) {
        const m = ev.data;
        if (m.type === "progress") {
          self.onProgress(m.text);
        } else if (m.type === "ready") {
          resolve();
        } else if (m.type === "fatal") {
          reject(new Error(m.text));
        } else if (m.type === "result") {
          const p = self.pending.get(m.id);
          if (p) {
            self.pending.delete(m.id);
            clearTimeout(p.timer);
            p.resolve(m.data);
          }
        }
      };
      worker.onerror = function (ev) {
        reject(new Error(ev.message || "the engine could not start"));
      };
    });
  };

  Engine.prototype.call = function (method) {
    const args = Array.prototype.slice.call(arguments, 1);
    const self = this;
    if (SERVER_MODE) {
      return fetch("/api/" + method, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(args) })
        .then(function (r) { return r.json(); });
    }
    return this.ready.then(function () {
      return new Promise(function (resolve) {
        const id = self.nextId++;
        const timer = setTimeout(function () { self._timeout(id, method); }, CALL_TIMEOUT_MS);
        self.pending.set(id, { resolve: resolve, timer: timer });
        self.worker.postMessage({ type: "call", id: id, method: method, payload: JSON.stringify(args) });
      });
    });
  };

  /* a call took too long: stop the worker, start a fresh one, put the saved session back */
  Engine.prototype._timeout = function (id, method) {
    const self = this;
    const stuck = self.pending.get(id);
    if (!stuck) return;
    self.pending.delete(id);
    const others = Array.from(self.pending.values());
    self.pending.clear();
    if (self.worker) self.worker.terminate();
    self.ready = self._startWorker().then(function () {
      const text = self.restoreState && self.restoreState();
      return text ? self.call("load_state", text) : null;
    });
    stuck.resolve({ ok: false, error: "Time out", detail: "the calculation took too long and was stopped", pos: null });
    others.forEach(function (p) { clearTimeout(p.timer); p.resolve({ ok: false, error: "Time out", detail: "stopped", pos: null }); });
  };

  window.SciEngine = Engine;
  window.SCI_SERVER_MODE = SERVER_MODE;
})();
