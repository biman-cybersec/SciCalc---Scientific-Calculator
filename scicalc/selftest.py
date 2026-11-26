"""selftest() runner

Module 46 of 47.  Taken from lines 18705-18792 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "selftest"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import CalcError
from .registry import REGISTRY
from .engine import Calculator
from .menu import (
    menu_area,
    menu_bmi,
    menu_factorial,
    menu_subtract,
    menu_theta_value,
    menu_total_surface_area,
)

from .tests import run_sections
from .tests.test_bad_input import _bad_input_checks


#  PART 10 : SELF-TEST AND ENTRY POINT
# ======================================================================================

def _fed(inputs, fn, *args):
    """Run an interactive function with pre-typed answers and return everything it printed."""
    import builtins
    import contextlib
    import io
    answers = iter(inputs)
    real_input = builtins.input
    builtins.input = lambda prompt="": next(answers)
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            fn(*args)
    finally:
        builtins.input = real_input
    return out.getvalue()


def selftest(show_uncovered=False, show_examples=True):
    """Quick built-in check:   python3 calculator.py --selftest   (--coverage lists functions without a cross-check)"""
    
    print(f"\n--- Total Registered Functions: {len(REGISTRY.functions())} ---")
    if show_examples:                               # default: one line per function (about 1200 lines); --quiet hides them
        for f in sorted(REGISTRY.functions(), key=lambda x: (x.category, x.name)):
            print(f"[{f.category}] {f.name} -> Example: {f.example}")
            
    problems, total = [], 0

    def check(label, got, want):
        nonlocal total
        total += 1
        if got != want:
            problems.append(f"{label}: got {got!r}, wanted {want!r}")

    def outcome(expr, calc=None):
        try:
            return (calc or Calculator()).evaluate(expr).text
        except CalcError as err:
            return err.message

    for f in REGISTRY.functions():                          # every documented example must be true
        expr, _, want = f.example.partition(" => ")
        got = outcome(expr)
        check(f"example of {f.name}", "ok" if want.startswith("<") and "ERROR" not in got else got,
              "ok" if want.startswith("<") else want)

    for expr, want in [("3+4*2", "11"), ("(3+4)*2", "14"), ("2^3^2", "512"), ("-2^2", "-4"),
                       ("6/2(1+2)", "1"), ("1/3+1/6", "0.5"), ("0.1+0.2", "0.3"), ("2pi", "6.283185307"),
                       ("sqrt(16)", "4"), ("(-8)^(1/3)", "-2"), ("5!", "120"), ("5 nCr 2", "10"),
                       ("7 mod 3", "1"), ("sin(30)", "0.5"), ("cos(90)", "0"), ("asin(0.5)", "30"),
                       ("2^100", "1.2676506×10^30"), ("20!", "2.432902008×10^18"), ("log10(1000)", "3"),
                       ("round(2.675,2)", "2.68"), ("200*15%", "30"), ("sin(30", "0.5"),
                       ("1/0", "Math ERROR"), ("tan(90)", "Math ERROR"), ("sqrt(-1)", "Math ERROR"),
                       ("2+", "Syntax ERROR"), ("foo(1)", "Syntax ERROR"), ("sin()", "Argument ERROR")]:
        check(expr, outcome(expr), want)

    calc = Calculator()
    for expr, want in [("5->A", "5"), ("2A+1", "11"), ("*2", "22"), ("Ans+PreAns", "33")]:
        check(expr, outcome(expr, calc), want)
    calc.set_angle("rad")
    check("sin(pi/2) in RAD", outcome("sin(pi/2)", calc), "1")

    # the old menu program: formulas that used to be wrong
    check("menu ellipse area", str(6 * math.pi) in _fed(["8", "3", "2"], menu_area), True)
    check("menu square pyramid total area", "= 96.0" in _fed(["7", "a", "6", "2", "5"], menu_total_surface_area), True)
    check("menu hemisphere total area", str(3 * math.pi) in _fed(["6", "2"], menu_total_surface_area), True)
    check("menu tan(90)", "UNDEFINED" in _fed(["90", "3"], menu_theta_value), True)
    check("menu 5!", "is 120" in _fed(["5"], menu_factorial), True)
    check("menu subtraction", "= 7" in _fed(["1", "10", "3"], menu_subtract), True)
    check("menu bmi", "22.86" in _fed(["70", "1", "1.75"], menu_bmi), True)

    covered = run_sections(check)
    _bad_input_checks(check)

    n_funcs, n_consts = REGISTRY.count()
    print(f"independent cross-check coverage: {len(covered)} of {n_funcs} functions")
    if show_uncovered:
        missing = sorted(f.name for f in REGISTRY.functions() if f.name not in covered)
        print("not cross-checked yet:", ", ".join(missing))
    print(f"selftest: {total} checks, {len(problems)} problem(s)   ({n_funcs} functions + {n_consts} constants)")
    for p in problems:
        print("  FAIL", p)
    return 1 if problems else 0
