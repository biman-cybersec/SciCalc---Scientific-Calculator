"""Exact fractions + clean floats, Lst/Mat/Cx value types

Module 3 of 47.  Taken from lines 238-526 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "arithmetic"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from typing import Any
import math
from fractions import Fraction

from .errors import ArgumentError, MathError

# ======================================================================================
#  PART 3 : ARITHMETIC (exact fractions + clean floats)
# ======================================================================================

# Exact + floating point arithmetic shared by the evaluator and the function library.
#
# Values are int, Fraction (exact) or float. Exact values stay exact: 1/3 + 1/6 = 1/2.
# Floats are rounded to 15 significant digits after every step (like a Casio's internal
# precision) so 0.1 + 0.2 is 0.3, and whole-number floats become ints.


MAX_BITS = 14000        # about 4200 digits: bigger numbers give Math ERROR
FLOAT_DIGITS = 15
MAX_FACTORIAL = 1500


def ar_is_exact(x):
    return isinstance(x, (int, Fraction)) and not isinstance(x, bool)


def ar_snap(x):
    return float(f"{x:.{FLOAT_DIGITS}g}")


def ar_check(n):
    if n.bit_length() > MAX_BITS:
        raise MathError("number too large")


class Lst(tuple):
    """A list of numbers, typed {1, 2, 3}."""
    __slots__ = ()


class Mat(tuple):
    """A matrix (tuple of equal-length row tuples), typed {{1, 2}, {3, 4}}."""
    __slots__ = ()


MAX_ELEMENTS = 10000


class Cx(complex):
    """A complex number with a non-zero imaginary part, typed 3+4i (a real result stays a plain number)."""
    __slots__ = ()


_CPLX: list[Any] = [False]                 # complex mode of the calculator that is evaluating (see Calculator.complex_mode)


def _box(x):
    return isinstance(x, (Lst, Mat))


def ar_normalize(x):
    # Allow string results (Base-N binary/hex, DMS strings) to pass straight through
    if isinstance(x, str):
        return x
    if isinstance(x, complex):
        re_, im_ = x.real, x.imag
        if not (math.isfinite(re_) and math.isfinite(im_)):
            raise MathError("result is undefined or infinite")
        scale = max(abs(re_), abs(im_))
        re_ = 0.0 if abs(re_) < 1e-14 * scale else ar_snap(re_)
        im_ = 0.0 if abs(im_) < 1e-14 * scale else ar_snap(im_)
        return Cx(re_, im_) if im_ != 0 else ar_normalize(re_)
    if isinstance(x, Lst):
        return Lst(ar_normalize(v) for v in x)
    if isinstance(x, Mat):
        return Mat(tuple(ar_normalize(v) for v in row) for row in x)
    if isinstance(x, bool):
        return 1 if x else 0
    if isinstance(x, int):
        return x
    if isinstance(x, Fraction):
        return x if x.denominator != 1 else x.numerator
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            raise MathError("result is undefined or infinite")
        # Snap whole-number floats to int
        if x.is_integer():
            return int(x)
        # Clean precision noise using significant digits instead of fixed decimals
        return ar_snap(x)
    raise TypeError(f"not a number: {x!r}")


def ar_add(a, b):
    return ar_normalize(a + b)


def ar_sub(a, b):
    return ar_normalize(a - b)


def ar_mul(a, b):
    return ar_normalize(a * b)


def ar_neg(a):
    return ar_normalize(-a)


def ar_div(a, b):
    if b == 0:
        raise MathError("division by zero")
    if isinstance(a, complex) or isinstance(b, complex):
        return ar_normalize(complex(a) / complex(b))
    if ar_is_exact(a) and ar_is_exact(b):
        return ar_normalize(Fraction(a) / Fraction(b))
    return ar_normalize(float(a) / float(b))


def ar_mod(a, b):
    if b == 0:
        raise MathError("modulo by zero")
    if ar_is_exact(a) and ar_is_exact(b):
        return ar_normalize(Fraction(a) % Fraction(b))
    return ar_normalize(float(a) % float(b))


def ar_power(a, b):
    if isinstance(b, float) and b.is_integer() and abs(b) < 1e6:
        b = int(b)
    if isinstance(a, complex) or isinstance(b, complex):
        if a == 0:
            if b == 0 or isinstance(b, complex) or b < 0:
                raise MathError("0 to this power is undefined")
            return 0
        return ar_normalize(complex(a) ** complex(b))
    if a == 0:
        if b == 0:
            raise MathError("0^0 is undefined")
        if b < 0:
            raise MathError("0 to a negative power")
        return 0
    if ar_is_exact(b) and Fraction(b).denominator == 1:          # whole-number exponent
        n = int(b)
        if ar_is_exact(a):
            fa = Fraction(a)
            bits = abs(n) * (math.log2(abs(fa.numerator)) + math.log2(fa.denominator))
            if bits > MAX_BITS:
                raise MathError("result too large")
            return ar_normalize(fa ** n)
        return ar_normalize(float(a) ** n)
    fa, fb = float(a), float(b)                               # fractional exponent
    if fa < 0 and _CPLX[0]:                                   # complex mode: principal value
        return ar_normalize(complex(fa) ** fb)
    if fa < 0:
        if ar_is_exact(b) and Fraction(b).denominator % 2 == 1:  # odd root of a negative: (-8)^(1/3)
            root = (-fa) ** fb
            return ar_normalize(-root if Fraction(b).numerator % 2 else root)
        raise MathError("negative number to a fractional power")
    return ar_normalize(fa ** fb)


def ar_factorial(x):
    if not ar_is_exact(x) or Fraction(x).denominator != 1 or x < 0:
        raise MathError("factorial needs a whole number >= 0")
    if x > MAX_FACTORIAL:
        raise MathError(f"factorial limited to {MAX_FACTORIAL}!")
    return ar_normalize(math.factorial(int(x)))


def ar_percent(x):
    return ar_div(x, 100)


# ---------- lists and matrices: arithmetic ----------
def _shape(x):
    return (len(x),) if isinstance(x, Lst) else (len(x), len(x[0]))


def _is_scalar(x):
    """A number a list can hold: real or complex."""
    return isinstance(x, (int, Fraction, float, complex)) and not isinstance(x, bool)


def _elem_text(v, fmt):
    from .display import _cx_text, format_number  # imported here because display is loaded after this module
    return _cx_text(v, fmt) if isinstance(v, complex) else format_number(v, fmt)


def _build_box(items):
    """The values written between { } become a list (numbers) or a matrix (equal-length lists)."""
    if len(items) > MAX_ELEMENTS:
        raise MathError("list too long")
    if all(_is_scalar(v) for v in items):
        return Lst(items)
    if all(isinstance(v, Lst) for v in items):
        if len({len(v) for v in items}) != 1:
            raise ArgumentError("all rows of a matrix need the same length")
        if len(items) * len(items[0]) > MAX_ELEMENTS:
            raise MathError("matrix too large")
        return Mat(tuple(v) for v in items)
    raise ArgumentError("a list holds numbers; a matrix is a list of equal-length lists")


def _ew1(op, x):
    if isinstance(x, Lst):
        return Lst(op(v) for v in x)
    return Mat(tuple(op(v) for v in row) for row in x)


def _ew(op, a, b):
    ba, bb = _box(a), _box(b)
    if ba and bb:
        if type(a) is not type(b) or _shape(a) != _shape(b):
            raise MathError("lists must have the same size")
        if isinstance(a, Lst):
            return Lst(op(x, y) for x, y in zip(a, b))
        return Mat(tuple(op(x, y) for x, y in zip(r, s)) for r, s in zip(a, b))
    if ba:
        if not _is_scalar(b):
            raise ArgumentError("cannot combine a list with this value")
        return _ew1(lambda v: op(v, b), a)
    if not _is_scalar(a):
        raise ArgumentError("cannot combine a list with this value")
    return _ew1(lambda v: op(a, v), b)


def _dot(u, v):
    t = 0
    for x, y in zip(u, v):
        t = ar_add(t, ar_mul(x, y))
    return t


def _mat_product(A, B):
    if len(A[0]) != len(B):
        raise MathError("matrix sizes do not fit for multiplication")
    cols = list(zip(*B))
    return Mat(tuple(_dot(r, c) for c in cols) for r in A)


def _box_binary(op, a, b):
    from .engine import _BINARY  # imported here because engine is loaded after this module
    if op == "*":
        if isinstance(a, Mat) and isinstance(b, Mat):
            return _mat_product(a, b)
        if isinstance(a, Mat) and isinstance(b, Lst):               # matrix times a column vector
            if len(a[0]) != len(b):
                raise MathError("matrix sizes do not fit for multiplication")
            return Lst(_dot(r, b) for r in a)
        if isinstance(a, Lst) and isinstance(b, Mat):               # row vector times a matrix
            if len(a) != len(b):
                raise MathError("matrix sizes do not fit for multiplication")
            return Lst(_dot(a, c) for c in zip(*b))
    elif op == "^":
        if isinstance(a, Mat) and _is_scalar(b):
            return _mat_power(a, b)
        if isinstance(b, Mat):
            raise MathError("cannot raise to a matrix power")
    elif op == "/" and isinstance(b, Mat):
        raise MathError("cannot divide by a matrix: multiply by its inverse instead")
    return _ew(_BINARY[op], a, b)


def _mat_power(M, n):
    if len(M) != len(M[0]):
        raise MathError("only a square matrix has powers")
    if not ar_is_exact(n) or Fraction(n).denominator != 1 or abs(n) > 1000:
        raise MathError("matrix power must be a whole number up to 1000")
    n = int(n)
    if n < 0:
        M, n = _mat_inverse(M), -n
    size = len(M)
    result = Mat(tuple(int(i == j) for j in range(size)) for i in range(size))
    base = M
    while n:
        if n & 1:
            result = _mat_product(result, base)
        n >>= 1
        if n:
            base = _mat_product(base, base)
        for row in result:
            for v in row:
                if isinstance(v, int) and v.bit_length() > MAX_BITS:
                    raise MathError("result too large")
    return result


def _mat_inverse(M):
    from .lib_vectors_matrices import _minv, _fr, _num  # imported here because lib_vectors_matrices is loaded after this module
    if len(M) != len(M[0]):
        raise MathError("only a square matrix has an inverse")
    exact = all(ar_is_exact(v) for row in M for v in row)
    inv = _minv([[_fr(v) for v in row] for row in M])
    return Mat(tuple(_num(q) if exact else float(q) for q in row) for row in inv)
