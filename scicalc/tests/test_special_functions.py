"""Checks: special functions.  Run alone with  python run_tests.py special_functions"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "special_functions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_special_functions_7(near, simpson):
    """special functions"""
    # ---------------------------------------------------------------- special functions
    for x in (0.3, 1.0, 2.2, 5.5):
        near(f"erf({x})", f"erf({x})", math.erf(x))
        near(f"erf_comp({x})", f"erf_comp({x})", math.erfc(x))
        near(f"gamma({x})", f"gamma({x})", math.gamma(x))
        near(f"lgamma({x})", f"lgamma({x})", math.lgamma(x))
        near(f"expm1({x})", f"expm1({x})", math.expm1(x))
        near(f"log1p({x})", f"log1p({x})", math.log1p(x))
        near(f"digamma recurrence at {x}", f"digamma({x}+1)-digamma({x})", 1 / x, 1e-9)
        near(f"lambertw({x}) solves w*e^w=x", f"lambertw({x})*exp(lambertw({x}))", x, 1e-9)
        near(f"gamma_inc_p({x}) from series", f"gamma_inc_p(2,{x})", 1 - math.exp(-x) * (1 + x), 1e-9)
        near(f"beta_inc symmetric {x}", f"beta_inc(2,3,{x / 6})+beta_inc(3,2,{1 - x / 6})", 1, 1e-9)
        near(f"beta({x})", f"beta({x},2)", math.gamma(x) * math.gamma(2) / math.gamma(x + 2))
    for y in (-0.8, -0.3, 0.1, 0.9):
        near(f"erf_inv({y}) round trip", f"erf(erf_inv({y}))", y, 1e-10)
    near("zeta(2)", "zeta(2)", math.pi ** 2 / 6, 1e-9)
    near("zeta(4)", "zeta(4)", math.pi ** 4 / 90, 1e-9)
    near("zeta(0.5)", "zeta(0.5)", -1.4603545088095868, 1e-8)
    near("digamma(1)", "digamma(1)", -0.5772156649015329, 1e-9)
    near("hyp2f1 = -ln(1-z)/z", "hyp2f1(1,1,2,0.4)", -math.log(0.6) / 0.4, 1e-10)
    for n in (0, 1, 2, 3):
        for x in (0.7, 2.5, 8.0):
            integral = simpson(lambda t: math.cos(n * t - x * math.sin(t)), 0.0, math.pi, 800) / math.pi
            near(f"bessel_j({n},{x}) integral rep.", f"bessel_j({n},{x})", integral, 1e-8)
    for x in (0.5, 2.0, 7.0):
        near(f"bessel_y wronskian at {x}", f"bessel_j(1,{x})*bessel_y(0,{x})-bessel_j(0,{x})*bessel_y(1,{x})", 2 / (math.pi * x), 1e-8)
    for mm in (0.0, 0.3, 0.8):
        near(f"elliptic_k({mm})", f"elliptic_k({mm})", simpson(lambda t: 1 / math.sqrt(1 - mm * math.sin(t) ** 2), 0, math.pi / 2, 400), 1e-9)
        near(f"elliptic_e({mm})", f"elliptic_e({mm})", simpson(lambda t: math.sqrt(1 - mm * math.sin(t) ** 2), 0, math.pi / 2, 400), 1e-9)
    for x in (1.0, 4.0, 10.0):
        near(f"sine_integral({x})", f"sine_integral({x})", simpson(lambda t: 1.0 if t == 0 else math.sin(t) / t, 0, x, 2000), 1e-9)
        near(f"fresnel_s({x / 4})", f"fresnel_s({x / 4})", simpson(lambda t: math.sin(math.pi * t * t / 2), 0, x / 4, 800), 1e-9)
        near(f"fresnel_c({x / 4})", f"fresnel_c({x / 4})", simpson(lambda t: math.cos(math.pi * t * t / 2), 0, x / 4, 800), 1e-9)
    near("cosine_integral(2)", "cosine_integral(2)", 0.4229808287748650, 1e-9)
    for nn in range(0, 12):
        near(f"sum_n2({nn})", f"sum_n2({nn})", sum(i * i for i in range(nn + 1)))
        near(f"sum_n3({nn})", f"sum_n3({nn})", sum(i ** 3 for i in range(nn + 1)))
        near(f"sum_odd({nn})", f"sum_odd({nn})", sum(2 * i + 1 for i in range(nn)))
    seq = [0, 1]
    for _ in range(20):
        seq.append(3 * seq[-1] - 2 * seq[-2])
    near("linrec2", "linrec2(3,-2,0,1,15)", seq[15])
