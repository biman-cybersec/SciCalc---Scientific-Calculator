"""Equation and table modes

Module 36 of 47.  Taken from lines 12153-12494 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_equations_tables"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import ArgumentError, CalcError, MathError
from .registry import register
from .arithmetic import Lst, Mat, _box_binary, _mat_inverse, ar_mul, ar_sub
from .lib_calculus import _make_fn
from .lib_vectors_matrices import _det, _fr, _num
from .lib_lists_matrices import _L, _M, _S, _qm
from .lib_chemistry import _cn

# ======================================================================================
#  EQUATION AND TABLE MODES (7)
#  simul(M)            simultaneous linear equations from the augmented matrix, 2 to 30 unknowns
#  poly_roots(L)       all roots (real and complex) of a polynomial, coefficients highest power
#                      first, degree 1 to 10; roots come as a list, reals first in ascending
#                      order, then complex ones by real part (repeated roots are found exactly
#                      for rational coefficients through a square-free factorisation)
#  poly_from_roots(L)  the monic polynomial with the given roots (inverse of poly_roots)
#  poly_ineq(L, op)    solution set of a polynomial inequality p(x) > 0, >=, <, <= as intervals
#  nsolve2(f, g, x0, y0) two nonlinear equations f(x,y)=0, g(x,y)=0 by Newton's method
#  table1(f, a, b, step) / table2(f, g, a, b, step)  Casio TABLE mode as a matrix of rows
#                      {x, f(x)} or {x, f(x), g(x)}; the command-line `table` prints it.
# ======================================================================================
_EQN = "Equations & Tables"


def _ef(name, desc, args, example, lists=False):
    return register(name, _EQN, desc, args, exact=True, lists=lists, example=example)


def _peval(c, x):
    r = 0
    for k in c:
        r = r * x + k
    return r


def _coeffs(L, max_deg=10):
    L = _L(L)
    if any(isinstance(v, complex) for v in L):
        raise ArgumentError("the coefficients must be real numbers")
    c = [float(v) for v in L]
    if len(c) < 2 or len(c) > max_deg + 1:
        raise MathError(f"the degree must be between 1 and {max_deg}")
    if c[0] == 0:
        raise MathError("the leading coefficient must not be 0")
    if not all(math.isfinite(v) for v in c):
        raise MathError("coefficients must be finite")
    return c


def _pnorm(a):
    while len(a) > 1 and a[0] == 0:
        a = a[1:]
    return a


def _pdivmod(a, b):
    a, b = list(a), _pnorm(b)
    steps = len(a) - len(b) + 1
    if steps <= 0:
        return [Fraction(0)], _pnorm(a)
    q = []
    for _ in range(steps):
        f = a[0] / b[0]
        q.append(f)
        for i in range(len(b)):
            a[i] -= f * b[i]
        a = a[1:]
    return q, _pnorm(a or [Fraction(0)])


def _pder(a):
    n = len(a) - 1
    return [a[k] * (n - k) for k in range(n)] or [Fraction(0)]


def _pgcd(a, b):
    a, b = _pnorm(a), _pnorm(b)
    while any(b):
        a, b = b, _pdivmod(a, b)[1]
    return [v / a[0] for v in a]


def _psub(a, b):
    n = max(len(a), len(b))
    a = [Fraction(0)] * (n - len(a)) + list(a)
    b = [Fraction(0)] * (n - len(b)) + list(b)
    return _pnorm([x - y for x, y in zip(a, b)])


def _squarefree_factors(p):
    """Yun's algorithm (exact, rational coefficients): [(multiplicity, squarefree factor), ...]."""
    p = _pnorm(p)
    g = _pgcd(p, _pder(p))
    b = _pdivmod(p, g)[0]
    c = _pdivmod(_pder(p), g)[0]
    d = _psub(c, _pder(b))
    out, i = [], 1
    while len(b) > 1 and i <= 12:
        a = _pgcd(b, d)
        b = _pdivmod(b, a)[0]
        c = _pdivmod(d, a)[0]
        d = _psub(c, _pder(b))
        if len(a) > 1:
            out.append((i, a))
        i += 1
    return out


def _roots_of(c):
    """Roots of c[0] x^n + ... + c[n] (c[0] != 0) as complex numbers; repeated roots are found
    exactly through an exact square-free factorisation of the (decimal) coefficients."""
    n = len(c) - 1
    if n <= 2:
        return _simple_roots(c)
    out = []
    for mult, fac in _squarefree_factors([_fr(v) for v in c]):
        out.extend(_simple_roots([float(v) for v in fac]) * mult)
    return out


