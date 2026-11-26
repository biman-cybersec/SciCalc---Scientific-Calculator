"""Checks: calculus.  Run alone with  python run_tests.py calculus"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "calculus"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from ..errors import CalcError
from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_calculus_17(near):
    """calculus, numerical methods, machine learning"""
    # ---------------------------------------------------------------- calculus, numerical methods, machine learning
    near("deriv", "deriv('x^3',2)", 12, 1e-6)
    near("integrate", "integrate('x^3',0,2)", 4, 1e-9)
    near("num_integrate_trap", "num_integrate_trap('x^2',0,3,2000)", 9, 1e-5)
    near("num_integrate_simpson", "num_integrate_simpson('x^3',0,2,100)", 4, 1e-9)
    near("num_integrate_simpson38", "num_integrate_simpson38('x^3',0,2,99)", 4, 1e-9)
    near("gauss_legendre_2 exact for cubics", "gauss_legendre_2('x^3',0,2)", 4, 1e-9)
    near("gauss_legendre_3 exact for quintics", "gauss_legendre_3('x^5',0,2)", 64 / 6, 1e-9)
    near("lagrange_interpolation", "lagrange_interpolation(1,2,3,4,1,8,27,64,2.5)", 2.5 ** 3, 1e-9)
    near("newton_divided_diff", "newton_divided_diff(1,2,3,4,1,8,27,64,2.5)", 2.5 ** 3, 1e-9)
    near("newton_forward_diff", "newton_forward_diff(1,2,3,4,1,8,27,64,1.5)", 1.5 ** 3, 1e-9)
    near("newton_backward_diff", "newton_backward_diff(1,2,3,4,1,8,27,64,3.5)", 3.5 ** 3, 1e-9)
    near("ode_rk4 y'=y", "ode_rk4('y',0,1,1,100)", math.e, 1e-8)
    near("ode_euler y'=y", "ode_euler('y',0,1,1,100000)", math.e, 1e-4)
    near("ode_rk4 y'=x+y", "ode_rk4('x + y',0,1,1,100)", 2 * math.e - 2, 1e-8)
    near("sigmoid", "sigmoid(1.2)", 1 / (1 + math.exp(-1.2)), 1e-12)
    near("relu", "relu(-3)", 0)
    near("relu positive", "relu(2.5)", 2.5)
    near("leaky_relu", "leaky_relu(-4)", -0.04, 1e-12)
    near("sinc", "sinc(1.3)", math.sin(1.3) / 1.3, 1e-12)
    near("soft_plus", "soft_plus(0.7)", math.log(1 + math.exp(0.7)), 1e-12)
    near("logistic_growth", "logistic_growth(100,9,1,2)", 100 / (1 + 9 * math.exp(-2)), 1e-12)


def checks_calculus_19(check, run, ev, ex):
    """Sprint 5 : calculus (RAD mode, closed forms)"""
    # ---------------------------------------------------------------- Sprint 5 : calculus (RAD mode, closed forms)
    rc = Calculator()
    rc.set_angle("rad")

    def evr(expr):
        return float(run(expr, rc).value)

    def nearr(label, expr, want, tol=1e-6):
        try:
            got = evr(expr)
        except CalcError as err:
            got = err.message
        ok = isinstance(got, float) and abs(got - want) <= tol * max(1.0, abs(want))
        check(label, "ok" if ok else got, "ok" if ok else want)

    def errr(label, expr):
        try:
            got = run(expr, rc).text
        except CalcError as err:
            got = err.message
        check(label, got, "Math ERROR")

    nearr("deriv exp(x) at 0 (old string-replace bug)", "deriv('exp(x)', 0)", 1)
    nearr("deriv x*exp(x) at 1", "deriv('x*exp(x)', 1)", 2 * math.e)
    nearr("deriv sin in RAD mode", "deriv('sin(x)', 1)", math.cos(1))
    check("deriv sin in DEG mode follows the angle mode", abs(ev("deriv('sin(x)', 0)") - math.pi / 180) < 1e-8, True)
    nearr("integrate exp(x) 0..1", "integrate('exp(x)', 0, 1)", math.e - 1)
    nearr("integrate sin 0..pi", "integrate('sin(x)', 0, pi)", 2)
    for n_ in range(1, 7):
        for x_ in (0.5, 1.3):
            tol_ = (1e-8, 1e-8, 1e-8, 1e-6, 1e-5, 2e-4)[n_ - 1]
            nearr(f"deriv_n sin n={n_} x={x_}", f"deriv_n('sin(x)', {n_}, {x_})", math.sin(x_ + n_ * math.pi / 2), tol_)
            nearr(f"deriv_n exp n={n_} x={x_}", f"deriv_n('exp(x)', {n_}, {x_})", math.exp(x_), tol_)
            nearr(f"deriv_n ln n={n_} x={x_}", f"deriv_n('ln(x)', {n_}, {x_})", (-1) ** (n_ - 1) * math.factorial(n_ - 1) / x_ ** n_, tol_)
    for n_ in range(1, 6):
        nearr(f"deriv_n x^5 n={n_} at 2", f"deriv_n('x^5', {n_}, 2)", math.perm(5, n_) * 2 ** (5 - n_), 1e-5)
    for x_, y_ in [(1, 2), (0.5, -1.5), (2, 0.3)]:
        nearr(f"partial_x at ({x_},{y_})", f"partial_x('x^2*y+sin(x*y)', {x_}, {y_})", 2 * x_ * y_ + y_ * math.cos(x_ * y_), 1e-6)
        nearr(f"partial_y at ({x_},{y_})", f"partial_y('x^2*y+sin(x*y)', {x_}, {y_})", x_ * x_ + x_ * math.cos(x_ * y_), 1e-6)
    for n_ in (2, 10, 100, 1000):
        nearr(f"integrate_simpson x^3 n={n_} exact", f"integrate_simpson('x^3', 0, 2, {n_})", 4, 1e-9)
    nearr("integrate_simpson sin", "integrate_simpson('sin(x)', 0, pi, 200)", 2, 1e-8)
    nearr("integrate_simpson exp", "integrate_simpson('exp(x)', 0, 1, 100)", math.e - 1, 1e-9)
    for n_ in (10, 100, 1000):
        h_ = 3 / n_
        nearr(f"integrate_trap x^2 n={n_} error is h^2*(b-a)*f''/12", f"integrate_trap('x^2', 0, 3, {n_})", 9 + h_ * h_ * 3 * 2 / 12, 1e-9)
    nearr("integrate_trap exact for lines", "integrate_trap('2*x+1', 0, 5, 3)", 30, 1e-12)
    for expr_, a_, b_, want in [("x^7", 0, 1, 0.125), ("sin(x)", 0, "pi", 2), ("ln(x)", 1, "e", 1), ("exp(x)", 0, 1, math.e - 1), ("1/(1+x^2)", 0, 1, math.pi / 4), ("x*sqrt(x+1)", 0, 3, 2 / 5 * 32 - 2 / 3 * 8 - (2 / 5 - 2 / 3))]:
        nearr(f"integrate_romberg {expr_}", f"integrate_romberg('{expr_}', {a_}, {b_})", want, 1e-7)
    for expr_, a_, want in [("exp(-x)", 0, 1), ("1/x^2", 1, 1), ("x*exp(-x)", 0, 1), ("exp(-x^2)", 0, math.sqrt(math.pi) / 2), ("1/(1+x^2)", 0, math.pi / 2), ("exp(-2*x)", 1, math.exp(-2) / 2)]:
        nearr(f"integrate_to_inf {expr_} from {a_}", f"integrate_to_inf('{expr_}', {a_})", want, 1e-6)
    nearr("double_integral x*y", "double_integral('x*y', 0, 2, 0, 3)", 9, 1e-9)
    nearr("double_integral x^2+y^2", "double_integral('x^2+y^2', 0, 1, 0, 2)", 1 / 3 * 2 + 8 / 3, 1e-9)
    nearr("double_integral sin(x)*cos(y)", "double_integral('sin(x)*cos(y)', 0, pi, 0, pi/2)", 2, 1e-7)
    nearr("double_integral exp(x+y)", "double_integral('exp(x+y)', 0, 1, 0, 1)", (math.e - 1) ** 2, 1e-7)
    for expr_, x0_, want in [("sin(x)/x", 0, 1), ("(1-cos(x))/x^2", 0, 0.5), ("(exp(x)-1)/x", 0, 1), ("(x^2-1)/(x-1)", 1, 2),
                             ("ln(1+x)/x", 0, 1), ("x^2", 3, 9), ("(sqrt(x+4)-2)/x", 0, 0.25), ("tan(x)/x", 0, 1), ("x*ln(x)", 0, 0)]:
        if expr_ == "x*ln(x)":
            nearr(f"limit_right {expr_}", f"limit_right('{expr_}', {x0_})", want, 2e-2)
        else:
            nearr(f"limit {expr_} at {x0_}", f"limit('{expr_}', {x0_})", want, 1e-6)
    nearr("limit_left abs(x)/x", "limit_left('abs(x)/x', 0)", -1, 1e-9)
    nearr("limit_right abs(x)/x", "limit_right('abs(x)/x', 0)", 1, 1e-9)
    nearr("limit_left 1/(1+exp(1/x))", "limit_left('1/(1+exp(1/x))', 0)", 1, 1e-6)
    nearr("limit_right 1/(1+exp(1/x))", "limit_right('1/(1+exp(1/x))', 0)", 0, 1e-6)
    for expr_, want in [("(2*x+1)/(x+3)", 2), ("exp(-x)", 0), ("1/x", 0), ("(1+1/x)^x", math.e), ("x/sqrt(x^2+1)", 1), ("(3*x^2+x)/(x^2-5)", 3)]:
        nearr(f"limit_inf {expr_}", f"limit_inf('{expr_}')", want, 1e-5)
    ex("sum_series x^2 1..100", "sum_series('x^2', 1, 100)", 338350)
    ex("sum_series 2^x 0..10", "sum_series('2^x', 0, 10)", 2047)
    ex("sum_series telescoping is exact", "sum_series('1/(x*(x+1))', 1, 99)", Fraction(99, 100))
    ex("sum_series empty range", "sum_series('x', 5, 1)", 0)
    ex("sum_series harmonic exact", "sum_series('1/x', 1, 6)", Fraction(49, 20))
    ex("prod_series x 1..10 is 10!", "prod_series('x', 1, 10)", 3628800)
    ex("prod_series (1+1/x) 1..9", "prod_series('1+1/x', 1, 9)", 10)
    ex("prod_series empty range", "prod_series('x', 3, 1)", 1)
    for x_ in (0.5, 1.0, -0.8):
        nearr(f"taylor exp deg 6 at {x_}", f"taylor_value('exp(x)', 0, {x_}, 6)", sum(x_ ** k / math.factorial(k) for k in range(7)), 1e-6)
        nearr(f"taylor sin deg 5 at {x_}", f"taylor_value('sin(x)', 0, {x_}, 5)", x_ - x_ ** 3 / 6 + x_ ** 5 / 120, 1e-6)
    nearr("taylor degree 0 is f(a)", "taylor_value('exp(x)', 1, 5, 0)", math.e, 1e-9)
    nearr("taylor ln about 1", "taylor_value('ln(x)', 1, 1.2, 4)", sum((-1) ** (k + 1) * 0.2 ** k / k for k in range(1, 5)), 1e-6)
    nearr("curve_length y=x", "curve_length('x', 0, 3)", 3 * math.sqrt(2), 1e-8)
    nearr("curve_length y=x^2", "curve_length('x^2', 0, 1)", math.sqrt(5) / 2 + math.asinh(2) / 4, 1e-7)
    nearr("curve_length arc of the unit circle", "curve_length('sqrt(1-x^2)', 0, 0.6)", math.asin(0.6), 1e-6)
    nearr("curve_length y=cosh(x)", "curve_length('cosh(x)', 0, 1)", math.sinh(1), 1e-7)
    nearr("area_between x and x^2", "area_between('x', 'x^2', 0, 1)", 1 / 6, 1e-8)
    nearr("area_between sin and cos (curves cross)", "area_between('sin(x)', 'cos(x)', 0, pi/2)", 2 * (math.sqrt(2) - 1), 1e-5)
    nearr("area_between is symmetric", "area_between('x^2', 'x', 0, 1)", 1 / 6, 1e-8)
    nearr("area_between a curve and itself", "area_between('x^3', 'x^3', 0, 2)", 0, 1e-12)
    nearr("vol_revolution_x y=x", "vol_revolution_x('x', 0, 3)", 9 * math.pi, 1e-9)
    nearr("vol_revolution_x sphere", "vol_revolution_x('sqrt(4-x^2)', -2, 2)", 4 / 3 * math.pi * 8, 1e-6)
    nearr("vol_revolution_x exp", "vol_revolution_x('exp(x)', 0, 1)", math.pi * (math.e ** 2 - 1) / 2, 1e-8)
    nearr("mean_value sin 0..pi", "mean_value('sin(x)', 0, pi)", 2 / math.pi, 1e-8)
    nearr("mean_value x^2 0..3", "mean_value('x^2', 0, 3)", 3, 1e-9)
    nearr("mean_value constant", "mean_value('7', 2, 9)", 7, 1e-9)
    nearr("curvature parabola at 0", "curvature('x^2', 0)", 2, 1e-7)
    nearr("curvature of the unit circle", "curvature('sqrt(1-x^2)', 0)", 1, 1e-6)
    nearr("curvature sin at pi/2", "curvature('sin(x)', pi/2)", 1, 1e-6)
    nearr("curvature x^3 at 1", "curvature('x^3', 1)", 6 / 10 ** 1.5, 1e-6)
    nearr("curvature of a line", "curvature('3*x+1', 2)", 0, 1e-7)
    nearr("critical_point parabola", "critical_point('(x-2)^2', 0, 5)", 2, 1e-6)
    nearr("critical_point sin", "critical_point('sin(x)', 0, 3)", math.pi / 2, 1e-6)
    nearr("critical_point cubic", "critical_point('x^3-3*x', 0, 3)", 1, 1e-6)
    nearr("critical_point exp(-x^2)", "critical_point('exp(-x^2)', -1, 2)", 0, 1e-6)
    errr("critical_point none", "critical_point('x', 0, 1)")
    errr("limit that diverges", "limit('1/x', 0)")
    errr("limit with different sides", "limit('abs(x)/x', 0)")
    errr("limit_inf that diverges", "limit_inf('x')")
    errr("limit_inf that diverges (square root)", "limit_inf('sqrt(x)')")
    errr("improper integral that diverges", "integrate_to_inf('1/x', 1)")
    errr("improper integral that diverges (x)", "integrate_to_inf('x', 0)")
    return {"nearr": nearr}
