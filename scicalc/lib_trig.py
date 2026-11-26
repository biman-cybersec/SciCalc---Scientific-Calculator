"""Trigonometry, inverse trig, hyperbolic, angle conversions

Module 7 of 47.  Taken from lines 1682-1943 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_trig"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register

# ======================================================================================
#  PART 7 : FUNCTION LIBRARY  -  add new functions here
# ======================================================================================


# ---------- 7a. Trigonometry ----------

# Trigonometry, inverse trigonometry, hyperbolic functions and angle conversions.
# Angles follow the calculator's mode (DEG / RAD / GRAD) unless the name says otherwise.


TRIG = "Trigonometry"
HYP = "Hyperbolic"
CONV = "Angle conversion"
_TINY = 1e-15


def _not_zero(x, what):
    if abs(x) < _TINY:
        raise MathError(f"{what} is undefined here")
    return x


# ---------------- trigonometric ----------------
@register("sin", TRIG, "Sine of an angle", angle_in=True, snap_zero=True, example="sin(30) => 0.5")
def sin(x):
    return math.sin(x)


@register("cos", TRIG, "Cosine of an angle", angle_in=True, snap_zero=True, example="cos(60) => 0.5")
def cos(x):
    return math.cos(x)


@register("tan", TRIG, "Tangent of an angle", angle_in=True, snap_zero=True, example="tan(45) => 1")
def tan(x):
    _not_zero(math.cos(x), "tan")
    return math.tan(x)


@register("sec", TRIG, "Secant = 1/cos", angle_in=True, snap_zero=True, example="sec(60) => 2")
def sec(x):
    return 1 / _not_zero(math.cos(x), "sec")


@register("csc", TRIG, "Cosecant = 1/sin", angle_in=True, snap_zero=True, aliases=("cosec",),
          example="csc(30) => 2")
def csc(x):
    return 1 / _not_zero(math.sin(x), "csc")


@register("cot", TRIG, "Cotangent = cos/sin", angle_in=True, snap_zero=True, example="cot(45) => 1")
def cot(x):
    return math.cos(x) / _not_zero(math.sin(x), "cot")


# ---------- Additional Trigonometric Functions ----------

@register("vers", TRIG, "Versine: vers(x) = 1 - cos(x)", angle_in=True, snap_zero=True, example="vers(0) => 0")
def vers(x):
    return 1 - math.cos(x)


@register("covers", TRIG, "Coversine: covers(x) = 1 - sin(x)", angle_in=True, snap_zero=True, example="covers(90) => 0")
def covers(x):
    return 1 - math.sin(x)


@register("haversine", TRIG, "Haversine function: haversine(x) = sin^2(x / 2)", angle_in=True, snap_zero=True, aliases=("haver",), example="haversine(180) => 1")
def haversine(x):
    return math.sin(x / 2.0) ** 2


@register("exsec", TRIG, "Exsecant: exsec(x) = sec(x) - 1", angle_in=True, snap_zero=True, example="exsec(0) => 0")
def exsec(x):
    c = _not_zero(math.cos(x), "exsec")
    return (1.0 / c) - 1.0


@register("excsc", TRIG, "Excosecant: excsc(x) = csc(x) - 1", angle_in=True, snap_zero=True, example="excsc(90) => 0")
def excsc(x):
    s = _not_zero(math.sin(x), "excsc")
    return (1.0 / s) - 1.0


@register("sincos", TRIG, "Combined sine and cosine product: sincos(x) = sin(x) * cos(x)", angle_in=True, snap_zero=True, example="sincos(30) => 0.4330127019")
def sincos(x):
    return math.sin(x) * math.cos(x)


# ---------------- inverse trigonometric (result is an angle) ----------------
@register("asin", TRIG, "Inverse sine, answer in the current angle mode", angle_out=True,
          aliases=("arcsin",), example="asin(0.5) => 30")
def asin(x):
    return math.asin(x)


@register("acos", TRIG, "Inverse cosine, answer in the current angle mode", angle_out=True,
          aliases=("arccos",), example="acos(0.5) => 60")
def acos(x):
    return math.acos(x)


@register("atan", TRIG, "Inverse tangent, answer in the current angle mode", angle_out=True,
          aliases=("arctan",), example="atan(1) => 45")
def atan(x):
    return math.atan(x)


@register("asec", TRIG, "Inverse secant", angle_out=True, aliases=("arcsec",), example="asec(2) => 60")
def asec(x):
    return math.acos(1 / x)


@register("acsc", TRIG, "Inverse cosecant", angle_out=True, aliases=("arccsc",), example="acsc(2) => 30")
def acsc(x):
    return math.asin(1 / x)


@register("acot", TRIG, "Inverse cotangent (range 0 to 180 degrees)", angle_out=True,
          aliases=("arccot",), example="acot(1) => 45")
def acot(x):
    return math.pi / 2 - math.atan(x)


@register("atan2", TRIG, "Angle of the point (x, y): atan2(y, x), full circle", args=2,
          angle_out=True, example="atan2(1,1) => 45")
def atan2(y, x):
    if y == 0 and x == 0:
        raise MathError("atan2(0,0) is undefined")
    return math.atan2(y, x)


# ---------- Classical, Navigational & Derived Trigonometric Functions ----------

@register("crd", TRIG, "Chord function: crd(x) = 2 * sin(x / 2)", angle_in=True, snap_zero=True, example="crd(60) => 1")
def crd(x):
    return 2 * math.sin(x / 2.0)


@register("vercos", TRIG, "Vercosine: vercos(x) = 1 - sin(x)", angle_in=True, snap_zero=True, example="vercos(90) => 0")
def vercos(x):
    return 1 - math.sin(x)


@register("covercos", TRIG, "Covercosine: covercos(x) = 1 - cos(x)", angle_in=True, snap_zero=True, example="covercos(0) => 0")
def covercos(x):
    return 1 - math.cos(x)


@register("ahaversine", TRIG, "Inverse haversine: ahaversine(h) = 2 * asin(sqrt(h))", angle_out=True, snap_zero=True, aliases=("invhaversine",), example="ahaversine(1) => 180")
def ahaversine(h):
    if h < 0 or h > 1:
        raise MathError("ahaversine argument must be between 0 and 1")
    return 2 * math.asin(math.sqrt(h))


@register("extan", TRIG, "Extangent: extan(x) = tan(x) - 1", angle_in=True, snap_zero=True, example="extan(45) => 0")
def extan(x):
    c = _not_zero(math.cos(x), "extan")
    return math.tan(x) - 1.0


@register("excot", TRIG, "Excotangent: excot(x) = csc(x) - 1", angle_in=True, snap_zero=True, example="excot(30) => 1")
def excot(x):
    s = _not_zero(math.sin(x), "excot")
    return (1.0 / s) - 1.0


# ---------------- hyperbolic ----------------
@register("sinh", HYP, "Hyperbolic sine", example="sinh(0) => 0")
def sinh(x):
    return math.sinh(x)


@register("cosh", HYP, "Hyperbolic cosine", example="cosh(0) => 1")
def cosh(x):
    return math.cosh(x)


@register("tanh", HYP, "Hyperbolic tangent", example="tanh(0) => 0")
def tanh(x):
    return math.tanh(x)


@register("sech", HYP, "Hyperbolic secant = 1/cosh", example="sech(0) => 1")
def sech(x):
    return 1 / math.cosh(x)


@register("csch", HYP, "Hyperbolic cosecant = 1/sinh", example="csch(1) => 0.8509181282")
def csch(x):
    return 1 / _not_zero(math.sinh(x), "csch")


@register("coth", HYP, "Hyperbolic cotangent = cosh/sinh", example="coth(1) => 1.313035285")
def coth(x):
    return math.cosh(x) / _not_zero(math.sinh(x), "coth")


@register("asinh", HYP, "Inverse hyperbolic sine", aliases=("arcsinh",), example="asinh(0) => 0")
def asinh(x):
    return math.asinh(x)


@register("acosh", HYP, "Inverse hyperbolic cosine (x >= 1)", aliases=("arccosh",), example="acosh(1) => 0")
def acosh(x):
    return math.acosh(x)


@register("atanh", HYP, "Inverse hyperbolic tangent (-1 < x < 1)", aliases=("arctanh",),
          example="atanh(0) => 0")
def atanh(x):
    return math.atanh(x)


@register("asech", HYP, "Inverse hyperbolic secant (0 < x <= 1)", example="asech(1) => 0")
def asech(x):
    return math.acosh(1 / x)


@register("acsch", HYP, "Inverse hyperbolic cosecant", example="acsch(1) => 0.881373587")
def acsch(x):
    return math.asinh(1 / x)


@register("acoth", HYP, "Inverse hyperbolic cotangent (|x| > 1)", example="acoth(2) => 0.5493061443")
def acoth(x):
    return math.atanh(1 / x)


# ---------------- angle conversions (independent of the angle mode) ----------------
@register("deg2rad", CONV, "Degrees to radians", example="deg2rad(180) => 3.141592654")
def deg2rad(x):
    return x * math.pi / 180


@register("rad2deg", CONV, "Radians to degrees", example="rad2deg(pi) => 180")
def rad2deg(x):
    return x * 180 / math.pi


@register("deg2grad", CONV, "Degrees to gradians", example="deg2grad(90) => 100")
def deg2grad(x):
    return x * 10 / 9


@register("grad2deg", CONV, "Gradians to degrees", example="grad2deg(100) => 90")
def grad2deg(x):
    return x * 9 / 10


@register("rad2grad", CONV, "Radians to gradians", example="rad2grad(pi) => 200")
def rad2grad(x):
    return x * 200 / math.pi


@register("grad2rad", CONV, "Gradians to radians", example="grad2rad(200) => 3.141592654")
def grad2rad(x):
    return x * math.pi / 200
