"""Plain-data API for apps (web, desktop, phone)

Module 45 of 47.  An app should talk to the calculator ONLY through this module: every answer is plain data
(dict / list / str / number / bool / None) that can be turned into JSON, and no Python exception ever escapes.

    eng = Engine()
    eng.evaluate("sqrt(12)")      -> {"ok": True, "expr": "sqrt(12)", "text": "3.464101615", "decimal": None, "kind": "number"}
    eng.evaluate("1/0")           -> {"ok": False, "error": "Math ERROR", "detail": "...", "pos": None}
    eng.configure({"angle": "rad", "sym": True})
    eng.functions()               -> [{"name", "category", "desc", "args", "example", "aliases"}, ...]

`dispatch(method, payload_json)` is the single door used by the browser (Pyodide) and by the test server:
the payload is a JSON list of arguments and the answer is a JSON string.
"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "api"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from typing import Any
import json
import math
import re
from fractions import Fraction

from .errors import CalcError, CalcSyntaxError
from .registry import REGISTRY
from .arithmetic import Lst, Mat
from .engine import ANGLE_MODES, Calculator

def _kind(value):
    """A short word for the screen: number, text, list, matrix, complex or bool."""
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, Mat):
        return "matrix"
    if isinstance(value, Lst):
        return "list"
    if isinstance(value, complex):
        return "complex"
    if isinstance(value, str):
        return "text"
    return "number"


def _plain(v):
    """A constant's value as something JSON can hold."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, Fraction)):
        return float(v) if isinstance(v, Fraction) or abs(v) > 2 ** 53 else int(v)
    if isinstance(v, float):
        return v if math.isfinite(v) else str(v)
    return str(v)


_MAX_CURVES = 8
_MAX_SAMPLES = 2000
_Y_EQUALS = re.compile(r"^\s*(?:y|f\s*\(\s*x\s*\))\s*=(?!=)\s*(.+)$", re.IGNORECASE)


class _Curve:
    """One graph line y = f(x): evaluates the text with X set, never raises (a bad point is None)."""

    def __init__(self, base, text, angle):
        m = _Y_EQUALS.match(str(text))
        self.text = (m.group(1) if m else str(text)).strip()
        self.calc = Calculator(base.registry)
        self.calc.angle = angle                      # the graph has its own angle setting (radians by default)
        self.calc.variables.update(base.variables)
        self.calc.user_functions = base.user_functions
        self.error = None                            # the first error message, kept for the screen
        self.fatal = not self.text                   # a syntax problem: no point can ever work
        if self.fatal:
            self.error = "Type an expression such as sin(x) or x^2-3"
            return
        for probe in (1.0, 0.5, 2.0):                # a syntax error shows up at once; a math error at one point is fine
            try:
                self.calc.variables["X"] = probe
                self.calc.evaluate(self.text)
                break
            except CalcSyntaxError as err:
                self.fatal = True
                self.error = f"{err.message}: {err.detail}" if err.detail else err.message
                return
            except CalcError:
                continue
            except Exception:                        # nothing may leak out of the engine
                continue
        self.count = 0

    def at(self, x):
        if self.fatal:
            return None
        self.count += 1
        if self.count % 200 == 0:
            self.calc.history.clear()
        self.calc.variables["X"] = x
        try:
            v = self.calc.evaluate(self.text).value
            if isinstance(v, complex):
                if abs(v.imag) > 1e-9 * max(1.0, abs(v.real)):
                    return None
                v = v.real
            y = float(v)
        except CalcError as err:
            if self.error is None:
                self.error = f"{err.message}: {err.detail}" if err.detail else err.message
            return None
        except Exception:
            return None
        return y if math.isfinite(y) else None


def _angle_ok(angle):
    return angle if angle in ANGLE_MODES else "rad"


def _bisect(g, a, b, ga):
    """A zero of g between a and b (g(a) and g(b) have opposite signs), or None if g breaks on the way."""
    for _ in range(80):
        m = (a + b) / 2
        gm = g(m)
        if gm is None:
            return None
        if gm == 0:
            return m
        if (gm < 0) == (ga < 0):
            a, ga = m, gm
        else:
            b = m
    return (a + b) / 2


_DISPLAY_KINDS = ("norm", "fix", "sci", "eng", "custom")