def _simple_roots(c):
    n = len(c) - 1
    if n == 1:
        return [complex(-c[1] / c[0])]
    if n == 2:
        a, b, k = c
        disc = b * b - 4 * a * k
        if disc >= 0:
            q = -0.5 * (b + math.copysign(math.sqrt(disc), b))
            r1 = q / a
            r2 = k / q if q != 0 else r1
            return [complex(r1), complex(r2)]
        s = math.sqrt(-disc) / (2 * a)
        return [complex(-b / (2 * a), -abs(s)), complex(-b / (2 * a), abs(s))]
    a = [v / c[0] for v in c]
    while a[-1] == 0:                                   # zero roots, split off
        a.pop()
        n -= 1
        if n == 0:
            return [0j] * (len(c) - 1)
    zeros = len(c) - 1 - n
    if n == 1:
        return [complex(-a[1])] + [0j] * zeros
    radius = 1 + max(abs(v) for v in a[1:])
    z = [radius * 0.5 * (0.4 + 0.9j) ** k for k in range(n)]
    for _ in range(4000):
        biggest = 0.0
        for i in range(n):
            den = 1
            for j in range(n):
                if j != i:
                    den *= z[i] - z[j]
            if den == 0:
                z[i] += 1e-8
                continue
            d = _peval(a, z[i]) / den
            z[i] -= d
            biggest = max(biggest, abs(d))
        if biggest < 1e-15 * max(1.0, max(abs(v) for v in z)):
            break
    da = [a[k] * (n - k) for k in range(n)]
    for i in range(n):                                  # Newton polish, accepted only when it helps
        for _ in range(6):
            p, dp = _peval(a, z[i]), _peval(da, z[i])
            if dp == 0:
                break
            nz = z[i] - p / dp
            if abs(_peval(a, nz)) < abs(p):
                z[i] = nz
            else:
                break
    return z + [0j] * zeros


def _clean_roots(zs):
    reals, cx = [], []
    for z in zs:
        if abs(z.imag) <= 1e-9 * max(1.0, abs(z.real)):
            reals.append(z.real)
        else:
            cx.append(z)
    reals.sort()
    cx.sort(key=lambda z: (round(z.real, 8), z.imag))
    return reals + cx


@_ef("simul", "Solve simultaneous linear equations from the augmented matrix {{a1, b1, c1}, {a2, b2, c2}} (n equations, n unknowns, n+1 columns): simul(M)", 1, "simul({{2, 1, 3}, {1, 3, 5}}) => {0.8, 1.4}", lists=True)
def simul(M):
    M = _M(M)
    n = len(M)
    if n < 2 or n > 30 or len(M[0]) != n + 1:
        raise MathError("need 2 to 30 equations with n unknowns each (n+1 columns)")
    if any(isinstance(v, complex) for row in M for v in row):
        raise ArgumentError("the coefficients must be real numbers")
    A = Mat(tuple(row[:n]) for row in M)
    b = Lst(row[n] for row in M)
    if _det(_qm(A)) == 0:
        raise MathError("no unique solution")
    return _box_binary("*", _mat_inverse(A), b)


@_ef("poly_roots", "All roots of a polynomial, coefficients highest power first, degree up to 10: poly_roots({1, -6, 11, -6})", 1, "poly_roots({1, -6, 11, -6}) => {1, 2, 3}", lists=True)
def poly_roots(L):
    return Lst(complex(z) if isinstance(z, complex) else z for z in _clean_roots(_roots_of(_coeffs(L))))


@_ef("poly_from_roots", "Monic polynomial coefficients (highest power first) from a list of roots: poly_from_roots({1, 2, 3})", 1, "poly_from_roots({1, 2, 3}) => {1, -6, 11, -6}", lists=True)
def poly_from_roots(L):
    L = _L(L)
    if len(L) > 30:
        raise MathError("at most 30 roots")
    c = [1]
    for r in L:
        nxt = c + [0]
        for i in range(len(c)):
            nxt[i + 1] = ar_sub(nxt[i + 1], ar_mul(r, c[i]))  # pyright: ignore[reportArgumentType, reportCallIssue]
        c = nxt
    return Lst(c)


def _g(x):
    return f"{x:.10g}"


