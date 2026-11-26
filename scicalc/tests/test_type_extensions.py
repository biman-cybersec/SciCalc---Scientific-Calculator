"""Checks: type extensions.  Run alone with  python run_tests.py type_extensions"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "type_extensions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_type_extensions_37(check, run, ev, near, fn, lit, rg8):
    """type extensions: statistics returning lists, solve_all"""
    # ================= type extensions: statistics returning lists, solve_all =================
    import statistics as _st
    def lsv(expr):                                   # a list result as Python floats
        return [float(v) for v in run(expr).value]
    for _ in range(20):
        n = rg8.randint(3, 9)
        v = [round(rg8.uniform(-20, 20), 2) for _ in range(n)]
        L = lit(v)
        m, sd = _st.mean(v), _st.stdev(v)
        z = lsv(f"zscores({L})")
        check("zscores", all(abs(a - (x - m) / sd) < 1e-9 for a, x in zip(z, v)), True)
        check("zscores have mean 0 and sd 1", abs(_st.mean(z)) < 1e-9 and abs(_st.stdev(z) - 1) < 1e-9, True)
        mm = lsv(f"minmax_list({L})")
        check("minmax_list range", abs(min(mm)) < 1e-12 and abs(max(mm) - 1) < 1e-12, True)
        check("minmax_list values", all(abs(a - (x - min(v)) / (max(v) - min(v))) < 1e-9 for a, x in zip(mm, v)), True)
        r = lsv(f"ranks({L})")
        check("ranks add to n(n+1)/2", abs(sum(r) - n * (n + 1) / 2) < 1e-9, True)
        check("ranks agree with sorting", all(abs(r[i] - (sorted(v).index(v[i]) + 1)) < 1e-9 for i in range(n)), True)   # no ties in the 2-decimal sample unless equal
        k = rg8.randint(1, n)
        ma = lsv(f"moving_avg({L},{k})")
        check("moving_avg", len(ma) == n - k + 1 and all(abs(ma[i] - _st.mean(v[i:i + k])) < 1e-9 for i in range(len(ma))), True)
        al = rg8.choice([0.1, 0.3, 0.5, 0.9, 1])
        ew = lsv(f"ewma({L},{al})")
        ref, s_ = [], None
        for x in v:
            s_ = x if s_ is None else al * x + (1 - al) * s_
            ref.append(s_)
        check("ewma", all(abs(a - b) < 1e-9 for a, b in zip(ew, ref)), True)
        qs = lsv(f"quartiles({L})")
        check("quartiles agree with q1, median, q3", abs(qs[0] - ev(f"q1({L})")) < 1e-9 and abs(qs[1] - ev(f"median({L})")) < 1e-9 and abs(qs[2] - ev(f"q3({L})")) < 1e-9, True)
        fn = lsv(f"five_number({L})")
        check("five_number", abs(fn[0] - min(v)) < 1e-12 and abs(fn[4] - max(v)) < 1e-12 and abs(fn[2] - _st.median(v)) < 1e-9, True)
        ps = [0, 10, 33, 50, 99, 100]
        pc = lsv(f"percentiles({L},{lit(ps)})")
        check("percentiles agree with percentile()", all(abs(a - ev(f"percentile({p},{L})")) < 1e-9 for a, p in zip(pc, ps)), True)
        d = lsv(f"describe({L})")
        check("describe", d[0] == n and abs(d[1] - m) < 1e-9 and abs(d[2] - sd) < 1e-9 and d[3] == min(v) and d[4] == max(v), True)
        fe = lsv(f"outlier_fences({L})")
        check("outlier fences agree with iqr()", abs(fe[0] - (qs[0] - 1.5 * ev(f"iqr({L})"))) < 1e-9 and abs(fe[1] - (qs[2] + 1.5 * ev(f"iqr({L})"))) < 1e-9, True)
        pr = lsv(f"proportions({lit([abs(x) + 1 for x in v])})")
        check("proportions add to 1", abs(sum(pr) - 1) < 1e-9, True)
        b = rg8.randint(1, 6)
        hc = lsv(f"histogram_counts({L},{b})")
        lo, hi = min(v), max(v)
        brute = [0] * b
        for x in v:
            for j in range(b):
                a_, b_ = lo + (hi - lo) * j / b, lo + (hi - lo) * (j + 1) / b
                if a_ <= x < b_ or (j == b - 1 and x == hi):
                    brute[j] += 1
                    break
        check("histogram_counts", [int(c) for c in hc] == brute and sum(hc) == n, True)
        w = [round(rg8.uniform(-20, 20), 2) for _ in range(n)]
        if len(set(v)) > 1:
            lf = lsv(f"linreg_fit({L},{lit(w)})")
            sl, ic = _st.linear_regression(v, w)
            check("linreg_fit against statistics.linear_regression", abs(lf[0] - sl) < 1e-9 and abs(lf[1] - ic) < 1e-9, True)
            check("linreg_fit agrees with linreg_slope/intercept/r2", abs(lf[0] - ev(f"linreg_slope({L},{lit(w)})")) < 1e-9 and abs(lf[1] - ev(f"linreg_intercept({L},{lit(w)})")) < 1e-9 and abs(lf[2] - ev(f"linreg_r2({L},{lit(w)})")) < 1e-9, True)
            check("r2 is the squared correlation", abs(lf[2] - _st.correlation(v, w) ** 2) < 1e-9, True)
            pf1 = lsv(f"polyfit({L},{lit(w)},1)")
            check("polyfit degree 1 is the regression line (highest power first)", abs(pf1[0] - sl) < 1e-9 and abs(pf1[1] - ic) < 1e-9, True)
    # polyfit recovers exact polynomials, and its residuals are orthogonal to every power of x
    for coeffs in ([1, 0, 1], [2, -3, 0.5, 4], [-1.5, 2], [3]):
        deg = len(coeffs) - 1
        xs = [-2, -1, 0, 1, 2, 3, 4]
        ys = [sum(c * x ** (deg - i) for i, c in enumerate(coeffs)) for x in xs]
        got = lsv(f"polyfit({lit(xs)},{lit(ys)},{deg})")
        check(f"polyfit recovers {coeffs}", all(abs(a - b) < 1e-8 for a, b in zip(got, coeffs)), True)
    xs, ys = [0, 1, 2, 3, 4, 5], [1.2, 2.9, 5.1, 7.2, 8.8, 11.3]
    cf = lsv(f"polyfit({lit(xs)},{lit(ys)},2)")
    res = [y - sum(c * x ** (2 - i) for i, c in enumerate(cf)) for x, y in zip(xs, ys)]
    check("polyfit residuals are orthogonal to 1, x, x^2", all(abs(sum(r * x ** k for r, x in zip(res, xs))) < 1e-8 for k in range(3)), True)
    near("poly_roots takes polyfit output", "list_sum(poly_roots(polyfit({0,1,2,3},{1,0,1,4},2)))", 2, 1e-6)
    # covariance and correlation matrices
    rows = [[1, 2, 5], [2, 4.5, 3], [3, 5, 4], [4, 9, 1], [5, 9.5, 2]]
    cm = run(f"cov_matrix({lit(rows)})").value
    rm = run(f"corr_matrix({lit(rows)})").value
    cols = [[r[j] for r in rows] for j in range(3)]
    for i in range(3):
        for j in range(3):
            check(f"cov[{i}][{j}]", abs(float(cm[i][j]) - _st.covariance(cols[i], cols[j])) < 1e-9, True)
            check(f"corr[{i}][{j}]", abs(float(rm[i][j]) - _st.correlation(cols[i], cols[j])) < 1e-9, True)
    # solve_all against poly_roots and closed forms
    check("cubic roots", lsv("solve_all('x^3-6x^2+11x-6',0,5)") == [1.0, 2.0, 3.0], True)
    for coeffs in ([1, -3, 2], [1, 0, -4], [1, -6, 11, -6], [2, -3, -5, 6], [1, 0, -10, 0, 9]):
        pr = sorted(float(r) for r in run(f"poly_roots({lit(coeffs)})").value if abs(complex(r).imag) < 1e-12)
        expr = "+".join(f"({c})*x^{len(coeffs) - 1 - i}" for i, c in enumerate(coeffs))
        got = lsv(f"solve_all('{expr}',-10,10)")
        check(f"solve_all matches poly_roots for {coeffs}", len(got) == len(pr) and all(abs(a - b) < 1e-8 for a, b in zip(got, pr)), True)
    check("double root found", len(lsv("solve_all('(x-1)^2',-3,3)")) == 1 and abs(lsv("solve_all('(x-1)^2',-3,3)")[0] - 1) < 1e-6, True)
    check("sine roots in degrees", lsv("solve_all('sin(x)',0,360)") == [0.0, 180.0, 360.0], True)
    near("exp root", "list_sum(solve_all('exp(x)-2',-5,5))", math.log(2))
    rad = Calculator(); rad.set_angle("rad")
    check("cos x = x root", abs(float(rad.evaluate("solve_all('cos(x)-x',0,1)").value[0]) - 0.7390851332151607) < 1e-9, True)
    ufn = Calculator(); ufn.evaluate("sq2(x)=x^2-2")
    check("solve_all sees user functions", abs(float(ufn.evaluate("solve_all('sq2(x)',0,5)").value[0]) - math.sqrt(2)) < 1e-9, True)
    check("solve_all feeds list functions", abs(ev("list_len(solve_all('x^2-4',-5,5))") - 2) < 1e-12, True)
    check("pole is not a root", _err("solve_all('1/x',-2,2)") == "Math ERROR", True)
    for e in ["zscores({1})", "zscores({2,2,2})", "zscores(5)", "zscores({{1,2},{3,4}})", "minmax_list({3,3})", "proportions({1,-1})", "moving_avg({1,2,3},0)",
              "moving_avg({1,2,3},4)", "moving_avg({1,2,3},1.5)", "ewma({1,2},0)", "ewma({1,2},1.5)", "quartiles(3)", "percentiles({1,2,3},{101})",
              "percentiles({1,2,3},{-1})", "describe({1})", "outlier_fences(2)", "histogram_counts({1,2},0)", "histogram_counts({2,2},3)",
              "histogram_counts({1,2},1.5)", "linreg_fit({1,2},{1})", "linreg_fit({1,1},{1,2})", "linreg_fit({1},{1})", "polyfit({1,2,3},{1,2},1)",
              "polyfit({1,1,1},{1,2,3},1)", "polyfit({1,2,3},{1,2,3},9)", "polyfit({1,2},{1,2},-1)", "polyfit({1,2},{1,2},2)", "cov_matrix({1,2,3})",
              "cov_matrix({{1,2}})", "corr_matrix({{1,2},{1,3}})", "corr_matrix(5)", "solve_all('x',1,1)", "solve_all('x',2,1)", "solve_all('x^2+1',-5,5)",
              "solve_all(5,0,1)", "solve_all('x^2',0)", "solve_all('sin(x)',0,1e999)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR", "Syntax ERROR"), True)
