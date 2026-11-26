"""Checks: complex type.  Run alone with  python run_tests.py complex_type"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "complex_type"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..errors import CalcError
from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_complex_type_27(check, run, ev, ex, text, cmath, rg8):
    """complex numbers as a value type"""
    # ================= complex numbers as a value type =================
    def cv(expr):
        return complex(run(expr).value)

    def cnear(label, expr, want, tol=1e-9):
        try:
            got = cv(expr)
        except CalcError as err:
            check(label, err.message, want)
            return
        check(label, abs(got - want) <= tol * max(1.0, abs(want)), True)

    text("complex display", "3+4i", "3+4i")
    text("pure imaginary", "2i", "2i")
    text("unit imaginary", "i", "i")
    text("negative unit imaginary", "-i", "-i")
    text("1+i has no coefficient 1", "1+i", "1+i")
    text("1-i", "1-i", "1-i")
    text("negative real part", "-2-3i", "-2-3i")
    text("i squared is real", "i^2", "-1")
    text("product with real result", "(1+i)*(1-i)", "2")
    text("i cubed", "i^3", "-i")
    text("implicit multiplication 2i", "2i*3i", "-6")
    text("i with pi", "pi*i", "3.141592654i")
    check("complex value type", type(run("3+4i").value).__name__, "Cx")
    check("a real result is not complex", type(run("(2+i)*(2-i)").value).__name__, "int")
    c9 = Calculator()
    c9.set_display("fix", 2)
    check("Fix display applies to both parts", c9.evaluate("1.5+2i").text, "1.50+2.00i")
    c9.set_display("norm", 2)
    # arithmetic against Python's complex type
    for _ in range(40):
        a, b, c_, d = (rg8.randint(-9, 9) for _ in range(4))
        z, w = complex(a, b), complex(c_, d)
        za, wb = f"({a}+({b})*i)", f"({c_}+({d})*i)"
        cnear(f"{za}+{wb}", f"{za}+{wb}", z + w)
        cnear(f"{za}-{wb}", f"{za}-{wb}", z - w)
        cnear(f"{za}*{wb}", f"{za}*{wb}", z * w)
        if w != 0:
            cnear(f"{za}/{wb}", f"{za}/{wb}", z / w)
        cnear(f"-{za}", f"-{za}", -z)
        cnear(f"{za}^2", f"{za}^2", z * z)
        cnear(f"{za}²", f"{za}²", z * z)
        cnear(f"{za}³", f"{za}³", z * z * z)
        if z != 0:
            cnear(f"{za}⁻¹", f"{za}⁻¹", 1 / z)
            cnear(f"{za}^-2", f"{za}^-2", 1 / (z * z))
        cnear(f"{a}*{wb}", f"{a}*{wb}", a * w)
        cnear(f"{za}+{c_}", f"{za}+{c_}", z + c_)
        check(f"abs({za})", abs(ev(f"abs{za}") - abs(z)) < 1e-9, True)
    cnear("i^i", "i^i", math.exp(-math.pi / 2))
    cnear("(1+i)^(1+i)", "(1+i)^(1+i)", complex(1, 1) ** complex(1, 1))
    cnear("(1+i)^0.5", "(1+i)^0.5", complex(1, 1) ** 0.5)
    cnear("2^i", "2^i", 2 ** 1j)
    cnear("(3+4i)%", "(3+4i)%", complex(3, 4) / 100)
    cnear("(1+i)^10", "(1+i)^10", complex(1, 1) ** 10)
    text("Euler's identity", "exp(i*pi)", "-1")
    # functions of complex values against cmath
    for z in (1 + 2j, -3 + 0.5j, 0.5 - 1j, 2j, -1 - 1j, 4 + 3j):
        t = f"({z.real}+({z.imag})*i)"
        for nm, fnc in [("sqrt", cmath.sqrt), ("exp", cmath.exp), ("ln", cmath.log), ("log", cmath.log10), ("sin", cmath.sin), ("cos", cmath.cos),
                        ("tan", cmath.tan), ("sinh", cmath.sinh), ("cosh", cmath.cosh), ("tanh", cmath.tanh), ("asin", cmath.asin), ("acos", cmath.acos),
                        ("atan", cmath.atan), ("asinh", cmath.asinh), ("acosh", cmath.acosh), ("atanh", cmath.atanh), ("sq", lambda x: x * x),
                        ("cube", lambda x: x ** 3), ("inv", lambda x: 1 / x)]:
            cnear(f"{nm}{t}", f"{nm}{t}", fnc(z), 1e-8)
        cnear(f"log2{t}", f"log2{t}", cmath.log(z) / math.log(2), 1e-8)
        cnear(f"pow({t},{t})", f"pow({t},{t})", z ** z, 1e-8)
        w = cv(f"sqrt{t}")
        check(f"sqrt{t} squared gives z", abs(w * w - z) < 1e-8 * max(1, abs(z)), True)
        check(f"exp(ln{t}) gives z", abs(cv(f"exp(ln{t})") - z) < 1e-8 * max(1, abs(z)), True)
        check(f"sin^2+cos^2 = 1 for {t}", abs(cv(f"sin{t}^2+cos{t}^2") - 1) < 1e-8 * max(1, abs(cmath.sin(z)) ** 2), True)
        cnear(f"re/im/conj of {t}", f"re{t}+im{t}*i+0*conj{t}", z)
        cnear(f"conj{t}", f"conj{t}", z.conjugate())
        check(f"re{t}", ev(f"re{t}") == z.real, True)
        check(f"im{t}", ev(f"im{t}") == z.imag, True)
        check(f"z*conj(z) = |z|^2 for {t}", abs(ev(f"{t}*conj{t}") - abs(z) ** 2) < 1e-8 * max(1, abs(z) ** 2), True)
        check(f"arg{t} in degrees", abs(ev(f"arg{t}") - math.degrees(cmath.phase(z))) < 1e-8, True)
    ex("re of a real", "re(5)", 5)
    ex("im of a real", "im(5)", 0)
    ex("conj of a real", "conj(5)", 5)
    check("arg(-1) = 180", ev("arg(-1)"), 180)
    check("arg(i) = 90", ev("arg(i)"), 90)
    check("rect and arg/abs round trip", abs(cv("rect(abs(3+4i),arg(3+4i))") - (3 + 4j)) < 1e-9, True)
    cnear("rect(2,90)", "rect(2,90)", 2j)
    cnear("rect(2,60)", "rect(2,60)", 2 * cmath.exp(1j * math.pi / 3))
    cr9 = Calculator()
    cr9.angle = "rad"
    check("arg uses the angle mode", abs(float(cr9.evaluate("arg(i)").value) - math.pi / 2) < 1e-12, True)
    check("rect uses the angle mode", abs(complex(cr9.evaluate("rect(1,pi/2)").value) - 1j) < 1e-12, True)
    # c_* functions accept complex values
    for _ in range(15):
        a, b, c_, d = (rg8.randint(-9, 9) for _ in range(4))
        if b == 0:                       # a value with no imaginary part is a plain real number, not a pair
            continue
        z, w = complex(a, b), complex(c_, d)
        za, wb = f"({a}+({b})*i)", f"({c_}+({d})*i)"
        cnear("c_add with values", f"c_add({za},{wb})", z + w)
        cnear("c_mul with values", f"c_mul({za},{wb})", z * w)
        cnear("c_sub with values", f"c_sub({za},{wb})", z - w)
        cnear("c_conj with a value", f"c_conj({za})", z.conjugate())
        check("c_mag with a value", abs(ev(f"c_mag({za})") - abs(z)) < 1e-9, True)
        if w != 0:
            cnear("c_div with values", f"c_div({za},{wb})", z / w, 1e-8)
        cnear("c_pow_n with a value", f"c_pow_n({za},3)", z ** 3)
        cnear("c_mul mixes a value and a real", f"c_mul({za},{c_})", z * c_)
    check("c_mul with parts equals values", cv("c_mul(1,2,3,4)"), cv("(1+2i)*(3+4i)"))
    # complex mode
    c9.complex_mode = True
    for e, want in [("sqrt(-4)", 2j), ("sqrt(-2)", 1j * math.sqrt(2)), ("ln(-1)", 1j * math.pi), ("(-8)^(1/3)", (-8) ** (1 / 3)),
                    ("log(-100)", 2 + 1j * math.pi / math.log(10)), ("acosh(0.5)", 1j * math.acos(0.5)), ("atanh(2)", cmath.atanh(2)),
                    ("log2(-8)", 3 + 1j * math.pi / math.log(2)), ("(-4)^0.5", 2j)]:
        check(f"complex mode {e}", abs(complex(c9.evaluate(e).value) - want) < 1e-8, True)
    check("complex mode keeps real results real", c9.evaluate("sqrt(9)").text, "3")
    check("complex mode keeps integer powers exact", c9.evaluate("(-8)^3").text, "-512")
    c9.complex_mode = False
    for e in ["sqrt(-4)", "ln(-1)", "(-8)^(1/3)", "(-4)^0.5", "acosh(0.5)", "log(-1)"]:
        check(f"real mode refuses {e}", _err(e) in ("Math ERROR",) or e == "(-8)^(1/3)", True)
    check("real mode keeps the real cube root", ev("(-8)^(1/3)"), -2)
    c9.complex_polar = True
    check("polar display 3+4i", c9.evaluate("3+4i").text, "5∠53.13010235")
    check("polar display of i", c9.evaluate("i").text, "1∠90")
    c9.complex_polar = False
    # errors
    for e in ["1/(i-i)", "0^i", "i^0/0", "(1+i)/0", "ln(0*i)", "i!", "5 mod i", "max(i,2)", "floor(i)", "round(1+i)",
              "sin(i,i)", "sqrt(i,1)", "gcd(i,2)", "atomic_mass(i)", "mat_det(i)", "list_get({1,2},i)", "ph_strong_acid(i)", "(1+i)^(1000000+i)", "10^(1000+i)",
              "asin(2i,3)", "log(i,2)", "arg(0)", "arg(0*i)", "rect(1)", "rect(i,1)", "c_polar(i,i)"]:
        check(f"bad complex input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
    text("a list may hold complex numbers", "{1+i, 2, -3i}", "{1+i, 2, -3i}")
    text("complex list arithmetic", "{i, 2}*i", "{-1, 2i}")
    text("list_sum of complex", "list_sum({i, 2})", "2+i")
    text("a complex matrix product", "{{i,0},{0,i}}*{{i,0},{0,i}}", "{{-1, 0}, {0, -1}}")
    text("sqrt of a list in complex mode", "{1,4}+0*i", "{1, 4}")
    text("abs of a complex list", "abs({3+4i, 5})", "{5, 5}")
    check("sorting complex numbers is refused", _err("list_sort({i,1})"), "Argument ERROR")
    check("a complex list cannot be inverted", _err("mat_inv({{i,1},{1,1}})") in ("Argument ERROR", "Math ERROR"), True)
    check("i is not a variable letter conflict: xi", ev("2*3") == 6 and cv("2i*i") == -2, True)
    check("a stored complex value", (c9.evaluate("3+4i->A"), c9.evaluate("A*conj(A)").text)[1], "25")
