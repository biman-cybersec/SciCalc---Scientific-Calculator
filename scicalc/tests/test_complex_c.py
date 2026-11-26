"""Checks: complex c.  Run alone with  python run_tests.py complex_c"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "complex_c"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_complex_c_21(check, run, ev, near, ex, text, cx):
    """Sprint 5 : complex numbers"""
    # ---------------------------------------------------------------- Sprint 5 : complex numbers
    zs = [(3, 4), (-2, 5), (0.5, -1.5), (-1, -1), (2, 0), (0, 1), (1.2, 0.7)]
    for (a, b) in zs:
        z = complex(a, b)
        tag = f"{a},{b}"
        near(f"c_abs2({tag})", f"c_abs2({tag})", a * a + b * b, 1e-12)
        check(f"c_recip({tag}) times z is 1", abs(cx(f"c_recip({tag})") * z - 1) < 1e-8, True)
        check(f"c_sqrt({tag}) squared", abs(cx(f"c_sqrt({tag})") ** 2 - z) < 1e-8, True)
        check(f"c_sqrt({tag}) is the principal root (Re >= 0)", cx(f"c_sqrt({tag})").real >= -1e-12, True)
        check(f"c_exp(c_ln({tag})) returns z", abs(cx(f"c_exp({cx(f'c_ln({tag})').real!r},{cx(f'c_ln({tag})').imag!r})") - z) < 1e-6, True)
        lnz = cx(f"c_ln({tag})")
        check(f"c_ln({tag}) = ln|z| + i arg z", abs(lnz - complex(math.log(math.hypot(a, b)), math.atan2(b, a))) < 1e-8, True)
        check(f"c_exp({tag}) by Euler", abs(cx(f"c_exp({tag})") - math.exp(a) * complex(math.cos(b), math.sin(b))) < 1e-8, True)
        check(f"c_sin({tag})", abs(cx(f"c_sin({tag})") - complex(math.sin(a) * math.cosh(b), math.cos(a) * math.sinh(b))) < 1e-8, True)
        check(f"c_cos({tag})", abs(cx(f"c_cos({tag})") - complex(math.cos(a) * math.cosh(b), -math.sin(a) * math.sinh(b))) < 1e-8, True)
        sn = complex(math.sin(a) * math.cosh(b), math.cos(a) * math.sinh(b))
        cs = complex(math.cos(a) * math.cosh(b), -math.sin(a) * math.sinh(b))
        check(f"c_tan({tag}) = sin/cos", abs(cx(f"c_tan({tag})") - sn / cs) < 1e-7 * max(1, abs(sn / cs)), True)
        shz = complex(math.sinh(a) * math.cos(b), math.cosh(a) * math.sin(b))
        chz = complex(math.cosh(a) * math.cos(b), math.sinh(a) * math.sin(b))
        check(f"c_sinh({tag})", abs(cx(f"c_sinh({tag})") - shz) < 1e-8, True)
        check(f"c_cosh({tag})", abs(cx(f"c_cosh({tag})") - chz) < 1e-8, True)
        check(f"c_tanh({tag}) = sinh/cosh", abs(cx(f"c_tanh({tag})") - shz / chz) < 1e-7 * max(1, abs(shz / chz)), True)
        check(f"cosh^2 - sinh^2 = 1 ({tag})", abs(chz * chz - shz * shz - 1) < 1e-9, True)
        for nm_, back in (("asin", "c_sin"), ("acos", "c_cos"), ("atan", "c_tan")):
            if nm_ == "atan" and (a, b) in ((0, 1), (0, -1)):
                check(f"c_atan({tag}) is a pole", _err(f"c_atan({tag})"), "Math ERROR")
                continue
            w = cx(f"c_{nm_}({tag})")
            check(f"{back}(c_{nm_}({tag})) returns z", abs(cx(f"{back}({w.real!r},{w.imag!r})") - z) < 1e-6 * max(1, abs(z)), True)
        for n_ in (0, 1, 2, 5, -3):
            want = 1 + 0j
            for _ in range(abs(n_)):
                want *= z
            if n_ < 0:
                want = 1 / want
            check(f"c_pow_n({tag},{n_}) by repeated multiplication", abs(cx(f"c_pow_n({tag},{n_})") - want) < 1e-6 * max(1, abs(want)), True)
        r_, t_ = text_polar = run(f"c_polar({tag})").text.split("∠")
        check(f"c_polar({tag}) modulus", abs(float(r_) - math.hypot(a, b)) < 1e-8, True)
        check(f"c_polar({tag}) angle", abs(float(t_) - math.degrees(math.atan2(b, a))) < 1e-7, True)
        check(f"c_from_polar(c_polar({tag})) round trip", abs(cx(f"c_from_polar({r_},{t_})") - z) < 1e-6, True)
        for (c_, d_) in [(1, 2), (-0.5, 3), (2, 0)]:
            w = complex(c_, d_)
            check(f"c_sub({tag},{c_},{d_})", abs(cx(f"c_sub({tag},{c_},{d_})") - (z - w)) < 1e-9, True)
            lnr, th = math.log(math.hypot(a, b)), math.atan2(b, a)
            if (a, b) != (0, 0):
                mod = math.exp(c_ * lnr - d_ * th)
                arg = d_ * lnr + c_ * th
                check(f"c_pow({tag},{c_},{d_}) = exp(w ln z)", abs(cx(f"c_pow({tag},{c_},{d_})") - mod * complex(math.cos(arg), math.sin(arg))) < 1e-7 * max(1, mod), True)
    text("c_polar 3+4i", "c_polar(3,4)", "5∠53.130102354")
    text("c_polar negative real", "c_polar(-2,0)", "2∠180")
    ex("c_pow 0^2", "c_pow(0,0,2,0)", 0)
    for (a, b, n) in [(-8, 0, 3), (1, 1, 4), (16, 0, 4), (0, 1, 2), (3, -4, 5)]:
        z = complex(a, b)
        roots = [cx(f"c_nth_root({a},{b},{n},{k})") for k in range(n)]
        check(f"c_nth_root({a},{b},{n}) every root raised to n gives z", all(abs(r ** n - z) < 1e-6 * max(1, abs(z)) for r in roots), True)
        check(f"c_nth_root({a},{b},{n}) roots are distinct", len({(round(r.real, 6), round(r.imag, 6)) for r in roots}) == n, True)
        check(f"c_nth_root({a},{b},{n}) k=0 is the principal root", abs(roots[0] - abs(z) ** (1 / n) * complex(math.cos(math.atan2(b, a) / n), math.sin(math.atan2(b, a) / n))) < 1e-8, True)
        check(f"c_nth_root({a},{b},{n}) roots sum to zero (n>1)", n == 1 or abs(sum(roots)) < 1e-6 * max(1, abs(z) ** (1 / n)), True)
    for n in (1, 2, 3, 4, 6, 8, 12):
        roots = [cx(f"c_roots_unity({n},{k})") for k in range(n)]
        for k, r in enumerate(roots):
            check(f"c_roots_unity({n},{k})", abs(r - complex(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n))) < 1e-8, True)
        check(f"c_roots_unity({n}) sum to 0 (n>1)", n == 1 or abs(sum(roots)) < 1e-8, True)
        check(f"c_roots_unity({n}) product is (-1)^(n+1)", abs(math.prod(roots) - (-1) ** (n + 1)) < 1e-7, True)
    for (a, b, c) in [(1, 2, 5), (1, -3, 2), (2, 0, 8), (1, 0, 1), (0.5, 1, 3), (3, -2, -1)]:
        r1, r2 = cx(f"c_quad_root1({a},{b},{c})"), cx(f"c_quad_root2({a},{b},{c})")
        check(f"quadratic ({a},{b},{c}): roots add to -b/a", abs(r1 + r2 + b / a) < 1e-8, True)
        check(f"quadratic ({a},{b},{c}): roots multiply to c/a", abs(r1 * r2 - c / a) < 1e-8, True)
        check(f"quadratic ({a},{b},{c}): root1 solves it", abs(a * r1 * r1 + b * r1 + c) < 1e-7, True)
        check(f"quadratic ({a},{b},{c}): root2 solves it", abs(a * r2 * r2 + b * r2 + c) < 1e-7, True)
        if b * b - 4 * a * c >= 0:
            check(f"quadratic ({a},{b},{c}) real: root1 agrees with quad_root1", abs(r1.real - ev(f"quad_root1({a},{b},{c})")) < 1e-8 and abs(r1.imag) < 1e-12, True)
    text("c_quad_root1 complex", "c_quad_root1(1,2,5)", "-1+2i")
    text("c_quad_root2 complex", "c_quad_root2(1,2,5)", "-1-2i")
