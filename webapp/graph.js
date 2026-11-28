/* SciCalc graph tab: plots up to 6 equations y = f(x) on one canvas.
   The values come from the Python engine (engine.call("sample", ...)); this file only draws and handles the finger / mouse.
   Zoom: mouse wheel, pinch, + / - buttons.  Pan: drag.  Trace: hover or tap.  Intersections and roots: "Find crossings". */
(function () {
  "use strict";

  const MAX_EQ = 6;
  const PALETTE = {
    dark: ["#ffb627", "#5cc8ff", "#7fe0b0", "#d9a6ff", "#ff8fab", "#f4f1a6"],
    light: ["#d9480f", "#1c6fd1", "#1f8a4c", "#9c36b5", "#c2255c", "#0b7285"]
  };
  const SUB = "₁₂₃₄₅₆";
  let api = null;                       // { engine, el, store, toast, getLine }
  let root = null, canvas = null, ctx = null, wrap = null, readout = null, status = null, listBox = null, found = null;
  let eqs = [], view = null, angle = "rad", nextId = 1;
  let samp = null;                       // the last samples: { x0, x1, n, curves: [{ ys, error, id }] }
  let marks = { roots: [], cross: [], from: 0, to: 0 };
  let pin = null, trace = null;
  let busy = false, dirty = false, timer = null, built = false, W = 0, H = 0, dpr = 1;
  const pointers = new Map();
  let drag = null, pinch = null, moved = false;

  /* ------------------------------------------------------------------ helpers */
  function colors() {
    const bg = getComputedStyle(document.documentElement).getPropertyValue("--panel").trim();
    const m = /^#([0-9a-f]{6})$/i.exec(bg);
    const dark = m ? (parseInt(m[1].slice(0, 2), 16) * 0.3 + parseInt(m[1].slice(2, 4), 16) * 0.59 + parseInt(m[1].slice(4, 6), 16) * 0.11) < 128 : true;
    return dark ? PALETTE.dark : PALETTE.light;
  }
  function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
  function fmt(v) {
    if (!isFinite(v)) return String(v);
    if (Math.abs(v) < 1e-12) return "0";
    const a = Math.abs(v);
    if (a >= 1e7 || a < 1e-4) return v.toExponential(4).replace(/\.?0+e/, "e").replace("e+", "e");
    return String(parseFloat(v.toPrecision(7)));
  }
  function save() {
    api.store.set("scicalc.graph", JSON.stringify({ eqs: eqs.map(function (e) { return { text: e.text, on: e.on, col: e.col }; }), view: view, angle: angle }));
  }
  function load() {
    try {
      const d = JSON.parse(api.store.get("scicalc.graph") || "null");
      if (d && Array.isArray(d.eqs)) {
        eqs = d.eqs.slice(0, MAX_EQ).map(function (e, i) { return { id: nextId++, text: String(e.text || ""), on: e.on !== false, col: typeof e.col === "number" ? e.col : i, error: null }; });
        if (d.view && isFinite(d.view.cx) && isFinite(d.view.cy) && d.view.ppx > 0 && d.view.ppy > 0) view = d.view;
        if (d.angle === "deg" || d.angle === "rad") angle = d.angle;
      }
    } catch (e) { /* start fresh */ }
    if (!eqs.length) eqs = [{ id: nextId++, text: "sin(x)", on: true, col: 0, error: null }];
  }
  function stripName(t) { return String(t).replace(/^\s*(?:y|f\s*\(\s*x\s*\))\s*=(?!=)\s*/i, ""); }

  /* ------------------------------------------------------------------ view maths */
  function resetView() {
    const w = Math.max(W, 100);
    view = { cx: 0, cy: 0, ppx: w / 20, ppy: w / 20 };
  }
  function px(x) { return W / 2 + (x - view.cx) * view.ppx; }
  function py(y) { return H / 2 - (y - view.cy) * view.ppy; }
  function wx(p) { return view.cx + (p - W / 2) / view.ppx; }
  function wy(p) { return view.cy - (p - H / 2) / view.ppy; }
  function clampView() {
    const lo = Math.max(W, 100) / 1e8, hi = Math.max(W, 100) / 1e-6;
    view.ppx = Math.min(hi, Math.max(lo, view.ppx));
    view.ppy = Math.min(hi, Math.max(lo, view.ppy));
    view.cx = Math.max(-1e9, Math.min(1e9, view.cx));
    view.cy = Math.max(-1e9, Math.min(1e9, view.cy));
  }
  function zoomAt(fx, fy, ax, ay) {            // factors for the x and y scale, keeping canvas point (ax, ay) still
    const x = wx(ax), y = wy(ay);
    view.ppx *= fx; view.ppy *= fy;
    clampView();
    view.cx = x - (ax - W / 2) / view.ppx;
    view.cy = y + (ay - H / 2) / view.ppy;
  }
  function changed() { draw(); save(); schedule(80); }

  /* ------------------------------------------------------------------ sampling */
  function needSample() {
    if (!samp) return true;
    const v0 = wx(0), v1 = wx(W), span = v1 - v0, cover = samp.x1 - samp.x0;
    return v0 < samp.x0 || v1 > samp.x1 || cover > span * 3 || cover < span * 1.05;
  }
  function schedule(ms, force) {
    clearTimeout(timer);
    timer = setTimeout(function () { if (force) samp = null; resample(); }, ms);
  }
  function resample() {
    if (!built || !view || W < 10) return;
    if (!needSample()) return;
    if (busy) { dirty = true; return; }
    const active = eqs.filter(function (e) { return e.on && e.text.trim(); });
    if (!active.length) { samp = null; draw(); setStatus(""); return; }
    const v0 = wx(0), v1 = wx(W), span = v1 - v0;
    const x0 = v0 - span * 0.25, x1 = v1 + span * 0.25;
    const n = Math.max(300, Math.min(1400, Math.round(W)));
    busy = true; dirty = false;
    setStatus("calculating…");
    api.engine.call("sample", active.map(function (e) { return e.text; }), x0, x1, n, angle).then(function (r) {
      busy = false;
      eqs.forEach(function (e) { e.error = null; });
      if (r && r.ok) {
        samp = { x0: x0, x1: x1, n: n, curves: r.curves.map(function (c, i) { return { ys: c.ys, error: c.error, id: active[i].id }; }) };
        r.curves.forEach(function (c, i) { active[i].error = c.error; });
        setStatus("");
      } else {
        samp = null;
        if (r && /unknown method/.test(String(r.error))) { staleEngine(); return; }
        setStatus(r && r.error ? r.error : "could not draw");
      }
      showErrors();
      draw();
      if (dirty || needSample()) schedule(30);
    }).catch(function () { busy = false; setStatus("the engine did not answer; try again"); });
  }
  /* The page is new but the saved Python engine is an old copy: clear the saved files once and reload to get the new ones. */
  function staleEngine() {
    let tried = false;
    try { tried = !!sessionStorage.getItem("scicalc.healed"); sessionStorage.setItem("scicalc.healed", "1"); } catch (e) { /* no session storage */ }
    if (tried) { setStatus("The saved calculator engine is out of date. Close the app completely and open it again."); return; }
    setStatus("Updating the app…");
    const go = function () { location.reload(); };
    const jobs = [];
    if (window.caches) jobs.push(caches.keys().then(function (ks) { return Promise.all(ks.filter(function (k) { return k.indexOf("scicalc-") === 0; }).map(function (k) { return caches.delete(k); })); }));
    if (navigator.serviceWorker) jobs.push(navigator.serviceWorker.getRegistrations().then(function (rs) { return Promise.all(rs.map(function (r) { return r.unregister(); })); }));
    Promise.all(jobs).then(go, go);
  }
  function setStatus(t) { if (status) status.textContent = t; }
  function showErrors() {
    if (!root) return;
    eqs.forEach(function (e) {
      const box = root.querySelector('[data-err="' + e.id + '"]');
      if (box) { box.textContent = e.error || ""; box.hidden = !e.error; }
    });
  }

  /* ------------------------------------------------------------------ drawing */
  function niceStep(raw) {
    const p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m < 1.5 ? 1 : m < 3.5 ? 2 : m < 7.5 ? 5 : 10) * p;
  }
  function draw() {
    if (!ctx || !view || W < 10) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = css("--screen") || "#08192f";
    ctx.fillRect(0, 0, W, H);
    const ink = css("--ink") || "#e8f0fb", muted = css("--muted") || "#9db6d9";
    const gridMinor = css("--grid-major") || "rgba(143,183,235,.14)", axis = css("--line-strong") || "#8fb7eb";
    const stepX = niceStep(90 / view.ppx), stepY = niceStep(70 / view.ppy);
    ctx.lineWidth = 1;
    ctx.font = "11px " + (css("--mono") || "monospace");
    // grid
    ctx.strokeStyle = gridMinor;
    ctx.beginPath();
    const gx0 = Math.ceil(wx(0) / stepX), gx1 = Math.floor(wx(W) / stepX);
    for (let i = gx0; i <= gx1 && i - gx0 < 400; i++) { const x = Math.round(px(i * stepX)) + 0.5; ctx.moveTo(x, 0); ctx.lineTo(x, H); }
    const gy0 = Math.ceil(wy(H) / stepY), gy1 = Math.floor(wy(0) / stepY);
    for (let j = gy0; j <= gy1 && j - gy0 < 400; j++) { const y = Math.round(py(j * stepY)) + 0.5; ctx.moveTo(0, y); ctx.lineTo(W, y); }
    ctx.stroke();
    // axes
    const ax = Math.min(W - 1, Math.max(0, px(0))), ay = Math.min(H - 1, Math.max(0, py(0)));
    ctx.strokeStyle = axis; ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(Math.round(ax) + 0.5, 0); ctx.lineTo(Math.round(ax) + 0.5, H); ctx.moveTo(0, Math.round(ay) + 0.5); ctx.lineTo(W, Math.round(ay) + 0.5); ctx.stroke();
    // tick labels
    ctx.fillStyle = muted; ctx.textBaseline = "top"; ctx.textAlign = "center";
    const labY = Math.min(H - 14, Math.max(2, ay + 3));
    for (let i = gx0; i <= gx1 && i - gx0 < 400; i++) {
      if (i === 0) continue;
      ctx.fillText(fmt(i * stepX), Math.min(W - 16, Math.max(16, px(i * stepX))), labY);
    }
    ctx.textAlign = ax > W - 46 ? "right" : "left"; ctx.textBaseline = "middle";
    const labX = ax > W - 46 ? ax - 5 : ax + 5;
    for (let j = gy0; j <= gy1 && j - gy0 < 400; j++) {
      if (j === 0) continue;
      ctx.fillText(fmt(j * stepY), labX, Math.min(H - 8, Math.max(8, py(j * stepY))));
    }
    // curves
    const pal = colors();
    if (samp) {
      ctx.lineWidth = 2; ctx.lineJoin = "round";
      samp.curves.forEach(function (c) {
        const eq = eqs.filter(function (e) { return e.id === c.id; })[0];
        if (!eq) return;
        ctx.strokeStyle = pal[eq.col % pal.length];
        ctx.beginPath();
        let pen = false, prevY = 0;
        const dx = (samp.x1 - samp.x0) / (samp.n - 1);
        for (let k = 0; k < samp.n; k++) {
          const y = c.ys[k];
          if (y === null) { pen = false; continue; }
          const X = px(samp.x0 + k * dx);
          let Y = py(y);
          if (X < -50 || X > W + 50) { pen = false; continue; }
          Y = Math.max(-1e5, Math.min(1e5, Y));
          if (pen && Math.abs(Y - prevY) > H * 1.5) pen = false;        // a jump such as tan(x) at an asymptote
          if (pen) ctx.lineTo(X, Y); else ctx.moveTo(X, Y);
          pen = true; prevY = Y;
        }
        ctx.stroke();
      });
    }
    // crossings and roots
    function dot(x, y, fill) {
      const X = px(x), Y = py(y);
      if (X < -6 || X > W + 6 || Y < -6 || Y > H + 6) return;
      ctx.beginPath(); ctx.arc(X, Y, 5, 0, 6.2832); ctx.fillStyle = fill; ctx.fill();
      ctx.lineWidth = 2; ctx.strokeStyle = ink; ctx.stroke();
    }
    marks.roots.forEach(function (r) { dot(r.x, 0, css("--screen") || "#08192f"); });
    marks.cross.forEach(function (c) { dot(c.x, c.y, pal[0]); });
    if (pin) {
      const X = px(pin.x), Y = py(pin.y);
      ctx.lineWidth = 2; ctx.strokeStyle = ink; ctx.beginPath(); ctx.arc(X, Y, 9, 0, 6.2832); ctx.stroke();
    }
    if (trace) {
      const X = px(trace.x), Y = py(trace.y);
      ctx.fillStyle = pal[trace.col % pal.length]; ctx.strokeStyle = ink; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(X, Y, 5, 0, 6.2832); ctx.fill(); ctx.stroke();
    }
  }

  /* ------------------------------------------------------------------ trace (nearest curve point under the pointer) */
  function traceAt(cx, cy) {
    if (!samp) return null;
    const x = wx(cx), dx = (samp.x1 - samp.x0) / (samp.n - 1);
    const k = Math.round((x - samp.x0) / dx);
    let best = null, bestD = 28;                              // within 28 px
    samp.curves.forEach(function (c) {
      for (let q = Math.max(0, k - 2); q <= Math.min(samp.n - 1, k + 2); q++) {
        const y = c.ys[q];
        if (y === null) continue;
        const X = px(samp.x0 + q * dx), Y = py(y);
        const d = Math.hypot(X - cx, Y - cy);
        if (d < bestD) {
          const eq = eqs.filter(function (e) { return e.id === c.id; })[0];
          if (eq) { bestD = d; best = { x: samp.x0 + q * dx, y: y, col: eq.col, eq: eq }; }
        }
      }
    });
    return best;
  }
  function showReadout() {
    const t = trace || pin;
    if (!t) { readout.textContent = "Drag to move, pinch or scroll to zoom, tap a curve to read it."; return; }
    const name = t.eq ? "y" + SUB[eqs.indexOf(t.eq)] + "  " : "";
    readout.textContent = name + "x = " + fmt(t.x) + "   y = " + fmt(t.y);
  }

  /* ------------------------------------------------------------------ pointer input */
  function localPoint(ev) {
    const r = canvas.getBoundingClientRect();
    return { x: ev.clientX - r.left, y: ev.clientY - r.top };
  }
  function onDown(ev) {
    canvas.setPointerCapture(ev.pointerId);
    pointers.set(ev.pointerId, localPoint(ev));
    moved = false;
    if (pointers.size === 1) { const p = pointers.get(ev.pointerId); drag = { x: p.x, y: p.y }; pinch = null; }
    if (pointers.size === 2) {
      const a = Array.from(pointers.values());
      pinch = { d: Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1 };
      drag = null;
    }
  }
  function onMove(ev) {
    const p = localPoint(ev);
    if (!pointers.has(ev.pointerId)) {
      if (ev.pointerType === "mouse") { trace = traceAt(p.x, p.y); showReadout(); draw(); }
      return;
    }
    pointers.set(ev.pointerId, p);
    if (pointers.size === 2 && pinch) {
      const a = Array.from(pointers.values());
      const d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y) || 1;
      const f = d / pinch.d;
      zoomAt(f, f, (a[0].x + a[1].x) / 2, (a[0].y + a[1].y) / 2);
      pinch.d = d; moved = true; trace = null;
      draw(); schedule(120);
    } else if (pointers.size === 1 && drag) {
      const dxp = p.x - drag.x, dyp = p.y - drag.y;
      if (Math.abs(dxp) + Math.abs(dyp) > 3) moved = true;
      if (moved) {
        view.cx -= dxp / view.ppx; view.cy += dyp / view.ppy;
        drag = { x: p.x, y: p.y }; trace = null;
        draw();
        if (needSample()) schedule(60);
      }
    }
  }
  function onUp(ev) {
    const p = pointers.get(ev.pointerId);
    pointers.delete(ev.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pointers.size === 1) { const q = Array.from(pointers.values())[0]; drag = { x: q.x, y: q.y }; }
    if (pointers.size === 0) {
      drag = null;
      if (moved) { save(); schedule(60); }
      else if (p) { trace = traceAt(p.x, p.y); if (!trace) pin = null; showReadout(); draw(); }
    }
  }
  function onWheel(ev) {
    ev.preventDefault();
    const p = localPoint(ev);
    const f = Math.exp(-ev.deltaY * 0.0015);
    if (ev.shiftKey) zoomAt(f, 1, p.x, p.y); else if (ev.altKey) zoomAt(1, f, p.x, p.y); else zoomAt(f, f, p.x, p.y);
    trace = null; changed();
  }
  function onKey(ev) {
    const step = 40;
    const k = ev.key;
    if (k === "ArrowLeft") view.cx -= step / view.ppx;
    else if (k === "ArrowRight") view.cx += step / view.ppx;
    else if (k === "ArrowUp") view.cy += step / view.ppy;
    else if (k === "ArrowDown") view.cy -= step / view.ppy;
    else if (k === "+" || k === "=") zoomAt(1.25, 1.25, W / 2, H / 2);
    else if (k === "-" || k === "_") zoomAt(0.8, 0.8, W / 2, H / 2);
    else if (k === "0") resetView();
    else return;
    ev.preventDefault(); changed();
  }

  /* ------------------------------------------------------------------ buttons */
  function zoomButton(f) { zoomAt(f, f, W / 2, H / 2); trace = null; changed(); }
  function fit() {
    if (!samp) { toast("Nothing to fit yet"); return; }
    const v0 = wx(0), v1 = wx(W), ys = [];
    const dx = (samp.x1 - samp.x0) / (samp.n - 1);
    samp.curves.forEach(function (c) {
      for (let k = 0; k < samp.n; k++) {
        const x = samp.x0 + k * dx;
        if (c.ys[k] !== null && x >= v0 && x <= v1) ys.push(c.ys[k]);
      }
    });
    if (!ys.length) { toast("Nothing to fit in this range"); return; }
    ys.sort(function (a, b) { return a - b; });
    let lo = ys[Math.floor(ys.length * 0.02)], hi = ys[Math.ceil(ys.length * 0.98) - 1];
    if (hi - lo < 1e-9) { lo -= 1; hi += 1; }
    const pad = (hi - lo) * 0.12;
    view.cy = (lo + hi) / 2; view.ppy = H / (hi - lo + 2 * pad);
    clampView(); trace = null; changed();
  }
  function toast(t) { api.toast(t); }

  function findCrossings() {
    const active = eqs.filter(function (e) { return e.on && e.text.trim(); });
    if (!active.length) { toast("Add an equation first"); return; }
    const v0 = wx(0), v1 = wx(W);
    setStatus("looking for crossings…");
    api.engine.call("analyze", active.map(function (e) { return e.text; }), v0, v1, angle).then(function (r) {
      setStatus("");
      if (!r || !r.ok) { toast(r && r.error ? r.error : "Could not analyse"); return; }
      marks = { roots: r.roots.map(function (q) { return { eq: active[q.curve], x: q.x }; }), cross: r.intersections.map(function (q) { return { a: active[q.a], b: active[q.b], x: q.x, y: q.y }; }), from: v0, to: v1 };
      renderFound(); draw();
    }).catch(function () { setStatus(""); });
  }
  function name(eq) { return "y" + SUB[eqs.indexOf(eq)]; }
  function renderFound() {
    found.textContent = "";
    const el = api.el;
    if (!marks.roots.length && !marks.cross.length) {
      found.appendChild(el("p", { class: "small-note", text: "No crossings in x from " + fmt(marks.from) + " to " + fmt(marks.to) + ". Touching points (such as x² at 0) are not detected." }));
      return;
    }
    found.appendChild(el("h3", { text: "Crossings for x from " + fmt(marks.from) + " to " + fmt(marks.to) }));
    const ul = el("ul", { class: "list" });
    function row(label, x, y, eq) {
      ul.appendChild(el("li", {}, [el("button", { class: "item", type: "button", onclick: function () {
        pin = { x: x, y: y, eq: eq || null };
        view.cx = x; view.cy = y; trace = null; showReadout(); changed();
      } }, [el("span", { class: "mono", text: label }), el("span", { class: "gx", text: "(" + fmt(x) + ", " + fmt(y) + ")" })])]));
    }
    marks.cross.forEach(function (c) { row(name(c.a) + " = " + name(c.b), c.x, c.y, c.a); });
    marks.roots.forEach(function (r) { row(name(r.eq) + " = 0", r.x, 0, r.eq); });
    found.appendChild(ul);
  }
  function clearMarks() { marks = { roots: [], cross: [], from: 0, to: 0 }; pin = null; if (found) found.textContent = ""; }

  /* ------------------------------------------------------------------ the pane */
  function eqRow(eq) {
    const el = api.el;
    const pal = colors();
    const cb = el("input", { type: "checkbox", "aria-label": "Show equation " + (eqs.indexOf(eq) + 1) });
    cb.checked = eq.on;
    cb.addEventListener("change", function () { eq.on = cb.checked; clearMarks(); samp = null; draw(); save(); schedule(10, true); });
    const sw = el("span", { class: "gswatch" });
    sw.style.background = pal[eq.col % pal.length];
    const label = el("label", { class: "gcheck", title: "Show or hide" }, [cb, sw]);
    const input = el("input", { type: "text", class: "geq", value: eq.text, placeholder: "e.g. sin(x)  or  x^2 - 3", "aria-label": "Equation " + (eqs.indexOf(eq) + 1), autocomplete: "off", autocorrect: "off", autocapitalize: "off", spellcheck: "false", enterkeyhint: "go" });
    let t = null;
    input.addEventListener("input", function () {
      eq.text = input.value; clearTimeout(t);
      t = setTimeout(function () { clearMarks(); samp = null; save(); schedule(10, true); }, 350);
    });
    input.addEventListener("keydown", function (ev) { if (ev.key === "Enter") { clearTimeout(t); eq.text = input.value; clearMarks(); samp = null; save(); schedule(0, true); } });
    const del = el("button", { type: "button", class: "btn danger gdel", text: "✕", "aria-label": "Remove equation " + (eqs.indexOf(eq) + 1), onclick: function () {
      eqs = eqs.filter(function (e) { return e !== eq; });
      if (!eqs.length) eqs.push({ id: nextId++, text: "", on: true, col: 0, error: null });
      clearMarks(); samp = null; build(); save(); schedule(10, true); draw();
    } });
    const lab = el("span", { class: "gname", text: "y" + SUB[eqs.indexOf(eq)] + " =" });
    return el("div", { class: "geqrow" }, [el("div", { class: "geqline" }, [label, lab, input, del]), el("div", { class: "gerr", "data-err": String(eq.id), hidden: "" })]);
  }
  function build() {
    const el = api.el;
    root.textContent = "";
    const list = el("div", { class: "geqs" }, eqs.map(eqRow));
    root.appendChild(list);
    const add = el("button", { type: "button", class: "btn", text: "Add equation", onclick: function () {
      if (eqs.length >= MAX_EQ) { toast("Up to " + MAX_EQ + " equations"); return; }
      const used = eqs.map(function (e) { return e.col; });
      let col = 0; while (used.indexOf(col) >= 0) col++;
      eqs.push({ id: nextId++, text: "", on: true, col: col, error: null });
      build(); save();
      const inputs = root.querySelectorAll(".geq"); inputs[inputs.length - 1].focus();
    } });
    const line = el("button", { type: "button", class: "btn", text: "Use calculator line", title: "Plot what is typed on the calculator screen", onclick: function () {
      const t = stripName(api.getLine()).trim();
      if (!t) { toast("The calculator line is empty"); return; }
      const empty = eqs.filter(function (e) { return !e.text.trim(); })[0];
      if (empty) empty.text = t;
      else if (eqs.length < MAX_EQ) { const used = eqs.map(function (e) { return e.col; }); let col = 0; while (used.indexOf(col) >= 0) col++; eqs.push({ id: nextId++, text: t, on: true, col: col, error: null }); }
      else { toast("Up to " + MAX_EQ + " equations"); return; }
      clearMarks(); samp = null; build(); save(); schedule(10, true);
    } });
    root.appendChild(el("div", { class: "gbar" }, [add, line]));

    const tools = el("div", { class: "gbar gtools" }, [
      el("button", { type: "button", class: "btn", text: "＋", "aria-label": "Zoom in", onclick: function () { zoomButton(1.4); } }),
      el("button", { type: "button", class: "btn", text: "－", "aria-label": "Zoom out", onclick: function () { zoomButton(1 / 1.4); } }),
      el("button", { type: "button", class: "btn", text: "Reset", title: "Back to x from -10 to 10", onclick: function () { resetView(); trace = null; changed(); } }),
      el("button", { type: "button", class: "btn", text: "Fit", title: "Fit the height to the curves", onclick: fit }),
      el("button", { type: "button", class: "btn primary", text: "Find crossings", title: "Intersections of the curves and where they cross the x axis", onclick: findCrossings }),
      el("button", { type: "button", class: "btn", id: "gFull", text: "Full screen", "aria-pressed": "false", onclick: toggleFull })
    ]);
    root.appendChild(tools);

    const angleSeg = el("div", { class: "gangle" }, [el("span", { class: "small-note", text: "Angles in sin, cos, tan:" }), el("div", { class: "seg" }, ["rad", "deg"].map(function (a) {
      return el("button", { type: "button", text: a === "rad" ? "Radians" : "Degrees", "aria-pressed": String(angle === a), onclick: function () {
        angle = a; clearMarks(); samp = null; build(); save(); schedule(10, true); draw();
      } });
    }))]);
    root.appendChild(angleSeg);

    wrap = el("div", { class: "gwrap" });
    canvas = el("canvas", { class: "gcanvas", tabindex: "0", role: "img", "aria-label": "Graph of the equations. Arrow keys move, plus and minus zoom, 0 resets." });
    wrap.appendChild(canvas);
    status = el("div", { class: "gstatus", role: "status" });
    wrap.appendChild(status);
    root.appendChild(wrap);
    readout = el("div", { class: "greadout mono", "aria-live": "polite" });
    root.appendChild(readout);
    found = el("div", { class: "gfound" });
    root.appendChild(found);
    listBox = null;

    ctx = canvas.getContext("2d");
    canvas.addEventListener("pointerdown", onDown);
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerup", onUp);
    canvas.addEventListener("pointercancel", function (ev) { pointers.delete(ev.pointerId); drag = null; pinch = null; });
    canvas.addEventListener("pointerleave", function (ev) { if (ev.pointerType === "mouse" && !pointers.size) { trace = null; showReadout(); draw(); } });
    canvas.addEventListener("wheel", onWheel, { passive: false });
    canvas.addEventListener("keydown", onKey);
    canvas.addEventListener("dblclick", function (ev) { const p = localPoint(ev); zoomAt(2, 2, p.x, p.y); changed(); });
    if (window.ResizeObserver) new ResizeObserver(sizeCanvas).observe(wrap);
    sizeCanvas();
    showReadout();
    if (marks.cross.length || marks.roots.length) renderFound();
    showErrors();
  }
  function sizeCanvas() {
    if (!canvas || !wrap) return;
    const r = wrap.getBoundingClientRect();
    if (r.width < 10 || r.height < 10) return;
    const oldW = W, oldH = H;
    dpr = Math.min(3, window.devicePixelRatio || 1);
    W = Math.round(r.width); H = Math.round(r.height);
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    if (!view) resetView();
    else if (oldW && oldW !== W) { const f = W / oldW; view.ppx *= f; view.ppy *= f; }    // keep the same window of x values
    draw();
    if (oldW !== W || oldH !== H) schedule(60);
  }
  function toggleFull() {
    const on = !document.getElementById("tab-graph").classList.contains("graph-full");
    document.getElementById("tab-graph").classList.toggle("graph-full", on);
    document.body.classList.toggle("noscroll", on);
    const b = document.getElementById("gFull");
    if (b) { b.textContent = on ? "Close full screen" : "Full screen"; b.setAttribute("aria-pressed", String(on)); }
    setTimeout(sizeCanvas, 30);
  }

  window.SciGraph = {
    init: function (opts) {
      api = opts;
      root = document.getElementById("tab-graph");
      load();
      document.addEventListener("keydown", function (ev) {
        if (ev.key === "Escape" && root.classList.contains("graph-full")) toggleFull();
      });
      document.querySelectorAll("#tabs button").forEach(function (b) {
        b.addEventListener("click", function () { if (root.classList.contains("graph-full") && b.dataset.tab !== "graph") toggleFull(); });
      });
    },
    show: function () {
      if (!built) { built = true; build(); }
      else sizeCanvas();
      schedule(10);
    },
    redraw: function () { if (built) { build(); draw(); } },
    /* for tests */
    _state: function () { return { eqs: eqs, view: view, samp: samp, marks: marks, W: W, H: H, angle: angle }; }
  };
})();
