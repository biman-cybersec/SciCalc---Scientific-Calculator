/* SciCalc screen: keypad, display, history, function browser, constants, memory and settings.
   All maths happens in the Python engine (see engine.js); this file only shows things and sends text. */
(function () {
  "use strict";

  const $ = function (id) { return document.getElementById(id); };
  const store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode: no saving */ } }
  };
  const engine = new SciEngine();
  engine.restoreState = function () { return store.get("scicalc.state"); };

  const expr = $("expr");
  let settings = { angle: "deg", display: "norm", digits: 2, fraction: "off", sym: false, base: "off", dms: false, complex: false, polar: false };
  let fnRows = [], coRows = [];
  let historyRows = [];                // {expr, text}
  let recallPos = -1;                  // position while walking back through history with the arrow keys
  let justEvaluated = false;           // the screen shows an answer: the next key starts something new
  let fnShown = 80, coShown = 80;
  let deferredInstall = null;

  /* ------------------------------------------------------------------ small helpers */
  function el(tag, attrs, children) {
    const e = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "text") e.textContent = attrs[k];
      else if (k === "class") e.className = attrs[k];
      else if (k.slice(0, 2) === "on") e.addEventListener(k.slice(2), attrs[k]);
      else e.setAttribute(k, attrs[k]);
    });
    (children || []).forEach(function (c) { e.appendChild(c); });
    return e;
  }
  let toastTimer = null;
  function toast(text) {
    const t = $("toast");
    t.textContent = text;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { t.classList.remove("show"); }, 2200);
  }
  function saveState() {
    engine.call("save_state").then(function (text) { if (typeof text === "string") store.set("scicalc.state", text); });
  }

  /* ------------------------------------------------------------------ typing into the expression */
  function insertText(t) {
    const s = expr.selectionStart == null ? expr.value.length : expr.selectionStart;
    const e = expr.selectionEnd == null ? s : expr.selectionEnd;
    expr.value = expr.value.slice(0, s) + t + expr.value.slice(e);
    const pos = s + t.length;
    expr.focus({ preventScroll: true });
    expr.setSelectionRange(pos, pos);
  }
  function backspace() {
    const s = expr.selectionStart == null ? expr.value.length : expr.selectionStart;
    const e = expr.selectionEnd == null ? s : expr.selectionEnd;
    if (s !== e) { expr.value = expr.value.slice(0, s) + expr.value.slice(e); expr.setSelectionRange(s, s); }
    else if (s > 0) { expr.value = expr.value.slice(0, s - 1) + expr.value.slice(s); expr.setSelectionRange(s - 1, s - 1); }
    expr.focus({ preventScroll: true });
  }
  function clearAll() {
    expr.value = "";
    $("result").textContent = "";
    $("result").className = "result";
    $("decimal").textContent = "";
    $("detail").textContent = "";
    $("prev").textContent = "";
    justEvaluated = false;
    expr.focus({ preventScroll: true });
  }
  /* kind: "val" a number or name, "op" an operator (after an answer it continues from Ans), "fn" a function */
  function press(text, kind) {
    if (justEvaluated) {
      if (kind === "op") expr.value = text.trim() === "->" ? "Ans" : "Ans";
      else expr.value = "";
      expr.setSelectionRange(expr.value.length, expr.value.length);
      justEvaluated = false;
    }
    insertText(text);
  }

  /* ------------------------------------------------------------------ calculating */
  function showError(r) {
    const res = $("result");
    res.className = "result error";
    res.textContent = r.error || "Error";
    $("decimal").textContent = "";
    $("detail").textContent = r.detail || "";
    if (typeof r.pos === "number" && r.pos >= 0 && r.pos <= expr.value.length) {
      expr.focus({ preventScroll: true });
      expr.setSelectionRange(r.pos, Math.min(r.pos + 1, expr.value.length));
    }
    justEvaluated = false;
  }
  function showResult(r) {
    const res = $("result");
    res.className = "result fresh" + (r.kind === "list" || r.kind === "matrix" || (r.text && r.text.length > 18) ? " small" : "");
    res.textContent = r.text;
    $("decimal").textContent = r.decimal != null && r.decimal !== "" ? "≈ " + r.decimal : "";
    $("detail").textContent = "";
    $("prev").textContent = r.expr + " =";
  }
  function evaluate() {
    const text = expr.value.trim();
    if (!text) return Promise.resolve();
    $("detail").textContent = "";
    return engine.call("evaluate", text).then(function (r) {
      if (r.ok) {
        showResult(r);
        historyRows.push({ expr: r.expr, text: r.text });
        recallPos = -1;
        justEvaluated = true;
        expr.select();
        renderHistory();
        saveState();
        if (!$("tab-memory").hidden) renderMemory();
      } else {
        showError(r);
      }
    });
  }

  /* ------------------------------------------------------------------ keys */
  const SCI_KEYS = [
    ["sin", "sin(", "fn"], ["cos", "cos(", "fn"], ["tan", "tan(", "fn"], ["sin⁻¹", "asin(", "fn", "arc sine"], ["cos⁻¹", "acos(", "fn", "arc cosine"],
    ["tan⁻¹", "atan(", "fn", "arc tangent"], ["ln", "ln(", "fn"], ["log", "log(", "fn"], ["eˣ", "e^(", "fn", "e to the power"], ["10ˣ", "10^(", "fn", "ten to the power"],
    ["√", "√(", "fn", "square root"], ["x²", "²", "op", "square"], ["xʸ", "^", "op", "power"], ["x⁻¹", "^(-1)", "op", "reciprocal"], ["n!", "!", "op", "factorial"],
    ["π", "π", "val", "pi"], ["e", "e", "val", "Euler number"], ["Ans", "Ans", "val", "previous answer"], ["%", "%", "op", "percent"], ["mod", " mod ", "op", "modulo"],
    ["nCr", " nCr ", "op", "combinations"], ["nPr", " nPr ", "op", "permutations"], ["abs", "abs(", "fn", "absolute value"], [",", ",", "val", "comma"], ["→", "->", "op", "store in a variable"],
    ["A", "A", "val", "variable A"], ["B", "B", "val", "variable B"], ["C", "C", "val", "variable C"], ["X", "X", "val", "variable X"], ["M", "M", "val", "memory M"],
    ["×10ⁿ", "×10^", "op", "times ten to the power"], ["M+", "M+", "mem", "add to memory"], ["M−", "M-", "mem", "subtract from memory"], ["DMS", "°", "op", "degrees"], ["sinh", "sinh(", "fn", "hyperbolic sine"]
  ];
  const NUM_KEYS = [
    ["AC", "AC", "del", "clear all"], ["(", "(", "fn", "open bracket"], [")", ")", "fn", "close bracket"], ["÷", "÷", "op", "divide"],
    ["7", "7", "val"], ["8", "8", "val"], ["9", "9", "val"], ["×", "×", "op", "multiply"],
    ["4", "4", "val"], ["5", "5", "val"], ["6", "6", "val"], ["−", "-", "op", "minus"],
    ["1", "1", "val"], ["2", "2", "val"], ["3", "3", "val"], ["+", "+", "op", "plus"],
    ["0", "0", "val"], [".", ".", "val", "decimal point"], ["⌫", "DEL", "del", "delete"], ["=", "EQ", "eq", "equals"]
  ];
  function buildKeys(container, defs, cls) {
    defs.forEach(function (d) {
      const label = d[0], text = d[1], kind = d[2];
      const b = el("button", { class: "key " + (kind === "fn" ? "fn" : kind === "op" || kind === "mem" ? "op" : kind === "del" ? "del" : kind === "eq" ? "eq" : "") + (cls ? " " + cls : ""), type: "button", text: label });
      if (d[3]) b.setAttribute("aria-label", d[3]);
      b.addEventListener("click", function () {
        if (navigator.vibrate) { try { navigator.vibrate(6); } catch (e) { /* not supported */ } }
        if (text === "AC") clearAll();
        else if (text === "DEL") { justEvaluated = false; backspace(); }
        else if (text === "EQ") evaluate();
        else if (kind === "mem") { expr.value = "Ans" + text; justEvaluated = false; evaluate(); }
        else press(text, kind);
      });
      container.appendChild(b);
    });
  }

  /* ------------------------------------------------------------------ mode bar */
  function renderModes() {
    const bar = $("modeBar");
    bar.textContent = "";
    const angle = el("button", { type: "button", text: settings.angle, "aria-label": "Angle mode " + settings.angle + ", tap to change", onclick: function () {
      const next = { deg: "rad", rad: "grad", grad: "deg" }[settings.angle];
      configure({ angle: next });
    } });
    bar.appendChild(angle);
    const disp = settings.display + " " + settings.digits;
    bar.appendChild(el("button", { type: "button", text: disp, onclick: function () { openTab("settings"); } }));
    [["fraction", settings.fraction !== "off", "frac"], ["sym", settings.sym, "exact"], ["complex", settings.complex, "complex"],
     ["polar", settings.polar, "polar"], ["dms", settings.dms, "dms"], ["base", settings.base !== "off", settings.base]].forEach(function (m) {
      if (m[1]) bar.appendChild(el("button", { type: "button", text: m[2], onclick: function () { openTab("settings"); } }));
    });
  }
  function configure(changes) {
    return engine.call("configure", changes).then(function (r) {
      if (r.ok) { settings = r.settings; renderModes(); renderSettings(); saveState(); }
      else toast(r.error || "That setting is not allowed");
    });
  }

  /* ------------------------------------------------------------------ tabs */
  function openTab(name) {
    document.querySelectorAll("#tabs button").forEach(function (b) { b.setAttribute("aria-selected", b.dataset.tab === name ? "true" : "false"); });
    ["history", "graph", "functions", "constants", "memory", "settings"].forEach(function (t) { $("tab-" + t).hidden = t !== name; });
    if (name === "memory") renderMemory();
    if (name === "history") renderHistory();
    if (name === "graph" && window.SciGraph) window.SciGraph.show();
  }

  function renderHistory() {
    const box = $("tab-history");
    box.textContent = "";
    box.appendChild(el("div", { class: "row" }, [
      el("button", { class: "btn danger", type: "button", text: "Clear history", onclick: function () {
        engine.call("clear_history").then(function () { historyRows = []; renderHistory(); saveState(); });
      } })
    ]));
    if (!historyRows.length) { box.appendChild(el("div", { class: "empty", text: "Your calculations will appear here." })); return; }
    const ul = el("ul", { class: "list hist" });
    historyRows.slice().reverse().forEach(function (h) {
      ul.appendChild(el("li", {}, [el("button", { class: "item", type: "button", "aria-label": "Use " + h.expr, onclick: function () {
        expr.value = h.expr; justEvaluated = false; expr.focus({ preventScroll: true });
      } }, [el("span", { class: "expr", text: h.expr }), el("span", { class: "res", text: "= " + h.text })])]));
    });
    box.appendChild(ul);
  }

  /* ------------------------------------------------------------------ function browser */
  function fillCategorySelect(select, rows, allLabel) {
    const counts = {};
    rows.forEach(function (r) { counts[r.category] = (counts[r.category] || 0) + 1; });
    select.textContent = "";
    select.appendChild(el("option", { value: "", text: allLabel + " (" + rows.length + ")" }));
    Object.keys(counts).sort().forEach(function (c) { select.appendChild(el("option", { value: c, text: c + " (" + counts[c] + ")" })); });
  }
  function matches(r, q) {
    return r.name.toLowerCase().indexOf(q) >= 0 || r.desc.toLowerCase().indexOf(q) >= 0 ||
      r.aliases.some(function (a) { return a.toLowerCase().indexOf(q) >= 0; });
  }
  function rank(r, q) {
    const n = r.name.toLowerCase();
    return n === q ? 0 : n.indexOf(q) === 0 ? 1 : n.indexOf(q) > 0 ? 2 : 3;
  }
  function filtered(rows, q, cat) {
    q = q.trim().toLowerCase();
    let out = rows.filter(function (r) { return (!cat || r.category === cat) && (!q || matches(r, q)); });
    if (q) out = out.slice().sort(function (a, b) { return rank(a, q) - rank(b, q) || (a.name < b.name ? -1 : 1); });
    return out;
  }
  function renderFunctions() {
    const list = filtered(fnRows, $("fnSearch").value, $("fnCat").value);
    const ul = $("fnList");
    ul.textContent = "";
    if (!list.length) ul.appendChild(el("li", { class: "empty", text: "No function matches." }));
    list.slice(0, fnShown).forEach(function (r) {
      ul.appendChild(el("li", {}, [el("button", { class: "item", type: "button", onclick: function () { showFunction(r); } }, [
        el("span", { class: "cat", text: r.category }), el("span", { class: "name", text: r.name }), el("span", { class: "desc", text: r.desc })
      ])]));
    });
    if (list.length > fnShown) ul.appendChild(el("li", {}, [el("button", { class: "btn", type: "button", text: "Show more (" + (list.length - fnShown) + " left)", onclick: function () { fnShown += 120; renderFunctions(); } })]));
  }
  function showFunction(r) {
    const box = $("fnDetail");
    box.textContent = "";
    const ex = r.example ? r.example.split(" => ")[0] : "";
    const btns = [el("button", { class: "btn primary", type: "button", text: "Insert", onclick: function () { press(r.name + "(", "fn"); } })];
    if (ex) btns.push(el("button", { class: "btn", type: "button", text: "Try the example", onclick: function () { expr.value = ex; justEvaluated = false; evaluate(); } }));
    btns.push(el("button", { class: "btn", type: "button", text: "Close", onclick: function () { box.textContent = ""; } }));
    box.appendChild(el("div", { class: "detailbox" }, [
      el("h3", { text: r.name }), el("div", { text: r.desc }),
      el("div", { class: "small-note", text: "Takes " + r.args + " · " + r.category + (r.aliases.length ? " · also: " + r.aliases.join(", ") : "") }),
      ex ? el("div", { class: "small-note", text: "Example: " + r.example }) : el("span"),
      el("div", { class: "btns" }, btns)
    ]));
    box.scrollIntoView({ block: "nearest" });
  }
  function renderConstants() {
    const list = filtered(coRows, $("coSearch").value, $("coCat").value);
    const ul = $("coList");
    ul.textContent = "";
    if (!list.length) ul.appendChild(el("li", { class: "empty", text: "No constant matches." }));
    list.slice(0, coShown).forEach(function (r) {
      ul.appendChild(el("li", {}, [el("button", { class: "item", type: "button", onclick: function () { press(r.name, "val"); toast("Inserted " + r.name); } }, [
        el("span", { class: "cat", text: r.category }), el("span", { class: "name", text: r.name }),
        el("span", { class: "desc", text: String(r.value) + " — " + r.desc })
      ])]));
    });
    if (list.length > coShown) ul.appendChild(el("li", {}, [el("button", { class: "btn", type: "button", text: "Show more (" + (list.length - coShown) + " left)", onclick: function () { coShown += 120; renderConstants(); } })]));
  }

  /* ------------------------------------------------------------------ memory */
  function renderMemory() {
    const box = $("tab-memory");
    Promise.all([engine.call("variables"), engine.call("user_functions")]).then(function (res) {
      const vars = res[0], funcs = res[1];
      box.textContent = "";
      box.appendChild(el("h3", { text: "Variables" }));
      const ul = el("ul", { class: "list" });
      Object.keys(vars).forEach(function (k) {
        ul.appendChild(el("li", {}, [el("button", { class: "item", type: "button", onclick: function () { press(k, "val"); } }, [
          el("span", { class: "name", text: k }), el("span", { class: "desc", text: vars[k] })
        ])]));
      });
      box.appendChild(ul);
      box.appendChild(el("p", { class: "small-note", text: "Store a value with  5→A  (type 5->A). Use M+ and M− to add or subtract the last answer." }));
      box.appendChild(el("h3", { text: "Your functions" }));
      if (!funcs.length) box.appendChild(el("p", { class: "small-note", text: "Define one by typing  f(x)=x^2+1  and pressing =. Then use f(3)." }));
      funcs.forEach(function (f) {
        box.appendChild(el("div", { class: "row" }, [
          el("button", { class: "btn", type: "button", text: f.name + "(" + f.params.join(",").toLowerCase() + ") = " + f.body, onclick: function () { press(f.name + "(", "fn"); } }),
          el("button", { class: "btn danger", type: "button", text: "Delete", onclick: function () { engine.call("delete_function", f.name).then(function () { renderMemory(); saveState(); }); } })
        ]));
      });
    });
  }

  /* ------------------------------------------------------------------ settings */
  function seg(label, options, current, onPick) {
    const wrap = el("fieldset", {}, [el("legend", { text: label })]);
    const s = el("div", { class: "seg" });
    options.forEach(function (o) {
      s.appendChild(el("button", { type: "button", text: o[1], "aria-pressed": String(current === o[0]), onclick: function () { onPick(o[0]); } }));
    });
    wrap.appendChild(s);
    return wrap;
  }
  function toggle(title, note, value, onChange) {
    const input = el("input", { type: "checkbox", "aria-label": title });
    input.checked = !!value;
    input.addEventListener("change", function () { onChange(input.checked); });
    return el("label", { class: "switch" }, [el("span", {}, [document.createTextNode(title), el("small", { text: note })]), input]);
  }
  function renderSettings() {
    const box = $("tab-settings");
    box.textContent = "";
    box.appendChild(seg("Angle", [["deg", "Degrees"], ["rad", "Radians"], ["grad", "Gradians"]], settings.angle, function (v) { configure({ angle: v }); }));
    const digitsMax = { norm: 2, fix: 9, sci: 10, eng: 10, custom: 10 };
    const dispFs = seg("Number format", [["norm", "Norm"], ["fix", "Fix"], ["sci", "Sci"], ["eng", "Eng"]], settings.display, function (v) {
      const d = v === "norm" ? Math.min(2, settings.digits || 2) || 2 : (v === "fix" ? Math.min(settings.digits, 9) : Math.max(1, Math.min(settings.digits, 10)));
      configure({ display: v, digits: v === "norm" ? (settings.display === "norm" ? settings.digits : 2) : d });
    });
    if (settings.display !== "norm") {
      const num = el("input", { type: "number", min: settings.display === "fix" ? "0" : "1", max: String(digitsMax[settings.display]), value: String(settings.digits), "aria-label": "Digits" });
      num.addEventListener("change", function () { configure({ digits: parseInt(num.value, 10) }); });
      dispFs.appendChild(el("div", { class: "row", style: "margin-top:8px" }, [el("span", { text: settings.display === "fix" ? "Decimal places" : "Significant digits" }), num]));
    }
    box.appendChild(dispFs);
    box.appendChild(seg("Fractions", [["off", "Off"], ["improper", "7/2"], ["mixed", "3 1/2"]], settings.fraction, function (v) { configure({ fraction: v }); }));
    box.appendChild(seg("Whole numbers in another base", [["off", "Off"], ["hex", "Hex"], ["bin", "Bin"], ["oct", "Oct"]], settings.base, function (v) { configure({ base: v }); }));
    box.appendChild(toggle("Exact forms", "show results like 2√3, π/6, √3/2", settings.sym, function (v) { configure({ sym: v }); }));
    box.appendChild(toggle("Complex numbers", "sqrt(-4) gives 2i", settings.complex, function (v) { configure({ complex: v }); }));
    box.appendChild(toggle("Polar form", "show complex results as r∠θ", settings.polar, function (v) { configure({ polar: v }); }));
    box.appendChild(toggle("Degrees° minutes′ seconds″", "show answers as degrees, minutes, seconds", settings.dms, function (v) { configure({ dms: v }); }));

    const theme = store.get("scicalc.theme") || "auto";
    box.appendChild(seg("Theme", [["auto", "Auto"], ["light", "Light"], ["dark", "Dark"]], theme, function (v) { store.set("scicalc.theme", v); applyTheme(); renderSettings(); }));
    const osk = store.get("scicalc.osk") === "1";
    box.appendChild(toggle("Use the device keyboard", "off = only the on-screen keys (no keyboard pops up on phones)", osk, function (v) { store.set("scicalc.osk", v ? "1" : "0"); applyKeyboard(); }));

    box.appendChild(el("fieldset", {}, [el("legend", { text: "Session" }), el("div", { class: "row" }, [
      el("button", { class: "btn", type: "button", text: "Save to a file", onclick: exportSession }),
      el("button", { class: "btn", type: "button", text: "Open a saved file", onclick: function () { $("importFile").click(); } }),
      el("button", { class: "btn danger", type: "button", text: "Reset everything", onclick: function () {
        if (!confirm("Reset all settings, variables, functions and history?")) return;
        engine.call("reset").then(function (s) { settings = s; historyRows = []; clearAll(); renderModes(); renderSettings(); renderHistory(); saveState(); toast("Reset"); });
      } })
    ])]));
    box.appendChild(el("p", { class: "small-note", id: "aboutText", text: "" }));
    engine.call("info").then(function (i) {
      const p = $("aboutText");
      if (p) p.textContent = creditText() + " " + i.functions + " functions, " + i.constants + " constants, " + i.categories + " categories. Runs fully offline on this device.";
    });
  }
  function exportSession() {
    engine.call("save_state").then(function (text) {
      const a = el("a", { href: URL.createObjectURL(new Blob([text], { type: "application/json" })), download: "scicalc-session.json" });
      document.body.appendChild(a); a.click(); a.remove();
    });
  }
  function importSession(file) {
    const reader = new FileReader();
    reader.onload = function () {
      engine.call("load_state", String(reader.result)).then(function (r) {
        if (!r.ok) { toast((r.error || "Error") + (r.detail ? ": " + r.detail : "")); return; }
        settings = r.settings;
        engine.call("history").then(function (h) { historyRows = h; renderHistory(); });
        renderModes(); renderSettings(); saveState(); toast("Session loaded");
      });
    };
    reader.readAsText(file);
  }

  /* ------------------------------------------------------------------ theme and keyboard */
  function applyTheme() {
    const t = store.get("scicalc.theme") || "auto";
    if (t === "auto") document.documentElement.removeAttribute("data-theme");
    else document.documentElement.setAttribute("data-theme", t);
  }
  function applyKeyboard() {
    expr.setAttribute("inputmode", store.get("scicalc.osk") === "1" ? "text" : "none");
  }

  /* ------------------------------------------------------------------ physical keyboard */
  expr.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") { ev.preventDefault(); evaluate(); return; }
    if (ev.key === "Escape") { ev.preventDefault(); clearAll(); return; }
    if (ev.key === "ArrowUp" || ev.key === "ArrowDown") {
      if (!historyRows.length) return;
      ev.preventDefault();
      recallPos = ev.key === "ArrowUp" ? Math.min(recallPos + 1, historyRows.length - 1) : Math.max(recallPos - 1, -1);
      expr.value = recallPos < 0 ? "" : historyRows[historyRows.length - 1 - recallPos].expr;
      justEvaluated = false;
      return;
    }
    if (ev.key === "Backspace" || ev.key === "Delete") { justEvaluated = false; return; }
    if (justEvaluated && ev.key.length === 1 && !ev.ctrlKey && !ev.metaKey && !ev.altKey) {
      if ("+-*/^×÷".indexOf(ev.key) >= 0) { expr.value = "Ans"; expr.setSelectionRange(3, 3); }
      else expr.value = "";
      justEvaluated = false;
    }
  });
  document.addEventListener("keydown", function (ev) {
    const t = ev.target;
    if (t === expr || ev.ctrlKey || ev.metaKey || ev.altKey || ev.key.length !== 1) return;
    if (t && (t.tagName === "INPUT" || t.tagName === "SELECT" || t.tagName === "TEXTAREA")) return;
    expr.focus();
  });
  /* ink ripple under the finger / pointer on every button, tab, row and switch */
  const reduceMotion = window.matchMedia ? window.matchMedia("(prefers-reduced-motion: reduce)") : { matches: false };
  document.addEventListener("pointerdown", function (ev) {
    if (reduceMotion.matches || !(ev.target instanceof Element)) return;
    const host = ev.target.closest("button, label.switch");
    if (!host || host.disabled) return;
    const r = host.getBoundingClientRect();
    const size = Math.max(r.width, r.height) * 2;
    const dot = document.createElement("span");
    dot.className = "ripple";
    dot.style.width = dot.style.height = size + "px";
    dot.style.left = (ev.clientX - r.left - size / 2) + "px";
    dot.style.top = (ev.clientY - r.top - size / 2) + "px";
    host.appendChild(dot);
    dot.addEventListener("animationend", function () { dot.remove(); });
  }, { passive: true });
  $("result").addEventListener("click", function () {
    const rs = $("result");
    rs.classList.remove("copied"); void rs.offsetWidth; rs.classList.add("copied");
    rs.addEventListener("animationend", function () { rs.classList.remove("copied"); }, { once: true });
    const text = $("result").textContent;
    if (!text || $("result").classList.contains("error")) return;
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function () { toast("Copied"); }, function () { toast("Could not copy"); });
  });

  /* ------------------------------------------------------------------ start */
  function setStatus(kind, text) {
    $("dot").className = "dot" + (kind ? " " + kind : "");
    $("statusText").textContent = text;
  }
  function failStart(message) {
    $("loadingText").textContent = "The calculator engine could not start.";
    $("loadingNote").textContent = message;
    $("loading").querySelector(".spinner").hidden = true;
    setStatus("bad", "engine error");
  }
  function creditText() {
    const c = window.SCICALC_CREDIT || {};
    return "\u00A9 " + (c.year || "") + " " + (c.owner || "") + ". " + (c.rights || "") + " SciCalc.";
  }
  function renderFooter() {
    const f = $("footer"), c = window.SCICALC_CREDIT || {};
    f.textContent = creditText();
    if (c.extra) f.appendChild(el("span", { class: "extra", text: c.extra }));
  }
  function start() {
    applyTheme();
    renderFooter();
    buildKeys($("sci"), SCI_KEYS, "");
    buildKeys($("num"), NUM_KEYS, "");
    applyKeyboard();
    $("toggleSci").addEventListener("click", function () {
      const k = $("keypad");
      k.classList.toggle("collapsed");
      const open = !k.classList.contains("collapsed");
      $("toggleSci").setAttribute("aria-expanded", String(open));
      $("toggleSci").textContent = open ? "Hide scientific keys" : "Show scientific keys";
    });
    document.querySelectorAll("#tabs button").forEach(function (b) { b.addEventListener("click", function () { openTab(b.dataset.tab); }); });
    $("fnSearch").addEventListener("input", function () { fnShown = 80; renderFunctions(); });
    $("fnCat").addEventListener("change", function () { fnShown = 80; renderFunctions(); });
    $("coSearch").addEventListener("input", function () { coShown = 80; renderConstants(); });
    $("coCat").addEventListener("change", function () { coShown = 80; renderConstants(); });
    const imp = el("input", { type: "file", id: "importFile", accept: "application/json,.json", hidden: "" });
    imp.addEventListener("change", function () { if (imp.files[0]) importSession(imp.files[0]); imp.value = ""; });
    document.body.appendChild(imp);
    window.addEventListener("beforeinstallprompt", function (ev) {
      ev.preventDefault(); deferredInstall = ev; $("installBtn").hidden = false;
    });
    $("installBtn").addEventListener("click", function () {
      if (!deferredInstall) return;
      deferredInstall.prompt(); deferredInstall = null; $("installBtn").hidden = true;
    });
    renderHistory();

    if (location.protocol === "file:") {
      failStart("This page was opened as a file. Open it through a web address instead: run serve.py (see README.txt) or host the folder on any web server.");
      return;
    }
    if (!window.SCI_SERVER_MODE && !window.Worker) { failStart("This browser cannot run Web Workers."); return; }
    if (!window.SCI_SERVER_MODE && typeof WebAssembly !== "object") { failStart("This browser does not support WebAssembly."); return; }

    engine.start(function (text) { $("loadingText").textContent = text; }).then(function () {
      return engine.call("settings");
    }).then(function (s) {
      settings = s;
      const saved = store.get("scicalc.state");
      return saved ? engine.call("load_state", saved).then(function (r) { if (r && r.ok) settings = r.settings; }) : null;
    }).then(function () {
      return Promise.all([engine.call("functions"), engine.call("constants"), engine.call("history")]);
    }).then(function (res) {
      fnRows = res[0]; coRows = res[1]; historyRows = res[2];
      fillCategorySelect($("fnCat"), fnRows, "All categories");
      fillCategorySelect($("coCat"), coRows, "All categories");
      renderFunctions(); renderConstants(); renderModes(); renderSettings(); renderHistory();
      if (window.SciGraph) window.SciGraph.init({ engine: engine, el: el, store: store, toast: toast, getLine: function () { return expr.value; } });
      $("loading").hidden = true;
      setStatus("ready", navigator.serviceWorker && navigator.serviceWorker.controller ? "ready · works offline" : "ready");
      expr.focus({ preventScroll: true });
    }).catch(function (err) {
      failStart(String(err && err.message || err));
    });

    if ("serviceWorker" in navigator && !window.SCI_SERVER_MODE) {
      navigator.serviceWorker.register("sw.js").then(function () {
        return navigator.serviceWorker.ready;
      }).then(function () {
        if ($("statusText").textContent.indexOf("ready") === 0) setStatus("ready", "ready · works offline");
      }).catch(function () { /* offline use is simply not available in this browser */ });
    }
  }
  window.SciApp = { engine: engine, press: press, evaluate: evaluate, getSettings: function () { return settings; } };
  start();
})();
