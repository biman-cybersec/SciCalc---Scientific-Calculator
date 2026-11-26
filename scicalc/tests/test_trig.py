"""Checks: trig.  Run alone with  python run_tests.py trig"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "trig"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_trig_10(check, run, near):
    """trigonometry and hyperbolic"""
    # ---------------------------------------------------------------- trigonometry and hyperbolic
    for deg in (0, 17, 30, 45, 60, 89, 120, 200, 300):
        r_ = math.radians(deg)
        near(f"sin({deg})", f"sin({deg})", math.sin(r_), 1e-12)
        near(f"cos({deg})", f"cos({deg})", math.cos(r_), 1e-12)
        near(f"sin^2+cos^2 at {deg}", f"sin({deg})^2+cos({deg})^2", 1, 1e-12)
        if abs(math.cos(r_)) > 1e-6:
            near(f"tan({deg})", f"tan({deg})", math.tan(r_), 1e-9)
            near(f"sec({deg})", f"sec({deg})", 1 / math.cos(r_), 1e-9)
        if abs(math.sin(r_)) > 1e-6:
            near(f"csc({deg})", f"csc({deg})", 1 / math.sin(r_), 1e-9)
            near(f"cot({deg})", f"cot({deg})", 1 / math.tan(r_), 1e-9)
        near(f"vers({deg})", f"vers({deg})", 1 - math.cos(r_), 1e-12)
        near(f"covers({deg})", f"covers({deg})", 1 - math.sin(r_), 1e-12)
        near(f"vercos({deg})", f"vercos({deg})", 1 - math.sin(r_), 1e-12)
        near(f"covercos({deg})", f"covercos({deg})", 1 - math.cos(r_), 1e-12)
        near(f"haversine({deg})", f"haversine({deg})", math.sin(r_ / 2) ** 2, 1e-12)
        near(f"crd({deg})", f"crd({deg})", 2 * math.sin(r_ / 2), 1e-12)
        near(f"sincos({deg})", f"sincos({deg})", math.sin(r_) * math.cos(r_), 1e-12)
        near(f"deg2rad({deg})", f"deg2rad({deg})", r_, 1e-12)
        near(f"rad2deg round trip({deg})", f"rad2deg(deg2rad({deg}))", deg, 1e-12)
        near(f"deg2grad({deg})", f"deg2grad({deg})", deg * 10 / 9, 1e-12)
        near(f"grad2deg round trip({deg})", f"grad2deg(deg2grad({deg}))", deg, 1e-12)
        near(f"rad2grad round trip({deg})", f"grad2rad(rad2grad({r_!r}))", r_, 1e-12)
        near(f"ahaversine round trip({deg % 180})", f"ahaversine(haversine({deg % 180}))", deg % 180, 1e-7)
        if abs(math.cos(r_)) > 1e-6:
            near(f"exsec({deg})", f"exsec({deg})", 1 / math.cos(r_) - 1, 1e-9)
            near(f"extan({deg})", f"extan({deg})", math.tan(r_) - 1, 1e-9)
        if abs(math.sin(r_)) > 1e-6:
            near(f"excsc({deg})", f"excsc({deg})", 1 / math.sin(r_) - 1, 1e-9)
            near(f"excot({deg})", f"excot({deg})", 1 / math.sin(r_) - 1, 1e-9)
    for v in (-0.9, -0.3, 0.2, 0.75):
        near(f"asin({v})", f"asin({v})", math.degrees(math.asin(v)), 1e-9)
        near(f"acos({v})", f"acos({v})", math.degrees(math.acos(v)), 1e-9)
        near(f"atan({v})", f"atan({v})", math.degrees(math.atan(v)), 1e-9)
        near(f"acot({v})", f"acot({v})", math.degrees(math.pi / 2 - math.atan(v)), 1e-9)
    for v in (1.5, 2.0, -3.0):
        near(f"asec({v})", f"asec({v})", math.degrees(math.acos(1 / v)), 1e-9)
        near(f"acsc({v})", f"acsc({v})", math.degrees(math.asin(1 / v)), 1e-9)
    for yy, xx in [(1, 1), (1, -1), (-2, -3), (3, 0.5)]:
        near(f"atan2({yy},{xx})", f"atan2({yy},{xx})", math.degrees(math.atan2(yy, xx)), 1e-9)
    for x in (-1.2, 0.4, 2.0):
        for nm in ("sinh", "cosh", "tanh"):
            near(f"{nm}({x})", f"{nm}({x})", getattr(math, nm)(x), 1e-12)
        near(f"cosh^2-sinh^2 at {x}", f"cosh({x})^2-sinh({x})^2", 1, 1e-12)
        near(f"asinh({x})", f"asinh({x})", math.asinh(x), 1e-12)
        near(f"sech({x})", f"sech({x})", 1 / math.cosh(x), 1e-12)
        if x != 0:
            near(f"csch({x})", f"csch({x})", 1 / math.sinh(x), 1e-12)
            near(f"coth({x})", f"coth({x})", 1 / math.tanh(x), 1e-12)
            near(f"acsch({x})", f"acsch({x})", math.asinh(1 / x), 1e-12)
    near("acosh(3)", "acosh(3)", math.acosh(3), 1e-12)
    near("atanh(0.4)", "atanh(0.4)", math.atanh(0.4), 1e-12)
    near("asech(0.5)", "asech(0.5)", math.acosh(2), 1e-12)
    near("acoth(2)", "acoth(2)", math.atanh(0.5), 1e-12)
    calc_rad = Calculator()
    calc_rad.set_angle("rad")
    check("sin(pi/6) in RAD", abs(run("sin(pi/6)", calc_rad).value - 0.5) < 1e-12, True)
    calc_gr = Calculator()
    calc_gr.set_angle("grad")
    check("sin(50) in GRAD is 45 degrees", abs(run("sin(50)", calc_gr).value - math.sin(math.pi / 4)) < 1e-12, True)
