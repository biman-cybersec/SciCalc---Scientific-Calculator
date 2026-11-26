"""The Calculator class: state, evaluator, sessions

Module 6 of 47.  Taken from lines 992-1681 of the original single-file calculator.py.
Every name used here is imported explicitly from the module that defines it.
"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "engine"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from typing import Any
import cmath
import math
import re
from dataclasses import dataclass
from fractions import Fraction

from .errors import ArgumentError, CalcError, CalcSyntaxError, MathError
from .registry import REGISTRY
from .arithmetic import (
    Cx,
    Lst,
    MAX_ELEMENTS,
    Mat,
    _CPLX,
    _box,
    _box_binary,
    _build_box,
    _elem_text,
    _ew1,
    _is_scalar,
    _mat_power,
    _shape,
    ar_add,
    ar_div,
    ar_factorial,
    ar_mod,
    ar_mul,
    ar_neg,
    ar_normalize,
    ar_percent,
    ar_power,
    ar_sub,
)
from .display import format_number, format_result
from .parser import Parser, VARIABLES, tokenize

# ======================================================================================
#  PART 6 : THE CALCULATOR (state + evaluator)
# ======================================================================================

# The Calculator object: holds the state (angle mode, display mode, variables, Ans,
# history) and evaluates what you type. No printing and no input() in here, so the same
# engine can later sit behind a GUI or a phone app unchanged.


# Functions that loop (or build huge integers) in proportion to an argument. A typo such as
# fib_mod(1e308, 7) must give Math ERROR at once instead of freezing the calculator.
# name -> (largest allowed value, argument positions it applies to; None = every argument)
_ACTIVE_CALC: list[Any] = [None]          # the calculator currently applying a function (set in Calculator._apply)

ARG_LIMITS = {
    "aliquot_sum": (10 ** 13, None), "divisors_count": (10 ** 13, None), "divisors_sum": (10 ** 13, None),
    "is_perfect": (10 ** 13, None), "is_abundant": (10 ** 13, None), "sigma_k": (10 ** 13, (1,)),
    "primitive_root": (10 ** 13, None), "harmonic_number": (5000, None), "derangements": (10 ** 4, None),
    "double_factorial": (10 ** 5, None), "integrate_simpson": (20000, (3,)), "integrate_trap": (20000, (3,)), "rising_factorial": (10 ** 5, (1,)), "falling_factorial": (10 ** 5, (1,)),
    "fib_mod": (10 ** 7, (0,)), "lucas": (10 ** 5, None), "pell": (10 ** 5, None), "tribonacci": (10 ** 5, None),
    "linrec2": (10 ** 5, (4,)), "mat_pow2": (10 ** 6, (4,)), "binom_term": (10 ** 4, (0, 1)),
    "gp_nth": (10 ** 5, (2,)), "gp_sum": (10 ** 5, (2,)), "bessel_y": (10 ** 5, (0,)), "bessel_j": (10 ** 5, (0,)),
    "ode_euler": (10 ** 6, (4,)), "ode_rk4": (10 ** 6, (4,)), "poisson_pmf": (10 ** 5, (1,)),
    "poisson_cdf": (10 ** 5, (0,)), "num_integrate_trap": (10 ** 5, (3,)), "num_integrate_simpson": (10 ** 5, (3,)),
    "num_integrate_simpson38": (10 ** 5, (3,)),
}

def _cx_inv(z):
    return 1 / z


def _cx_root3(z):
    if z == 0:
        return 0j
    return z ** (1 / 3)


# name -> (implementation on complex numbers, number of arguments); trigonometric ones use radians
_CX_FUNCS = {
    "sqrt": (cmath.sqrt, 1), "cbrt": (_cx_root3, 1), "exp": (cmath.exp, 1), "ln": (cmath.log, 1),
    "log": (cmath.log10, 1), "log2": (lambda z: cmath.log(z) / math.log(2), 1),
    "sin": (cmath.sin, 1), "cos": (cmath.cos, 1), "tan": (cmath.tan, 1),
    "sinh": (cmath.sinh, 1), "cosh": (cmath.cosh, 1), "tanh": (cmath.tanh, 1),
    "asin": (cmath.asin, 1), "acos": (cmath.acos, 1), "atan": (cmath.atan, 1),
    "asinh": (cmath.asinh, 1), "acosh": (cmath.acosh, 1), "atanh": (cmath.atanh, 1),
    "sq": (lambda z: z * z, 1), "cube": (lambda z: z * z * z, 1), "inv": (_cx_inv, 1),
    "pow": (lambda a, b: a ** b, 2),
}
_CX_DOMAIN = {"sqrt", "ln", "log", "log2", "acosh", "atanh"}     # real functions that complex mode extends
_CX_PAIR_ARGS = {"c_mag", "c_arg", "c_conj", "c_add", "c_sub", "c_mul", "c_div", "c_recip", "c_abs2", "c_pow_n",
                 "c_pow", "c_sqrt", "c_exp", "c_ln", "c_sin", "c_cos", "c_tan", "c_sinh", "c_cosh", "c_tanh",
                 "c_asin", "c_acos", "c_atan", "c_polar", "c_nth_root"}


def _cx_expand(func, args):
    """The c_* functions take real and imaginary parts: c_mul(a, b, c, d).  A complex number (or a
    real one) may stand for such a pair: c_mul(1+2i, 3+4i), c_conj(3+4i), c_pow_n(1+i, 4)."""
    need = func.max_args
    if not any(isinstance(a, complex) for a in args):
        return args
    parts = []
    for a in args:
        parts.extend((a.real, a.imag) if isinstance(a, complex) else (a,))
    if len(parts) == need:
        return parts
    if need % 2 == 0 and len(args) == need // 2:                      # every argument is a complex number
        out = []
        for a in args:
            out.extend((a.real, a.imag) if isinstance(a, complex) else (a, 0))
        return out
    return args


ANGLE_MODES = ("deg", "rad", "grad")


@dataclass
class Result:
    expr: str
    value: Any               # int, Fraction, float, complex, Lst, Mat or str
    text: str                # what the display shows
    decimal: Any = None   # decimal form when `text` is a fraction


MAX_CALL_DEPTH = 25            # user functions calling user functions
MAX_USER_CALLS = 20000         # user-function calls allowed in one evaluation
_DEFINE = re.compile(r"([A-Za-z][A-Za-z0-9_]*)\s*\(\s*([A-Za-z](?:\s*,\s*[A-Za-z])*)\s*\)\s*=(?!=)\s*(.*)$", re.S)


def _whole_or_none(v):
    """The integer value of a whole-number result, else None."""
    if isinstance(v, int):
        return v
    if isinstance(v, Fraction) and v.denominator == 1:
        return int(v)
    if isinstance(v, float) and math.isfinite(v) and v == int(v) and abs(v) < 2 ** 63:
        return int(v)
    return None


def _enc_value(v):
    """A value as plain JSON data (no pickle): exact numbers stay exact."""
    if isinstance(v, bool):
        return {"t": "b", "v": v}
    if isinstance(v, int):
        return {"t": "i", "v": str(v)}
    if isinstance(v, Fraction):
        return {"t": "q", "v": f"{v.numerator}/{v.denominator}"}
    if isinstance(v, complex):
        return {"t": "c", "v": [repr(v.real), repr(v.imag)]}
    if isinstance(v, float):
        return {"t": "f", "v": repr(v)}
    if isinstance(v, Mat):
        return {"t": "m", "v": [[_enc_value(x) for x in row] for row in v]}
    if isinstance(v, Lst):
        return {"t": "l", "v": [_enc_value(x) for x in v]}
    if isinstance(v, str):
        return {"t": "s", "v": v}
    raise ValueError(f"cannot save a value of type {type(v).__name__}")


def _dec_value(j, depth=0):
    if depth > 3 or not isinstance(j, dict) or "t" not in j or "v" not in j:
        raise ValueError("bad value")
    t, v = j["t"], j["v"]
    if t == "b" and isinstance(v, bool):
        return v
    if t == "i":
        return int(v)
    if t == "q":
        q = Fraction(v)
        return q if q.denominator != 1 else int(q)
    if t == "f":
        x = float(v)
        if not math.isfinite(x):
            raise ValueError("not finite")
        return x
    if t == "c":
        re_, im_ = float(v[0]), float(v[1])
        if not (math.isfinite(re_) and math.isfinite(im_)):
            raise ValueError("not finite")
        return Cx(re_, im_)
    if t == "l" and isinstance(v, list) and len(v) <= MAX_ELEMENTS:
        return Lst(_dec_value(x, depth + 1) for x in v)
    if t == "m" and isinstance(v, list) and sum(len(r) for r in v) <= MAX_ELEMENTS:
        if len({len(r) for r in v}) > 1:
            raise ValueError("ragged matrix")
        return Mat(tuple(_dec_value(x, depth + 1) for x in r) for r in v)
    if t == "s" and isinstance(v, str) and len(v) <= 1000:
        return v
    raise ValueError("bad value")


_SESSION_LIMIT = 5_000_000


def save_session(calc, path):
    import json
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(calc.to_dict(), fh, indent=1, ensure_ascii=False)


def load_session(calc, path):
    import json
    import os
    if os.path.getsize(path) > _SESSION_LIMIT:
        raise ArgumentError("the session file is too large")
    with open(path, encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except ValueError as err:
            raise ArgumentError(f"the session file is not valid JSON ({err})")
    calc.load_dict(data)


_SYM_TOL = 1e-12                 # relative match needed before a decimal is shown as an exact form
_SYM_DEN = 1000                  # largest denominator tried for plain fractions and for the coefficient of pi
_SYM_PI_DEN = 720


def _squarefree(n):
    """n = k^2 m with m squarefree: returns (k, m)."""
    k, m, d = 1, n, 2
    while d * d <= m:
        while m % (d * d) == 0:
            m //= d * d
            k *= d
        d += 1 if d == 2 else 2
    return k, m


def _coef_text(q, body):
    """q * body as text: 1 -> body, 3/2 -> 3body/2, -1/4 -> -body/4."""
    sign = "-" if q < 0 else ""
    a, b = abs(q.numerator), q.denominator
    head = body if a == 1 else f"{a}{body}"
    return f"{sign}{head}" + (f"/{b}" if b != 1 else "")


def sym_text(x):
    """Exact form of a real number when it is a simple one: p/q, (p/q)pi or (a/b)sqrt(m); else None.

    This recognises a decimal result; it does not do algebra.  Matching needs agreement to a relative 1e-12
    and small denominators, so a result such as 0.8660254037844386 becomes √3/2 while 0.123456789 stays decimal.
    """
    if isinstance(x, bool):
        return None
    if isinstance(x, int):
        return str(x)
    if isinstance(x, Fraction):
        return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    if not isinstance(x, float) or not math.isfinite(x):
        return None
    if x == 0:
        return "0"
    ax = abs(x)
    if ax < 1e-9 or ax > 1e9:
        return None
    ok = lambda cand: abs(cand - ax) <= _SYM_TOL * ax
    sign = -1 if x < 0 else 1
    q = Fraction(ax).limit_denominator(_SYM_DEN)                 # 1. a fraction
    if q != 0 and ok(float(q)):
        return str(sign * q.numerator) if q.denominator == 1 else f"{'-' if sign < 0 else ''}{q.numerator}/{q.denominator}"
    q = Fraction(ax / math.pi).limit_denominator(_SYM_PI_DEN)     # 2. a fraction of pi
    if q != 0 and ok(float(q) * math.pi):
        return _coef_text(sign * q, "π")
    sq = Fraction(ax * ax).limit_denominator(_SYM_DEN)            # 3. a multiple of a square root: x^2 = p/q
    if sq != 0 and ok(math.sqrt(float(sq))):
        p, qd = sq.numerator, sq.denominator
        if p * qd <= 10 ** 9:
            k, m = _squarefree(p * qd)                            # sqrt(p/q) = sqrt(p q)/q = k sqrt(m)/q
            if m > 1:
                return _coef_text(sign * Fraction(k, qd), f"√{m}")
    return None


def _frac_text(q, mode):
    sign = "-" if q < 0 else ""
    q = abs(q)
    if mode == "mixed" and q > 1:
        whole, rest = divmod(q.numerator, q.denominator)
        return f"{sign}{whole} {rest}/{q.denominator}" if rest else f"{sign}{whole}"
    return f"{sign}{q.numerator}/{q.denominator}"


def _base_text(n, base):
    sign = "-" if n < 0 else ""
    n = abs(n)
    return sign + {"hex": f"0x{n:X}", "bin": f"0b{n:b}", "oct": f"0o{n:o}"}[base]


class Calculator:
    def __init__(self, registry=REGISTRY):
        self.registry = registry
        self.reset()

    def reset(self):
        self.angle = "deg"
        self.complex_mode = False       # complex mode: sqrt(-4), ln(-1), (-8)^(1/3) give complex values
        self.complex_polar = False      # show complex results as r∠θ
        self.display = ("norm", 2)
        self.base_display: str | None = None        # None, "hex", "bin" or "oct": show whole-number results in that base
        self.dms_display = False        # show real results as degrees-minutes-seconds
        self.frac_display: str | None = None        # None, "improper" (7/2) or "mixed" (3 1/2): show exact fractions as fractions
        self.sym_display = False        # recognise results such as 2√3, π/6, √3/2 and show them exactly
        self.user_functions = {}        # f(x)=x^2+1  ->  {"f": (["X"], "x^2+1", tree)}
        self._depth = 0                 # nesting of user-function calls
        self._budget: list[int] = [0]              # calls left for this evaluation (shared with child calculators)
        self.variables: dict[str, Any] = {v: 0 for v in VARIABLES}
        self.ans: Any = 0
        self.preans: Any = 0
        self.history = []

    # ---------------- settings ----------------
    def set_angle(self, mode):
        mode = mode.lower()
        if mode not in ANGLE_MODES:
            raise ValueError("angle mode must be deg, rad or grad")
        self.angle = mode

    def set_display(self, kind, n=2):
        ranges = {"norm": (1, 2), "fix": (0, 9), "sci": (1, 10), "eng": (1, 10), "custom": (0, 10)}
        if kind not in ranges or not ranges[kind][0] <= n <= ranges[kind][1]:
            raise ValueError("use: norm 1|2, fix 0-9, sci 1-10, eng 1-10, custom 0-10")
        self.display = (kind, n)

    def to_radians(self, x):
        x = float(x)
        return {"deg": x * math.pi / 180, "rad": x, "grad": x * math.pi / 200}[self.angle]

    def from_radians(self, r):
        return {"deg": r * 180 / math.pi, "rad": r, "grad": r * 200 / math.pi}[self.angle]

    # ---------------- evaluating ----------------
    def evaluate(self, text):
        original = text
        text = text.strip()
        if text.endswith("="):
            text = text[:-1].rstrip()
        if not text:
            raise CalcSyntaxError("nothing to calculate", 0)

        if text.replace(" ", "").upper() in ("M+", "M-"):                    # memory keys
            op = ar_add if "+" in text else ar_sub
            self.variables["M"] = op(self.variables["M"], self.ans)
            return self._finish(original, self.variables["M"])

        _CPLX[0] = self.complex_mode
        defined = self._try_define(original, text)
        if defined is not None:
            return defined
        if self._depth == 0:
            self._budget[0] = MAX_USER_CALLS
        offset = 0
        if text[0] in "+*/^×÷²³!%":                                          # "*2" means "Ans*2"
            text, offset = "Ans" + text, 3
        try:
            tokens = tokenize(text, self._known)
            tree, target = Parser(tokens, self.registry, self.user_functions).parse()
            value = ar_normalize(self._eval(tree))
        except CalcError as err:
            if err.pos is not None:
                err.pos = max(0, err.pos - offset)
            raise
        except (OverflowError, ZeroDivisionError, ValueError):
            raise MathError("result out of range")
        except TypeError:
            raise ArgumentError("cannot use these values together")
        except RecursionError:
            raise CalcSyntaxError("expression is too complex")
        if target:
            self.variables[target] = value
        return self._finish(original, value)

    def _finish(self, expr, value):
        self.preans, self.ans = self.ans, value
        text, decimal = self.format(value)
        result = Result(expr.strip(), value, text, decimal)
        self.history.append(result)
        return result

    def format(self, value):
        from .lib_vectors_solver_basen import deg2dms  # imported here because lib_vectors_solver_basen is loaded after this module
        if self.frac_display:
            shown = self._frac_format(value)
            if shown is not None:
                return shown
        if self.sym_display and not self.base_display and not self.dms_display:
            shown = self._sym_format(value)
            if shown is not None:
                return shown
        if not isinstance(value, (str, complex, Lst, Mat)):
            if self.base_display and not isinstance(value, bool):
                whole = _whole_or_none(value)
                if whole is not None:
                    return _base_text(whole, self.base_display), None
            elif self.dms_display:
                try:
                    return deg2dms(value), None
                except (TypeError, ValueError, OverflowError):
                    pass
        return format_result(value, self.display, self.angle if self.complex_polar else None)

    # ---------------- sessions ----------------
    def to_dict(self):
        """Everything needed to continue later: settings, variables, Ans, user functions, recent history."""
        return {
            "scicalc_session": 1,
            "angle": self.angle, "display": list(self.display),
            "complex_mode": self.complex_mode, "complex_polar": self.complex_polar,
            "base_display": self.base_display, "dms_display": self.dms_display, "frac_display": self.frac_display,
            "sym_display": self.sym_display,
            "variables": {k: _enc_value(v) for k, v in self.variables.items()},
            "ans": _enc_value(self.ans), "preans": _enc_value(self.preans),
            "functions": {n: [list(params), body] for n, (params, body, _t) in self.user_functions.items()},
            "history": [{"expr": r.expr, "value": _enc_value(r.value), "text": r.text} for r in self.history[-200:]],
        }

    def load_dict(self, d):
        """Replace the whole state from a saved session. Nothing changes if anything in it is invalid."""
        if not isinstance(d, dict) or d.get("scicalc_session") != 1:
            raise ArgumentError("this is not a SCICALC session file")
        new = Calculator(self.registry)
        try:
            new.set_angle(d.get("angle", "deg"))
            kind, n = d.get("display", ["norm", 2])
            new.set_display(kind, int(n))
            new.complex_mode = bool(d.get("complex_mode", False))
            new.complex_polar = bool(d.get("complex_polar", False))
            base = d.get("base_display")
            frac = d.get("frac_display")
            if base not in (None, "hex", "bin", "oct") or frac not in (None, "improper", "mixed"):
                raise ValueError("bad display setting")
            new.base_display, new.frac_display = base, frac
            new.dms_display = bool(d.get("dms_display", False))
            new.sym_display = bool(d.get("sym_display", False))
            saved_vars = d.get("variables", {})
            if not isinstance(saved_vars, dict) or any(k not in VARIABLES for k in saved_vars):
                raise ValueError("bad variable name")
            for k, v in saved_vars.items():
                new.variables[k] = _dec_value(v)
            new.ans, new.preans = _dec_value(d.get("ans", _enc_value(0))), _dec_value(d.get("preans", _enc_value(0)))
            funcs = d.get("functions", {})
            if not isinstance(funcs, dict) or len(funcs) > 200:
                raise ValueError("bad function table")
            for name, (params, body) in funcs.items():          # two passes so functions may call each other
                if not isinstance(params, list) or not isinstance(body, str):
                    raise ValueError("bad function")
                new.user_functions[name.lower()] = ([str(q).upper() for q in params], body, None)
            for name, (params, body) in funcs.items():
                _CPLX[0] = new.complex_mode
                new._try_define(f"{name}({','.join(params)})={body}", f"{name}({','.join(params)})={body}")
            hist = d.get("history", [])
            if not isinstance(hist, list):
                raise ValueError("bad history")
            for h in hist[-200:]:
                new.history.append(Result(str(h["expr"]), _dec_value(h["value"]), str(h["text"]), None))
        except CalcError:
            raise
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError, ZeroDivisionError, IndexError, RecursionError) as err:
            raise ArgumentError(f"the session file is damaged ({err})")
        for attr in ("angle", "display", "complex_mode", "complex_polar", "base_display", "dms_display", "frac_display",
                     "sym_display", "variables", "ans", "preans", "user_functions", "history"):
            setattr(self, attr, getattr(new, attr))

    def _sym_format(self, value):
        """Symbolic text for a real number or for a list/matrix with at least one recognisable entry."""
        def one(v):
            if isinstance(v, (int, bool, complex)) or isinstance(v, str):
                return None
            t = sym_text(v)
            return t if t is not None and not t.lstrip("-").isdigit() else None
        if isinstance(value, (int, float, Fraction)) and not isinstance(value, bool):
            t = one(value)
            if t is None:
                return None
            return t, format_number(value, self.display)
        if isinstance(value, (Lst, Mat)):
            rows = list(value) if isinstance(value, Mat) else [value]
            if not any(one(v) is not None for row in rows for v in row):
                return None
            def cell(v):
                return one(v) or _elem_text(v, self.display)
            if isinstance(value, Lst):
                return "{" + ", ".join(cell(v) for v in value) + "}", None
            return "{" + ", ".join("{" + ", ".join(cell(v) for v in row) + "}" for row in value) + "}", None
        return None

    def _frac_format(self, value):
        """Exact fractions as p/q (or mixed numbers); None when the value has no fraction in it."""
        def one(v):
            if isinstance(v, Fraction) and v.denominator != 1:
                return _frac_text(v, self.frac_display)
            return None
        if isinstance(value, Fraction):
            t = one(value)
            return (t, format_number(value, self.display)) if t else None
        if isinstance(value, (Lst, Mat)) and any(isinstance(v, Fraction) and v.denominator != 1
                                                 for row in (value if isinstance(value, Mat) else [value]) for v in row):
            def cell(v):
                return one(v) or self._sym_cell(v) or _elem_text(v, self.display)
            if isinstance(value, Lst):
                return "{" + ", ".join(cell(v) for v in value) + "}", None
            return "{" + ", ".join("{" + ", ".join(cell(v) for v in row) + "}" for row in value) + "}", None
        return None

    def _sym_cell(self, v):
        """Symbolic text of one list entry when sym mode is on (used inside fraction-mode lists)."""
        if not self.sym_display or isinstance(v, (bool, int, complex, str)):
            return None
        t = sym_text(v)
        return t if t is not None and not t.lstrip("-").isdigit() else None

    def _known(self, name):
        return (name in ("ans", "preans", "mod", "npr", "ncr") or name in self.user_functions
                or self.registry.knows(name))

    # ---------------- user-defined functions ----------------
    def _try_define(self, original, text):
        m = _DEFINE.match(text)
        if not m:
            return None
        name, plist, body = m.group(1).lower(), m.group(2), m.group(3).strip()
        params = [p.strip().upper() for p in plist.split(",")]
        if name in ("ans", "preans", "mod", "npr", "ncr", "e", "i") or self.registry.knows(name) \
                or self.registry.constant(name) is not None:
            raise ArgumentError(f"'{name}' is already a built-in name")
        if len(params) > 8 or len(set(params)) != len(params) or any(p not in "ABCDFMXY" for p in params):
            raise ArgumentError("parameters must be different letters from A B C D F M X Y (at most 8)")
        if not body:
            raise CalcSyntaxError("the function needs a formula after '='", len(text))
        previous = self.user_functions.get(name)
        self.user_functions[name] = (params, body, None)            # visible while parsing: allows recursion
        try:
            tree, target = Parser(tokenize(body, self._known), self.registry, self.user_functions).parse()
            if target:
                raise CalcSyntaxError("a function body cannot store into a variable", 0)
        except Exception:
            if previous is None:
                del self.user_functions[name]
            else:
                self.user_functions[name] = previous
            raise
        self.user_functions[name] = (params, body, tree)
        shown = f"{m.group(1)}({', '.join(p.lower() for p in params)}) = {body}"
        return Result(original.strip(), shown, shown, None)

    def delete_function(self, name):
        if name.lower() not in self.user_functions:
            raise ArgumentError(f"no user function named '{name}'")
        del self.user_functions[name.lower()]

    def list_functions(self):
        return [f"{n}({', '.join(p.lower() for p in params)}) = {body}"
                for n, (params, body, _t) in sorted(self.user_functions.items())]

    def _call_user(self, name, args, pos):
        params, _body, tree = self.user_functions[name]
        if len(args) != len(params):
            raise ArgumentError(f"{name} needs {len(params)} argument(s)", pos)
        if self._depth >= MAX_CALL_DEPTH:
            raise MathError("function calls nested too deeply", pos)
        self._budget[0] -= 1
        if self._budget[0] < 0:
            raise MathError("too many function calls", pos)
        child = Calculator(self.registry)
        child.angle, child.complex_mode, child.complex_polar = self.angle, self.complex_mode, self.complex_polar
        child.variables.update(self.variables)
        child.ans, child.preans = self.ans, self.preans
        child.user_functions = self.user_functions
        child._depth, child._budget = self._depth + 1, self._budget
        for p, a in zip(params, args):
            child.variables[p] = a
        return ar_normalize(child._eval(tree))

    # ---------------- the tree walker ----------------
    def _eval(self, node):
        kind = node[0]
        if kind == "num":
            return ar_normalize(node[1])
        if kind == "str":
            return node[1]
        if kind == "const":
            return ar_normalize(self.registry.constant(node[1]).value)  # pyright: ignore[reportOptionalMemberAccess]
        if kind == "var":
            return self.variables[node[1]]
        if kind == "ans":
            return self.ans if node[1] == 0 else self.preans
        if kind == "imag":
            return Cx(0.0, 1.0)
        if kind == "list":
            return _build_box([self._eval(a) for a in node[1]])
        if kind == "neg":
            v = self._eval(node[1])
            return _ew1(ar_neg, v) if _box(v) else ar_neg(v)
        if kind == "bin":
            op, left, right = node[1], self._eval(node[2]), self._eval(node[3])
            if _box(left) or _box(right):
                return _box_binary(op, left, right)
            return _BINARY[op](left, right)
        if kind == "post":
            return self._postfix(node[1], self._eval(node[2]))
        if kind == "call":
            func = self.registry.function(node[1])
            return self._apply(func, [self._eval(a) for a in node[2]], node[3])
        if kind == "ucall":
            return self._call_user(node[1], [self._eval(a) for a in node[2]], node[3])
        raise CalcSyntaxError("cannot evaluate this")

    def _postfix(self, op, x):
        if _box(x):
            if isinstance(x, Mat) and op in ("²", "³", "⁻¹"):
                return _mat_power(x, {"²": 2, "³": 3, "⁻¹": -1}[op])
            return _ew1(lambda v: self._postfix(op, v), x)
        if op == "!":
            return ar_factorial(x)
        if op == "%":
            return ar_percent(x)
        if op == "²":
            return ar_power(x, 2)
        if op == "³":
            return ar_power(x, 3)
        if op == "⁻¹":
            return ar_div(1, x)
        if op == "°":                                    # 30° -> current angle unit
            if self.angle == "deg":
                return x
            return ar_mul(x, math.pi / 180) if self.angle == "rad" else ar_mul(x, Fraction(10, 9))
        raise CalcSyntaxError(f"unknown operator {op}")

    def _apply_boxed(self, func, args, pos):
        """A scalar function called with lists/matrices.  Variadic functions (mean, irr, npv ...)
        take the list's elements as their arguments; other functions work element by element
        (sin({1,2,3})); if the argument count does not fit, the elements are spliced in
        (det3({{1,2,3},{4,5,6},{7,8,9}}))."""
        n = len(args)
        variadic = func.max_args is None or func.max_args >= 50
        if variadic or not func.min_args <= n <= func.max_args:  # pyright: ignore[reportOperatorIssue]
            flat = []
            for a in args:
                if isinstance(a, Lst):
                    flat.extend(a)
                elif isinstance(a, Mat):
                    flat.extend(v for row in a for v in row)
                else:
                    flat.append(a)
            if len(flat) > MAX_ELEMENTS:
                raise MathError("list too long", pos)
            return self._apply(func, flat, pos)
        boxes = [a for a in args if _box(a)]
        first = boxes[0]
        for b in boxes:
            if type(b) is not type(first) or _shape(b) != _shape(first):
                raise MathError("lists must have the same size", pos)
        cols = [list(a) if isinstance(a, Lst) else [v for row in a for v in row] if isinstance(a, Mat) else None
                for a in args]
        count = len(cols[args.index(first)])  # pyright: ignore[reportArgumentType]
        out = []
        for k in range(count):
            r = self._apply(func, [c[k] if c is not None else a for c, a in zip(cols, args)], pos)
            if not _is_scalar(r):
                raise ArgumentError(f"{func.name} does not give a number for each element", pos)
            out.append(r)
        if isinstance(first, Lst):
            return Lst(out)
        width = len(first[0])
        return Mat(tuple(out[i:i + width]) for i in range(0, len(out), width))

    def _apply_complex(self, func, args, pos):
        """A function called with a complex argument: the common functions have complex versions
        (radians for the trigonometric ones); anything else cannot take complex numbers."""
        entry = _CX_FUNCS.get(func.name)
        if entry is None:
            return None
        impl, nargs = entry
        if len(args) != nargs:
            raise ArgumentError(f"{func.name} takes {func.arity_text}", pos)
        try:
            return ar_normalize(impl(*[complex(a) for a in args]))
        except (ValueError, ZeroDivisionError, OverflowError):
            raise MathError(f"{func.name} is not defined for this input", pos)

    def _apply(self, func, args, pos=None):
        if func.name in _CX_PAIR_ARGS:
            args = _cx_expand(func, args)
        if any(isinstance(a, complex) for a in args):
            out = self._apply_complex(func, args, pos)
            if out is not None:
                return out
        if not func.lists and any(_box(a) for a in args):
            return self._apply_boxed(func, args, pos)
        n = len(args)
        if n < func.min_args or (func.max_args is not None and n > func.max_args):
            raise ArgumentError(f"{func.name} takes {func.arity_text}", pos)
        limit = ARG_LIMITS.get(func.name)
        if limit:
            cap, where = limit
            for i, a in enumerate(args):
                if (where is None or i in where) and isinstance(a, (int, float, Fraction)) \
                        and not isinstance(a, bool) and abs(a) > cap:
                    raise MathError("input too large for this function", pos)
        _ACTIVE_CALC[0] = self
        if func.angle_in:
            args = [self.to_radians(args[0])] + args[1:]
        if not func.exact:
            args = [float(a) for a in args]
        try:
            out = func.fn(*args)
        except (CalcError, ValueError, ZeroDivisionError, OverflowError) as err:
            if self.complex_mode and func.name in _CX_DOMAIN and len(args) == 1 and _is_scalar(args[0]):
                try:                                    # complex mode widens the domain (sqrt(-4) = 2i)
                    return ar_normalize(_CX_FUNCS[func.name][0](complex(args[0])))
                except (ValueError, ZeroDivisionError, OverflowError):
                    pass
            if isinstance(err, CalcError):
                raise
            raise MathError(f"{func.name} is not defined for this input", pos)
        except TypeError:
            raise ArgumentError(f"{func.name} cannot use these values", pos)
        if func.angle_out:
            out = self.from_radians(out)
        if func.snap_zero and isinstance(out, float) and abs(out) < 1e-14:
            out = 0.0
        return ar_normalize(out)


_BINARY = {"+": ar_add, "-": ar_sub, "*": ar_mul, "/": ar_div,
           "^": ar_power, "mod": ar_mod}
