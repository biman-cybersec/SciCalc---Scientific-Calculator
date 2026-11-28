"""Checks: the plain-data API (scicalc/api.py).  Run alone with  python run_tests.py api"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "api"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import json
import math

from ..registry import REGISTRY

from ..api import Engine, dispatch, _METHODS


def checks_api_42(check):
    """application programming interface: answers are plain data, nothing leaks"""
    e = Engine()
    r = e.evaluate("sqrt(12)+1")
    check("api ok answer keys", sorted(r), ["decimal", "expr", "kind", "ok", "text"])
    check("api ok answer", (r["ok"], r["text"], r["kind"]), (True, "4.464101615", "number"))
    check("api exact fraction keeps decimal", (e.evaluate("1/3+1/6")["text"], e.evaluate("7/2")["kind"]), ("0.5", "number"))
    for expr in ["8^(-1)", "1/3+1/6", "7/2", "0.1+0.2", "{1/2,3}", "2/3"]:
        json.dumps(e.evaluate(expr))                                            # Decimal values must not reach JSON
        check(f"api {expr} is JSON", json.loads(dispatch("evaluate", json.dumps([expr])))["ok"], True)
    fr = Engine()
    fr.configure({"fraction": "improper"})
    check("api fraction mode: text and decimal", (fr.evaluate("7/2")["text"], fr.evaluate("7/2")["decimal"], fr.evaluate("1/8")["decimal"]), ("7/2", "3.5", "0.125"))
    check("api decimal equal to text is dropped", Engine().evaluate("7/2")["decimal"], None)
    for expr, kind in [("{1,2,3}", "list"), ("{{1,2},{3,4}}", "matrix"), ("2+2", "number")]:
        check(f"api kind of {expr}", e.evaluate(expr).get("kind"), kind)
    ce = Engine()
    ce.configure({"complex": True})
    check("api complex kind", (ce.evaluate("sqrt(-4)")["kind"], ce.evaluate("sqrt(-4)")["text"]), ("complex", "2i"))
    for expr, err in [("1/0", "Math ERROR"), ("sin(", "Syntax ERROR"), ("sqrt()", "Argument ERROR"), ("", "Syntax ERROR"), ("2 +* 3", "Syntax ERROR")]:
        r = e.evaluate(expr)
        check(f"api error {expr!r}", (r["ok"], r["error"]), (False, err))
        check(f"api error {expr!r} is JSON", json.loads(json.dumps(r)) == r, True)
    check("api error position", e.evaluate("2+*3")["pos"] is not None, True)
    for weird in [None, 5, 3.5, "x" * 100000, "((((" * 500, "9" * 5000 + "^9" * 20, "\x00", "😀", "sin(30)\n+1"]:
        r = e.evaluate(weird)
        check(f"api weird input {str(weird)[:12]!r} gives a dict with ok", isinstance(r, dict) and "ok" in r, True)
        json.dumps(r)
    # state: variables, Ans, history, user functions
    e = Engine()
    e.evaluate("5->A")
    e.evaluate("A*2")
    check("api Ans and variable", (e.variables()["A"], e.variables()["Ans"]), ("5", "10"))
    check("api history", [h["text"] for h in e.history()], ["5", "10"])
    check("api history limit", len(e.history(1)), 1)
    check("api clear history", (e.clear_history()["ok"], e.history(), e.variables()["Ans"]), (True, [], "10"))
    e.evaluate("5")
    e.evaluate("10")
    e.evaluate("mysq(x)=x^2+1")
    check("api user function", (e.user_functions()[0]["name"], e.evaluate("mysq(3)")["text"]), ("mysq", "10"))
    check("api delete function", (e.delete_function("mysq")["ok"], e.user_functions()), (True, []))
    check("api delete missing function", e.delete_function("nope")["ok"], False)
    # settings
    s = e.settings()
    check("api default settings", s, {"angle": "deg", "display": "norm", "digits": 2, "fraction": "off", "sym": False,
                                      "base": "off", "dms": False, "complex": False, "polar": False})
    r = e.configure({"angle": "rad", "sym": True})
    check("api configure ok", (r["ok"], r["settings"]["angle"], r["settings"]["sym"]), (True, "rad", True))
    check("api angle applies", e.evaluate("asin(0.5)")["text"], "π/6")
    check("api configure fix 3", (e.configure({"display": "fix", "digits": 3, "sym": False})["ok"], e.evaluate("1/3")["text"]), (True, "0.333"))
    before = e.settings()
    for bad in [{"angle": "turns"}, {"display": "fancy"}, {"display": "fix", "digits": 99}, {"fraction": "half"}, {"base": "dec"},
                {"digits": "x"}, {"angle": "deg", "display": "nope"}, 5, None, []]:
        r = e.configure(bad)
        check(f"api bad settings {bad!r}", (r["ok"], e.settings() == before), (False, True))
    check("api reset", (e.reset()["angle"], e.history()), ("deg", []))
    check("api base and frac", (e.configure({"base": "hex", "fraction": "mixed"})["ok"], e.evaluate("255")["text"]), (True, "0xFF"))
    # browsing
    fl = e.functions()
    check("api functions count", len(fl), len(REGISTRY.functions()))
    check("api function row", sorted(fl[0]), ["aliases", "args", "category", "desc", "example", "name"])
    check("api functions sorted", fl == sorted(fl, key=lambda r: (r["category"], r["name"])), True)
    check("api functions are JSON", len(json.dumps(fl)) > 1000, True)
    cl = e.constants()
    check("api constants count", len(cl), len(REGISTRY.constants()))
    pi = [k for k in cl if k["name"] == "pi"][0]
    check("api constant pi", abs(pi["value"] - math.pi) < 1e-15, True)
    json.dumps(cl)
    cats = e.categories()
    check("api categories add up", sum(c["functions"] for c in cats), len(fl))
    check("api info", e.info(), {"functions": len(fl), "constants": len(cl), "categories": len(cats)})
    # save and load
    a = Engine()
    a.evaluate("7->B")
    a.evaluate("trip(x)=x*3")
    a.configure({"angle": "grad", "display": "sci", "digits": 4})
    text = a.save_state()
    b = Engine()
    r = b.load_state(text)
    check("api load ok", r["ok"], True)
    check("api load settings", b.settings()["angle"], "grad")
    check("api load variable and function", (b.evaluate("B")["text"], b.evaluate("trip(2)")["text"]), ("7.000×10^0", "6.000×10^0"))
    for bad in ["", "not json", "[]", '{"scicalc_session": 2}', '{"scicalc_session": 1, "angle": "x"}', "null", '{"scicalc_session":1,"variables":{"Q":1}}']:
        r = b.load_state(bad)
        check(f"api bad state {bad[:20]!r}", (r["ok"], b.settings()["angle"]), (False, "grad"))
    # dispatch: the single door used by the browser
    check("api dispatch evaluate", json.loads(dispatch("evaluate", '["2+3"]'))["text"], "5")
    check("api dispatch no payload", json.loads(dispatch("info"))["functions"], len(fl))
    for method, payload in [("nope", "[]"), ("evaluate", "{"), ("evaluate", "{}"), ("evaluate", "[]"), ("configure", "[1]"), ("history", '["x"]'),
                            ("__class__", "[]"), ("evaluate", "[[1,2]]"), ("load_state", "[5]")]:
        out = json.loads(dispatch(method, payload))
        check(f"api dispatch {method} {payload}", isinstance(out, (dict, list)), True)
    check("api dispatch refuses unknown", json.loads(dispatch("__init__", "[]"))["ok"], False)
    check("api methods listed", set(_METHODS) <= set(dir(Engine)), True)
    # every documented example works through the API without a leak
    bad = []
    for f in fl:
        expr, _, want = f["example"].partition(" => ")
        out = json.loads(dispatch("evaluate", json.dumps([expr])))
        if "ok" not in out:
            bad.append(f["name"])
    check("api every example returns an answer", bad, [])
    # graphing: sample() and analyze()
    g = Engine()
    s = g.sample(["sin(x)", "y=x^2", "1/x", "foo(x)", "x^2 +"], -2, 2, 5)
    check("graph sample ok", s["ok"], True)
    ys = [c["ys"] for c in s["curves"]]
    check("graph sample x^2", ys[1], [4.0, 1.0, 0.0, 1.0, 4.0])
    check("graph sample gap at a pole", (ys[2][2], ys[2][0]), (None, -0.5))
    check("graph sample radians by default", abs(ys[0][4] - math.sin(2)) < 1e-12, True)
    check("graph sample degrees on request", abs(g.sample(["sin(x)"], 0, 30, 2, "deg")["curves"][0]["ys"][1] - 0.5) < 1e-12, True)
    check("graph sample unknown name error", s["curves"][3]["error"], "Syntax ERROR: unknown name 'foo'")
    check("graph sample syntax error", s["curves"][4]["ys"], [None] * 5)
    check("graph sample good curves have no error", [c["error"] for c in s["curves"][:3]], [None, None, None])
    g.evaluate("5->A")
    check("graph sample uses variables", g.sample(["A*x"], 0, 1, 2)["curves"][0]["ys"], [0.0, 5.0])
    check("graph sample leaves the angle setting alone", g.settings()["angle"], "deg")
    for args in [([], 0, 1), (["x"], 1, 0), (["x"], 0, 1, 1), (["x"], 0, 1, 5000), (["x"] * 9, 0, 1), ("x", 0, 1), (["x"], float("nan"), 1), (["x"], "a", 1)]:
        out = json.loads(dispatch("sample", json.dumps(list(args), allow_nan=True)))
        check(f"graph sample bad input {str(args)[:30]}", out["ok"], False)
    a = g.analyze(["x^2-2", "x", "tan(x)", "1/x"], -4, 4)
    check("graph analyze ok", a["ok"], True)
    r0 = sorted(round(r["x"], 6) for r in a["roots"] if r["curve"] == 0)
    check("graph roots of x^2-2", r0, [-1.414214, 1.414214])
    check("graph no root for 1/x", [r for r in a["roots"] if r["curve"] == 3], [])
    check("graph tan roots are pi multiples", sorted(round(r["x"], 6) for r in a["roots"] if r["curve"] == 2), [-3.141593, 0.0, 3.141593])
    ix = sorted((round(p["x"], 6), round(p["y"], 6)) for p in a["intersections"] if (p["a"], p["b"]) == (0, 1))
    check("graph intersections of x^2-2 and x", ix, [(-1.0, -1.0), (2.0, 2.0)])
    check("graph asymptotes are not intersections", [p for p in a["intersections"] if (p["a"], p["b"]) == (2, 3) and abs(p["y"]) > 1e6], [])
    check("graph analyze bad range", g.analyze(["x"], 2, 1)["ok"], False)
    check("graph analyze is JSON", len(json.dumps(a)) > 10, True)
