"""Checks: vectors complex text.  Run alone with  python run_tests.py vectors_complex_text"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "vectors_complex_text"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..arithmetic import Mat

from .helpers import _err, _expr_error  # noqa: F401


def checks_vectors_complex_text_14(check, run, ev, near, text, cmath):
    """vectors, matrices, complex, text results"""
    # ---------------------------------------------------------------- vectors, matrices, complex, text results
    def mtext(expr):
        v = run(expr).value
        return [list(r) for r in v] if isinstance(v, Mat) else list(v)

    A2 = [[3, -1], [2, 5]]
    B2 = [[4, 0], [-2, 7]]
    mm = lambda P, Q: [[sum(P[i][k] * Q[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    check("mat_mul2", mtext("mat_mul2(3,-1,2,5,4,0,-2,7)"), mm(A2, B2))
    check("mat_add2", mtext("mat_add2(3,-1,2,5,4,0,-2,7)"), [[7, -1], [0, 12]])
    check("mat_transpose2", mtext("mat_transpose2(3,-1,2,5)"), [[3, 2], [-1, 5]])
    check("mat_scalar_mul2", mtext("mat_scalar_mul2(3,3,-1,2,5)"), [[9, -3], [6, 15]])
    check("mat_pow2", mtext("mat_pow2(3,-1,2,5,3)"), mm(mm(A2, A2), A2))
    inv_ = mtext("mat_inv2(3,-1,2,5)")
    check("mat_inv2 times matrix is identity", all(abs(c_ - e_) < 1e-5 for r1, r2 in zip(mm(A2, inv_), [[1, 0], [0, 1]]) for c_, e_ in zip(r1, r2)), True)
    near("det2", "det2(3,-1,2,5)", 17)
    near("trace2", "trace2(3,-1,2,5)", 8)
    near("mat_rank2 full", "mat_rank2(3,-1,2,5)", 2)
    near("mat_rank2 deficient", "mat_rank2(1,2,2,4)", 1)
    near("mat_rank2 zero", "mat_rank2(0,0,0,0)", 0)
    lam = ev("eigenvalues2(4,1,2,3)")
    check("eigenvalues2 satisfies the characteristic polynomial", abs(lam * lam - 7 * lam + 10) < 1e-9, True)
    near("spectral_radius2", "spectral_radius2(4,1,2,3)", 5)
    near("is_idempotent2", "is_idempotent2(3,-6,1,-2)", 1)
    near("is_idempotent2 no", "is_idempotent2(1,2,3,4)", 0)
    near("is_nilpotent2", "is_nilpotent2(1,-1,1,-1)", 1)
    near("is_nilpotent2 no", "is_nilpotent2(1,2,3,4)", 0)
    M3 = [[2, -3, 1], [2, 0, -1], [1, 4, 5]]
    near("det3 by cofactors", "det3(2,-3,1,2,0,-1,1,4,5)",
         2 * (0 * 5 + 1 * 4) - (-3) * (2 * 5 + 1 * 1) + 1 * (2 * 4 - 0 * 1))
    u, v = (1, 2, 3), (-4, 5, 6)
    cr = mtext("cross3(1,2,3,-4,5,6)")
    check("cross3 is perpendicular to both", (sum(a * b for a, b in zip(cr, u)), sum(a * b for a, b in zip(cr, v))), (0, 0))  # pyright: ignore[reportArgumentType, reportCallIssue]
    check("cross3 values", cr, [2 * 6 - 3 * 5, 3 * -4 - 1 * 6, 1 * 5 - 2 * -4])
    near("dot2", "dot2(1,2,3,4)", 11)
    near("dot3", "dot3(1,2,3,-4,5,6)", 1 * -4 + 2 * 5 + 3 * 6)
    near("mag2", "mag2(6,8)", 10)
    near("mag3", "mag3(2,3,6)", 7)
    near("angle_vectors2", "angle_vectors2(1,0,1,1)", 45, 1e-9)
    near("vector_projection", "vector_projection(3,4,1,0)", 3)
    near("vector_proj3 (scale factor k in proj = k*v)", "vector_proj3(1,2,3,0,0,2)", 1.5)
    cx = lambda expr: complex(run(expr).value)
    for a, b, c, d in [(1, 2, 3, 4), (-2, 5, 0.5, -3), (0, 1, 1, 0)]:
        z1, z2 = complex(a, b), complex(c, d)
        check(f"c_add {a},{b},{c},{d}", abs(cx(f"c_add({a},{b},{c},{d})") - (z1 + z2)) < 1e-9, True)
        check(f"c_mul {a},{b},{c},{d}", abs(cx(f"c_mul({a},{b},{c},{d})") - z1 * z2) < 1e-9, True)
        check(f"c_div {a},{b},{c},{d}", abs(cx(f"c_div({a},{b},{c},{d})") - z1 / z2) < 1e-5, True)
        check(f"c_conj {a},{b}", abs(cx(f"c_conj({a},{b})") - z1.conjugate()) < 1e-9, True)
        near(f"c_mag {a},{b}", f"c_mag({a},{b})", abs(z1))
        near(f"c_arg {a},{b}", f"c_arg({a},{b})", math.degrees(cmath.phase(z1)), 1e-9)
        near(f"polar2rect_re {a},{b}", f"polar2rect_re(c_mag({a},{b}),c_arg({a},{b}))", a, 1e-9)
        near(f"polar2rect_im {a},{b}", f"polar2rect_im(c_mag({a},{b}),c_arg({a},{b}))", b, 1e-9)
    text("dms2deg/deg2dms", "deg2dms(45.5)", "45°30'0.0\"")
    near("dms2deg", "dms2deg(45,30,36)", 45 + 30 / 60 + 36 / 3600)
    near("dms2deg negative", "dms2deg(-10,15,0)", -(10 + 15 / 60))
    return {"cx": cx, "mtext": mtext}
