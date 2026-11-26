"""Sprint 5C: c_* complex functions

Module 29 of 47.  Taken from lines 9534-9684 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_complex_c"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import cmath
import math

from .errors import MathError
from .registry import register
from .lib_powers_rounding import _whole

# ======================================================================================
#  SPRINT 5 - PART C : COMPLEX NUMBERS (23)
#  Results are text "x+yi" (9 decimals).  c_polar / c_from_polar use DEGREES (like c_arg and
#  polar2rect_re); the transcendental functions (c_sin, c_exp, ...) take the real and imaginary
#  parts as ordinary numbers and always work in radians.
# ======================================================================================

def _cz(a, b):
    return complex(float(a), float(b))


def _cclean(v):
    v = round(v, 9)
    if v == 0:
        v = 0.0
    return int(v) if float(v).is_integer() else v


def _cstr(z):
    """A complex result (a value, not text); a real result (imaginary part 0) becomes a plain number."""
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise MathError("result is not finite")
    return z


def _cr(name, desc, args, example, exact=False):
    return register(name, "Complex Numbers", desc, args, exact=exact, example=example)


@_cr("c_sub", "Complex subtraction (a+bi) - (c+di): c_sub(a, b, c, d)", 4, "c_sub(5, 3, 2, 7) => 3-4i")
def c_sub(a, b, c, d):
    return _cstr(_cz(a, b) - _cz(c, d))


@_cr("c_recip", "Reciprocal 1 / (a+bi): c_recip(a, b)", 2, "c_recip(0, 2) => -0.5i")
def c_recip(a, b):
    z = _cz(a, b)
    if z == 0:
        raise MathError("division by zero")
    return _cstr(1 / z)


@_cr("c_abs2", "Squared magnitude a^2 + b^2: c_abs2(a, b)", 2, "c_abs2(3, 4) => 25")
def c_abs2(a, b):
    return a * a + b * b


@_cr("c_pow_n", "(a+bi)^n for a whole number n: c_pow_n(a, b, n)", 3, "c_pow_n(1, 1, 4) => -4", exact=True)
def c_pow_n(a, b, n):
    n = _whole(n, "n")
    if abs(n) > 10000:
        raise MathError("exponent too large")
    return _cstr(_cz(a, b) ** n)


@_cr("c_pow", "(a+bi)^(c+di): c_pow(a, b, c, d)", 4, "c_pow(0, 1, 0, 1) => 0.2078795764")
def c_pow(a, b, c, d):
    z, w = _cz(a, b), _cz(c, d)
    if z == 0:
        if w == 0 or w.real <= 0:
            raise MathError("0 to this power is undefined")
        return _cstr(0j)
    return _cstr(cmath.exp(w * cmath.log(z)))


@_cr("c_sqrt", "Principal square root of a+bi: c_sqrt(a, b)", 2, "c_sqrt(-4, 0) => 2i")
def c_sqrt(a, b):
    return _cstr(cmath.sqrt(_cz(a, b)))


@_cr("c_exp", "e^(a+bi): c_exp(a, b)", 2, "c_exp(0, 3.141592653589793) => -1")
def c_exp(a, b):
    return _cstr(cmath.exp(_cz(a, b)))


@_cr("c_ln", "Principal natural logarithm of a+bi: c_ln(a, b)", 2, "c_ln(-1, 0) => 3.141592654i")
def c_ln(a, b):
    return _cstr(cmath.log(_cz(a, b)))


def _ctrig(name, fn, desc, example):
    @_cr(name, desc, 2, example)
    def f(a, b):
        return _cstr(fn(_cz(a, b)))
    f.__name__ = name
    return f


c_sin = _ctrig("c_sin", cmath.sin, "Complex sine (radians): c_sin(a, b)", "c_sin(0, 1) => 1.175201194i")
c_cos = _ctrig("c_cos", cmath.cos, "Complex cosine (radians): c_cos(a, b)", "c_cos(0, 1) => 1.543080635")
c_tan = _ctrig("c_tan", cmath.tan, "Complex tangent (radians): c_tan(a, b)", "c_tan(0, 1) => 0.761594156i")
c_sinh = _ctrig("c_sinh", cmath.sinh, "Complex hyperbolic sine: c_sinh(a, b)", "c_sinh(0, 1) => 0.8414709848i")
c_cosh = _ctrig("c_cosh", cmath.cosh, "Complex hyperbolic cosine: c_cosh(a, b)", "c_cosh(0, 1) => 0.5403023059")
c_tanh = _ctrig("c_tanh", cmath.tanh, "Complex hyperbolic tangent: c_tanh(a, b)", "c_tanh(0, 1) => 1.557407725i")
c_asin = _ctrig("c_asin", cmath.asin, "Complex inverse sine (radians, principal): c_asin(a, b)", "c_asin(2, 0) => 1.570796327+1.316957897i")
c_acos = _ctrig("c_acos", cmath.acos, "Complex inverse cosine (radians, principal): c_acos(a, b)", "c_acos(2, 0) => -1.316957897i")
c_atan = _ctrig("c_atan", cmath.atan, "Complex inverse tangent (radians, principal): c_atan(a, b)", "c_atan(0, 0.5) => 0.5493061443i")


@_cr("c_polar", "Polar form text r∠theta (theta in degrees): c_polar(a, b)", 2, "c_polar(0, 2) => 2∠90")
def c_polar(a, b):
    z = _cz(a, b)
    return f"{_cclean(abs(z))}∠{_cclean(math.degrees(cmath.phase(z)))}"


@_cr("c_from_polar", "Rectangular form of r∠theta (theta in degrees): c_from_polar(r, theta)", 2, "c_from_polar(2, 90) => 2i")
def c_from_polar(r, theta):
    return _cstr(cmath.rect(r, math.radians(theta)))


@_cr("c_nth_root", "k-th (0..n-1) of the n n-th roots of a+bi: c_nth_root(a, b, n, k)", 4, "c_nth_root(-8, 0, 3, 0) => 1+1.732050808i", exact=True)
def c_nth_root(a, b, n, k):
    n, k = _whole(n, "n"), _whole(k, "k")
    if not 1 <= n <= 10000:
        raise MathError("n must be between 1 and 10000")
    if not 0 <= k < n:
        raise MathError("k must be between 0 and n-1")
    z = _cz(a, b)
    if z == 0:
        return _cstr(0j)
    r, t = abs(z), cmath.phase(z)
    return _cstr(cmath.rect(r ** (1 / n), (t + 2 * math.pi * k) / n))


@_cr("c_roots_unity", "k-th (0..n-1) n-th root of unity: c_roots_unity(n, k)", 2, "c_roots_unity(4, 1) => i", exact=True)
def c_roots_unity(n, k):
    n, k = _whole(n, "n"), _whole(k, "k")
    if not 1 <= n <= 10000:
        raise MathError("n must be between 1 and 10000")
    if not 0 <= k < n:
        raise MathError("k must be between 0 and n-1")
    return _cstr(cmath.rect(1.0, 2 * math.pi * k / n))


def _cquad(a, b, c, sign):
    if a == 0:
        raise MathError("a must not be zero")
    d = cmath.sqrt(complex(b * b - 4 * a * c))
    return _cstr((-b + sign * d) / (2 * a))


@_cr("c_quad_root1", "First root (-b + sqrt(disc)) / 2a of ax^2+bx+c, real or complex: c_quad_root1(a, b, c)", 3, "c_quad_root1(1, 2, 5) => -1+2i")
def c_quad_root1(a, b, c):
    return _cquad(a, b, c, 1)


@_cr("c_quad_root2", "Second root (-b - sqrt(disc)) / 2a of ax^2+bx+c: c_quad_root2(a, b, c)", 3, "c_quad_root2(1, 2, 5) => -1-2i")
def c_quad_root2(a, b, c):
    return _cquad(a, b, c, -1)
