"""Checks: equations tables.  Run alone with  python run_tests.py equations_tables"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "equations_tables"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..errors import CalcError
from ..lib_equations_tables import _peval

from .helpers import _err, _expr_error  # noqa: F401


def checks_equations_tables_29(check, run, near, ex, text, _Fr, _it, bisect8, leibniz8, lit, nl, rg8, rnd, val8):
    """equation and table modes"""
    # ================= equation and table modes =================
    # --- simul: build a system with a known solution
    for n in (2, 2, 3, 3, 3, 4, 4, 5, 6):
        for _ in range(4):
            Am = rnd(n, n)
            if leibniz8(Am) == 0 if n <= 5 else False:
                continue
            xs = [rg8.randint(-9, 9) for _ in range(n)]
            bs = [sum(Am[i][j] * xs[j] for j in range(n)) for i in range(n)]
            aug = [Am[i] + [bs[i]] for i in range(n)]
            if n == 6 and abs(sum(map(abs, (v for r in Am for v in r)))) == 0:
                continue
            try:
                got = val8(f"simul({lit(aug)})")
            except CalcError:
                check(f"simul {n}x{n} singular case is a genuine singular matrix", n == 6, True)
                continue
            check(f"simul {n} unknowns recovers the solution", tuple(got), tuple(xs))
    ex("simul 2x2 hand", "simul({{2,1,3},{1,3,5}})", (_Fr(4, 5), _Fr(7, 5)))
    ex("simul 3x3 hand", "simul({{1,1,1,6},{0,2,5,-4},{2,5,-1,27}})", (5, 3, -2))
    for e in ["simul({{1,2,3},{2,4,6}})", "simul({{1,2,3},{2,4,7}})", "simul({{1,2},{3,4}})", "simul({{1,2,3}})", "simul({1,2,3})", "simul(5)", "simul({{i,1,1},{1,1,1}})", "simul({{1,2,3},{4,5}})"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR", "Syntax ERROR"), True)
    # --- poly_from_roots against elementary symmetric polynomials
    for _ in range(25):
        k = rg8.randint(1, 7)
        rts = [rg8.randint(-6, 6) for _ in range(k)]
        want = [(-1) ** j * sum(math.prod(c_) for c_ in _it.combinations(rts, j)) for j in range(k + 1)]
        ex("poly_from_roots vs Vieta", f"poly_from_roots({lit(rts)})", tuple(want))
    text("poly_from_roots with complex roots", "poly_from_roots({i, -i})", "{1, 0, 1}")
    text("poly_from_roots with a complex pair", "poly_from_roots({1+i, 1-i})", "{1, -2, 2}")
    # --- poly_roots: recovery of constructed roots, residuals, Vieta
    for _ in range(40):
        k = rg8.randint(1, 6)
        rts = sorted(rg8.sample([x / 2 for x in range(-12, 13)], k))
        cf = [float(v) for v in val8(f"poly_from_roots({lit(rts)})")]
        got = [complex(v) for v in val8(f"poly_roots({lit(cf)})")]
        check(f"poly_roots recovers {rts}", len(got) == k and all(abs(g.imag) < 1e-9 for g in got) and all(abs(g.real - w) < 1e-7 for g, w in zip(got, rts)), True)
    for _ in range(40):
        deg = rg8.randint(1, 8)
        cf = [rg8.choice([-1, 1]) * rg8.randint(1, 9) / rg8.choice([1, 2, 4]) for _ in range(deg + 1)]
        got = [complex(v) for v in val8(f"poly_roots({lit(cf)})")]
        check(f"poly_roots count is the degree ({deg})", len(got), deg)
        ok = all(abs(_peval(cf, z)) <= 1e-7 * sum(abs(v) * max(1.0, abs(z)) ** (deg - i) for i, v in enumerate(cf)) for z in got)
        check(f"poly_roots residuals are tiny {cf}", ok, True)
        check("Vieta: sum of roots", abs(sum(got) + cf[1] / cf[0]) < 1e-7 * max(1, abs(cf[1] / cf[0])), True)
        prod_ = 1
        for z in got:
            prod_ *= z
        check("Vieta: product of roots", abs(prod_ - (-1) ** deg * cf[-1] / cf[0]) < 1e-6 * max(1, abs(cf[-1] / cf[0])), True)
    text("x^2+1", "poly_roots({1,0,1})", "{-i, i}")
    text("x^3-1", "poly_roots({1,0,0,-1})", "{1, -0.5-0.8660254038i, -0.5+0.8660254038i}")
    text("x^4-1", "poly_roots({1,0,0,0,-1})", "{-1, 1, -i, i}")
    text("cubic 1,2,3", "poly_roots({1,-6,11,-6})", "{1, 2, 3}")
    text("quadratic", "poly_roots({2,-3,-2})", "{-0.5, 2}")
    text("linear", "poly_roots({4,-2})", "{0.5}")
    text("zero roots", "poly_roots({1,0,-1,0})", "{-1, 0, 1}")
    text("triple root exactly", "poly_roots({1,-3,3,-1})", "{1, 1, 1}")
    text("quartic double roots", "poly_roots({1,-2,-1,2,0})", "{-1, 0, 1, 2}")
    text("decimal triple root", "poly_roots({1,-0.3,0.03,-0.001})", "{0.1, 0.1, 0.1}")
    text("quintuple root", "poly_roots({1,-5,10,-10,5,-1})", "{1, 1, 1, 1, 1}")
    text("repeated pair", "poly_roots({1,0,-2,0,1})", "{-1, -1, 1, 1}")
    text("quadratic with complex roots", "poly_roots({1,2,5})", "{-1-2i, -1+2i}")
    text("x^4 = 0", "poly_roots({1,0,0,0,0})", "{0, 0, 0, 0}")
    check("roots of a degree-10 polynomial", len(val8("poly_roots({1,0,0,0,0,0,0,0,0,0,-1})")), 10)
    for e in ["poly_roots({0,1,2})", "poly_roots({5})", "poly_roots({1,2,3,4,5,6,7,8,9,10,11,12})", "poly_roots(5)", "poly_roots({1,i,1})", "poly_roots({{1,2},{3,4}})",
              "poly_from_roots(5)", "poly_from_roots({1,'a'})"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR", "Syntax ERROR"), True)
    # --- poly_ineq against sign sampling
    text("x^2-3x+2 > 0", "poly_ineq({1,-3,2},'>')", "(-inf, 1) U (2, inf)")
    text("x^2-3x+2 >= 0", "poly_ineq({1,-3,2},'>=')", "(-inf, 1] U [2, inf)")
    text("x^2-3x+2 < 0", "poly_ineq({1,-3,2},'<')", "(1, 2)")
    text("x^2-3x+2 <= 0", "poly_ineq({1,-3,2},'<=')", "[1, 2]")
    text("no real roots, positive", "poly_ineq({1,0,1},'>')", "all real numbers")
    text("no real roots, negative", "poly_ineq({1,0,1},'<')", "no solution")
    text("double root <= 0 is one point", "poly_ineq({1,-2,1},'<=')", "{1}")
    text("double root > 0 leaves out the point", "poly_ineq({1,-2,1},'>')", "(-inf, 1) U (1, inf)")
    text("double root >= 0 is everything", "poly_ineq({1,-2,1},'>=')", "all real numbers")
    text("triple root", "poly_ineq({1,-3,3,-1},'>')", "(1, inf)")
    text("cubic", "poly_ineq({1,0,-1,0},'>')", "(-1, 0) U (1, inf)")
    text("cubic <=", "poly_ineq({1,0,-1,0},'<=')", "(-inf, -1] U [0, 1]")
    text("unicode operators", "poly_ineq({1,-3,2},'≥')", "(-inf, 1] U [2, inf)")
    text("linear", "poly_ineq({2,-4},'<')", "(-inf, 2)")
    text("negative leading coefficient", "poly_ineq({-1,0,4},'>')", "(-2, 2)")
    text("irrational roots", "poly_ineq({1,0,-2},'<')", "(-1.414213562, 1.414213562)")

    def member(txt, x):
        if txt == "all real numbers":
            return True
        if txt == "no solution":
            return False
        for part in txt.split(" U "):
            if part.startswith("{"):
                if abs(x - float(part[1:-1])) < 1e-9:
                    return True
                continue
            lo_s, hi_s = part[1:-1].split(", ")
            lo = -math.inf if lo_s == "-inf" else float(lo_s)
            hi = math.inf if hi_s == "inf" else float(hi_s)
            lc, hc = part[0] == "[", part[-1] == "]"
            if (x > lo or (lc and x == lo)) and (x < hi or (hc and x == hi)):
                return True
        return False
    for _ in range(40):
        k = rg8.randint(1, 5)
        rts = sorted(rg8.sample(range(-8, 9), k))
        lead = rg8.choice([-2, -1, 1, 3])
        mult = [rg8.choice([1, 1, 2]) for _ in rts]
        flat = [r for r, m in zip(rts, mult) for _ in range(m)]
        cf = [lead * float(v) for v in val8(f"poly_from_roots({lit(flat)})")]
        for op in (">", ">=", "<", "<="):
            txt = run(f"poly_ineq({lit(cf)},'{op}')").text
            bad_pts = []
            for _s in range(60):
                x = rg8.uniform(-11, 11)
                if min(abs(x - r) for r in rts) < 1e-3:
                    continue
                v = _peval(cf, x)
                want = v > 0 if op[0] == ">" else v < 0
                if member(txt, x) != want:
                    bad_pts.append(x)
            for r in rts:                              # at a root the polynomial is 0: only non-strict operators hold
                if member(txt, float(r)) != (len(op) == 2):
                    bad_pts.append(float(r))
            check(f"poly_ineq {cf} {op} -> {txt}", bad_pts, [])
    for e in ["poly_ineq({1,2},'=')", "poly_ineq({1,2},5)", "poly_ineq({0,1,2},'>')", "poly_ineq({5},'>')", "poly_ineq(5,'>')", "poly_ineq({1,2})"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR", "Syntax ERROR"), True)
    # --- nsolve2
    nl("circle and line", "nsolve2('x^2+y^2-4','x-y',1,1)", [math.sqrt(2), math.sqrt(2)], 1e-10)
    nl("circle and line, other start", "nsolve2('x^2+y^2-4','x-y',-1,-2)", [-math.sqrt(2), -math.sqrt(2)], 1e-10)
    nl("parabola and line", "nsolve2('y-x^2','y-x-2',3,5)", [2, 4], 1e-10)
    nl("parabola and line, other root", "nsolve2('y-x^2','y-x-2',-2,1)", [-1, 1], 1e-10)
    nl("exp and line", "nsolve2('exp(x)-y','x+y-3',1,1)", [bisect8(lambda x: math.exp(x) + x - 3, 0, 2), 3 - bisect8(lambda x: math.exp(x) + x - 3, 0, 2)], 1e-9)
    nl("linear system by Newton", "nsolve2('2*x+y-5','x-y-1',0,0)", [2, 1], 1e-10)
    for xs_, ys_ in [(1, 2), (-3, 0.5), (2.5, -1.5)]:
        f1, f2 = f"x*y-({xs_ * ys_})", f"x+y-({xs_ + ys_})"
        got = [float(v) for v in val8(f"nsolve2('{f1}','{f2}',{xs_ + 0.4},{ys_ - 0.3})")]
        check(f"nsolve2 sum/product {xs_},{ys_}", all(abs(a - b) < 1e-8 for a, b in zip(sorted(got), sorted([xs_, ys_]))), True)
    for e in ["nsolve2('x^2+1','y',1,1)", "nsolve2('x','y','a',1)", "nsolve2('x^2+y^2+1','x',1,1)", "nsolve2('1/x','y',0,1)", "nsolve2('x',5,1,1)", "nsolve2('x','y',1)", "nsolve2('x','y',{1},1)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
    # --- table mode
    for expr_, fn_ in [("x^2", lambda x: x * x), ("sin(x)", lambda x: math.sin(math.radians(x))), ("2*x+1", lambda x: 2 * x + 1), ("sqrt(x)", math.sqrt)]:
        for a_, b_, st_ in [(0, 10, 1), (0, 1, 0.25), (1, 5, 2), (10, 0, -2.5), (0, 360, 45)]:
            rows = val8(f"table1('{expr_}',{a_},{b_},{st_})")
            xs_ = [a_ + k * st_ for k in range(int((b_ - a_) / st_ + 1e-9) + 1)]
            check(f"table1 {expr_} {a_}..{b_}", len(rows) == len(xs_) and all(abs(r[0] - x) < 1e-12 and abs(r[1] - fn_(x)) < 1e-9 for r, x in zip(rows, xs_)), True)
    rows = val8("table2('x^2','x^3',0,2,0.5)")
    check("table2 rows", [(r[0], r[1], r[2]) for r in rows], [(0, 0, 0), (_Fr(1, 2), 0.25, 0.125), (1, 1, 1), (_Fr(3, 2), 2.25, 3.375), (2, 4, 8)])
    check("table1 is a matrix", type(val8("table1('x',0,3,1)")).__name__, "Mat")
    check("table1 columns", val8("mat_cols(table1('x',0,3,1))"), 2)
    check("table2 columns", val8("mat_cols(table2('x','x',0,3,1))"), 3)
    check("table rows count", val8("mat_rows(table1('x',0,100,1))"), 101)
    text("table uses the angle mode", "table1('sin(x)',0,90,90)", "{{0, 0}, {90, 1}}")
    near("table feeds list functions", "list_sum(mat_col(table1('x^2',1,4,1),2))", 30, 1e-12)
    near("table feeds linreg", "linreg_slope(mat_col(table1('3*x+2',0,5,1),1),mat_col(table1('3*x+2',0,5,1),2))", 3, 1e-9)
    check("500 rows allowed", val8("mat_rows(table1('x',1,500,1))"), 500)
    for e in ["table1('x',0,10,0)", "table1('x',0,10,-1)", "table1('x',10,0,1)", "table1('x',1,501,1)", "table1('1/x',-1,1,1)", "table1('x',0,1)", "table1(5,0,1,1)", "table1('',0,1,1)",
              "table1('x',0,1,{1})", "table2('x','1/x',-1,1,1)", "table2('x',0,1,1)", "table2('x','y',0,1)", "table1('x',0,i,1)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
