"""Sprint 5A: calculus and numerical analysis

Module 27 of 47.  Taken from lines 8924-9318 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_calculus"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from typing import Any, Callable
import math

from .errors import ArgumentError, CalcError, MathError
from .registry import register
from .arithmetic import ar_add, ar_mul, ar_normalize
from .engine import Calculator, _ACTIVE_CALC
from .lib_powers_rounding import _whole
from .lib_vectors_solver_basen import CAT_CALC

# ======================================================================================
#  SPRINT 5 - PART A : CALCULUS AND NUMERICAL ANALYSIS
#  Expression strings use x (and y).  They are evaluated by the calculator's own parser, in
#  the calling calculator's angle mode (so sin(x) in RAD mode is the usual calculus sine).
#  Numerical answers are good to about 8 significant digits.
# ======================================================================================

def _make_fn(expr, exact=False) -> Callable[..., Any]:
    """Turn an expression string (or a callable) into f(x, y=0)."""
    if callable(expr):
        return expr
    if not isinstance(expr, str):
        raise ArgumentError("this function needs an expression in quotes, such as 'x^2+1'")
    text = expr.strip().strip("'\"")
    if not text:
        raise ArgumentError("empty expression")
    calc = Calculator()
    base = _ACTIVE_CALC[0]
    if base is not None:
        calc.angle = base.angle
        calc.complex_mode = base.complex_mode
        calc.variables.update(base.variables)
        calc.user_functions = base.user_functions
    counter = [0]

    def f(x, y=0.0):
        calc.variables["X"] = x
        calc.variables["Y"] = y
        counter[0] += 1
        if counter[0] % 256 == 0:
            calc.history.clear()
        try:
            v = calc.evaluate(text).value
        except CalcError:
            raise MathError("the expression could not be evaluated")
        if exact:
            return v
        try:
            return float(v)
        except (TypeError, ValueError):
            raise MathError("the expression must give a real number")
    return f


def _snap8(v):
    """Numerical results are good to ~8 digits; show them without 1e-10 noise."""
    if v == 0 or not math.isfinite(v):
        return v
    return float(f"{v:.9g}")


_GL_CACHE = {}


def _gl_nodes(n):
    """Gauss-Legendre nodes and weights on [-1, 1] (Newton iteration on P_n)."""
    if n in _GL_CACHE:
        return _GL_CACHE[n]
    xs, ws = [], []
    for i in range(n):
        x = math.cos(math.pi * (i + 0.75) / (n + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-16:
                break
        p0, p1 = 1.0, x
        for k in range(2, n + 1):
            p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
        dp = n * (x * p1 - p0) / (x * x - 1)
        xs.append(x)
        ws.append(2 / ((1 - x * x) * dp * dp))
    _GL_CACHE[n] = (xs, ws)
    return xs, ws


def _gl_int(f, a, b, panels=8, n=12):
    xs, ws = _gl_nodes(n)
    h = (b - a) / panels
    total = 0.0
    for p in range(panels):
        lo = a + p * h
        mid, half = lo + h / 2, h / 2
        total += half * sum(w * f(mid + half * x) for x, w in zip(xs, ws))
    return total


_DN_STEP = {1: (0.15, 5), 2: (0.5, 6), 3: (0.5, 6), 4: (0.3, 5), 5: (0.6, 5), 6: (0.8, 5)}


def _gl_conv(f, a, b, panels=8, n=12):
    """Gauss-Legendre with a convergence check: refuses integrands that blow up inside [a, b]."""
    coarse = _gl_int(f, a, b, panels, n)
    fine = _gl_int(f, a, b, panels * 2, n)
    if not (math.isfinite(coarse) and math.isfinite(fine)) or abs(fine - coarse) > 1e-3 * max(1.0, abs(fine)):
        raise MathError("integral does not converge")
    return fine


def _dn(f, n, x, y=None, levels=None):
    """n-th derivative by central differences with Richardson extrapolation.
    Step sizes were tuned per order; accuracy is about 9 digits for n <= 3, 7 for n = 4, 6 for n = 5, 4 for n = 6."""
    g = f if y is None else (lambda t: f(t, y))
    h0, default_levels = _DN_STEP[n]
    levels = levels or default_levels
    try:
        g(x)                              # the function must be defined at x itself
    except (OverflowError, ValueError, ZeroDivisionError):
        raise MathError("function is not defined at this point")
    for _ in range(8):
        try:
            rows = []
            for lv in range(levels):
                h = h0 / 2 ** lv
                s = 0.0
                for k in range(n + 1):
                    s += (-1) ** k * math.comb(n, k) * g(x + (n / 2 - k) * h)
                rows.append(s / h ** n)
            tab = [rows]
            for j in range(1, levels):
                prev = tab[-1]
                tab.append([prev[i + 1] + (prev[i + 1] - prev[i]) / (4 ** j - 1) for i in range(len(prev) - 1)])
            return tab[-1][0]
        except (MathError, OverflowError, ValueError, ZeroDivisionError):
            h0 /= 2
    raise MathError("derivative could not be evaluated")


def _limit_side(g, x0, side, from_inf=False):
    """Limit of g(x0 + side*h) as h -> 0+ using Neville extrapolation in h."""
    hs = [0.05 / 2 ** k for k in range(6)]
    vals = []
    for h in hs:
        try:
            vals.append(g(x0 + side * h))
        except (MathError, OverflowError, ValueError, ZeroDivisionError):
            vals.append(None)
    good = [(h, v) for h, v in zip(hs, vals) if v is not None and math.isfinite(v)]
    if len(good) < 4:
        raise MathError("limit does not exist")
    mags = [abs(v) for h, v in good[-4:]]
    if all(mags[i + 1] > 1.25 * mags[i] for i in range(len(mags) - 1)):
        raise MathError("limit is infinite or does not exist")
    pts = good[-5:]
    T = [v for h, v in pts]
    hh = [h for h, v in pts]
    for j in range(1, len(T)):
        T = [(hh[i] * T[i + 1] - hh[i + j] * T[i]) / (hh[i] - hh[i + j]) for i in range(len(T) - 1)]
    est = T[0]
    lo, hi = min(v for h, v in pts), max(v for h, v in pts)
    span = hi - lo
    if not (lo - span <= est <= hi + span):
        est = pts[-1][1]
    return est


def _s5(name, desc, args, example, exact=True):
    return register(name, CAT_CALC, desc, args, exact=exact, example=example)


@_s5("deriv_n", "n-th derivative of 'expr' at x (n = 1..6; about 9 digits up to n=3, 7 at n=4, 6 at n=5, 4 at n=6): deriv_n('expr', n, x)", 3, "deriv_n('x^3', 2, 2) => 12")
def deriv_n(expr, n, x):
    n = _whole(n, "n")
    if not 1 <= n <= 6:
        raise MathError("n must be between 1 and 6")
    return ar_normalize(_snap8(_dn(_make_fn(expr), n, float(x))))


@_s5("partial_x", "Partial derivative with respect to x at (x, y): partial_x('expr', x, y)", 3, "partial_x('x^2*y', 3, 2) => 12")
def partial_x(expr, x, y):
    f = _make_fn(expr)
    return ar_normalize(_snap8(_dn(lambda t: f(t, float(y)), 1, float(x))))


@_s5("partial_y", "Partial derivative with respect to y at (x, y): partial_y('expr', x, y)", 3, "partial_y('x^2*y', 3, 2) => 9")
def partial_y(expr, x, y):
    f = _make_fn(expr)
    return ar_normalize(_snap8(_dn(lambda t: f(float(x), t), 1, float(y))))


@_s5("integrate_simpson", "Simpson's rule with n (even) steps: integrate_simpson('expr', a, b, n)", 4, "integrate_simpson('x^2', 0, 3, 10) => 9")
def integrate_simpson(expr, a, b, n):
    n = _whole(n, "n")
    if n < 2 or n % 2:
        raise MathError("n must be an even number of at least 2")
    f = _make_fn(expr)
    a, b = float(a), float(b)
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * f(a + i * h)
    return ar_normalize(total * h / 3)


@_s5("integrate_trap", "Trapezoid rule with n steps: integrate_trap('expr', a, b, n)", 4, "integrate_trap('x', 0, 4, 4) => 8")
def integrate_trap(expr, a, b, n):
    n = _whole(n, "n")
    if n < 1:
        raise MathError("n must be at least 1")
    f = _make_fn(expr)
    a, b = float(a), float(b)
    h = (b - a) / n
    total = (f(a) + f(b)) / 2
    for i in range(1, n):
        total += f(a + i * h)
    return ar_normalize(total * h)


@_s5("integrate_romberg", "Romberg integration of 'expr' from a to b: integrate_romberg('expr', a, b)", 3, "integrate_romberg('x^3', 0, 2) => 4")
def integrate_romberg(expr, a, b):
    f = _make_fn(expr)
    a, b = float(a), float(b)
    R = [[(b - a) * (f(a) + f(b)) / 2]]
    for k in range(1, 11):
        n = 2 ** k
        h = (b - a) / n
        mid = sum(f(a + (2 * i - 1) * h) for i in range(1, n // 2 + 1))
        row = [R[-1][0] / 2 + h * mid]
        for j in range(1, k + 1):
            row.append(row[j - 1] + (row[j - 1] - R[-1][j - 1]) / (4 ** j - 1))
        R.append(row)
        if k >= 3 and abs(row[-1] - R[-2][-1]) <= 1e-13 * max(1.0, abs(row[-1])):
            break
    return ar_normalize(_snap8(R[-1][-1]))


@_s5("integrate_to_inf", "Improper integral of 'expr' from a to infinity: integrate_to_inf('expr', a)", 2, "integrate_to_inf('exp(-x)', 0) => 1")
def integrate_to_inf(expr, a):
    f = _make_fn(expr)
    a = float(a)

    def g(t):                                   # x = a + t/(1-t), dx = dt/(1-t)^2
        x = a + t / (1 - t)
        return f(x) / (1 - t) ** 2
    total = _gl_int(g, 0.0, 1.0, panels=16, n=16)
    total2 = _gl_int(g, 0.0, 1.0, panels=32, n=16)
    if not (math.isfinite(total) and math.isfinite(total2)) or abs(total - total2) > 1e-6 * max(1.0, abs(total2)):
        raise MathError("integral does not converge")
    total = total2
    return ar_normalize(_snap8(total))


@_s5("double_integral", "Double integral of 'expr(x,y)' over the rectangle [xa,xb] x [ya,yb]: double_integral('expr', xa, xb, ya, yb)", 5, "double_integral('x*y', 0, 2, 0, 3) => 9")
def double_integral(expr, xa, xb, ya, yb):
    f = _make_fn(expr)
    xa, xb, ya, yb = float(xa), float(xb), float(ya), float(yb)
    def dbl(p):
        return _gl_int(lambda x: _gl_int(lambda y: f(x, y), ya, yb, panels=p, n=12), xa, xb, panels=p, n=12)
    coarse, total = dbl(2), dbl(4)
    if not (math.isfinite(total) and abs(total - coarse) <= 1e-3 * max(1.0, abs(total))):
        raise MathError("integral does not converge")
    return ar_normalize(_snap8(total))


@_s5("limit", "Two-sided limit of 'expr' as x approaches x0: limit('expr', x0)", 2, "limit('(x^2-1)/(x-1)', 1) => 2")
def limit(expr, x0):
    g = _make_fn(expr)
    x0 = float(x0)
    left = _limit_side(g, x0, -1)
    right = _limit_side(g, x0, +1)
    if abs(left - right) > 1e-6 * max(1.0, abs(left), abs(right)):
        raise MathError("the left and right limits differ")
    return ar_normalize(_snap8((left + right) / 2))


@_s5("limit_left", "Limit of 'expr' as x approaches x0 from the left: limit_left('expr', x0)", 2, "limit_left('abs(x)/x', 0) => -1")
def limit_left(expr, x0):
    return ar_normalize(_snap8(_limit_side(_make_fn(expr), float(x0), -1)))


@_s5("limit_right", "Limit of 'expr' as x approaches x0 from the right: limit_right('expr', x0)", 2, "limit_right('abs(x)/x', 0) => 1")
def limit_right(expr, x0):
    return ar_normalize(_snap8(_limit_side(_make_fn(expr), float(x0), +1)))


@_s5("limit_inf", "Limit of 'expr' as x grows without bound: limit_inf('expr')", 1, "limit_inf('(2*x+1)/(x+3)') => 2")
def limit_inf(expr):
    f = _make_fn(expr)
    return ar_normalize(_snap8(_limit_side(lambda t: f(1 / t), 0.0, +1)))


@_s5("sum_series", "Sum of 'expr' for x = a..b (whole numbers): sum_series('expr', a, b)", 3, "sum_series('x^2', 1, 4) => 30")
def sum_series(expr, a, b):
    a, b = _whole(a, "a"), _whole(b, "b")
    if b - a > 20000:
        raise MathError("too many terms (limit 20000)")
    f = _make_fn(expr, exact=True)
    total = 0
    for k in range(a, b + 1):
        total = ar_add(total, f(k))
    return total


@_s5("prod_series", "Product of 'expr' for x = a..b (whole numbers): prod_series('expr', a, b)", 3, "prod_series('x', 1, 5) => 120")
def prod_series(expr, a, b):
    a, b = _whole(a, "a"), _whole(b, "b")
    if b - a > 20000:
        raise MathError("too many terms (limit 20000)")
    f = _make_fn(expr, exact=True)
    total = 1
    for k in range(a, b + 1):
        total = ar_mul(total, f(k))
    return total


@_s5("taylor_value", "Taylor polynomial of degree n (0..6) about a, evaluated at x: taylor_value('expr', a, x, n)", 4, "taylor_value('x^2', 0, 3, 2) => 9")
def taylor_value(expr, a, x, n):
    n = _whole(n, "n")
    if not 0 <= n <= 6:
        raise MathError("degree must be between 0 and 6")
    f = _make_fn(expr)
    a, x = float(a), float(x)
    total = f(a)
    for k in range(1, n + 1):
        total += _dn(f, k, a) * (x - a) ** k / math.factorial(k)
    return ar_normalize(_snap8(total))


@_s5("curve_length", "Length of the curve y = expr(x) from a to b: curve_length('expr', a, b)", 3, "curve_length('x', 0, 3) => 4.24264069")
def curve_length(expr, a, b):
    f = _make_fn(expr)
    d = lambda t: _dn(f, 1, t, levels=4)
    total = _gl_conv(lambda t: math.sqrt(1 + d(t) ** 2), float(a), float(b), panels=4, n=10)
    return ar_normalize(_snap8(total))


@_s5("area_between", "Area between the curves y = f(x) and y = g(x) from a to b: area_between('f', 'g', a, b)", 4, "area_between('x', 'x^2', 0, 1) => 0.166666667")
def area_between(fe, ge, a, b):
    f, g = _make_fn(fe), _make_fn(ge)
    total = integrate_simpson_core(lambda t: abs(f(t) - g(t)), float(a), float(b), 2000)
    return ar_normalize(_snap8(total))


def integrate_simpson_core(f, a, b, n):
    h = (b - a) / n
    total = f(a) + f(b)
    for i in range(1, n):
        total += (4 if i % 2 else 2) * f(a + i * h)
    return total * h / 3


@_s5("vol_revolution_x", "Volume of y = expr(x) rotated about the x-axis from a to b: vol_revolution_x('expr', a, b)", 3, "vol_revolution_x('x', 0, 3) => 28.2743339")
def vol_revolution_x(expr, a, b):
    f = _make_fn(expr)
    return ar_normalize(_snap8(math.pi * _gl_conv(lambda t: f(t) ** 2, float(a), float(b))))


@_s5("mean_value", "Average value of 'expr' on [a, b]: mean_value('expr', a, b)", 3, "mean_value('x^2', 0, 3) => 3")
def mean_value(expr, a, b):
    a, b = float(a), float(b)
    if a == b:
        raise MathError("a and b must differ")
    return ar_normalize(_snap8(_gl_conv(_make_fn(expr), a, b) / (b - a)))


@_s5("curvature", "Curvature of y = expr(x) at x: curvature('expr', x)", 2, "curvature('x^2', 0) => 2")
def curvature(expr, x):
    f = _make_fn(expr)
    x = float(x)
    d1, d2 = _dn(f, 1, x), _dn(f, 2, x)
    return ar_normalize(_snap8(abs(d2) / (1 + d1 * d1) ** 1.5))


@_s5("critical_point", "Stationary point (f'(x) = 0) of 'expr' in [a, b]: critical_point('expr', a, b)", 3, "critical_point('(x-2)^2', 0, 5) => 2")
def critical_point(expr, a, b):
    f = _make_fn(expr)
    a, b = float(a), float(b)
    if a >= b:
        raise MathError("need a < b")
    d = lambda t: _dn(f, 1, t, levels=4)
    n = 200
    xs = [a + (b - a) * i / n for i in range(n + 1)]
    ds = [d(t) for t in xs]
    for i in range(n):
        lo, hi, dlo, dhi = xs[i], xs[i + 1], ds[i], ds[i + 1]
        if dlo == 0:
            return ar_normalize(_snap8(lo))
        if dlo * dhi < 0:
            for _ in range(60):
                mid = (lo + hi) / 2
                dm = d(mid)
                if dlo * dm <= 0:
                    hi, dhi = mid, dm
                else:
                    lo, dlo = mid, dm
            return ar_normalize(_snap8((lo + hi) / 2))
    if ds[-1] == 0:
        return ar_normalize(_snap8(xs[-1]))
    raise MathError("no stationary point in this interval")
