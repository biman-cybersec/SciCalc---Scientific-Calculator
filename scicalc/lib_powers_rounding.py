"""Powers, roots, exp/log, rounding, integers, random

Module 8 of 47.  Taken from lines 1944-2167 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_powers_rounding"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
import random
from fractions import Fraction

from .errors import MathError
from .registry import register
from .arithmetic import ar_div, ar_is_exact, ar_mul, ar_neg, ar_power, ar_sub

# ---------- 7b. Powers, roots, exponentials, logarithms ----------

# Powers, roots, exponentials and logarithms. Roots and powers stay exact when they can:
# sqrt(16) = 4, sqrt(1/4) = 1/2, 8^(1/3) = 2.


POW = "Powers & Roots"
LOG = "Exponential & Log"


def _exact_root(x, k):
    """Exact k-th root of an int/Fraction if it is a perfect power, else None."""
    f = Fraction(x)
    if f < 0:
        return None

    def iroot(n):
        if n.bit_length() > 1000:
            return None
        r = round(n ** (1.0 / k))
        for c in (r - 1, r, r + 1):
            if c >= 0 and c ** k == n:
                return c
        return None

    a, b = iroot(f.numerator), iroot(f.denominator)
    return None if a is None or b is None else Fraction(a, b)


def _nth_root(n, x):
    if not ar_is_exact(n) or Fraction(n).denominator != 1 or n == 0:
        raise MathError("the root index must be a non-zero whole number")
    n = int(n)
    if n < 0:
        return ar_div(1, _nth_root(-n, x))
    if x < 0:
        if n % 2 == 0:
            raise MathError("even root of a negative number")
        return ar_neg(_nth_root(n, -x))
    if ar_is_exact(x):
        r = _exact_root(x, n)
        if r is not None:
            return r
    return float(x) ** (1.0 / n)


@register("sqrt", POW, "Square root", exact=True, example="sqrt(16) => 4")
def sqrt(x):
    return _nth_root(2, x)


@register("cbrt", POW, "Cube root (works for negatives)", exact=True, example="cbrt(-27) => -3")
def cbrt(x):
    return _nth_root(3, x)


@register("root", POW, "n-th root: root(n, x)", args=2, exact=True, example="root(4,81) => 3")
def root(n, x):
    return _nth_root(n, x)


@register("sq", POW, "Square, x^2", exact=True, example="sq(5) => 25")
def sq(x):
    return ar_power(x, 2)


@register("cube", POW, "Cube, x^3", exact=True, example="cube(3) => 27")
def cube(x):
    return ar_power(x, 3)


@register("inv", POW, "Reciprocal, 1/x", exact=True, example="inv(4) => 0.25")
def inv(x):
    return ar_div(1, x)


@register("pow", POW, "Power: pow(x, y) = x^y", args=2, exact=True, example="pow(2,10) => 1024")
def pow_(x, y):
    return ar_power(x, y)


@register("exp10", POW, "Ten to the power x", exact=True, example="exp10(3) => 1000")
def exp10(x):
    return ar_power(10, x)


@register("hypot", POW, "Length of the hypotenuse: sqrt(x^2 + y^2)", args=2, example="hypot(3,4) => 5")
def hypot(x, y):
    return math.hypot(x, y)


@register("exp", LOG, "e to the power x", example="exp(1) => 2.718281828")
def exp(x):
    return math.exp(x)


@register("ln", LOG, "Natural logarithm (base e)", example="ln(e) => 1")
def ln(x):
    return math.log(x)


@register("log", LOG, "Common logarithm (base 10)", aliases=("log10",), example="log(1000) => 3")
def log(x):
    return math.log10(x)


@register("log2", LOG, "Binary logarithm (base 2)", example="log2(8) => 3")
def log2(x):
    return math.log2(x)


@register("logb", LOG, "Logarithm to any base: logb(base, x)", args=2, example="logb(2,8) => 3")
def logb(base, x):
    return math.log(x) / math.log(base)


# ---------- 7c. Rounding, integers, fractions, random ----------

# Rounding, integer parts, min/max, fractions and random numbers.


CAT_ROUND = "Rounding & Integers"


def _frac(x):
    """Exact Fraction of a number; floats are read as the decimal you typed (2.675 -> 2675/1000)."""
    return Fraction(str(x)) if isinstance(x, float) else Fraction(x)


def _whole(x, what):
    if not ar_is_exact(x) or Fraction(x).denominator != 1:
        raise MathError(f"{what} must be a whole number")
    return int(x)


@register("abs", CAT_ROUND, "Absolute value", exact=True, example="abs(-5) => 5")
def abs_(x):
    return abs(x)


@register("sign", CAT_ROUND, "Sign of a number: -1, 0 or 1", exact=True, example="sign(-3) => -1")
def sign(x):
    return (x > 0) - (x < 0)


@register("floor", CAT_ROUND, "Greatest integer not above x", exact=True, aliases=("intg",),
          example="floor(-2.5) => -3")
def floor(x):
    return math.floor(x)


@register("ceil", CAT_ROUND, "Smallest integer not below x", exact=True, example="ceil(2.1) => 3")
def ceil(x):
    return math.ceil(x)


@register("trunc", CAT_ROUND, "Integer part (cuts off the decimals)", exact=True, aliases=("int",),
          example="trunc(-2.7) => -2")
def trunc(x):
    return math.trunc(x)


@register("fpart", CAT_ROUND, "Fractional part: x minus its integer part", exact=True,
          example="fpart(5.25) => 0.25")
def fpart(x):
    return ar_sub(x, math.trunc(x))


@register("round", CAT_ROUND, "Round half away from zero: round(x) or round(x, digits)", args=(1, 2),
          exact=True, example="round(2.675,2) => 2.68")
def round_(x, digits=0):
    d = _whole(digits, "digits")
    if abs(d) > 30:
        raise MathError("digits out of range")
    scale = Fraction(10) ** d
    q = _frac(x) * scale
    r = math.floor(abs(q) + Fraction(1, 2))
    result = Fraction(r if q >= 0 else -r) / scale
    return float(result) if isinstance(x, float) else result


@register("quo", CAT_ROUND, "Integer quotient: quo(17, 5) = 3", args=2, exact=True, example="quo(17,5) => 3")
def quo(a, b):
    if b == 0:
        raise MathError("division by zero")
    return math.floor(_frac(a) / _frac(b))


@register("rem", CAT_ROUND, "Remainder: rem(17, 5) = 2", args=2, exact=True, example="rem(17,5) => 2")
def rem(a, b):
    return ar_sub(a, ar_mul(b, quo(a, b)))


@register("min", CAT_ROUND, "Smallest of the given numbers", args=(1, None), exact=True, example="min(3,1,2) => 1")
def min_(*xs):
    return min(xs)


@register("max", CAT_ROUND, "Largest of the given numbers", args=(1, None), exact=True, example="max(3,1,2) => 3")
def max_(*xs):
    return max(xs)


@register("tofrac", CAT_ROUND, "Turn a decimal into a fraction (like S<=>D)", exact=True,
          example="tofrac(0.75) => 0.75")
def tofrac(x):
    return Fraction(x).limit_denominator(10 ** 6)


@register("rand", CAT_ROUND, "Random decimal from 0 to 1 (3 places, like Ran#)", args=0,
          example="rand() => <random>")
def rand():
    return round(random.random(), 3)


@register("randint", CAT_ROUND, "Random whole number between a and b (inclusive)", args=2, exact=True,
          example="randint(1,1) => 1")
def randint(a, b):
    a, b = _whole(a, "a"), _whole(b, "b")
    if a > b:
        raise MathError("a must not be larger than b")
    return random.randint(a, b)
