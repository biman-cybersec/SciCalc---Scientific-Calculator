"""Checks: input features.  Run alone with  python run_tests.py input_features"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "input_features"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_input_features_30(check, run, near, text):
    """input features"""
    # ---------------------------------------------------------------- input features
    # base-N literals, cross-checked against Python's int(text, base)
    for text, base in [("FF", 16), ("1010", 2), ("17", 8), ("DEADBEEF", 16), ("7F", 16), ("1", 2), ("777", 8)]:
        pre = {16: "0x", 2: "0b", 8: "0o"}[base]
        check(f"literal {pre}{text}", run(pre + text).value, int(text, base))
    check("literal prefix case", run("0XfF").value, 255)
    check("literal arithmetic", run("0xFF+0b101-0o10").value, 255 + 5 - 8)
    check("literal in function", run("sqrt(0b10000)").value, 4)
    # DMS input, hand computed: 1 + 30/60 + 15/3600
    near("dms literal", "1°30'15\"", 1 + 30 / 60 + 15 / 3600, 1e-12)
    near("dms minutes only", "45°30'", 45.5, 1e-12)
    near("dms in sin", "sin(30°0'0\")", 0.5, 1e-12)
    near("dms round trip", "dms2deg(12,34,56)-12°34'56\"", 0, 1e-12)
    rad = Calculator(); rad.set_angle("rad")
    check("dms honours angle mode", abs(float(rad.evaluate("90°0'0\"").value) - math.pi / 2) < 1e-12, True)
    check("plain degrees still work", run("30°").value, 30)
    # display modes
    show = Calculator(); show.base_display = "hex"
    check("hex display", show.evaluate("255").text, "0xFF")
    check("hex negative", show.evaluate("-255").text, "-0xFF")
    check("hex leaves fractions", show.evaluate("1/2").text, "0.5")
    show.base_display = "bin"
    check("bin display", show.evaluate("10").text, "0b1010")
    show.base_display = "oct"
    check("oct display", show.evaluate("64").text, "0o100")
    show.base_display = None; show.dms_display = True
    check("dms display", show.evaluate("45.5").text, "45°30'0.0\"")
    check("dms display of dms input", show.evaluate("1°30'15\"").text, "1°30'15.0\"")
    # user-defined functions
    uf = Calculator()
    check("define reports", uf.evaluate("f(x)=x^2+1").text, "f(x) = x^2+1")
    check("define keeps Ans", uf.evaluate("7").value, 7)
    uf.evaluate("f(x)=x^2+1")
    check("call", uf.evaluate("f(3)").value, 10)
    check("Ans unchanged by define", uf.ans, 10)
    check("call in expression", uf.evaluate("2f(3)+f(1)").value, 22)
    check("nested call", uf.evaluate("f(f(2))").value, 26)
    uf.evaluate("area(x,y)=x*y")
    check("two parameters", uf.evaluate("area(3,4)").value, 12)
    uf.evaluate("h(a)=a+X")
    uf.evaluate("5->X")
    check("global variable inside body", uf.evaluate("h(1)").value, 6)
    check("call does not clobber variable", uf.evaluate("X").value, 5)
    uf.evaluate("t(x)=sin(x)")
    check("angle mode in body", abs(float(uf.evaluate("t(30)").value) - 0.5) < 1e-12, True)
    uf.set_angle("rad")
    check("angle mode follows", abs(float(uf.evaluate("t(pi/6)").value) - 0.5) < 1e-12, True)
    uf.set_angle("deg")
    check("variable F still works", (uf.evaluate("3->F"), uf.evaluate("F*2").value)[1], 6)
    check("listed", uf.list_functions()[0].startswith("area(x, y)"), True)
    uf.delete_function("f")
    check("deleted function is a product again", uf.evaluate("f(3)").value, 3 * uf.variables["F"])
    sv = Calculator(); sv.evaluate("k1(x)=x^2+1")
    check("solve with user function", abs(float(sv.evaluate("solve('k1(x)-5',1)").value) - 2) < 1e-8, True)
    check("table with user function", sv.evaluate("table1('k1(x)',1,2,1)").text, "{{1, 2}, {2, 5}}")
    rec = Calculator(); rec.evaluate("r(x)=r(x)+1")
    check("endless recursion stops", _expr_error(rec, "r(1)"), "Math ERROR")
    rec.evaluate("w(x)=w(x-1)+w(x-1)")
    check("exponential recursion stops", _expr_error(rec, "w(3)"), "Math ERROR")
    for expr in ["sin(x)=2", "pi(x)=1", "q(x,x)=1", "q(z)=1", "q(x)=", "q(x)=x+", "q(x)=3->A", "e(x)=1",
                 "q(a,b,c,d,f,m,x,y,x)=1"]:
        check(f"bad definition {expr}", _expr_error(Calculator(), expr) != "", True)
    check("wrong argument count", _expr_error(uf, "area(1)"), "Argument ERROR")
    check("undefined call is a product", Calculator().evaluate("a(3)").value, 0)
    for expr in ["0b2", "0x", "1°70'", "5°'"]:
        check(f"bad literal {expr}", _err(expr) in ("", "Syntax ERROR", "Math ERROR"), True)
