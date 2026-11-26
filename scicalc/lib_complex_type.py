"""Complex numbers as a value type

Module 35 of 47.  Taken from lines 12101-12152 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_complex_type"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import ArgumentError, MathError
from .registry import register
from .engine import _ACTIVE_CALC
from .lib_science_basic import CAT_COMPLEX

# ======================================================================================
#  COMPLEX NUMBERS AS A VALUE TYPE
#  i is the imaginary unit:  3+4i, (1+2i)*(3-i), i^2 = -1, 2i.  A result whose imaginary part
#  is 0 is an ordinary real number.  + - * / ^ ² ³ ⁻¹ % work on complex values; sqrt, cbrt,
#  exp, ln, log, log2, sin ... atanh, sq, cube, inv, pow and abs accept them (trigonometric
#  functions of a complex argument use radians).  re, im, conj, arg and rect are below.
#  The c_* functions take (real, imaginary) pairs; a complex value may stand for a pair:
#  c_mul(1+2i, 3+4i) = c_mul(1, 2, 3, 4).  "complex on" (the Calculator.complex_mode switch)
#  widens real functions: sqrt(-4) = 2i, ln(-1) = πi, (-8)^(1/3) = 1+1.732i.  "complex polar"
#  shows results as r∠θ in the current angle mode.  Lists and matrices hold real numbers only.
# ======================================================================================
def _cxf(name, desc, args, example):
    return register(name, CAT_COMPLEX, desc, args, exact=True, example=example)


@_cxf("re", "Real part of a number: re(3+4i)", 1, "re(3+4i) => 3")
def cx_re(z):
    if not isinstance(z, (int, Fraction, float, complex)):
        raise ArgumentError("this needs a number")
    return z.real


@_cxf("im", "Imaginary part of a number: im(3+4i)", 1, "im(3+4i) => 4")
def cx_im(z):
    if not isinstance(z, (int, Fraction, float, complex)):
        raise ArgumentError("this needs a number")
    return z.imag if isinstance(z, complex) else 0


@_cxf("conj", "Complex conjugate: conj(3+4i)", 1, "conj(3+4i) => 3-4i")
def cx_conj(z):
    if not isinstance(z, (int, Fraction, float, complex)):
        raise ArgumentError("this needs a number")
    return z.conjugate() if isinstance(z, complex) else z


@register("arg", CAT_COMPLEX, "Argument (angle) of a number in the current angle mode: arg(1+i)", 1, exact=True, angle_out=True, example="arg(1+i) => 45")
def cx_arg(z):
    if not isinstance(z, (int, Fraction, float, complex)):
        raise ArgumentError("this needs a number")
    z = complex(z)
    if z == 0:
        raise MathError("the argument of 0 is undefined")
    return math.atan2(z.imag, z.real)


@register("rect", CAT_COMPLEX, "Complex number from modulus and angle (angle in the current angle mode): rect(2, 90)", 2, example="rect(2, 90) => 2i")
def cx_rect(r, theta):
    t = _ACTIVE_CALC[0].to_radians(theta) if _ACTIVE_CALC[0] is not None else theta
    return complex(r * math.cos(t), r * math.sin(t))
