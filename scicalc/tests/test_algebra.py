"""Checks: algebra.  Run alone with  python run_tests.py algebra"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "algebra"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_algebra_9(check, ev, near, csv):
    """algebra and sequences"""
    # ---------------------------------------------------------------- algebra and sequences
    for a, b, c in [(1, -3, 2), (2, 5, -3), (1, 0, -9), (1, 2, 1), (3, -7, 2)]:
        d = b * b - 4 * a * c
        near(f"quad_disc({a},{b},{c})", f"quad_disc({a},{b},{c})", d)
        near(f"quad_root1({a},{b},{c})", f"quad_root1({a},{b},{c})", (-b + math.sqrt(d)) / (2 * a))
        near(f"quad_root2({a},{b},{c})", f"quad_root2({a},{b},{c})", (-b - math.sqrt(d)) / (2 * a))
        near(f"quad_vertex_x({a},{b},{c})", f"quad_vertex_x({a},{b},{c})", -b / (2 * a))
        near(f"quad_vertex_y({a},{b},{c})", f"quad_vertex_y({a},{b},{c})", a * (b / (2 * a)) ** 2 - b * b / (2 * a) + c)
        near(f"vieta_sum({a},{b},{c})", f"vieta_sum({a},{b},{c})", -b / a)
        near(f"vieta_prod({a},{b},{c})", f"vieta_prod({a},{b},{c})", c / a)
        near(f"complete_sq_h({a},{b},{c})", f"complete_sq_h({a},{b},{c})", -b / (2 * a))
        near(f"complete_sq_k({a},{b},{c})", f"complete_sq_k({a},{b},{c})", c - b * b / (4 * a))
    for a, b, c, dd in [(1, -6, 11, -6), (1, 0, 0, -8), (2, -3, -11, 6), (1, 0, 1, 0)]:
        disc = 18 * a * b * c * dd - 4 * b ** 3 * dd + b * b * c * c - 4 * a * c ** 3 - 27 * a * a * dd * dd
        near(f"cubic_disc({a},{b},{c},{dd})", f"cubic_disc({a},{b},{c},{dd})", disc)
        root = ev(f"cubic_real_root({a},{b},{c},{dd})")
        check(f"cubic_real_root({a},{b},{c},{dd}) is a root", abs(a * root ** 3 + b * root ** 2 + c * root + dd) < 1e-9, True)
    for a1, b1, c1, a2, b2, c2 in [(1, 1, 3, 1, -1, 1), (1, 2, 3, 3, 4, 5), (2, -1, 4, 1, 3, 9)]:
        x = ev(f"lin2_x({a1},{b1},{c1},{a2},{b2},{c2})")
        y = ev(f"lin2_y({a1},{b1},{c1},{a2},{b2},{c2})")
        check(f"lin2 residuals {a1},{b1},{c1},{a2},{b2},{c2}", abs(a1 * x + b1 * y - c1) + abs(a2 * x + b2 * y - c2) < 1e-9, True)
    sysm = [[1, 1, 1, 6], [0, 2, 5, -4], [2, 5, -1, 27]]
    flat = ",".join(str(v) for row in sysm for v in row)
    sol = [ev(f"lin3_{c}({flat})") for c in "xyz"]
    check("lin3 residuals", all(abs(sum(row[i] * sol[i] for i in range(3)) - row[3]) < 1e-9 for row in sysm), True)
    near("line_slope", "line_slope(1,2,5,10)", 2)
    near("line_intercept", "line_intercept(1,2,5,10)", 0)
    coeffs = [2, -3, 0, 5]
    for x in (-2, 0.5, 3):
        near(f"poly_eval at {x}", f"poly_eval({x},{csv(coeffs)})", sum(c * x ** (3 - i) for i, c in enumerate(coeffs)))
        near(f"poly_deriv_eval at {x}", f"poly_deriv_eval({x},{csv(coeffs)})", 6 * x * x - 6 * x)
        near(f"synth_rem at {x}", f"synth_rem({x},{csv(coeffs)})", sum(c * x ** (3 - i) for i, c in enumerate(coeffs)))
    near("poly_integral", "poly_integral(1,3,2,-3,0,5)", (0.5 * 81 - 27 + 15) - (0.5 - 1 + 5))
    near("bisect", "bisect('x^3-x-2',1,2)", 1.5213797068045676, 1e-9)
    near("newton", "newton('x^3-x-2',1.5)", 1.5213797068045676, 1e-9)
    near("secant", "secant('x^3-x-2',1,2)", 1.5213797068045676, 1e-9)
    near("fixed_point", "fixed_point('cos(x)',0.5)", 0.7390851332151607, 1e-9)
    near("solve_exp", "solve_exp(2,3,18)", 2)
    near("solve", "solve('x^2-4',3)", 2, 1e-8)
    near("root_bisection", "root_bisection('x^3-x-2',1,2)", 1.5213797068045676, 1e-6)
    near("root_newton", "root_newton('x^3-x-2',1.5)", 1.5213797068045676, 1e-6)
    near("pf_a", "pf_a(1,1,1,2)", -2)
    near("pf_b", "pf_b(1,1,1,2)", 3)
    near("pf identity", "pf_a(3,5,1,4)/(2-1)+pf_b(3,5,1,4)/(2-4)", (3 * 2 + 5) / ((2 - 1) * (2 - 4)))
    for n in range(0, 8):
        near(f"binom_term(7,{n},2,3)", f"binom_term(7,{n},2,3)", math.comb(7, n) * 2 ** (7 - n) * 3 ** n)
    near("ap_nth", "ap_nth(2,3,10)", 2 + 9 * 3)
    near("ap_sum", "ap_sum(2,3,10)", sum(2 + 3 * i for i in range(10)))
    near("ap_count", "ap_count(2,3,29)", 10)
    near("gp_nth", "gp_nth(2,3,5)", 2 * 3 ** 4)
    near("gp_sum", "gp_sum(2,3,5)", sum(2 * 3 ** i for i in range(5)))
    near("gp_sum_inf", "gp_sum_inf(3,0.25)", sum(3 * 0.25 ** i for i in range(80)))
    near("hp_nth", "hp_nth(6,3,5)", 1 / (1 / 6 + 4 * (1 / 3 - 1 / 6)))
