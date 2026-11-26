"""Sprint 2A: numerical methods and differential equations

Module 20 of 47.  Taken from lines 5976-6284 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_numerical"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .registry import register
from .lib_regression import _parse_numeric_args

# ==============================================================================
# SPRINT 2 - BATCH 2A: NUMERICAL METHODS & DIFFERENTIAL EQUATIONS (EXPANDED)
# ==============================================================================

CAT_NUMERICAL = "Numerical Methods & ODEs"


def _eval_expr(expr_str, variables):
    """Universal helper evaluator compatible with SciCalc's parser & selftest."""
    if callable(expr_str):
        if "y" in variables:
            return float(expr_str(variables["x"], variables["y"]))  # pyright: ignore[reportArgumentType]
        return float(expr_str(variables["x"]))  # pyright: ignore[reportArgumentType]

    if hasattr(expr_str, "eval") and callable(expr_str.eval):
        return float(expr_str.eval(variables))  # pyright: ignore[reportArgumentType]

    cleaned = str(expr_str).strip().strip("'\"")
    cleaned = cleaned.replace("^", "**").replace("×", "*").replace("÷", "/")

    allowed_globals = {
        "__builtins__": None,
        "math": math,
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
        "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
        "exp": math.exp, "log": math.log, "log10": math.log10,
        "sqrt": math.sqrt, "pi": math.pi, "e": math.e, "abs": abs
    }
    try:
        return float(eval(cleaned, {**allowed_globals, **variables}))
    except Exception as exc:
        raise ValueError("Math ERROR")


@register("root_bisection", CAT_NUMERICAL, "Find root of an expression string within interval [a, b] using Bisection method", args=(3, 5), exact=True, example="root_bisection('x^3 - x - 2', 1, 2) => 1.521379709")
def root_bisection(expr_str, a, b, tol=1e-7, max_iter=100):
    a, b, tol = float(a), float(b), float(tol)
    max_iter = int(max_iter)

    fa = _eval_expr(expr_str, {"x": a})
    fb = _eval_expr(expr_str, {"x": b})
    if fa * fb > 0:
        raise ValueError("Math ERROR: Root not bracketed")

    c = a
    for _ in range(max_iter):
        c = (a + b) / 2.0
        fc = _eval_expr(expr_str, {"x": c})
        if abs(fc) < tol or (b - a) / 2.0 < tol:
            return c
        if fa * fc < 0:
            b = c
            fb = fc
        else:
            a = c
            fa = fc
    return c


@register("root_newton", CAT_NUMERICAL, "Find root using Newton-Raphson method given expression and initial guess x0", args=(2, 4), exact=True, example="root_newton('x^2 - 4', 3) => 2")
def root_newton(expr_str, x0, tol=1e-7, max_iter=100):
    x0, tol = float(x0), float(tol)
    max_iter = int(max_iter)

    def f(x_val):
        return _eval_expr(expr_str, {"x": x_val})

    h = 1e-5

    def df(x_val):
        return (f(x_val + h) - f(x_val - h)) / (2.0 * h)

    x = x0
    for _ in range(max_iter):
        fx = f(x)
        if abs(fx) < tol:
            return x
        dfx = df(x)
        if dfx == 0:
            raise ValueError("Math ERROR: Derivative zero")
        x = x - fx / dfx
    return x


@register("num_integrate_trap", CAT_NUMERICAL, "Numerical integration using Trapezoidal rule given expression, start a, end b, and intervals n", args=(3, 4), exact=True, example="num_integrate_trap('x^2', 0, 3, 100) => 9.00045")
def num_integrate_trap(expr_str, a, b, n=100):
    a, b, n = float(a), float(b), int(n)
    if n <= 0:
        raise ValueError("Math ERROR")
    h = (b - a) / n
    s = 0.5 * (_eval_expr(expr_str, {"x": a}) + _eval_expr(expr_str, {"x": b}))
    for i in range(1, n):
        s += _eval_expr(expr_str, {"x": a + i * h})
    return s * h


@register("num_integrate_simpson", CAT_NUMERICAL, "Numerical integration using Simpson's 1/3 rule given expression, start a, end b, and even intervals n", args=(3, 4), exact=True, example="num_integrate_simpson('x^2', 0, 3, 100) => 9")
def num_integrate_simpson(expr_str, a, b, n=100):
    a, b, n = float(a), float(b), int(n)
    if n <= 0 or n % 2 != 0:
        raise ValueError("Math ERROR")
    h = (b - a) / n
    s = _eval_expr(expr_str, {"x": a}) + _eval_expr(expr_str, {"x": b})
    for i in range(1, n):
        val = _eval_expr(expr_str, {"x": a + i * h})
        s += 4 * val if i % 2 != 0 else 2 * val
    return s * (h / 3.0)