@_ef("poly_ineq", "Solution set of p(x) > 0, >=, < or <= for a real polynomial (coefficients highest power first, degree up to 10) as intervals: poly_ineq({1, -3, 2}, '>')", 2, "poly_ineq({1, -3, 2}, '>') => (-inf, 1) U (2, inf)", lists=True)
def poly_ineq(L, op):
    c = _coeffs(L)
    if not isinstance(op, str) or op.strip() not in (">", ">=", "<", "<=", "≥", "≤"):
        raise ArgumentError("the operator must be '>', '>=', '<' or '<=' in quotes")
    op = {"≥": ">=", "≤": "<="}.get(op.strip(), op.strip())
    want_pos, closed = op[0] == ">", len(op) == 2
    rs = []
    for r in _clean_roots(_roots_of(c)):
        if isinstance(r, float):
            if rs and abs(r - rs[-1]) <= 1e-7 * max(1.0, abs(r)):
                rs[-1] = (rs[-1] + r) / 2
            else:
                rs.append(r)
    # pieces: open intervals between breakpoints, then the breakpoints themselves
    edges = [-math.inf] + rs + [math.inf]
    pieces = []                                         # (lo, hi, is_point, satisfied)
    for k in range(len(edges) - 1):
        lo, hi = edges[k], edges[k + 1]
        if lo == -math.inf and hi == math.inf:
            mid = 0.0
        elif lo == -math.inf:
            mid = hi - 1 - abs(hi)
        elif hi == math.inf:
            mid = lo + 1 + abs(lo)
        else:
            mid = (lo + hi) / 2
        v = _peval(c, mid)
        pieces.append([lo, hi, False, v > 0 if want_pos else v < 0])
        if hi != math.inf:
            pieces.append([hi, hi, True, closed])
    out, cur = [], None
    for lo, hi, is_pt, ok in pieces:
        if ok:
            if cur is None:
                cur = [lo, hi, is_pt, is_pt]            # closed at the left end when it starts with a point
            else:
                cur[1] = hi
                cur[3] = is_pt
        elif cur is not None:
            out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    if not out:
        return "no solution"
    if len(out) == 1 and out[0][0] == -math.inf and out[0][1] == math.inf:
        return "all real numbers"
    parts = []
    for lo, hi, lc, hc in out:
        if lo == hi:
            parts.append("{" + _g(lo) + "}")
        else:
            left = "(-inf" if lo == -math.inf else ("[" if lc else "(") + _g(lo)
            right = "inf)" if hi == math.inf else _g(hi) + ("]" if hc else ")")
            parts.append(f"{left}, {right}")
    return " U ".join(parts)


@_ef("nsolve2", "Solve f(x, y) = 0 and g(x, y) = 0 near a starting point by Newton's method: nsolve2('x^2+y^2-4', 'x-y', 1, 1)", 4, "nsolve2('x^2+y^2-4', 'x-y', 1, 1) => {1.414213562, 1.414213562}")
def nsolve2(f, g, x0, y0):
    F, G = _make_fn(f), _make_fn(g)
    x, y = _cn(x0), _cn(y0)

    def res(x, y):
        return F(x, y), G(x, y)
    for _ in range(200):
        f0, g0 = res(x, y)
        norm = math.hypot(f0, g0)
        if norm < 1e-13:
            break
        h = 1e-6 * max(1.0, abs(x)), 1e-6 * max(1.0, abs(y))
        fx = (F(x + h[0], y) - F(x - h[0], y)) / (2 * h[0])
        fy = (F(x, y + h[1]) - F(x, y - h[1])) / (2 * h[1])
        gx = (G(x + h[0], y) - G(x - h[0], y)) / (2 * h[0])
        gy = (G(x, y + h[1]) - G(x, y - h[1])) / (2 * h[1])
        det = fx * gy - fy * gx
        if det == 0 or not math.isfinite(det):
            raise MathError("the Jacobian is singular here; try another starting point")
        dx, dy = (f0 * gy - g0 * fy) / det, (g0 * fx - f0 * gx) / det
        t = 1.0
        while t > 1e-6:                                 # backtrack until the residual shrinks
            nx, ny = x - t * dx, y - t * dy
            try:
                if math.hypot(*res(nx, ny)) < norm:
                    break
            except CalcError:
                pass
            t /= 2
        else:
            raise MathError("no solution found from this starting point")
        x, y = nx, ny
    else:
        raise MathError("no solution found from this starting point")
    if max(abs(x), abs(y)) > 1e12:
        raise MathError("no solution found from this starting point")
    return Lst((x, y))


_TABLE_ROWS = 500


def _table_x(a, b, step):
    a, b, step = _fr(_S(a)), _fr(_S(b)), _fr(_S(step))
    if step == 0 or (b - a) * step < 0:
        raise MathError("the step must lead from start to end")
    count = int((b - a) / step) + 1
    if count > _TABLE_ROWS:
        raise MathError(f"a table has at most {_TABLE_ROWS} rows")
    return [_num(a + k * step) for k in range(count)]


@_ef("table1", "TABLE mode: rows {x, f(x)} for x from start to end in steps (up to 500 rows): table1('x^2', 0, 3, 1)", 4, "table1('x^2', 0, 2, 1) => {{0, 0}, {1, 1}, {2, 4}}")
def table1(f, a, b, step):
    F = _make_fn(f)
    xs = _table_x(a, b, step)
    return Mat((x, F(float(x))) for x in xs)


@_ef("table2", "TABLE mode with two functions: rows {x, f(x), g(x)}: table2('x^2', 'x^3', 0, 2, 1)", 5, "table2('x^2', 'x^3', 0, 2, 1) => {{0, 0, 0}, {1, 1, 1}, {2, 4, 8}}")
def table2(f, g, a, b, step):
    F, G = _make_fn(f), _make_fn(g)
    xs = _table_x(a, b, step)
    return Mat((x, F(float(x)), G(float(x))) for x in xs)
