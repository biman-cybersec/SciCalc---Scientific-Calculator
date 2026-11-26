"""Vectors, equation solver, unit helpers, DMS, base-N

Module 13 of 47.  Taken from lines 2998-3219 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_vectors_solver_basen"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import ArgumentError, CalcError, MathError
from .registry import register
from .arithmetic import ar_add, ar_div, ar_mul, ar_normalize, ar_sub

# ---------- 7k. Vectors & Matrices ----------

CAT_VEC = "Vectors & Matrices"


@register("dot2", CAT_VEC, "Dot product of two 2D vectors: dot2(ux, uy, vx, vy)", args=4, exact=True, example="dot2(1,2,3,4) => 11")
def dot2(ux, uy, vx, vy):
    return ar_add(ar_mul(ux, vx), ar_mul(uy, vy))


@register("dot3", CAT_VEC, "Dot product of two 3D vectors: dot3(ux, uy, uz, vx, vy, vz)", args=6, exact=True, example="dot3(1,2,3,4,5,6) => 32")
def dot3(ux, uy, uz, vx, vy, vz):
    return ar_add(ar_add(ar_mul(ux, vx), ar_mul(uy, vy)), ar_mul(uz, vz))


@register("mag2", CAT_VEC, "Magnitude (length) of a 2D vector: mag2(x, y)", args=2, example="mag2(3,4) => 5")
def mag2(x, y):
    return math.hypot(x, y)


@register("mag3", CAT_VEC, "Magnitude (length) of a 3D vector: mag3(x, y, z)", args=3, example="mag3(2,3,6) => 7")
def mag3(x, y, z):
    return math.sqrt(x*x + y*y + z*z)


@register("det2", CAT_VEC, "Determinant of a 2x2 matrix [[a,b],[c,d]]: det2(a, b, c, d)", args=4, exact=True, example="det2(1,2,3,4) => -2")
def det2(a, b, c, d):
    return ar_sub(ar_mul(a, d), ar_mul(b, c))


# ---------- 7l. Equation Solver ----------

CAT_SOLVE = "Solver"


@register("solve", CAT_SOLVE, "Approximate root using Newton-Raphson: solve('expr_in_x', guess)", args=2, exact=True, example="solve('x^2 - 4', 1) => 2")
def solve_eq(expr_str, guess):
    from .lib_calculus import _make_fn  # imported here because lib_calculus is loaded after this module
    if not isinstance(expr_str, str):
        raise ArgumentError("solve requires a string expression in terms of x, e.g., 'x^2 - 4'")
    
    x0 = float(guess)
    h = 1e-6
    max_iter = 100
    tolerance = 1e-12
    f = _make_fn(expr_str)                 # sees the variables, angle mode and user functions

    for _ in range(max_iter):
        try:
            fx = f(x0)
        except CalcError:
            raise MathError("solver could not evaluate expression at this point")

        if abs(fx) < tolerance:
            return ar_normalize(x0)

        try:
            dfx = (f(x0 + h) - f(x0 - h)) / (2 * h)
        except CalcError:
            raise MathError("solver derivative calculation failed")

        if abs(dfx) < 1e-15:
            raise MathError("derivative is zero, solver stalled")

        x1 = x0 - fx / dfx
        if abs(x1 - x0) < tolerance:
            return ar_normalize(x1)
        x0 = x1

    raise MathError("solver did not converge")


# ---------- 7m. Expanded Unit Conversions ----------

CAT_UNITS = "Unit Conversions"


@register("bar2psi", CAT_UNITS, "Bars to pounds per square inch (psi)", example="bar2psi(1) => 14.5037738")
def bar2psi(bar):
    return ar_mul(bar, 14.5037738)


@register("psi2bar", CAT_UNITS, "Psi to bars", example="psi2bar(14.5038) => 1.000001806")
def psi2bar(psi):
    return ar_div(psi, 14.5037738)


@register("joule2cal", CAT_UNITS, "Joules to calories (thermochemical)", example="joule2cal(4.184) => 1")
def joule2cal(j):
    return ar_div(j, 4.184)


@register("cal2joule", CAT_UNITS, "Calories to Joules (thermochemical)", example="cal2joule(1) => 4.184")
def cal2joule(cal):
    return ar_mul(cal, 4.184)


@register("kb2mb", CAT_UNITS, "Kilobytes to Megabytes (decimal)", example="kb2mb(1000) => 1")
def kb2mb(kb):
    return ar_div(kb, 1000)


@register("mb2gb", CAT_UNITS, "Megabytes to Gigabytes (decimal)", example="mb2gb(1000) => 1")
def mb2gb(mb):
    return ar_div(mb, 1000)


# ---------- 7n. Numerical Calculus ----------

CAT_CALC = "Calculus"


@register("deriv", CAT_CALC, "Numerical derivative of 'expr' at x: deriv('expr', x)", args=2, exact=True, example="deriv('x^2', 3) => 6")
def deriv(expr_str, x_val):
    from .lib_calculus import _dn, _make_fn, _snap8  # imported here because lib_calculus is loaded after this module
    f = _make_fn(expr_str)
    return ar_normalize(_snap8(_dn(f, 1, float(x_val))))


@register("integrate", CAT_CALC, "Definite integral of 'expr' from a to b (Gauss-Legendre): integrate('expr', a, b)", args=3, exact=True, example="integrate('x^2', 0, 3) => 9")
def integrate(expr_str, a_val, b_val):
    from .lib_calculus import _gl_conv, _make_fn, _snap8  # imported here because lib_calculus is loaded after this module
    f = _make_fn(expr_str)
    return ar_normalize(_snap8(_gl_conv(f, float(a_val), float(b_val))))


# ---------- 7o. DMS (Degrees, Minutes, Seconds) ----------

CAT_DMS = "DMS & Angles"


@register("dms2deg", CAT_DMS, "Convert DMS to decimal degrees: dms2deg(deg, min, sec)", args=3, exact=True, example="dms2deg(45, 30, 0) => 45.5")
def dms2deg(d, m, s):
    sign = -1 if (d < 0 or (d == 0 and (m < 0 or s < 0))) else 1
    total = abs(float(d)) + abs(float(m)) / 60.0 + abs(float(s)) / 3600.0
    return ar_normalize(sign * total)


@register("deg2dms", CAT_DMS, "Convert decimal degrees to DMS string: deg2dms(decimal_deg)", args=1, example="deg2dms(45.5) => 45°30'0.0\"")
def deg2dms(deg_val):
    d_total = float(deg_val)
    sign = "-" if d_total < 0 else ""
    d_total = abs(d_total)
    
    d = int(d_total)
    m_float = (d_total - d) * 60
    m = int(m_float)
    s = round((m_float - m) * 60, 4)
    
    if s >= 60:
        s = 0
        m += 1
    if m >= 60:
        m = 0
        d += 1
        
    return f"{sign}{d}°{m}'{s}\""


# ---------- 7p. Base-N & Bitwise Logic ----------

CAT_BASE = "Base-N & Logic"


@register("dec2bin", CAT_BASE, "Convert decimal to binary: dec2bin(n)", example="dec2bin(42) => 0b101010")
def dec2bin(n):
    return bin(int(n))


@register("bin2dec", CAT_BASE, "Convert binary string or integer to decimal", args=1, exact=True, example="bin2dec(101010) => 42")
def bin2dec(s):
    return int(str(s), 2)


@register("dec2oct", CAT_BASE, "Convert decimal to octal: dec2oct(n)", example="dec2oct(64) => 0o100")
def dec2oct(n):
    return oct(int(n))


@register("oct2dec", CAT_BASE, "Convert octal string or integer to decimal", args=1, exact=True, example="oct2dec(100) => 64")
def oct2dec(s):
    return int(str(s), 8)


@register("dec2hex", CAT_BASE, "Convert decimal to hex: dec2hex(n)", example="dec2hex(255) => 0xff")
def dec2hex(n):
    return hex(int(n))


@register("hex2dec", CAT_BASE, "Convert hex string to decimal", args=1, exact=True, example="hex2dec('ff') => 255")
def hex2dec(s):
    clean = str(s).strip()
    return int(clean, 16)

@register("bitand", CAT_BASE, "Bitwise AND: bitand(a, b)", args=2, exact=True, example="bitand(12, 10) => 8")
def bitand(a, b):
    return int(a) & int(b)


@register("bitor", CAT_BASE, "Bitwise OR: bitor(a, b)", args=2, exact=True, example="bitor(12, 10) => 14")
def bitor(a, b):
    return int(a) | int(b)


@register("bitxor", CAT_BASE, "Bitwise XOR: bitxor(a, b)", args=2, exact=True, example="bitxor(12, 10) => 6")
def bitxor(a, b):
    return int(a) ^ int(b)


@register("bitnot", CAT_BASE, "Bitwise NOT: bitnot(a)", args=1, exact=True, example="bitnot(5) => -6")
def bitnot(a):
    return ~int(a)


@register("shl", CAT_BASE, "Bitwise shift left: shl(val, shifts)", args=2, exact=True, example="shl(3, 2) => 12")
def shl(a, b):
    return int(a) << int(b)


@register("shr", CAT_BASE, "Bitwise shift right: shr(val, shifts)", args=2, exact=True, example="shr(12, 2) => 3")
def shr(a, b):
    return int(a) >> int(b)