@register("num_integrate_simpson38", CAT_NUMERICAL, "Numerical integration using Simpson's 3/8 rule given expression, start a, end b, and intervals n (multiple of 3)", args=(3, 4), exact=True, example="num_integrate_simpson38('x^2', 0, 3, 99) => 9")
def num_integrate_simpson38(expr_str, a, b, n=99):
    a, b, n = float(a), float(b), int(n)
    if n <= 0 or n % 3 != 0:
        raise ValueError("Math ERROR")
    h = (b - a) / n
    s = _eval_expr(expr_str, {"x": a}) + _eval_expr(expr_str, {"x": b})
    for i in range(1, n):
        val = _eval_expr(expr_str, {"x": a + i * h})
        s += 2 * val if i % 3 == 0 else 3 * val
    return s * (3.0 * h / 8.0)


@register("gauss_legendre_2", CAT_NUMERICAL, "Gauss-Legendre 2-point quadrature for numerical integration", args=(2, 3), exact=True, example="gauss_legendre_2('x^2', 0, 3) => 9")
def gauss_legendre_2(expr_str, a, b):
    a, b = float(a), float(b)
    c1 = 0.5 * (b - a)
    c2 = 0.5 * (b + a)
    x1 = -1.0 / math.sqrt(3.0)
    x2 = 1.0 / math.sqrt(3.0)
    val1 = _eval_expr(expr_str, {"x": c1 * x1 + c2})
    val2 = _eval_expr(expr_str, {"x": c1 * x2 + c2})
    return c1 * (val1 + val2)


@register("gauss_legendre_3", CAT_NUMERICAL, "Gauss-Legendre 3-point quadrature for numerical integration", args=(2, 3), exact=True, example="gauss_legendre_3('x^3', 0, 2) => 4")
def gauss_legendre_3(expr_str, a, b):
    a, b = float(a), float(b)
    c1 = 0.5 * (b - a)
    c2 = 0.5 * (b + a)
    x_nodes = [-math.sqrt(3.0 / 5.0), 0.0, math.sqrt(3.0 / 5.0)]
    weights = [5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0]
    s = sum(w * _eval_expr(expr_str, {"x": c1 * x + c2}) for x, w in zip(x_nodes, weights))
    return c1 * s


@register("lagrange_interpolation", CAT_NUMERICAL, "Lagrange interpolation to evaluate polynomial at target x given x points, y points, and target x", args=(3, 99), example="lagrange_interpolation(1, 2, 3, 1, 4, 9, 2.5) => 6.25")
def lagrange_interpolation(*args):
    flat = _parse_numeric_args(args)
    if len(flat) < 3:
        raise ValueError("Math ERROR")
    x_val = flat[-1]
    rem = flat[:-1]
    half = len(rem) // 2
    x_pts, y_pts = rem[:half], rem[half:]

    n = len(x_pts)
    if n != len(y_pts) or n == 0:
        raise ValueError("Math ERROR")

    total = 0.0
    for i in range(n):
        term = y_pts[i]
        for j in range(n):
            if i != j:
                if x_pts[i] == x_pts[j]:
                    raise ValueError("Math ERROR")
                term *= (x_val - x_pts[j]) / (x_pts[i] - x_pts[j])
        total += term
    return total


@register("newton_divided_diff", CAT_NUMERICAL, "Newton's divided difference interpolation polynomial evaluated at target x", args=(3, 99), example="newton_divided_diff(1, 2, 3, 1, 4, 9, 2.5) => 6.25")
def newton_divided_diff(*args):
    flat = _parse_numeric_args(args)
    if len(flat) < 3:
        raise ValueError("Math ERROR")
    x_val = flat[-1]
    rem = flat[:-1]
    half = len(rem) // 2
    x_pts, y_pts = rem[:half], rem[half:]

    n = len(x_pts)
    if n != len(y_pts) or n == 0:
        raise ValueError("Math ERROR")

    coef = list(y_pts)
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            den = x_pts[i] - x_pts[i - j]
            if den == 0:
                raise ValueError("Math ERROR")
            coef[i] = (coef[i] - coef[i - 1]) / den

    result = coef[n - 1]
    for k in range(n - 2, -1, -1):
        result = coef[k] + (x_val - x_pts[k]) * result
    return result


