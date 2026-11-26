"""Sprint 8: list and matrix types

Module 33 of 47.  Taken from lines 11220-11612 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_lists_matrices"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import ArgumentError, MathError
from .registry import register
from .arithmetic import (
    Lst,
    MAX_BITS,
    MAX_ELEMENTS,
    Mat,
    _box_binary,
    _dot,
    _is_scalar,
    _mat_inverse,
    _mat_power,
    _mat_product,
    ar_add,
    ar_is_exact,
    ar_mul,
    ar_sub,
)
from .lib_powers_rounding import _whole
from .lib_calculus import _make_fn
from .lib_vectors_matrices import _det, _fr, _num, _rank

# ======================================================================================
#  SPRINT 8 : LIST AND MATRIX TYPES
#  A list is typed {1, 2, 3}; a matrix is a list of equal-length lists {{1, 2}, {3, 4}}.
#  (Round brackets and [ ] stay ordinary grouping.)  Arithmetic works element by element:
#  {1,2,3}*2, {1,2}+{10,20}, sin({30,90}).  Matrix*matrix, matrix*vector, M^n (also M^-1,
#  M⁻¹) are real matrix algebra.  Any function that takes "many numbers" (mean, stdev, irr,
#  payback, npv, max, ...) accepts a list in their place: mean({1,2,3}), irr({-100,110}).
#  Other scalar functions work element by element; if the argument count does not fit, the
#  elements are spliced in, so det3({{1,2,3},{4,5,6},{7,8,9}}) works.
#  Positions are 1-based.  Integer/fraction input stays exact.  Results are stored with
#  ->  like numbers:  {1,2,3} -> A.
# ======================================================================================
_LST = "Lists"
_MTX = "Matrices"


def _lf(name, desc, args, example, cat=_LST):
    return register(name, cat, desc, args, exact=True, lists=True, example=example)


def _L(x):
    if not isinstance(x, Lst):
        raise ArgumentError("this needs a list such as {1, 2, 3}")
    return x


def _M(x):
    if not isinstance(x, Mat):
        raise ArgumentError("this needs a matrix such as {{1, 2}, {3, 4}}")
    return x


def _S(x):
    if not _is_scalar(x):
        raise ArgumentError("this needs a number")
    return x


def _lpos(i, n, what="position"):
    i = _whole(_S(i), what)
    if not 1 <= i <= n:
        raise MathError(f"{what} must be between 1 and {n}")
    return i


def _size(v, hi, what):
    v = _whole(_S(v), what)
    if not 1 <= v <= hi:
        raise MathError(f"{what} must be between 1 and {hi}")
    return v


def _qm(M):
    return [[_fr(v) for v in row] for row in M]


def _exact_m(M):
    return all(ar_is_exact(v) for row in M for v in row)


def _qout(q, exact):
    return _num(q) if exact else float(q)


def _sq(M, cap=30):
    M = _M(M)
    if len(M) != len(M[0]) or len(M) > cap:
        raise MathError(f"needs a square matrix of size at most {cap}")
    return M


# ---------- lists ----------
@_lf("list_len", "Number of elements in a list or matrix: list_len({4, 5, 6})", 1, "list_len({4, 5, 6}) => 3")
def list_len(L):
    if isinstance(L, Mat):
        return len(L) * len(L[0])
    return len(_L(L))


@_lf("list_get", "Element at a 1-based position: list_get({10, 20, 30}, 2)", 2, "list_get({10, 20, 30}, 2) => 20")
def list_get(L, i):
    L = _L(L)
    return L[_lpos(i, len(L)) - 1]


@_lf("list_slice", "Elements from position i to j (1-based, inclusive): list_slice(L, i, j)", 3, "list_slice({1, 2, 3, 4, 5}, 2, 4) => {2, 3, 4}")
def list_slice(L, i, j):
    L = _L(L)
    i, j = _lpos(i, len(L), "start"), _lpos(j, len(L), "end")
    if i > j:
        raise MathError("start must not be after end")
    return Lst(L[i - 1:j])


@_lf("list_sort", "Sort a list ascending (or descending when the second argument is not 0): list_sort(L [, desc])", (1, 2), "list_sort({3, 1, 2}) => {1, 2, 3}")
def list_sort(L, desc=0):
    return Lst(sorted(_L(L), reverse=_S(desc) != 0))


@_lf("list_rev", "Reverse a list: list_rev(L)", 1, "list_rev({1, 2, 3}) => {3, 2, 1}")
def list_rev(L):
    return Lst(reversed(_L(L)))


@_lf("list_sum", "Sum of the elements: list_sum(L)", 1, "list_sum({1, 2, 3, 4}) => 10")
def list_sum(L):
    t = 0
    for v in _L(L):
        t = ar_add(t, v)
    return t


def _guard(v):
    if isinstance(v, int) and v.bit_length() > MAX_BITS:
        raise MathError("result too large")
    return v


@_lf("list_prod", "Product of the elements: list_prod(L)", 1, "list_prod({1, 2, 3, 4}) => 24")
def list_prod(L):
    t = 1
    for v in _L(L):
        t = _guard(ar_mul(t, v))
    return t


@_lf("list_cumsum", "Running totals: list_cumsum(L)", 1, "list_cumsum({1, 2, 3, 4}) => {1, 3, 6, 10}")
def list_cumsum(L):
    out, t = [], 0
    for v in _L(L):
        t = ar_add(t, v)
        out.append(t)
    return Lst(out)


@_lf("list_cumprod", "Running products: list_cumprod(L)", 1, "list_cumprod({1, 2, 3, 4}) => {1, 2, 6, 24}")
def list_cumprod(L):
    out, t = [], 1
    for v in _L(L):
        t = _guard(ar_mul(t, v))
        out.append(t)
    return Lst(out)


@_lf("list_diff", "Differences between neighbours (one element shorter): list_diff(L)", 1, "list_diff({1, 4, 9, 16}) => {3, 5, 7}")
def list_diff(L):
    L = _L(L)
    if len(L) < 2:
        raise MathError("needs at least two elements")
    return Lst(ar_sub(b, a) for a, b in zip(L, L[1:]))


@_lf("list_seq", "The list {1, 2, ..., n}: list_seq(n)", 1, "list_seq(5) => {1, 2, 3, 4, 5}")
def list_seq(n):
    return Lst(range(1, _size(n, MAX_ELEMENTS, "n") + 1))


@_lf("list_range", "From a to b (inclusive) in steps: list_range(a, b [, step])", (2, 3), "list_range(1, 2, 0.25) => {1, 1.25, 1.5, 1.75, 2}")
def list_range(a, b, step=1):
    a, b, step = _fr(_S(a)), _fr(_S(b)), _fr(_S(step))
    if step == 0 or (b - a) * step < 0:
        raise MathError("the step must lead from a towards b")
    count = int((b - a) / step) + 1
    if count > MAX_ELEMENTS:
        raise MathError("list too long")
    return Lst(_num(a + k * step) for k in range(count))


@_lf("list_linspace", "n evenly spaced values from a to b inclusive: list_linspace(a, b, n)", 3, "list_linspace(0, 1, 5) => {0, 0.25, 0.5, 0.75, 1}")
def list_linspace(a, b, n):
    n = _size(n, MAX_ELEMENTS, "n")
    if n < 2:
        raise MathError("n must be at least 2")
    a, b = _fr(_S(a)), _fr(_S(b))
    return Lst(_num(a + (b - a) * k / (n - 1)) for k in range(n))


@_lf("list_concat", "Join two lists: list_concat(A, B)", 2, "list_concat({1, 2}, {3}) => {1, 2, 3}")
def list_concat(A, B):
    A, B = _L(A), _L(B)
    if len(A) + len(B) > MAX_ELEMENTS:
        raise MathError("list too long")
    return Lst(A + B)


@_lf("list_append", "Add a value at the end: list_append(L, v)", 2, "list_append({1, 2}, 3) => {1, 2, 3}")
def list_append(L, v):
    L = _L(L)
    if len(L) >= MAX_ELEMENTS:
        raise MathError("list too long")
    return Lst(L + (_S(v),))


@_lf("list_fill", "A list of n copies of a value: list_fill(n, v)", 2, "list_fill(3, 7) => {7, 7, 7}")
def list_fill(n, v):
    return Lst([_S(v)] * _size(n, MAX_ELEMENTS, "n"))


@_lf("list_dot", "Dot product of two lists of the same length: list_dot(A, B)", 2, "list_dot({1, 2, 3}, {4, 5, 6}) => 32")
def list_dot(A, B):
    A, B = _L(A), _L(B)
    if len(A) != len(B):
        raise MathError("lists must have the same size")
    return _dot(A, B)


@_lf("list_map", "Apply an expression in x to every element: list_map('x^2+1', L)", 2, "list_map('x^2 + 1', {1, 2, 3}) => {2, 5, 10}")
def list_map(expr, L):
    L = _L(L)
    f = _make_fn(expr)
    return Lst(f(float(v)) for v in L)


@_lf("list_argmax", "Position (1-based) of the largest element, first one if tied: list_argmax(L)", 1, "list_argmax({3, 9, 2, 9}) => 2")
def list_argmax(L):
    L = _L(L)
    return L.index(max(L)) + 1


@_lf("list_argmin", "Position (1-based) of the smallest element, first one if tied: list_argmin(L)", 1, "list_argmin({3, 1, 2, 1}) => 2")
def list_argmin(L):
    L = _L(L)
    return L.index(min(L)) + 1


@_lf("list_index", "Position (1-based) of the first element equal to v; Math ERROR if absent: list_index(L, v)", 2, "list_index({5, 6, 7}, 7) => 3")
def list_index(L, v):
    L = _L(L)
    if _S(v) not in L:
        raise MathError("value not in the list")
    return L.index(v) + 1


@_lf("list_count", "How many elements equal v: list_count(L, v)", 2, "list_count({1, 2, 1, 1}, 1) => 3")
def list_count(L, v):
    return _L(L).count(_S(v))


@_lf("list_unique", "Sorted list without repeats: list_unique({3, 1, 3, 2})", 1, "list_unique({3, 1, 3, 2}) => {1, 2, 3}")
def list_unique(L):
    return Lst(sorted(set(_L(L))))


# ---------- matrices ----------
def _mf(name, desc, args, example):
    return _lf(name, desc, args, example, cat=_MTX)


@_mf("mat_new", "Build an r x c matrix from a list of r*c numbers, row by row: mat_new(r, c, L)", 3, "mat_new(2, 2, {1, 2, 3, 4}) => {{1, 2}, {3, 4}}")
def mat_new(r, c, L):
    r, c = _size(r, 100, "rows"), _size(c, 100, "columns")
    L = _L(L)
    if len(L) != r * c:
        raise MathError(f"the list needs {r * c} numbers")
    return Mat(tuple(L[i * c:(i + 1) * c]) for i in range(r))


@_mf("mat_eye", "Identity matrix of size n: mat_eye(n)", 1, "mat_eye(2) => {{1, 0}, {0, 1}}")
def mat_eye(n):
    n = _size(n, 100, "n")
    return Mat(tuple(int(i == j) for j in range(n)) for i in range(n))


@_mf("mat_zeros", "Matrix of zeros, r rows and c columns: mat_zeros(r, c)", 2, "mat_zeros(1, 2) => {{0, 0}}")
def mat_zeros(r, c):
    r, c = _size(r, 100, "rows"), _size(c, 100, "columns")
    return Mat((0,) * c for _ in range(r))


@_mf("mat_diag", "Square matrix with the list on its diagonal: mat_diag({1, 2})", 1, "mat_diag({1, 2}) => {{1, 0}, {0, 2}}")
def mat_diag(L):
    L = _L(L)
    if len(L) > 100:
        raise MathError("matrix too large")
    n = len(L)
    return Mat(tuple(L[i] if i == j else 0 for j in range(n)) for i in range(n))


@_mf("mat_rows", "Number of rows: mat_rows(M)", 1, "mat_rows({{1, 2, 3}, {4, 5, 6}}) => 2")
def mat_rows(M):
    return len(_M(M))


@_mf("mat_cols", "Number of columns: mat_cols(M)", 1, "mat_cols({{1, 2, 3}, {4, 5, 6}}) => 3")
def mat_cols(M):
    return len(_M(M)[0])


@_mf("mat_get", "Element at row i, column j (1-based): mat_get(M, i, j)", 3, "mat_get({{1, 2}, {3, 4}}, 2, 1) => 3")
def mat_get(M, i, j):
    M = _M(M)
    return M[_lpos(i, len(M), "row") - 1][_lpos(j, len(M[0]), "column") - 1]


@_mf("mat_row", "Row i as a list: mat_row(M, i)", 2, "mat_row({{1, 2}, {3, 4}}, 2) => {3, 4}")
def mat_row(M, i):
    M = _M(M)
    return Lst(M[_lpos(i, len(M), "row") - 1])


@_mf("mat_col", "Column j as a list: mat_col(M, j)", 2, "mat_col({{1, 2}, {3, 4}}, 2) => {2, 4}")
def mat_col(M, j):
    M = _M(M)
    j = _lpos(j, len(M[0]), "column")
    return Lst(row[j - 1] for row in M)


@_mf("mat_t", "Transpose: mat_t(M)", 1, "mat_t({{1, 2, 3}, {4, 5, 6}}) => {{1, 4}, {2, 5}, {3, 6}}")
def mat_t(M):
    return Mat(zip(*_M(M)))


@_mf("mat_flatten", "All elements row by row as a list: mat_flatten(M)", 1, "mat_flatten({{1, 2}, {3, 4}}) => {1, 2, 3, 4}")
def mat_flatten(M):
    return Lst(v for row in _M(M) for v in row)


@_mf("mat_trace", "Sum of the diagonal of a square matrix: mat_trace(M)", 1, "mat_trace({{1, 2}, {3, 4}}) => 5")
def mat_trace(M):
    M = _sq(M, 100)
    t = 0
    for i in range(len(M)):
        t = ar_add(t, M[i][i])
    return t


@_mf("mat_det", "Determinant of a square matrix up to 30 x 30: mat_det(M)", 1, "mat_det({{1, 2}, {3, 4}}) => -2")
def mat_det(M):
    M = _sq(M)
    return _qout(_det(_qm(M)), _exact_m(M))


@_mf("mat_inv", "Inverse of a square matrix (Math ERROR if singular): mat_inv(M)", 1, "mat_inv({{1, 2}, {3, 4}}) => {{-2, 1}, {1.5, -0.5}}")
def mat_inv(M):
    return _mat_inverse(_sq(M))


@_mf("mat_rank", "Rank of a matrix: mat_rank(M)", 1, "mat_rank({{1, 2}, {2, 4}}) => 1")
def mat_rank(M):
    M = _M(M)
    if len(M) > 30 or len(M[0]) > 30:
        raise MathError("matrix too large")
    return _rank(_qm(M))


@_mf("mat_mul", "Matrix product (same as A*B): mat_mul(A, B)", 2, "mat_mul({{1, 2}, {3, 4}}, {{0, 1}, {1, 0}}) => {{2, 1}, {4, 3}}")
def mat_mul(A, B):
    return _mat_product(_M(A), _M(B))


@_mf("mat_pow", "Matrix power with a whole exponent, negative = inverse (same as M^n): mat_pow(M, n)", 2, "mat_pow({{1, 1}, {1, 0}}, 10) => {{89, 55}, {55, 34}}")
def mat_pow(M, n):
    return _mat_power(_sq(M), _S(n))


@_mf("mat_solve", "Solve A x = b for x (A square, b a list): mat_solve(A, b)", 2, "mat_solve({{2, 1}, {1, 3}}, {3, 5}) => {0.8, 1.4}")
def mat_solve(A, b):
    A, b = _sq(A), _L(b)
    if len(b) != len(A):
        raise MathError("b needs one number per row of A")
    return _box_binary("*", _mat_inverse(A), b)


@_mf("mat_rref", "Reduced row echelon form: mat_rref(M)", 1, "mat_rref({{1, 2}, {3, 4}}) => {{1, 0}, {0, 1}}")
def mat_rref(M):
    M = _M(M)
    if len(M) > 30 or len(M[0]) > 30:
        raise MathError("matrix too large")
    exact = _exact_m(M)
    A = _qm(M)
    rows, cols, r = len(A), len(A[0]), 0
    for c in range(cols):
        p = next((k for k in range(r, rows) if A[k][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        pv = A[r][c]
        A[r] = [x / pv for x in A[r]]
        for k in range(rows):
            if k != r and A[k][c] != 0:
                f = A[k][c]
                A[k] = [x - f * y for x, y in zip(A[k], A[r])]
        r += 1
        if r == rows:
            break
    return Mat(tuple(_qout(q, exact) for q in row) for row in A)


@_mf("mat_norm_f", "Frobenius norm, the square root of the sum of squares of all elements: mat_norm_f(M)", 1, "mat_norm_f({{3, 0}, {0, 4}}) => 5")
def mat_norm_f(M):
    return math.sqrt(math.fsum(float(v) ** 2 for row in _M(M) for v in row))
