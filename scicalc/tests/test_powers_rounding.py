"""Checks: powers rounding.  Run alone with  python run_tests.py powers_rounding"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "powers_rounding"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .helpers import _err, _expr_error  # noqa: F401


def checks_powers_rounding_11(check, ev, near, ex):
    """powers, logs, rounding"""
    # ---------------------------------------------------------------- powers, logs, rounding
    for x in (0.5, 2, 9, 123.456):
        near(f"sqrt({x})", f"sqrt({x})", math.sqrt(x))
        near(f"cbrt({x})", f"cbrt({x})", x ** (1 / 3), 1e-12)
        near(f"exp({x})", f"exp({x})", math.exp(x), 1e-12)
        near(f"ln({x})", f"ln({x})", math.log(x), 1e-12)
        near(f"log({x})", f"log({x})", math.log10(x), 1e-12)
        near(f"log2({x})", f"log2({x})", math.log2(x), 1e-12)
        near(f"logb(3,{x})", f"logb(3,{x})", math.log(x, 3), 1e-12)
        near(f"sq({x})", f"sq({x})", x * x)
        near(f"cube({x})", f"cube({x})", x ** 3)
        near(f"inv({x})", f"inv({x})", 1 / x)
        near(f"pow({x},3)", f"pow({x},3)", x ** 3)
        near(f"exp10({x})", f"exp10({x})", 10 ** x, 1e-12)
        near(f"hypot({x},4)", f"hypot({x},4)", math.hypot(x, 4))
        near(f"root(3,{x})", f"root(3,{x})", x ** (1 / 3), 1e-12)
    for x in (-7.5, -2.5, -0.4, 0.4, 2.5, 7.5):
        near(f"abs({x})", f"abs({x})", abs(x))
        near(f"floor({x})", f"floor({x})", math.floor(x))
        near(f"ceil({x})", f"ceil({x})", math.ceil(x))
        near(f"trunc({x})", f"trunc({x})", math.trunc(x))
        near(f"sign({x})", f"sign({x})", (x > 0) - (x < 0))
        near(f"fpart({x})", f"fpart({x})", x - math.trunc(x))
        near(f"round({x})", f"round({x})", math.copysign(math.floor(abs(x) + 0.5), x))
    for a, b in [(17, 5), (-17, 5), (17, -5), (20, 4)]:
        near(f"quo({a},{b})", f"quo({a},{b})", a // b)
        near(f"rem({a},{b})", f"rem({a},{b})", a - b * (a // b))
    near("min", "min(3,-1,2)", -1)
    near("max", "max(3,-1,2)", 3)
    near("tofrac", "tofrac(0.75)", 0.75)
    near("randint range", "randint(5,5)", 5)
    check("rand in [0,1]", 0 <= ev("rand()") <= 1, True)
    ex("exact fraction sqrt(1/4)", "sqrt(1/4)", Fraction(1, 2))
    ex("exact 1/3+1/6", "1/3+1/6", Fraction(1, 2))
