"""Checks: symbolic output.  Run alone with  python run_tests.py symbolic_output"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "symbolic_output"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from ..engine import Calculator, sym_text

from .helpers import _err, _expr_error  # noqa: F401


def checks_symbolic_output_40(check, run, text, _json, cli, rg8):
    """symbolic-looking output"""
    # ================= symbolic-looking output =================
    def squarefree_(n):                                # independent test helper: smallest-prime search
        return all(n % (d * d) for d in range(2, int(n ** 0.5) + 1))
    def expect_text(coef, body):                       # build the canonical text the long way round
        sign = "-" if coef < 0 else ""
        a, b = abs(coef.numerator), coef.denominator
        if a == 1:
            core = body
        else:
            core = str(a) + body
        return sign + core + ("/" + str(b) if b != 1 else "")
    squarefrees = [m for m in range(2, 120) if squarefree_(m)]
    for _ in range(300):
        q = Fraction(rg8.randint(-60, 60), rg8.randint(1, 50))
        if q == 0:
            continue
        x = float(q)
        want = (str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}")
        check(f"sym fraction {q}", sym_text(x), want)
        q2 = Fraction(rg8.randint(-40, 40), rg8.randint(1, 36))
        if q2 != 0:
            check(f"sym pi multiple {q2}", sym_text(float(q2) * math.pi), expect_text(q2, "π"))
        a = Fraction(rg8.randint(1, 30), rg8.randint(1, 30)) * rg8.choice([-1, 1])
        m = rg8.choice(squarefrees)
        got = sym_text(float(a) * math.sqrt(m))
        check(f"sym root {a}*sqrt({m})", got, expect_text(a, f"√{m}"))
        back = Calculator().evaluate(got).value            # the text is valid input and gives the same number
        check(f"sym root text evaluates back ({got})", abs(float(back) - float(a) * math.sqrt(m)) <= 1e-12 * abs(float(a) * math.sqrt(m)), True)
    for text, val in [("√3/2", math.sqrt(3) / 2), ("√2/2", math.sqrt(2) / 2), ("√3/3", 1 / math.sqrt(3)), ("2√3", math.sqrt(12)), ("3√2", math.sqrt(18)),
                      ("√6/3", math.sqrt(6) / 3), ("-√5", -math.sqrt(5)), ("π", math.pi), ("-π/2", -math.pi / 2), ("π/6", math.pi / 6),
                      ("3π/4", 3 * math.pi / 4), ("2π", 2 * math.pi), ("5π/3", 5 * math.pi / 3), ("1/3", 1 / 3), ("-7/8", -0.875), ("3/10", 0.3),
                      ("√2", math.sqrt(2)), ("√7/4", math.sqrt(7) / 4), ("10√2", math.sqrt(200))]:
        check(f"sym known form {text}", sym_text(val), text)
    for val in [math.e, math.log(2), math.sin(1), 0.123456789123, 1.2345678, math.pi ** 2, math.e * math.pi, math.sqrt(2) + 1, 1e-12, 1e12,
                math.sqrt(2) * math.pi, 2 ** (1 / 3), math.log(10), 0.1234567890123456]:
        check(f"sym leaves {val!r} alone", sym_text(val), None)
    check("sym zero", sym_text(0.0), "0")
    check("sym integers", sym_text(5), "5")
    check("sym big integers", sym_text(10 ** 30), str(10 ** 30))
    check("sym Fraction", sym_text(Fraction(-3, 4)), "-3/4")
    check("sym bool", sym_text(True), None)
    check("sym nan", sym_text(float("nan")), None)
    check("sym inf", sym_text(float("inf")), None)
    check("sym string", sym_text("x"), None)
    check("sym tiny", sym_text(1e-10), None)
    # the calculator mode
    sy = Calculator(); sy.sym_display = True
    for expr, want in [("sqrt(12)", "2√3"), ("pi/6", "π/6"), ("sin(60)", "√3/2"), ("sin(45)", "√2/2"), ("tan(30)", "√3/3"), ("cos(60)", "1/2"),
                       ("0.75", "3/4"), ("1/3+1/6", "1/2"), ("-sqrt(8)", "-2√2"), ("2^0.5", "√2"), ("10", "10"), ("2.718281828459045", "2.718281828"),
                       ("sqrt(3)*sqrt(3)", "3"), ("{sqrt(2),3,pi}", "{√2, 3, π}"), ("{{sqrt(3),1},{1/2,pi/2}}", "{{√3, 1}, {1/2, π/2}}"),
                       ("{1,2,3}", "{1, 2, 3}"), ("{0.123456,0.5}", "{0.123456, 1/2}")]:
        check(f"sym mode {expr}", sy.evaluate(expr).text, want)
    r_ = sy.evaluate("sqrt(12)")
    check("sym mode keeps the decimal as the second value", r_.decimal, "3.464101615")
    check("sym mode leaves Ans numeric", sy.ans == math.sqrt(12) or abs(float(sy.ans) - math.sqrt(12)) < 1e-12, True)
    check("sym answer feeds the next line", sy.evaluate("Ans*2").text, "4√3")
    check("sym answer with the exact fraction", sy.evaluate("sqrt(12)/sqrt(3)").text, "2")
    rad = Calculator(); rad.sym_display = True; rad.set_angle("rad")
    check("sym asin in radians", rad.evaluate("asin(0.5)").text, "π/6")
    check("sym acos in radians", rad.evaluate("acos(0)").text, "π/2")
    rad.set_angle("deg")
    check("sym asin in degrees stays a number", rad.evaluate("asin(0.5)").text, "30")
    sy.frac_display = "mixed"
    check("sym with mixed fractions", sy.evaluate("7/2").text, "3 1/2")
    check("sym with mixed fractions in a list", sy.evaluate("{7/2,sqrt(2)}").text, "{3 1/2, √2}")
    sy.frac_display = None; sy.base_display = "hex"
    check("sym yields to base display", sy.evaluate("255").text, "0xFF")
    sy.base_display = None; sy.dms_display = True
    check("sym yields to DMS display", sy.evaluate("45.5").text, "45°30'0.0\"")
    sy.dms_display = False; sy.set_display("sci", 3)
    check("sym ignores the number format for exact forms", sy.evaluate("sqrt(12)").text, "2√3")
    check("sym uses the number format for other numbers", sy.evaluate("0.123456789").text, "1.23×10^-1")
    sy.set_display("norm", 2); sy.complex_mode = True
    check("sym with complex mode on leaves complex values", sy.evaluate("sqrt(-4)").text, "2i")
    check("sym with complex mode on still shows real exact forms", sy.evaluate("sqrt(12)").text, "2√3")
    sy2 = Calculator(); sy2.sym_display = True
    check("sym is off after reset", (sy2.reset(), sy2.sym_display)[1], False)
    ses2 = Calculator(); ses2.sym_display = True
    d_ = ses2.to_dict()
    ld = Calculator(); ld.load_dict(d_)
    check("sym is saved in a session", ld.sym_display, True)
    check("sym session setting must be sane", _json.loads(_json.dumps(d_))["sym_display"], True)
    h_, out = cli(Calculator(), "sym")
    check("sym command reports", "off" in out, True)
    c3 = Calculator()
    h_, out = cli(c3, "sym on"); check("sym on", c3.sym_display is True and "on" in out, True)
    h_, out = cli(c3, "sym maybe"); check("sym refuses nonsense", c3.sym_display is True and "use:" in out, True)
    h_, out = cli(c3, "sym off"); check("sym off", c3.sym_display is False, True)
    # sym_form
    for expr, want in [("sym_form(sqrt(12))", "2√3"), ("sym_form(pi/6)", "π/6"), ("sym_form(0.75)", "3/4"), ("sym_form(7)", "7"), ("sym_form(1/3)", "1/3"),
                       ("sym_form(-sqrt(2)/2)", "-√2/2"), ("sym_form(sin(60))", "√3/2")]:
        check(f"{expr}", run(expr).text, want)
    for e in ["sym_form(e)", "sym_form(ln(2))", "sym_form({1,2})", "sym_form('x')", "sym_form(3+4i)", "sym_form()", "sym_form(1,2)", "sym_form(1e-12)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
