"""List/matrix statistics and solve_all

Module 43 of 47.  Taken from lines 14094-14401 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_type_extensions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import ArgumentError, CalcError, MathError
from .registry import register
from .arithmetic import Lst, Mat, ar_snap
from .lib_calculus import _make_fn
from .lib_lists_matrices import _L
from .lib_chemistry import _cn

#  TYPE EXTENSIONS : STATISTICS THAT RETURN LISTS, AND solve_all
#  zscores({..}), ranks, moving averages, five-number summary, regression fits and
#  covariance matrices give lists and matrices that feed straight into other functions:
#  poly_roots(polyfit(X, Y, 2)).   solve_all finds every real root of an expression in x
#  over an interval.  Quartiles and percentiles use linear interpolation, like q1 and
#  percentile.  Sample (n - 1) deviations are used throughout.
# ======================================================================================
_LSR = "Lists & Statistics"


def _lsr(name, desc, args, example):
    return register(name, _LSR, desc, args, example=example, lists=True, exact=True)


def _lsvec(L, minimum=1):
    out = [_cn(v) for v in _L(L)]
    if len(out) < minimum:
        raise MathError(f"this needs at least {minimum} value(s)")
    if any(not math.isfinite(v) for v in out):
        raise MathError("the list holds a value that is not finite")
    return out


def _lsint(x, lo, hi, what):
    x = _cn(x)
    if not math.isfinite(x) or x != int(x) or not lo <= x <= hi:
        raise MathError(f"{what} must be a whole number from {lo} to {hi}")
    return int(x)


def _lsmean(v):
    return math.fsum(v) / len(v)


def _lssd(v):
    m = _lsmean(v)
    return math.sqrt(math.fsum((x - m) ** 2 for x in v) / (len(v) - 1))


def _lspct(sorted_v, p):
    """Percentile p (0-100) by linear interpolation of a sorted list."""
    k = (len(sorted_v) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    if lo == hi:
        return sorted_v[lo]
    return sorted_v[lo] * (hi - k) + sorted_v[hi] * (k - lo)


@_lsr("zscores", "Standardise a list: (x - mean) / sample standard deviation", 1, "zscores({1, 2, 3}) => {-1, 0, 1}")
def zscores(L):
    v = _lsvec(L, 2)
    m, s = _lsmean(v), _lssd(v)
    if s == 0:
        raise MathError("all values are equal")
    return Lst([ar_snap((x - m) / s) for x in v])


@_lsr("ranks", "Ranks of the values, 1 = smallest, ties share the average rank", 1, "ranks({10, 30, 20, 20}) => {1, 4, 2.5, 2.5}")
def ranks(L):
    v = _lsvec(L)
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return Lst([ar_snap(x) for x in out])


@_lsr("minmax_list", "Scale a list into 0..1: (x - min) / (max - min)", 1, "minmax_list({2, 4, 6}) => {0, 0.5, 1}")
def minmax_list(L):
    v = _lsvec(L)
    lo, hi = min(v), max(v)
    if hi == lo:
        raise MathError("all values are equal")
    return Lst([ar_snap((x - lo) / (hi - lo)) for x in v])


@_lsr("proportions", "Each value as a share of the total: x / sum", 1, "proportions({1, 1, 2}) => {0.25, 0.25, 0.5}")
def proportions(L):
    v = _lsvec(L)
    t = math.fsum(v)
    if t == 0:
        raise MathError("the values add up to zero")
    return Lst([ar_snap(x / t) for x in v])


@_lsr("moving_avg", "Moving average over windows of k values: moving_avg(L, k)", 2, "moving_avg({1, 2, 3, 4, 5}, 3) => {2, 3, 4}")
def moving_avg(L, k):
    v = _lsvec(L)
    k = _lsint(k, 1, len(v), "the window")
    return Lst([ar_snap(math.fsum(v[i:i + k]) / k) for i in range(len(v) - k + 1)])


@_lsr("ewma", "Exponentially weighted moving average, s0 = x0, s = a x + (1 - a) s: ewma(L, alpha)", 2, "ewma({10, 20, 30}, 0.5) => {10, 15, 22.5}")
def ewma(L, alpha):
    v = _lsvec(L)
    a = _cn(alpha)
    if not 0 < a <= 1:
        raise MathError("alpha is in (0, 1]")
    out, s = [], v[0]
    for x in v:
        s = x if not out else a * x + (1 - a) * s
        out.append(ar_snap(s))
    return Lst(out)


@_lsr("quartiles", "The list {Q1, median, Q3} (linear interpolation)", 1, "quartiles({1, 2, 3, 4, 5, 6, 7, 8}) => {2.75, 4.5, 6.25}")
def quartiles(L):
    v = sorted(_lsvec(L))
    return Lst([ar_snap(_lspct(v, p)) for p in (25, 50, 75)])


@_lsr("five_number", "The list {min, Q1, median, Q3, max}", 1, "five_number({1, 2, 3, 4, 5, 6, 7, 8}) => {1, 2.75, 4.5, 6.25, 8}")
def five_number(L):
    v = sorted(_lsvec(L))
    return Lst([ar_snap(_lspct(v, p)) for p in (0, 25, 50, 75, 100)])


@_lsr("percentiles", "Several percentiles at once: percentiles(L, P) with P a list of values 0-100", 2, "percentiles({1, 2, 3, 4, 5}, {10, 50, 90}) => {1.4, 3, 4.6}")
def percentiles(L, P):
    v = sorted(_lsvec(L))
    ps = _lsvec(P)
    if any(not 0 <= p <= 100 for p in ps):
        raise MathError("percentiles are between 0 and 100")
    return Lst([ar_snap(_lspct(v, p)) for p in ps])


@_lsr("describe", "The list {n, mean, sample stdev, min, max}", 1, "describe({2, 4, 4, 4, 5, 5, 7, 9}) => {8, 5, 2.138089935, 2, 9}")
def describe(L):
    v = _lsvec(L, 2)
    return Lst([len(v), ar_snap(_lsmean(v)), ar_snap(_lssd(v)), ar_snap(min(v)), ar_snap(max(v))])


@_lsr("outlier_fences", "The list {Q1 - 1.5 IQR, Q3 + 1.5 IQR}: values outside are outliers", 1, "outlier_fences({1, 2, 3, 4, 5, 6, 7, 8}) => {-2.5, 11.5}")
def outlier_fences(L):
    v = sorted(_lsvec(L))
    q1, q3 = _lspct(v, 25), _lspct(v, 75)
    return Lst([ar_snap(q1 - 1.5 * (q3 - q1)), ar_snap(q3 + 1.5 * (q3 - q1))])


@_lsr("histogram_counts", "Counts in equal-width bins from min to max (last bin includes max): histogram_counts(L, bins)", 2,
      "histogram_counts({1, 2, 2, 3, 9, 10}, 3) => {4, 0, 2}")
def histogram_counts(L, bins):
    v = _lsvec(L)
    b = _lsint(bins, 1, 1000, "the number of bins")
    lo, hi = min(v), max(v)
    if hi == lo:
        raise MathError("all values are equal")
    width = (hi - lo) / b
    counts = [0] * b
    for x in v:
        counts[min(b - 1, int((x - lo) / width))] += 1
    return Lst(counts)


@_lsr("linreg_fit", "Least-squares line through (X, Y): the list {slope, intercept, r^2}", 2, "linreg_fit({1, 2, 3}, {2, 4, 6}) => {2, 0, 1}")
def linreg_fit(X, Y):
    x, y = _lsvec(X, 2), _lsvec(Y, 2)
    if len(x) != len(y):
        raise MathError("lists must have the same size")
    mx, my = _lsmean(x), _lsmean(y)
    sxx = math.fsum((a - mx) ** 2 for a in x)
    sxy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y))
    syy = math.fsum((b - my) ** 2 for b in y)
    if sxx == 0:
        raise MathError("all x values are equal")
    slope = sxy / sxx
    r2 = 1.0 if syy == 0 else sxy * sxy / (sxx * syy)
    return Lst([ar_snap(slope), ar_snap(my - slope * mx), ar_snap(r2)])


@_lsr("polyfit", "Least-squares polynomial through (X, Y): coefficients, highest power first (feeds poly_roots): polyfit(X, Y, degree)", 3,
      "polyfit({0, 1, 2, 3}, {1, 2, 5, 10}, 2) => {1, 0, 1}")
def polyfit(X, Y, deg):
    x, y = _lsvec(X, 2), _lsvec(Y, 2)
    if len(x) != len(y):
        raise MathError("lists must have the same size")
    d = _lsint(deg, 0, 8, "the degree")
    if len(set(x)) <= d:
        raise MathError("not enough different x values for this degree")
    fx, fy = [Fraction(v) for v in x], [Fraction(v) for v in y]
    n = d + 1
    A = [[sum(xi ** (i + j) for xi in fx) for j in range(n)] + [sum(yi * xi ** i for xi, yi in zip(fx, fy))] for i in range(n)]
    for c in range(n):                                  # exact Gauss-Jordan on the normal equations
        piv = next((r for r in range(c, n) if A[r][c] != 0), None)
        if piv is None:
            raise MathError("the fit is singular")
        A[c], A[piv] = A[piv], A[c]
        inv = 1 / A[c][c]
        A[c] = [v * inv for v in A[c]]  # pyright: ignore[reportArgumentType, reportCallIssue]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return Lst([ar_snap(float(A[i][n])) for i in range(n - 1, -1, -1)])


def _lscols(M):
    if not isinstance(M, Mat):
        raise ArgumentError("this needs a matrix whose columns are the variables")
    rows = [[_cn(v) for v in r] for r in M]
    if len(rows) < 2:
        raise MathError("this needs at least 2 observations (rows)")
    return [[r[j] for r in rows] for j in range(len(rows[0]))]


@_lsr("cov_matrix", "Sample covariance matrix of the columns of a matrix (rows = observations)", 1, "cov_matrix({{1, 2}, {2, 4}, {3, 6}}) => {{1, 2}, {2, 4}}")
def cov_matrix(M):
    cols = _lscols(M)
    means = [_lsmean(c) for c in cols]
    n = len(cols[0])
    return Mat(tuple(Lst(ar_snap(math.fsum((a - means[i]) * (b - means[j]) for a, b in zip(cols[i], cols[j])) / (n - 1))
                         for j in range(len(cols))) for i in range(len(cols))))


@_lsr("corr_matrix", "Correlation matrix of the columns of a matrix (rows = observations)", 1, "corr_matrix({{1, 2}, {2, 4}, {3, 7}}) => {{1, 0.9933992678}, {0.9933992678, 1}}")
def corr_matrix(M):
    cols = _lscols(M)
    means = [_lsmean(c) for c in cols]
    n = len(cols[0])
    cov = [[math.fsum((a - means[i]) * (b - means[j]) for a, b in zip(cols[i], cols[j])) / (n - 1) for j in range(len(cols))] for i in range(len(cols))]
    if any(cov[i][i] == 0 for i in range(len(cols))):
        raise MathError("a column is constant")
    return Mat(tuple(Lst(ar_snap(1.0 if i == j else max(-1.0, min(1.0, cov[i][j] / math.sqrt(cov[i][i] * cov[j][j]))))
                         for j in range(len(cols))) for i in range(len(cols))))


@register("solve_all", "Equations & Tables",
          "Every real root of an expression in x on [lo, hi], as a list: solve_all('x^3-6x^2+11x-6', 0, 5)", args=3, exact=True,
          example="solve_all('x^3 - 6x^2 + 11x - 6', 0, 5) => {1, 2, 3}")
def solve_all(expr, lo, hi):
    f = _make_fn(expr)
    lo, hi = _cn(lo), _cn(hi)
    if not (math.isfinite(lo) and math.isfinite(hi)) or lo >= hi:
        raise MathError("the interval needs lo < hi")
    n = 4000
    xs = [lo + (hi - lo) * k / n for k in range(n + 1)]
    ys = []
    for x in xs:
        try:
            ys.append(f(x))
        except CalcError:
            ys.append(math.nan)
    scale = max([abs(y) for y in ys if math.isfinite(y)] or [1.0])
    roots = []

    def add(r):
        if not any(abs(r - q) <= 1e-9 * max(1.0, abs(r)) for q in roots):
            roots.append(r)

    for k in range(n):
        a, b, fa, fb = xs[k], xs[k + 1], ys[k], ys[k + 1]
        if not (math.isfinite(fa) and math.isfinite(fb)):
            continue
        if fa == 0:
            add(a)
        elif fa * fb < 0:
            for _ in range(80):
                m = (a + b) / 2
                try:
                    fm = f(m)
                except CalcError:
                    break
                if fm == 0:
                    a = b = m
                    break
                if fa * fm < 0:
                    b, fb = m, fm
                else:
                    a, fa = m, fm
            r = (a + b) / 2
            try:
                if abs(f(r)) <= 1e-6 * max(1.0, scale) and abs(f(r)) <= max(abs(fa), abs(fb), 1e-6):
                    add(r)
            except CalcError:
                pass
    if math.isfinite(ys[n]) and ys[n] == 0:
        add(xs[n])
    for k in range(1, n):                               # touching roots (double roots): a dip of |f| to zero without a sign change
        y0, y1, y2 = ys[k - 1], ys[k], ys[k + 1]
        if all(math.isfinite(v) for v in (y0, y1, y2)) and abs(y1) <= abs(y0) and abs(y1) <= abs(y2) and y0 * y2 >= 0 and y1 != 0:
            a, b = xs[k - 1], xs[k + 1]
            try:
                for _ in range(100):
                    m1, m2 = a + (b - a) / 3, b - (b - a) / 3
                    if abs(f(m1)) < abs(f(m2)):
                        b = m2
                    else:
                        a = m1
                r = (a + b) / 2
                if abs(f(r)) <= 1e-12 * max(1.0, scale):
                    add(r)
            except CalcError:
                pass
        if len(roots) > 200:
            raise MathError("too many roots in this interval")
    if not roots:
        raise MathError("no root found in the interval")
    roots.sort()
    return Lst([ar_snap(float(f"{r:.12g}")) for r in roots])


# ======================================================================================
