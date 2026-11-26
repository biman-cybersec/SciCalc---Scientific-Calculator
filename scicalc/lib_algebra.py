"""Sprint 3B: algebra, equations and sequences

Module 23 of 47.  Taken from lines 7030-7379 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_algebra"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import MathError
from .registry import register
from .arithmetic import ar_is_exact
from .lib_powers_rounding import _whole
from .lib_numerical import _eval_expr, root_bisection, root_newton

# --- SPRINT 3: PART B - ALGEBRA, EQUATIONS & SEQUENCES ---

CAT_ALGEBRA = "Algebra & Sequences"


def _alg_div(a, b, what="division"):
    """Exact division for int/Fraction, float division otherwise; zero -> Math ERROR."""
    if b == 0:
        raise MathError(what if what != "division" else "division by zero")
    if ar_is_exact(a) and ar_is_exact(b):
        return Fraction(a, b) if not isinstance(a, Fraction) and not isinstance(b, Fraction) \
            else Fraction(a) / Fraction(b)
    return a / b


def _alg_out(x):
    """Fractions with denominator 1 become ints so results print cleanly."""
    if isinstance(x, Fraction) and x.denominator == 1:
        return int(x)
    return x


def _alg_sqrt(d):
    """Exact square root when d is a perfect square (int/Fraction), float otherwise."""
    if d < 0:
        raise MathError("no real roots")
    if isinstance(d, int):
        r = math.isqrt(d)
        return r if r * r == d else math.sqrt(d)
    if isinstance(d, Fraction):
        n, m = math.isqrt(d.numerator), math.isqrt(d.denominator)
        if n * n == d.numerator and m * m == d.denominator:
            return Fraction(n, m)
    return math.sqrt(d)


def _alg_coeffs(coeffs, name):
    if len(coeffs) < 1:
        raise MathError(name + " needs at least one coefficient")
    return list(coeffs)


# ---- Quadratics & cubics ----------------------------------------------------------

@register("quad_disc", CAT_ALGEBRA, "Discriminant b^2 - 4ac of ax^2+bx+c: quad_disc(a, b, c)", 3, exact=True, example="quad_disc(1, -3, 2) => 1")
def quad_disc(a, b, c):
    return _alg_out(b * b - 4 * a * c)


def _quad_root(a, b, c, sign):
    if a == 0:
        raise MathError("a must not be 0")
    d = b * b - 4 * a * c
    return _alg_out(_alg_div(-b + sign * _alg_sqrt(d), 2 * a))


@register("quad_root1", CAT_ALGEBRA, "Real root (-b + sqrt(D)) / 2a of ax^2+bx+c: quad_root1(a, b, c)", 3, exact=True, example="quad_root1(1, -3, 2) => 2")
def quad_root1(a, b, c):
    return _quad_root(a, b, c, 1)


@register("quad_root2", CAT_ALGEBRA, "Real root (-b - sqrt(D)) / 2a of ax^2+bx+c: quad_root2(a, b, c)", 3, exact=True, example="quad_root2(1, -3, 2) => 1")
def quad_root2(a, b, c):
    return _quad_root(a, b, c, -1)


@register("quad_vertex_x", CAT_ALGEBRA, "x of the parabola vertex, -b/2a: quad_vertex_x(a, b, c)", 3, exact=True, example="quad_vertex_x(1, -4, 3) => 2")
def quad_vertex_x(a, b, c):
    return _alg_out(_alg_div(-b, 2 * a))


@register("quad_vertex_y", CAT_ALGEBRA, "y of the parabola vertex, c - b^2/4a: quad_vertex_y(a, b, c)", 3, exact=True, example="quad_vertex_y(1, -4, 3) => -1")
def quad_vertex_y(a, b, c):
    return _alg_out(c - _alg_div(b * b, 4 * a))


@register("cubic_disc", CAT_ALGEBRA, "Discriminant of ax^3+bx^2+cx+d: cubic_disc(a, b, c, d)", 4, exact=True, example="cubic_disc(1, -6, 11, -6) => 4")
def cubic_disc(a, b, c, d):
    return _alg_out(18 * a * b * c * d - 4 * b ** 3 * d + b * b * c * c - 4 * a * c ** 3 - 27 * a * a * d * d)


@register("cubic_real_root", CAT_ALGEBRA, "A real root of ax^3+bx^2+cx+d (the largest if there are three): cubic_real_root(a, b, c, d)", 4, example="cubic_real_root(1, 0, 0, -8) => 2")
def cubic_real_root(a, b, c, d):
    if a == 0:
        raise MathError("a must not be 0")
    p = (3 * a * c - b * b) / (3 * a * a)
    q = (2 * b ** 3 - 9 * a * b * c + 27 * a * a * d) / (27 * a ** 3)
    shift = b / (3 * a)
    inner = q * q / 4 + p ** 3 / 27
    if inner > 1e-14 or p == 0:
        s = math.sqrt(max(inner, 0.0))
        t = math.copysign(abs(-q / 2 + s) ** (1 / 3), -q / 2 + s) + \
            math.copysign(abs(-q / 2 - s) ** (1 / 3), -q / 2 - s)
    elif inner >= -1e-14 and abs(p) < 1e-300:
        t = 0.0
    else:
        m = 2 * math.sqrt(-p / 3)
        arg = max(-1.0, min(1.0, 3 * q / (p * m)))
        t = m * math.cos(math.acos(arg) / 3)       # k = 0 gives the largest root
    return t - shift


# ---- Linear systems ---------------------------------------------------------------

@register("lin2_x", CAT_ALGEBRA, "x in a1x+b1y=c1, a2x+b2y=c2: lin2_x(a1,b1,c1,a2,b2,c2)", 6, exact=True, example="lin2_x(1, 1, 3, 1, -1, 1) => 2")
def lin2_x(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    return _alg_out(_alg_div(c1 * b2 - c2 * b1, det, "singular system (no unique solution)"))


@register("lin2_y", CAT_ALGEBRA, "y in a1x+b1y=c1, a2x+b2y=c2: lin2_y(a1,b1,c1,a2,b2,c2)", 6, exact=True, example="lin2_y(1, 1, 3, 1, -1, 1) => 1")
def lin2_y(a1, b1, c1, a2, b2, c2):
    det = a1 * b2 - a2 * b1
    return _alg_out(_alg_div(a1 * c2 - a2 * c1, det, "singular system (no unique solution)"))


def _det3(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _lin3(col, v):
    rows = [list(v[0:4]), list(v[4:8]), list(v[8:12])]
    base = [r[:3] for r in rows]
    det = _det3(base)
    sub = [r[:3] for r in rows]
    for i in range(3):
        sub[i][col] = rows[i][3]
    return _alg_out(_alg_div(_det3(sub), det, "singular system (no unique solution)"))


_LIN3_DOC = "a1x+b1y+c1z=d1, a2x+b2y+c2z=d2, a3x+b3y+c3z=d3"
_LIN3_ARGS = "(a1,b1,c1,d1, a2,b2,c2,d2, a3,b3,c3,d3)"
_LIN3_EX = "(1, 1, 1, 6, 0, 2, 5, -4, 2, 5, -1, 27)"


@register("lin3_x", CAT_ALGEBRA, "x in " + _LIN3_DOC + ": lin3_x" + _LIN3_ARGS, 12, exact=True, example="lin3_x" + _LIN3_EX + " => 5")
def lin3_x(*v):
    return _lin3(0, v)


@register("lin3_y", CAT_ALGEBRA, "y in " + _LIN3_DOC + ": lin3_y" + _LIN3_ARGS, 12, exact=True, example="lin3_y" + _LIN3_EX + " => 3")
def lin3_y(*v):
    return _lin3(1, v)


@register("lin3_z", CAT_ALGEBRA, "z in " + _LIN3_DOC + ": lin3_z" + _LIN3_ARGS, 12, exact=True, example="lin3_z" + _LIN3_EX + " => -2")
def lin3_z(*v):
    return _lin3(2, v)


# ---- Lines & polynomials ----------------------------------------------------------

@register("line_slope", CAT_ALGEBRA, "Slope of the line through two points: line_slope(x1, y1, x2, y2)", 4, exact=True, example="line_slope(1, 2, 3, 6) => 2")
def line_slope(x1, y1, x2, y2):
    if x1 == x2:
        raise MathError("vertical line has no slope")
    return _alg_out(_alg_div(y2 - y1, x2 - x1))


@register("line_intercept", CAT_ALGEBRA, "y-intercept of the line through two points: line_intercept(x1, y1, x2, y2)", 4, exact=True, example="line_intercept(1, 2, 3, 6) => 0")
def line_intercept(x1, y1, x2, y2):
    m = line_slope(x1, y1, x2, y2)
    return _alg_out(y1 - m * x1)


@register("poly_eval", CAT_ALGEBRA, "Value of a polynomial at x, coefficients highest power first: poly_eval(x, an, ..., a0)", (2, None), exact=True, example="poly_eval(2, 1, 2, 3) => 11")
def poly_eval(x, *coeffs):
    result = 0
    for c in _alg_coeffs(coeffs, "poly_eval"):
        result = result * x + c
    return _alg_out(result)


@register("poly_deriv_eval", CAT_ALGEBRA, "Derivative of a polynomial at x: poly_deriv_eval(x, an, ..., a0)", (2, None), exact=True, example="poly_deriv_eval(2, 1, 2, 3) => 6")
def poly_deriv_eval(x, *coeffs):
    coeffs = _alg_coeffs(coeffs, "poly_deriv_eval")
    n = len(coeffs) - 1
    result = 0
    for i, c in enumerate(coeffs[:-1]):
        result = result * x + c * (n - i)
    return _alg_out(result)


@register("poly_integral", CAT_ALGEBRA, "Definite integral of a polynomial from a to b: poly_integral(a, b, an, ..., a0)", (3, None), exact=True, example="poly_integral(0, 1, 3, 2, 1) => 3")
def poly_integral(a, b, *coeffs):
    coeffs = _alg_coeffs(coeffs, "poly_integral")
    n = len(coeffs) - 1

    def antiderivative(x):
        total = 0
        for i, c in enumerate(coeffs):
            power = n - i + 1
            total += _alg_div(c * x ** power, power)
        return total
    return _alg_out(antiderivative(b) - antiderivative(a))


@register("synth_rem", CAT_ALGEBRA, "Remainder of the polynomial divided by (x - r), by synthetic division: synth_rem(r, an, ..., a0)", (2, None), exact=True, example="synth_rem(1, 1, 2, 3) => 6")
def synth_rem(r, *coeffs):
    carry = 0
    for c in _alg_coeffs(coeffs, "synth_rem"):
        carry = carry * r + c
    return _alg_out(carry)


# ---- Root finding -----------------------------------------------------------------

@register("bisect", CAT_ALGEBRA, "Root of f(x) in [a, b] by bisection: bisect('expr', a, b)", 3, exact=True, example="bisect('x^2-2', 0, 2) => 1.414213562")
def bisect(expr_str, a, b):
    return root_bisection(expr_str, a, b, 1e-13, 200)


@register("newton", CAT_ALGEBRA, "Root of f(x) by Newton's method from a start x0: newton('expr', x0)", 2, exact=True, example="newton('x^2-2', 1) => 1.414213562")
def newton(expr_str, x0):
    return root_newton(expr_str, x0, 1e-12, 200)


@register("secant", CAT_ALGEBRA, "Root of f(x) by the secant method from two starts: secant('expr', x0, x1)", 3, exact=True, example="secant('x^2-2', 1, 2) => 1.414213562")
def secant(expr_str, x0, x1):
    x0, x1 = float(x0), float(x1)
    f0, f1 = _eval_expr(expr_str, {"x": x0}), _eval_expr(expr_str, {"x": x1})
    for _ in range(200):
        if abs(f1) < 1e-13:
            return x1
        if f1 == f0:
            raise MathError("secant line is flat")
        x0, x1 = x1, x1 - f1 * (x1 - x0) / (f1 - f0)
        f0, f1 = f1, _eval_expr(expr_str, {"x": x1})
    return x1


@register("fixed_point", CAT_ALGEBRA, "Solve x = g(x) by fixed-point iteration: fixed_point('g(x)', x0)", 2, exact=True, example="fixed_point('cos(x)', 0.5) => 0.7390851332")
def fixed_point(expr_str, x0):
    x = float(x0)
    for _ in range(5000):
        nxt = _eval_expr(expr_str, {"x": x})
        if abs(nxt - x) < 1e-13:
            return nxt
        x = nxt
    raise MathError("iteration did not converge")


# ---- Advanced algebra -------------------------------------------------------------

@register("vieta_sum", CAT_ALGEBRA, "Sum of the roots of ax^2+bx+c, -b/a: vieta_sum(a, b, c)", 3, exact=True, example="vieta_sum(1, -5, 6) => 5")
def vieta_sum(a, b, c):
    return _alg_out(_alg_div(-b, a))


@register("vieta_prod", CAT_ALGEBRA, "Product of the roots of ax^2+bx+c, c/a: vieta_prod(a, b, c)", 3, exact=True, example="vieta_prod(1, -5, 6) => 6")
def vieta_prod(a, b, c):
    return _alg_out(_alg_div(c, a))


@register("solve_exp", CAT_ALGEBRA, "Solve a*b^x = c for x: solve_exp(a, b, c)", 3, example="solve_exp(2, 3, 18) => 2")
def solve_exp(a, b, c):
    if a == 0 or b <= 0 or b == 1 or c / a <= 0:
        raise MathError("no real solution")
    return math.log(c / a) / math.log(b)


@register("pf_a", CAT_ALGEBRA, "A in (px+q)/((x-r1)(x-r2)) = A/(x-r1) + B/(x-r2): pf_a(p, q, r1, r2)", 4, exact=True, example="pf_a(1, 1, 1, 2) => -2")
def pf_a(p, q, r1, r2):
    return _alg_out(_alg_div(p * r1 + q, r1 - r2, "roots must be different"))


@register("pf_b", CAT_ALGEBRA, "B in (px+q)/((x-r1)(x-r2)) = A/(x-r1) + B/(x-r2): pf_b(p, q, r1, r2)", 4, exact=True, example="pf_b(1, 1, 1, 2) => 3")
def pf_b(p, q, r1, r2):
    return _alg_out(_alg_div(p * r2 + q, r2 - r1, "roots must be different"))


@register("complete_sq_h", CAT_ALGEBRA, "h in ax^2+bx+c = a(x-h)^2 + k: complete_sq_h(a, b, c)", 3, exact=True, example="complete_sq_h(1, -4, 3) => 2")
def complete_sq_h(a, b, c):
    return _alg_out(_alg_div(-b, 2 * a))


@register("complete_sq_k", CAT_ALGEBRA, "k in ax^2+bx+c = a(x-h)^2 + k: complete_sq_k(a, b, c)", 3, exact=True, example="complete_sq_k(1, -4, 3) => -1")
def complete_sq_k(a, b, c):
    return _alg_out(c - _alg_div(b * b, 4 * a))


@register("binom_term", CAT_ALGEBRA, "Term k (from 0) of (a+b)^n: C(n,k) a^(n-k) b^k: binom_term(n, k, a, b)", 4, exact=True, example="binom_term(5, 2, 1, 2) => 40")
def binom_term(n, k, a, b):
    nv, kv = _whole(n, "binom_term"), _whole(k, "binom_term")
    if nv < 0 or kv < 0 or kv > nv:
        raise MathError("need 0 <= k <= n")
    return _alg_out(math.comb(nv, kv) * a ** (nv - kv) * b ** kv)


# ---- Progressions -----------------------------------------------------------------

@register("ap_nth", CAT_ALGEBRA, "n-th term of an arithmetic progression: ap_nth(a1, d, n)", 3, exact=True, example="ap_nth(2, 3, 10) => 29")
def ap_nth(a1, d, n):
    return _alg_out(a1 + (_whole(n, "ap_nth") - 1) * d)


@register("ap_sum", CAT_ALGEBRA, "Sum of the first n terms of an AP: ap_sum(a1, d, n)", 3, exact=True, example="ap_sum(2, 3, 10) => 155")
def ap_sum(a1, d, n):
    nv = _whole(n, "ap_sum")
    return _alg_out(_alg_div(nv * (2 * a1 + (nv - 1) * d), 2))


@register("ap_count", CAT_ALGEBRA, "Number of terms of an AP from a1 to last with step d: ap_count(a1, d, last)", 3, exact=True, example="ap_count(2, 3, 29) => 10")
def ap_count(a1, d, last):
    n = _alg_div(last - a1, d) + 1
    if n < 1 or (isinstance(n, Fraction) and n.denominator != 1) or (isinstance(n, float) and n != int(n)):
        raise MathError("last term is not in the progression")
    return int(n)


@register("gp_nth", CAT_ALGEBRA, "n-th term of a geometric progression: gp_nth(a1, r, n)", 3, exact=True, example="gp_nth(2, 3, 5) => 162")
def gp_nth(a1, r, n):
    nv = _whole(n, "gp_nth")
    if nv < 1:
        raise MathError("n must be >= 1")
    return _alg_out(a1 * Fraction(r) ** (nv - 1) if isinstance(r, (int, Fraction)) else a1 * r ** (nv - 1))


@register("gp_sum", CAT_ALGEBRA, "Sum of the first n terms of a GP: gp_sum(a1, r, n)", 3, exact=True, example="gp_sum(2, 3, 5) => 242")
def gp_sum(a1, r, n):
    nv = _whole(n, "gp_sum")
    if nv < 0:
        raise MathError("n must be >= 0")
    if r == 1:
        return _alg_out(a1 * nv)
    rr = Fraction(r) if isinstance(r, (int, Fraction)) else r
    return _alg_out(a1 * _alg_div(1 - rr ** nv, 1 - rr))


@register("gp_sum_inf", CAT_ALGEBRA, "Sum to infinity of a GP, a1/(1-r) for |r| < 1: gp_sum_inf(a1, r)", 2, exact=True, example="gp_sum_inf(1, 0.5) => 2")
def gp_sum_inf(a1, r):
    if abs(r) >= 1:
        raise MathError("series diverges for |r| >= 1")
    return _alg_out(_alg_div(a1, 1 - r))


@register("hp_nth", CAT_ALGEBRA, "n-th term of a harmonic progression from its first two terms: hp_nth(a1, a2, n)", 3, exact=True, example="hp_nth(6, 3, 3) => 2")
def hp_nth(a1, a2, n):
    if a1 == 0 or a2 == 0:
        raise MathError("terms must be non-zero")
    nv = _whole(n, "hp_nth")
    if nv < 1:
        raise MathError("n must be >= 1")
    inv1, inv2 = _alg_div(1, a1), _alg_div(1, a2)
    return _alg_out(_alg_div(1, inv1 + (nv - 1) * (inv2 - inv1), "term is undefined"))