class Engine:
    """One calculator with its own settings, variables, history and user functions."""

    def __init__(self):
        self.calc = Calculator()
        self._functions_cache = None
        self._constants_cache = None

    # ---------------- calculating ----------------
    def evaluate(self, expr):
        try:
            r = self.calc.evaluate(str(expr))
        except CalcError as err:
            return {"ok": False, "error": err.message, "detail": err.detail, "pos": err.pos}
        except Exception as err:                       # nothing may leak out of the engine
            return {"ok": False, "error": "Math ERROR", "detail": f"{type(err).__name__}", "pos": None}
        decimal = None if r.decimal is None or str(r.decimal) == r.text else str(r.decimal)   # Decimal -> text for JSON
        return {"ok": True, "expr": r.expr, "text": r.text, "decimal": decimal, "kind": _kind(r.value)}

    def history(self, limit=200):
        return [{"expr": r.expr, "text": r.text} for r in self.calc.history[-int(limit):]]

    def clear_history(self):
        self.calc.history.clear()
        return {"ok": True}

    def variables(self):
        out = {}
        for name, value in self.calc.variables.items():
            out[name] = self.calc.format(value)[0]
        out["Ans"] = self.calc.format(self.calc.ans)[0]
        return out

    def user_functions(self):
        return [{"name": n, "params": list(p), "body": b} for n, (p, b, _t) in sorted(self.calc.user_functions.items())]

    def delete_function(self, name):
        try:
            self.calc.delete_function(str(name))
        except CalcError as err:
            return {"ok": False, "error": err.message, "detail": err.detail}
        return {"ok": True}

    def reset(self):
        self.calc.reset()
        return self.settings()

    # ---------------- settings ----------------
    def settings(self):
        c = self.calc
        return {"angle": c.angle, "display": c.display[0], "digits": c.display[1],
                "fraction": c.frac_display or "off", "sym": bool(c.sym_display),
                "base": c.base_display or "off", "dms": bool(c.dms_display),
                "complex": bool(c.complex_mode), "polar": bool(c.complex_polar)}

    def configure(self, changes):
        """Apply settings given as {"angle": "rad", "display": "fix", "digits": 3, "fraction": "mixed", "sym": True, ...}.

        Nothing changes if any value is invalid; the answer is {"ok": True, "settings": {...}} or {"ok": False, "error": ...}.
        """
        c = self.calc
        if not isinstance(changes, dict):
            return {"ok": False, "error": "settings must be an object"}
        want = self.settings()
        want.update(changes)
        try:
            if want["angle"] not in ANGLE_MODES:
                raise ValueError("angle must be deg, rad or grad")
            if want["display"] not in _DISPLAY_KINDS:
                raise ValueError("display must be norm, fix, sci, eng or custom")
            digits = int(want["digits"])
            if want["fraction"] not in ("off", "improper", "mixed"):
                raise ValueError("fraction must be off, improper or mixed")
            if want["base"] not in ("off", "hex", "bin", "oct"):
                raise ValueError("base must be off, hex, bin or oct")
            probe = Calculator(c.registry)
            probe.set_display(want["display"], digits)                 # checks the digit range
        except (ValueError, KeyError, TypeError) as err:
            return {"ok": False, "error": str(err)}
        c.set_angle(want["angle"])
        c.set_display(want["display"], digits)
        c.frac_display = None if want["fraction"] == "off" else want["fraction"]
        c.base_display = None if want["base"] == "off" else want["base"]
        c.sym_display = bool(want["sym"])
        c.dms_display = bool(want["dms"])
        c.complex_mode = bool(want["complex"])
        c.complex_polar = bool(want["polar"])
        return {"ok": True, "settings": self.settings()}

    # ---------------- graphing ----------------
    def _graph_args(self, exprs, xmin, xmax, n):
        if not isinstance(exprs, list) or not exprs or len(exprs) > _MAX_CURVES:
            raise ValueError(f"give 1 to {_MAX_CURVES} expressions")
        xmin, xmax, n = float(xmin), float(xmax), int(n)
        if not (math.isfinite(xmin) and math.isfinite(xmax)) or xmin >= xmax:
            raise ValueError("the x range is not valid")
        if not 2 <= n <= _MAX_SAMPLES:
            raise ValueError(f"the number of points must be 2 to {_MAX_SAMPLES}")
        return xmin, xmax, n

    def sample(self, exprs, xmin, xmax, n=400, angle="rad"):
        """y values of each expression at n evenly spaced x from xmin to xmax (None where the value is not a real number).

        {"ok": True, "curves": [{"ys": [...], "error": None or "message"}, ...]}.  x[i] = xmin + i*(xmax-xmin)/(n-1).
        """
        try:
            xmin, xmax, n = self._graph_args(exprs, xmin, xmax, n)
        except (ValueError, TypeError) as err:
            return {"ok": False, "error": str(err)}
        angle = _angle_ok(angle)
        step = (xmax - xmin) / (n - 1)
        out = []
        for text in exprs:
            c = _Curve(self.calc, text, angle)
            ys = [None] * n if c.fatal else [c.at(xmin + i * step) for i in range(n)]
            if any(y is not None for y in ys):
                error = None                              # some points are fine; a gap (like 1/x at 0) is not an error
            else:
                error = c.error or "nothing to draw in this range"
            out.append({"ys": ys, "error": error})
        return {"ok": True, "curves": out}

    def analyze(self, exprs, xmin, xmax, angle="rad"):
        """Where each curve crosses the x axis and where curves cross each other, inside [xmin, xmax].

        {"ok": True, "roots": [{"curve", "x"}], "intersections": [{"a", "b", "x", "y"}]}.  Points where a curve only touches
        the axis without crossing it (such as x^2 at 0) are not found; jumps such as tan(x) at pi/2 are not counted.
        """
        try:
            xmin, xmax, n = self._graph_args(exprs, xmin, xmax, 1500)
        except (ValueError, TypeError) as err:
            return {"ok": False, "error": str(err)}
        angle = _angle_ok(angle)
        step = (xmax - xmin) / (n - 1)
        xs = [xmin + i * step for i in range(n)]
        curves = [_Curve(self.calc, t, angle) for t in exprs]
        ys = [[None] * n if c.fatal else [c.at(x) for x in xs] for c in curves]
        roots, crossings = [], []
        def scan(i, j):
            fa, ga = curves[i], (curves[j] if j is not None else None)
            if j is None:
                d = ys[i]
            else:
                d = [None if p is None or q is None else p - q for p, q in zip(ys[i], ys[j])]

            def diff(x):
                a = fa.at(x)
                if a is None:
                    return None
                if ga is None:
                    return a
                b = ga.at(x)
                return None if b is None else a - b
            found = []
            for k in range(n):
                here = d[k]
                if here is None:
                    continue
                nxt = d[k + 1] if k + 1 < n else None
                if here == 0:
                    found.append(xs[k])
                elif nxt is not None and here * nxt < 0:
                    x = _bisect(diff, xs[k], xs[k + 1], here)
                    if x is None:
                        continue
                    scale = max(1.0, abs(fa.at(x) or 0.0))
                    r = diff(x)
                    if r is not None and abs(r) <= 1e-6 * scale:        # a real crossing, not a jump through infinity
                        found.append(x)
            clean = []
            for x in found:
                if not clean or abs(x - clean[-1]) > 1e-9 * max(1.0, abs(x)):
                    clean.append(x)
            return clean, fa

        for i, c in enumerate(curves):
            if c.fatal:
                continue
            xs_found, fa = scan(i, None)
            for x in xs_found[:60]:
                roots.append({"curve": i, "x": x})
        for i in range(len(curves)):
            for j in range(i + 1, len(curves)):
                if curves[i].fatal or curves[j].fatal:
                    continue
                xs_found, fa = scan(i, j)
                for x in xs_found[:60]:
                    y = fa.at(x)
                    if y is not None:
                        crossings.append({"a": i, "b": j, "x": x, "y": y})
        return {"ok": True, "roots": roots, "intersections": crossings}

    # ---------------- browsing ----------------
    def functions(self):
        if self._functions_cache is None:
            rows = [{"name": f.name, "category": f.category, "desc": f.desc, "args": f.arity_text,
                     "example": f.example, "aliases": list(f.aliases)} for f in REGISTRY.functions()]
            rows.sort(key=lambda r: (r["category"], r["name"]))
            self._functions_cache = rows
        return self._functions_cache

    def constants(self):
        if self._constants_cache is None:
            rows = [{"name": k.name, "value": _plain(k.value), "category": k.category, "desc": k.desc,
                     "aliases": list(k.aliases)} for k in REGISTRY.constants()]
            rows.sort(key=lambda r: (r["category"], r["name"]))
            self._constants_cache = rows
        return self._constants_cache

    def categories(self):
        counts = {}
        for r in self.functions():
            counts[r["category"]] = counts.get(r["category"], 0) + 1
        return [{"name": k, "functions": v} for k, v in sorted(counts.items())]

    def info(self):
        n_func, n_const = REGISTRY.count()
        return {"functions": n_func, "constants": n_const, "categories": len(self.categories())}

    # ---------------- saving ----------------
    def save_state(self):
        """The whole session as a JSON string (settings, variables, Ans, user functions, recent history)."""
        return json.dumps(self.calc.to_dict())

    def load_state(self, text):
        try:
            data = json.loads(text)
            self.calc.load_dict(data)
        except CalcError as err:
            return {"ok": False, "error": err.message, "detail": err.detail}
        except (ValueError, TypeError, RecursionError):
            return {"ok": False, "error": "Argument ERROR", "detail": "the saved session is not valid"}
        return {"ok": True, "settings": self.settings()}


_METHODS = ("evaluate", "history", "clear_history", "variables", "user_functions", "delete_function", "reset", "settings", "configure",
            "functions", "constants", "categories", "info", "save_state", "load_state", "sample", "analyze")
_ENGINE: list[Any] = [None]


def shared_engine():
    """The shared Engine used by dispatch (created on first use)."""
    if _ENGINE[0] is None:
        _ENGINE[0] = Engine()
    return _ENGINE[0]


def dispatch(method, payload="[]"):
    """Call an Engine method by name with JSON arguments; always returns a JSON string.

    A bad method name or bad payload gives {"ok": false, "error": ...} instead of an exception.
    """
    if method not in _METHODS:
        return json.dumps({"ok": False, "error": f"unknown method {method}"})
    try:
        args = json.loads(payload)
        if not isinstance(args, list):
            raise ValueError("arguments must be a list")
        out = getattr(shared_engine(), method)(*args)
        return json.dumps(out)
    except (ValueError, TypeError) as err:
        return json.dumps({"ok": False, "error": f"bad request: {err}"})
    except Exception as err:                           # nothing may leak out of the engine
        return json.dumps({"ok": False, "error": f"{type(err).__name__}"})
