"""Checks: units.  Run alone with  python run_tests.py units"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "units"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from ..engine import Calculator
from ..lib_units import CONVERSION_REGISTRY

from .helpers import _err, _expr_error  # noqa: F401


def checks_units_1(check, cov, near):
    """unit conversions"""
    # ---------------------------------------------------------------- unit conversions
    for (a, b), f in sorted(CONVERSION_REGISTRY.items()):
        name = f.__name__
        cov(name)
        near(f"{name} equals convert('{a}','{b}')", f'convert(37.5,"{a}","{b}")', f(37.5), 1e-12)
        near(f"{name} callable at the prompt", f"{name}(37.5)", f(37.5), 1e-12)
        back = CONVERSION_REGISTRY.get((b, a))
        if back is not None and back is not f:
            cov(back.__name__)
            for x in (1.0, 37.5, 1e-3):
                rt = back(f(x))
                check(f"round trip {a}->{b}->{a} at {x}", abs(rt - x) <= 1e-12 * max(1.0, abs(x), abs(f(x))), True)
    for expr, want in [("ft2m(1)", 0.3048), ("mi2km(1)", 1.609344), ("nmi2km(1)", 1.852), ("in2cm(1)", 2.54),
                       ("lb2kg(1)", 0.45359237), ("atm2pa(1)", 101325.0), ("kwh2j(1)", 3.6e6),
                       ("f_to_k(32)", 273.15), ("k_to_f(373.15)", 212.0), ("kgf2n(1)", 9.80665),
                       ("l2gal(3.785411784)", 1.0), ("mpg2l100km(30)", 235.214583333 / 30)]:
        near(f"unit anchor {expr}", expr, want, 1e-9)
    for expr, want in [("bar2psi(1)", 14.5037738), ("psi2bar(14.5037738)", 1.0), ("cal2joule(1)", 4.184),
                       ("joule2cal(4.184)", 1.0), ("kb2mb(2000)", 2.0), ("mb2gb(3000)", 3.0)]:
        near(f"unit anchor {expr}", expr, want, 1e-7)
    check("mpg2l100km(0) is an error", Calculator().evaluate("1").text and _err("mpg2l100km(0)"), "Math ERROR")
