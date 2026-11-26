"""Checks: lists matrices.  Run alone with  python run_tests.py lists_matrices"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "lists_matrices"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import random

from ..errors import CalcError
from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_lists_matrices_25(check, run, ev, near, ex, text):
    """Sprint 8: list and matrix types"""
    # ================= Sprint 8: list and matrix types =================
    import itertools as _it
    from fractions import Fraction as _Fr
    rg8 = random.Random(11)

    def flat8(v):
        if isinstance(v, (tuple, list)):
            out = []
            for x in v:
                out.extend(flat8(x))
            return out
        return [float(v)]

    def nl(label, expr, want, tol=1e-9):
        try:
            got = flat8(run(expr).value)
        except CalcError as err:
            got = err.message
        w = flat8(want)
        ok = isinstance(got, list) and len(got) == len(w) and all(abs(a - b) <= tol * max(1.0, abs(b)) for a, b in zip(got, w))
        check(label, "ok" if ok else got, "ok" if ok else w)

    def val8(expr):
        return run(expr).value

    def lit(v):
        if isinstance(v, (list, tuple)):
            return "{" + ",".join(lit(x) for x in v) + "}"
        return str(v)

    # --- literals, shapes, display
    text("list display", "{1,2,3}", "{1, 2, 3}")
    text("matrix display", "{{1,2},{3,4}}", "{{1, 2}, {3, 4}}")
    text("list of fractions", "{1/2, 1/4}", "{0.5, 0.25}")
    text("list with expressions", "{1+1, 2*3, sqrt(16)}", "{2, 6, 4}")
    text("nested parentheses stay grouping", "[2+3]*(4)", "20")
    text("single element list", "{5}", "{5}")
    text("missing closing brace at the end is allowed", "{1,2", "{1, 2}")
    text("implicit multiplication with a list", "2{1,2}", "{2, 4}")
    text("list inside a function keeps display mode", "{1,2.5}", "{1, 2.5}")
    c8 = Calculator()
    c8.set_display("fix", 2)
    check("Fix display applies to every element", c8.evaluate("{1,2.5}").text, "{1.00, 2.50}")
    c8.evaluate("{1,2,3} -> A")
    check("a list can be stored in a variable", c8.evaluate("A*2").text, "{2.00, 4.00, 6.00}")
    check("Ans holds the list", c8.evaluate("{4,5}").text + c8.evaluate("Ans+1").text, "{4.00, 5.00}{5.00, 6.00}")
    # --- element-wise arithmetic against plain Python
    for _ in range(25):
        n = rg8.randint(1, 6)
        a = [rg8.randint(-9, 9) for _ in range(n)]
        b = [rg8.randint(1, 9) for _ in range(n)]
        k = rg8.randint(1, 9)
        ex("list + list", f"{lit(a)}+{lit(b)}", tuple(x + y for x, y in zip(a, b)))
        ex("list - list", f"{lit(a)}-{lit(b)}", tuple(x - y for x, y in zip(a, b)))
        ex("list * list is element-wise", f"{lit(a)}*{lit(b)}", tuple(x * y for x, y in zip(a, b)))
        ex("list / list exact", f"{lit(a)}/{lit(b)}", tuple(_Fr(x, y) if _Fr(x, y).denominator != 1 else int(_Fr(x, y)) for x, y in zip(a, b)))
        ex("list * scalar", f"{lit(a)}*{k}", tuple(x * k for x in a))
        ex("scalar - list", f"{k}-{lit(a)}", tuple(k - x for x in a))
        ex("negated list", f"-{lit(a)}", tuple(-x for x in a))
        ex("list ^ 2", f"{lit(a)}^2", tuple(x * x for x in a))
        ex("list squared postfix", f"{lit(a)}²", tuple(x * x for x in a))
    ex("list mod", "{7,8,9} mod 4", (3, 0, 1))
    ex("percent on a list", "{50,25}%", (_Fr(1, 2), _Fr(1, 4)))
    ex("factorial on a list", "{3,4}!", (6, 24))
    # --- matrix algebra against hand-written triple loops
    def mm(A, B):
        return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))) for i in range(len(A)))
    def rnd(r, c):
        return [[rg8.randint(-5, 5) for _ in range(c)] for _ in range(r)]
    for _ in range(20):
        r, m, c = rg8.randint(1, 4), rg8.randint(1, 4), rg8.randint(1, 4)
        A, B = rnd(r, m), rnd(m, c)
        ex("matrix product", f"{lit(A)}*{lit(B)}", mm(A, B))
        ex("mat_mul equals *", f"mat_mul({lit(A)},{lit(B)})", mm(A, B))
        ex("matrix + matrix", f"{lit(A)}+{lit(A)}", tuple(tuple(2 * v for v in row) for row in A))
        ex("transpose", f"mat_t({lit(A)})", tuple(zip(*A)))
        v = [rg8.randint(-5, 5) for _ in range(m)]
        ex("matrix times vector", f"{lit(A)}*{lit(v)}", tuple(sum(x * y for x, y in zip(row, v)) for row in A))
        w = [rg8.randint(-5, 5) for _ in range(r)]
        ex("vector times matrix", f"{lit(w)}*{lit(A)}", tuple(sum(w[i] * A[i][j] for i in range(r)) for j in range(m)))
    def leibniz8(M):
        n = len(M)
        tot = 0
        for p in _it.permutations(range(n)):
            sgn = 1
            for i in range(n):
                for j in range(i + 1, n):
                    if p[i] > p[j]:
                        sgn = -sgn
            term = sgn
            for i in range(n):
                term *= M[i][p[i]]
            tot += term
        return tot
    for n in (1, 2, 3, 4, 5):
        for _ in range(6):
            M = rnd(n, n)
            d = leibniz8(M)
            ex(f"mat_det {n}x{n} vs permutation expansion", f"mat_det({lit(M)})", d)
            if d != 0:
                inv = val8(f"mat_inv({lit(M)})")
                prod = mm(M, [[inv[i][j] for j in range(n)] for i in range(n)])
                check(f"M*inv(M) = I for {n}x{n}", all(prod[i][j] == int(i == j) for i in range(n) for j in range(n)), True)
                check("M^-1 equals mat_inv", val8(f"{lit(M)}^-1"), inv)
                check("M⁻¹ equals mat_inv", val8(f"{lit(M)}⁻¹"), inv)
                b = [rg8.randint(-5, 5) for _ in range(n)]
                x = val8(f"mat_solve({lit(M)},{lit(b)})")
                check(f"mat_solve satisfies A x = b ({n})", tuple(sum(M[i][j] * x[j] for j in range(n)) for i in range(n)), tuple(b))
            else:
                text(f"singular matrix has no inverse ({n})", f"mat_inv({lit(M)})", "Math ERROR")
    ex("mat_det uses 1x1", "mat_det({{7}})", 7)
    nl("mat_det of a float matrix", "mat_det({{0.5,1.5},{2,4}})", 0.5 * 4 - 1.5 * 2)
    nl("mat_inv of a float matrix", "mat_inv({{0.5,1},{2,4.5}})", [4.5 / 0.25, -1 / 0.25, -2 / 0.25, 0.5 / 0.25])
    F = [[0, 1], [1, 1]]
    def mpow8(M, k):
        R = [[int(i == j) for j in range(len(M))] for i in range(len(M))]
        for _ in range(k):
            R = [list(r) for r in mm(R, M)]
        return tuple(tuple(r) for r in R)
    for k in (0, 1, 2, 5, 12, 30):
        ex(f"matrix power {k} vs repeated product", f"{lit(F)}^{k}", mpow8(F, k))
    for M in ([[2, 1], [1, 1]], [[1, 2, 0], [0, 1, 3], [1, 0, 1]]):
        ex("M^-3 equals (M^3)^-1", f"{lit(M)}^-3", val8(f"mat_inv({lit(mpow8(M, 3))})"))
        ex("M² postfix equals M*M", f"{lit(M)}²", mpow8(M, 2))
        ex("M³ postfix equals M^3", f"{lit(M)}³", mpow8(M, 3))
        ex("mat_pow equals ^", f"mat_pow({lit(M)},4)", mpow8(M, 4))
    ex("fib matrix 30", "{{1,1},{1,0}}^30", ((1346269, 832040), (832040, 514229)))
    ex("matrix times identity", "{{1,2},{3,4}}*mat_eye(2)", ((1, 2), (3, 4)))
    # --- shape helpers
    ex("mat_eye 3", "mat_eye(3)", ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    ex("mat_zeros", "mat_zeros(2,3)", ((0, 0, 0), (0, 0, 0)))
    ex("mat_diag", "mat_diag({1,2,3})", ((1, 0, 0), (0, 2, 0), (0, 0, 3)))
    ex("mat_new row by row", "mat_new(2,3,{1,2,3,4,5,6})", ((1, 2, 3), (4, 5, 6)))
    ex("mat_flatten undoes mat_new", "mat_flatten(mat_new(3,2,{1,2,3,4,5,6}))", (1, 2, 3, 4, 5, 6))
    ex("mat_rows", "mat_rows({{1,2,3},{4,5,6}})", 2)
    ex("mat_cols", "mat_cols({{1,2,3},{4,5,6}})", 3)
    ex("mat_get", "mat_get({{1,2,3},{4,5,6}},2,3)", 6)
    ex("mat_row", "mat_row({{1,2,3},{4,5,6}},1)", (1, 2, 3))
    ex("mat_col", "mat_col({{1,2,3},{4,5,6}},3)", (3, 6))
    ex("mat_trace", "mat_trace({{1,2,3},{4,5,6},{7,8,9}})", 15)
    ex("transpose twice", "mat_t(mat_t({{1,2,3},{4,5,6}}))", ((1, 2, 3), (4, 5, 6)))
    ex("rank full", "mat_rank({{1,0},{0,1}})", 2)
    ex("rank deficient 3x3", "mat_rank({{1,2,3},{4,5,6},{7,8,9}})", 2)
    ex("rank of a wide matrix", "mat_rank({{1,2,3,4},{2,4,6,8}})", 1)
    ex("rank of zeros", "mat_rank(mat_zeros(2,2))", 0)
    ex("rref of a full-rank system", "mat_rref({{1,2,3},{4,5,6},{7,8,10}})", ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
    ex("rref of a rank-1 matrix", "mat_rref({{2,4},{1,2}})", ((1, 2), (0, 0)))
    ex("rref augmented system", "mat_rref({{1,1,3},{1,-1,1}})", ((1, 0, 2), (0, 1, 1)))
    ex("mat_solve exact fractions", "mat_solve({{2,1},{1,3}},{3,5})", (_Fr(4, 5), _Fr(7, 5)))
    nl("mat_norm_f", "mat_norm_f({{1,2},{2,4}})", 5.0)
    # --- list functions against Python
    for _ in range(15):
        n = rg8.randint(1, 8)
        a = [rg8.randint(-9, 9) for _ in range(n)]
        ex("list_len", f"list_len({lit(a)})", n)
        ex("list_sum", f"list_sum({lit(a)})", sum(a))
        ex("list_sort", f"list_sort({lit(a)})", tuple(sorted(a)))
        ex("list_sort descending", f"list_sort({lit(a)},1)", tuple(sorted(a, reverse=True)))
        ex("list_rev", f"list_rev({lit(a)})", tuple(reversed(a)))
        ex("list_cumsum", f"list_cumsum({lit(a)})", tuple(_it.accumulate(a)))
        pr = 1
        cp = []
        for v in a:
            pr *= v
            cp.append(pr)
        ex("list_prod", f"list_prod({lit(a)})", pr)
        ex("list_cumprod", f"list_cumprod({lit(a)})", tuple(cp))
        ex("list_unique", f"list_unique({lit(a)})", tuple(sorted(set(a))))
        ex("list_argmax", f"list_argmax({lit(a)})", a.index(max(a)) + 1)
        ex("list_argmin", f"list_argmin({lit(a)})", a.index(min(a)) + 1)
        ex("list_count", f"list_count({lit(a)},{a[0]})", a.count(a[0]))
        ex("list_index", f"list_index({lit(a)},{a[-1]})", a.index(a[-1]) + 1)
        i = rg8.randint(1, n)
        ex("list_get", f"list_get({lit(a)},{i})", a[i - 1])
        j = rg8.randint(i, n)
        ex("list_slice", f"list_slice({lit(a)},{i},{j})", tuple(a[i - 1:j]))
        if n >= 2:
            ex("list_diff", f"list_diff({lit(a)})", tuple(y - x for x, y in zip(a, a[1:])))
        b = [rg8.randint(-9, 9) for _ in range(n)]
        ex("list_dot", f"list_dot({lit(a)},{lit(b)})", sum(x * y for x, y in zip(a, b)))
        ex("list_concat", f"list_concat({lit(a)},{lit(b)})", tuple(a + b))
        ex("list_append", f"list_append({lit(a)},7)", tuple(a + [7]))
    ex("list_seq", "list_seq(6)", (1, 2, 3, 4, 5, 6))
    ex("list_fill", "list_fill(4,2)", (2, 2, 2, 2))
    ex("list_range up", "list_range(2,10,3)", (2, 5, 8))
    ex("list_range includes the end", "list_range(0,1,0.25)", (0, _Fr(1, 4), _Fr(1, 2), _Fr(3, 4), 1))
    ex("list_range down", "list_range(5,1,-2)", (5, 3, 1))
    ex("list_range default step", "list_range(3,6)", (3, 4, 5, 6))
    ex("list_range 0.1 steps are exact decimals", "list_range(0,0.3,0.1)", (0, _Fr(1, 10), _Fr(1, 5), _Fr(3, 10)))
    ex("list_linspace", "list_linspace(0,10,5)", (0, _Fr(5, 2), 5, _Fr(15, 2), 10))
    nl("list_map squares", "list_map('x^2', {1,2,3,4})", [1, 4, 9, 16])
    nl("list_map uses the angle mode", "list_map('sin(x)', {30,90})", [0.5, 1])
    # --- existing functions take lists
    cf = [-1000, 300, 400, 500]
    near("irr takes a list", f"irr({lit(cf)})", ev("irr(-1000,300,400,500)"), 1e-12)
    near("payback takes a list", f"payback({lit(cf)})", 2.6, 1e-12)
    near("npv takes the rate and a list", "npv(10,{-1000,300,400,500})", ev("npv(10,-1000,300,400,500)"), 1e-12)
    near("irr of a list built from functions", "irr(list_concat({-100},list_fill(3,40)))", ev("irr(-100,40,40,40)"), 1e-12)
    near("mean of a list", "mean({1,2,3,4})", 2.5, 1e-12)
    near("mean of two lists spliced", "mean({1,2},{3,4})", 2.5, 1e-12)
    near("stdev of a list", "stdev({2,4,4,4,5,5,7,9})", ev("stdev(2,4,4,4,5,5,7,9)"), 1e-12)
    near("median of a list", "median({3,1,2})", 2, 1e-12)
    near("max of a list and a number", "max({1,9,3},5)", 9, 1e-12)
    near("gcd of a list", "gcd({12,18,30})", 6, 1e-12)
    near("mean of a matrix uses every element", "mean({{1,2},{3,4}})", 2.5, 1e-12)
    near("linear regression on two lists", "linreg_slope({1,2,3,4},{2,4,6,8})", 2, 1e-9)
    near("det3 takes a matrix", "det3({{1,2,3},{4,5,6},{7,8,10}})", -3, 1e-12)
    near("det2 takes a matrix", "det2({{1,2},{3,4}})", -2, 1e-12)
    nl("sin of a list", "sin({0,30,90})", [0, 0.5, 1])
    nl("sqrt of a matrix is element-wise", "sqrt({{1,4},{9,16}})", [1, 2, 3, 4])
    nl("atan2 of two lists is element-wise", "atan2({1,0},{0,1})", [90, 0])
    nl("a scalar is repeated against a list", "atan2({1,1},1)", [45, 45])
    nl("round of a list", "round({1.4,2.6})", [1, 3])
    check("element-wise result keeps the list type", type(val8("sin({1,2})")).__name__, "Lst")
    check("element-wise result keeps the matrix type", type(val8("sin({{1,2},{3,4}})")).__name__, "Mat")
    text("a list of results prints with the display mode", "{1,2}/3", "{0.3333333333, 0.6666666667}")
    # --- errors
    for e in ["{}", "{1,", "{1,2)", "{1,,2}", "(1,2}", "{1 2}", "}", "{{}"]:
        check(f"syntax {e}", _err(e) in ("Syntax ERROR", ""), True)
    for e in ["{1,2}+{1,2,3}", "{{1,2},{3,4}}+{1,2}", "{{1,2},{3}}", "{1,{2,3}}", "{{1,2},{3,4}}*{1,2,3}", "{1,2}*{{1,2},{3,4},{5,6}}",
              "{{1,2,3},{4,5,6}}*{{1,2,3},{4,5,6}}", "{{1,2},{3,4}}^0.5", "{{1,2,3},{4,5,6}}^2", "2^{{1,2},{3,4}}", "1/{{1,2},{3,4}}",
              "{{1,2},{3,4}}/{{1,2},{3,4}}", "{{1,2,3},{4,5,6}}⁻¹", "{{1,2},{2,4}}⁻¹", "{{1,2},{3,4}}^2000", "{1,2}+'a'",
              "sqrt({-1,4})", "{0,1}⁻¹", "ln({1,0})", "atan2({1,2},{1,2,3})", "sin({1,2},{1,2})", "{1,2}^{1,2,3}"]:
        check(f"bad list input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
    for e in ["list_get({1,2},0)", "list_get({1,2},3)", "list_get({1,2},1.5)", "list_get(5,1)", "list_slice({1,2,3},3,2)", "list_slice({1,2,3},0,2)",
              "list_slice({1,2,3},1,4)", "list_sort(5)", "list_sort({1,2},{1})", "list_rev(5)", "list_sum(5)", "list_sum({{1,2},{3,4}})", "list_prod(5)",
              "list_cumsum(5)", "list_cumprod(5)", "list_diff({1})", "list_diff(5)", "list_seq(0)", "list_seq(10001)", "list_seq(1.5)", "list_seq({1,2})",
              "list_range(1,5,0)", "list_range(1,5,-1)", "list_range(5,1)", "list_range(1,100000)", "list_range({1},2)", "list_linspace(0,1,1)",
              "list_linspace(0,1,10001)", "list_concat(1,{2})", "list_concat({1},2)", "list_append(1,2)", "list_append({1},{2})", "list_fill(0,1)",
              "list_fill(2,{1})", "list_dot({1,2},{1})", "list_dot(1,2)", "list_map('x',5)", "list_map('1/x',{0})", "list_map('x',{1},{2})", "list_argmax(5)",
              "list_argmin(5)", "list_index({1,2},3)", "list_index(5,3)", "list_count(5,1)", "list_unique(5)", "list_len(5)",
              "mat_new(2,2,{1,2,3})", "mat_new(0,2,{1})", "mat_new(2,2,5)", "mat_eye(0)", "mat_eye(101)", "mat_eye(1.5)", "mat_zeros(0,1)", "mat_zeros(1,0)",
              "mat_diag(5)", "mat_rows({1,2})", "mat_cols(5)", "mat_get({{1,2}},2,1)", "mat_get({{1,2}},1,3)", "mat_get({1,2},1,1)", "mat_row({{1,2}},2)",
              "mat_col({{1,2}},3)", "mat_t({1,2})", "mat_flatten({1,2})", "mat_trace({{1,2,3},{4,5,6}})", "mat_det({{1,2,3},{4,5,6}})", "mat_det({1,2})",
              "mat_inv({{1,2,3},{4,5,6}})", "mat_inv({{0,0},{0,0}})", "mat_rank(5)", "mat_mul({{1,2}},{{1,2}})", "mat_mul(1,2)", "mat_pow({{1,2}},2)",
              "mat_pow({{1,2},{3,4}},1.5)", "mat_pow({{1,2},{3,4}},1001)", "mat_pow({{1,2},{2,4}},-1)", "mat_solve({{1,2},{2,4}},{1,2})",
              "mat_solve({{1,2},{3,4}},{1})", "mat_solve({{1,2},{3,4}},5)", "mat_rref(5)", "mat_norm_f({1,2})"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
    return {"_Fr": _Fr, "_it": _it, "flat8": flat8, "leibniz8": leibniz8, "lit": lit, "nl": nl, "rg8": rg8, "rnd": rnd, "val8": val8}


def checks_lists_matrices_28(check, near, ex, flat8, leibniz8, lit, rg8, rnd, val8):
    """old matrix functions now return real matrices/lists"""
    # ================= old matrix functions now return real matrices/lists =================
    for _ in range(12):
        A = rnd(3, 3)
        B = rnd(3, 3)
        flatA, flatB = ",".join(str(v) for r in A for v in r), ",".join(str(v) for r in B for v in r)
        ex("mat_mul3 returns a matrix", f"mat_mul3({flatA},{flatB})", tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3)))
        ex("mat_mul3 equals the * operator", f"mat_mul3({lit(A)},{lit(B)})", val8(f"{lit(A)}*{lit(B)}"))
        ex("mat_add3 equals +", f"mat_add3({lit(A)},{lit(B)})", val8(f"{lit(A)}+{lit(B)}"))
        ex("mat_transpose3 equals mat_t", f"mat_transpose3({lit(A)})", val8(f"mat_t({lit(A)})"))
        ex("mat_scalar3 equals scalar *", f"mat_scalar3(3,{lit(A)})", val8(f"3*{lit(A)}"))
        ex("mat_pow3 equals ^", f"mat_pow3({lit(A)},3)", val8(f"{lit(A)}^3"))
        ex("trace3 takes a matrix", f"trace3({lit(A)})", sum(A[i][i] for i in range(3)))
        ex("det3 takes a matrix", f"det3({lit(A)})", leibniz8(A))
        if leibniz8(A) != 0:
            check("mat_inv3 equals mat_inv", all(abs(x - y) < 1e-8 for x, y in zip(flat8(val8(f"mat_inv3({lit(A)})")), flat8(val8(f"mat_inv({lit(A)})")))), True)
        P = rnd(2, 2)
        Q = rnd(2, 2)
        fp, fq = ",".join(str(v) for r in P for v in r), ",".join(str(v) for r in Q for v in r)
        ex("mat_mul2 returns a matrix", f"mat_mul2({fp},{fq})", tuple(tuple(sum(P[i][k] * Q[k][j] for k in range(2)) for j in range(2)) for i in range(2)))
        ex("mat_mul2 takes matrices", f"mat_mul2({lit(P)},{lit(Q)})", val8(f"{lit(P)}*{lit(Q)}"))
        ex("mat_transpose2 equals mat_t", f"mat_transpose2({lit(P)})", val8(f"mat_t({lit(P)})"))
        ex("mat_add2 equals +", f"mat_add2({lit(P)},{lit(Q)})", val8(f"{lit(P)}+{lit(Q)}"))
        u, v = [rg8.randint(-5, 5) for _ in range(3)], [rg8.randint(-5, 5) for _ in range(3)]
        cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        ex("cross3 returns a list", f"cross3({lit(u)},{lit(v)})", cr)
        ex("cross3 result usable in list functions", f"list_dot(cross3({lit(u)},{lit(v)}),{lit(u)})", 0)
    check("old and new inverse compose to identity", val8("mat_inv2(4,7,2,6)*{{4,7},{2,6}}"), ((1, 0), (0, 1)))
    check("ci result is a list", type(val8("ci_z_mean(50,5,30,0.95)")).__name__, "Lst")
    near("ci interval is centred on the mean", "list_sum(ci_z_mean(50,5,30,0.95))/2", 50, 1e-9)
    near("ci interval element access", "list_get(ci_proportion(45,100,0.95),1)", 0.352493023, 1e-8)