@register("newton_forward_diff", CAT_NUMERICAL, "Newton's forward difference interpolation for equally spaced points", args=(3, 99), example="newton_forward_diff(1, 2, 3, 1, 4, 9, 1.5) => 2.25")
def newton_forward_diff(*args):
    flat = _parse_numeric_args(args)
    if len(flat) < 3:
        raise ValueError("Math ERROR")
    x_val = flat[-1]
    rem = flat[:-1]
    half = len(rem) // 2
    x_pts, y_pts = rem[:half], rem[half:]

    n = len(x_pts)
    if n != len(y_pts) or n < 2:
        raise ValueError("Math ERROR")

    h = x_pts[1] - x_pts[0]
    u = (x_val - x_pts[0]) / h

    diff_table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        diff_table[i][0] = y_pts[i]

    for j in range(1, n):
        for i in range(n - j):
            diff_table[i][j] = diff_table[i + 1][j - 1] - diff_table[i][j - 1]

    def u_cal(u_val, k):
        temp = 1.0
        for i in range(k):
            temp *= (u_val - i)
        return temp

    sum_val = diff_table[0][0]
    factorial = 1.0
    for i in range(1, n):
        factorial *= i
        sum_val += (u_cal(u, i) * diff_table[0][i]) / factorial
    return sum_val


@register("newton_backward_diff", CAT_NUMERICAL, "Newton's backward difference interpolation for equally spaced points", args=(3, 99), example="newton_backward_diff(1, 2, 3, 1, 4, 9, 2.5) => 6.25")
def newton_backward_diff(*args):
    flat = _parse_numeric_args(args)
    if len(flat) < 3:
        raise ValueError("Math ERROR")
    x_val = flat[-1]
    rem = flat[:-1]
    half = len(rem) // 2
    x_pts, y_pts = rem[:half], rem[half:]

    n = len(x_pts)
    if n != len(y_pts) or n < 2:
        raise ValueError("Math ERROR")

    h = x_pts[1] - x_pts[0]
    u = (x_val - x_pts[n - 1]) / h

    diff_table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        diff_table[i][0] = y_pts[i]

    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            diff_table[i][j] = diff_table[i][j - 1] - diff_table[i - 1][j - 1]

    def u_cal_back(u_val, k):
        temp = 1.0
        for i in range(k):
            temp *= (u_val + i)
        return temp

    sum_val = diff_table[n - 1][0]
    factorial = 1.0
    for i in range(1, n):
        factorial *= i
        sum_val += (u_cal_back(u, i) * diff_table[n - 1][i]) / factorial
    return sum_val


@register("ode_euler", CAT_NUMERICAL, "Solve ODE dy/dx = f(x, y) using Euler's method given expression string, x0, y0, target x, and step count n", args=(4, 5), exact=True, example="ode_euler('x + y', 0, 1, 1, 10) => 3.18748492")
def ode_euler(expr_str, x0, y0, x_target, n=100):
    x0, y0, x_target, n = float(x0), float(y0), float(x_target), int(n)
    if n <= 0:
        raise ValueError("Math ERROR")
    h = (x_target - x0) / n
    x, y = x0, y0
    for _ in range(n):
        y += h * _eval_expr(expr_str, {"x": x, "y": y})
        x += h
    return y


@register("ode_rk4", CAT_NUMERICAL, "Solve ODE dy/dx = f(x, y) using 4th-order Runge-Kutta method", args=(4, 5), exact=True, example="ode_rk4('x + y', 0, 1, 1, 10) => 3.436559488")
def ode_rk4(expr_str, x0, y0, x_target, n=100):
    x0, y0, x_target, n = float(x0), float(y0), float(x_target), int(n)
    if n <= 0:
        raise ValueError("Math ERROR")
    h = (x_target - x0) / n
    x, y = x0, y0
    for _ in range(n):
        k1 = h * _eval_expr(expr_str, {"x": x, "y": y})
        k2 = h * _eval_expr(expr_str, {"x": x + 0.5 * h, "y": y + 0.5 * k1})
        k3 = h * _eval_expr(expr_str, {"x": x + 0.5 * h, "y": y + 0.5 * k2})
        k4 = h * _eval_expr(expr_str, {"x": x + h, "y": y + k3})
        y += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        x += h
    return y


# Global registry dictionary
