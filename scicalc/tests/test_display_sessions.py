"""Checks: display sessions.  Run alone with  python run_tests.py display_sessions"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "display_sessions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from fractions import Fraction

from ..errors import CalcError
from ..arithmetic import Cx, Lst, Mat
from ..engine import Calculator, load_session, save_session
from ..cli import _command

from .helpers import _err, _expr_error  # noqa: F401


def checks_display_sessions_39(check, text, rg8):
    """ENG display, fraction display, sessions, constants browser"""
    # ================= ENG display, fraction display, sessions, constants browser =================
    import io as _io, os as _os, json as _json, tempfile as _tf, contextlib as _cl
    # ---- ENG: exponent is a multiple of 3, 1 <= mantissa < 1000, and the value matches the rounded number
    eng = Calculator()
    for digits in (1, 2, 3, 4, 6, 10):
        eng.set_display("eng", digits)
        for _ in range(60):
            x = rg8.choice([-1, 1]) * rg8.uniform(1, 9.999) * 10 ** rg8.randint(-14, 14)
            txt = eng.format(x)[0]
            mant, _, ex_ = (txt[1:] if txt.startswith("-") else txt).partition("×10^")
            e_ = int(ex_) if ex_ else 0
            m_ = float(mant)
            ok = e_ % 3 == 0 and 1 <= m_ < 1000 and abs(m_ * 10.0 ** e_ - abs(x)) <= abs(x) * (10 ** -(digits - 1)) * 1.0000001 + 1e-300
            check(f"eng {digits} digits of {x:.5g} -> {txt}", ok and txt.startswith("-") == (x < 0), True)
            sig = len(mant.replace(".", "").lstrip("0"))
            check(f"eng {digits} keeps {digits} digit(s): {txt}", sig == max(digits, len(mant.replace('.', ''))) or len(mant.replace(".", "")) >= digits, True)
    eng.set_display("eng", 3)
    for expr, want in [("12345", "12.3×10^3"), ("0.00123", "1.23×10^-3"), ("1500", "1.50×10^3"), ("100", "100"), ("1", "1.00"),
                       ("999999", "1.00×10^6"), ("-0.000045678", "-45.7×10^-6"), ("1234567", "1.23×10^6"), ("0", "0"), ("0.5", "500×10^-3")]:
        check(f"eng 3 shows {expr}", eng.evaluate(expr).text, want)
    eng.set_display("eng", 1)
    check("eng 1", eng.evaluate("12345").text, "10×10^3")
    check("eng invalid digits", _expr_error(Calculator(), "1") == "", True)
    for bad in (0, 11):
        try:
            Calculator().set_display("eng", bad)
            check(f"eng {bad} refused", False, True)
        except ValueError:
            check(f"eng {bad} refused", True, True)
    eng2 = Calculator(); eng2.set_display("eng", 4)
    check("eng on a list", eng2.evaluate("{1500,0.002}").text, "{1.500×10^3, 2.000×10^-3}")
    check("eng on a complex number", eng2.format(Cx(1500, 2))[0] != "", True)
    # ---- fraction display
    fr = Calculator(); fr.frac_display = "improper"
    for expr, want in [("7/2", "7/2"), ("-7/3", "-7/3"), ("1/3+1/6", "1/2"), ("6/3", "2"), ("0.5", "0.5"), ("{1/2,3}", "{1/2, 3}"),
                       ("{{1/2,1},{3/4,2}}", "{{1/2, 1}, {3/4, 2}}"), ("2^-3", "1/8")]:
        check(f"frac improper {expr}", fr.evaluate(expr).text, want)
    fr.frac_display = "mixed"
    for expr, want in [("7/2", "3 1/2"), ("-7/3", "-2 1/3"), ("1/2", "1/2"), ("-1/2", "-1/2"), ("22/7", "3 1/7"), ("{5/3,1/2}", "{1 2/3, 1/2}"), ("100/3", "33 1/3")]:
        check(f"frac mixed {expr}", fr.evaluate(expr).text, want)
    for _ in range(40):                             # every fraction text parses back to the same exact value
        q = Fraction(rg8.randint(-500, 500), rg8.randint(1, 60))
        for mode in ("improper", "mixed"):
            fr.frac_display = mode
            t = fr.format(q)[0]
            sign = -1 if t.startswith("-") else 1
            parts = t.lstrip("-").split()
            if len(parts) == 2:
                back = sign * (int(parts[0]) + Fraction(parts[1]))
            else:
                back = sign * Fraction(parts[0])
            check(f"frac {mode} round trip {q}", back == q, True)
    fr.frac_display = None
    check("frac off shows decimals", fr.evaluate("7/2").text, "3.5")
    check("frac does not touch floats", Calculator().evaluate("0.1+0.2").text, "0.3")
    # ---- sessions
    def roundtrip(calc):
        fd, path = _tf.mkstemp(suffix=".json")
        _os.close(fd)
        try:
            save_session(calc, path)
            raw = open(path, encoding="utf-8").read()
            other = Calculator()
            load_session(other, path)
            return other, raw
        finally:
            _os.unlink(path)
    ses = Calculator()
    for line in ["{1,2,3}->A", "{{1,2},{3,4}}->B", "7/3->C", "2.5->D", "10^30->E", "f(x)=x^2+A", "h(x)=f(x)+1", "area(x,y)=x*y", "5+5"]:
        ses.evaluate(line)
    ses.complex_mode = True
    ses.evaluate("sqrt(-4)->X")
    ses.set_angle("rad"); ses.set_display("sci", 4); ses.complex_polar = True
    ses.base_display, ses.dms_display, ses.frac_display = "hex", True, "mixed"
    back, raw = roundtrip(ses)
    check("session is JSON text", isinstance(_json.loads(raw), dict) and "pickle" not in raw, True)
    for name in "ABCDEXYFM":
        check(f"session variable {name}", back.variables[name] == ses.variables[name] and type(back.variables[name]) is type(ses.variables[name]), True)
    check("session list type", isinstance(back.variables["A"], Lst) and isinstance(back.variables["B"], Mat), True)
    check("session exact fraction", back.variables["C"] == Fraction(7, 3) and isinstance(back.variables["C"], Fraction), True)
    check("session big integer", back.variables["E"] == 10 ** 30 and isinstance(back.variables["E"], int), True)
    check("session complex", back.variables["X"] == 2j and isinstance(back.variables["X"], Cx), True)
    check("session settings", (back.angle, back.display, back.complex_mode, back.complex_polar, back.base_display, back.dms_display, back.frac_display) ==
          ("rad", ("sci", 4), True, True, "hex", True, "mixed"), True)
    check("session Ans", back.ans == ses.ans and back.preans == ses.preans, True)
    check("session functions", sorted(back.list_functions()) == sorted(ses.list_functions()), True)
    check("session history", [(h.expr, h.text) for h in back.history] == [(h.expr, h.text) for h in ses.history], True)
    back.base_display = back.dms_display = back.frac_display = None; back.complex_mode = False; back.set_angle("deg"); back.set_display("norm", 2)  # pyright: ignore[reportAttributeAccessIssue]
    check("restored function works", back.evaluate("h(2)").text, "{6, 7, 8}")
    check("restored function calling function", back.evaluate("f(3)").text, "{10, 11, 12}")
    check("restored two-argument function", back.evaluate("area(3,4)").value, 12)
    check("restored list arithmetic", back.evaluate("A*2").text, "{2, 4, 6}")
    good = _json.loads(raw)
    # functions that call each other in either order survive a round trip
    fd, path = _tf.mkstemp(suffix=".json")
    _os.close(fd)
    with open(path, "w", encoding="utf-8") as fh:               # b is listed before the a it calls
        fh.write(_json.dumps({**good, "functions": {"bb": [["X"], "aa(x)*2"], "aa": [["X"], "x+1"]}}))
    mb = Calculator()
    load_session(mb, path)
    _os.unlink(path)
    check("function loaded before the one it calls", mb.evaluate("bb(3)").value, 8)
    # damaged or hostile files change nothing and never leak Python errors
    keep = Calculator(); keep.evaluate("5->A"); keep.set_angle("grad")
    bad_files = {
        "not json": "{oops", "empty": "", "list": "[1,2]", "wrong tag": '{"scicalc_session": 2}', "no tag": "{}",
        "bad variable": _json.dumps({**good, "variables": {"Z": {"t": "i", "v": "1"}}}),
        "bad angle": _json.dumps({**good, "angle": "turns"}),
        "bad display": _json.dumps({**good, "display": ["fix", 99]}),
        "bad display kind": _json.dumps({**good, "display": ["nope", 1]}),
        "bad base": _json.dumps({**good, "base_display": "ternary"}),
        "bad frac": _json.dumps({**good, "frac_display": "x"}),
        "bad value type": _json.dumps({**good, "ans": {"t": "zz", "v": 1}}),
        "bad int": _json.dumps({**good, "ans": {"t": "i", "v": "abc"}}),
        "bad fraction": _json.dumps({**good, "ans": {"t": "q", "v": "1/0"}}),
        "infinite float": _json.dumps({**good, "ans": {"t": "f", "v": "inf"}}),
        "nan float": _json.dumps({**good, "ans": {"t": "f", "v": "nan"}}),
        "ragged matrix": _json.dumps({**good, "ans": {"t": "m", "v": [[{"t": "i", "v": "1"}], [{"t": "i", "v": "1"}, {"t": "i", "v": "2"}]]}}),
        "deep nesting": _json.dumps({**good, "ans": {"t": "l", "v": [{"t": "l", "v": [{"t": "l", "v": [{"t": "l", "v": [{"t": "l", "v": []}]}]}]}]}}),
        "function with built-in name": _json.dumps({**good, "functions": {"sin": [["X"], "x"]}}),
        "function with bad body": _json.dumps({**good, "functions": {"zz": [["X"], "x+"]}}),
        "function with bad params": _json.dumps({**good, "functions": {"zz": [["Q"], "1"]}}),
        "function table not a dict": _json.dumps({**good, "functions": [1]}),
        "function entry not a pair": _json.dumps({**good, "functions": {"zz": "x"}}),
        "history not a list": _json.dumps({**good, "history": 5}),
        "history entry broken": _json.dumps({**good, "history": [{"expr": "1"}]}),
        "variables not a dict": _json.dumps({**good, "variables": [1]}),
    }
    for label, text in bad_files.items():
        fd, path = _tf.mkstemp(suffix=".json")
        _os.close(fd)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
            try:
                load_session(keep, path)
                ok = False
            except CalcError:
                ok = True
            check(f"bad session '{label}' is refused", ok, True)
            check(f"bad session '{label}' changes nothing", keep.variables["A"] == 5 and keep.angle == "grad" and not keep.user_functions, True)
        finally:
            _os.unlink(path)
    # the CLI commands
    def cli(calc, line):
        buf = _io.StringIO()
        with _cl.redirect_stdout(buf):
            handled = _command(calc, line)
        return handled, buf.getvalue()
    d_ = _tf.mkdtemp()
    sp = _os.path.join(d_, "mine")
    c1 = Calculator(); c1.evaluate("9->A")
    h_, out = cli(c1, f"save {sp}")
    check("save command", h_ is True and "saved to" in out and _os.path.exists(sp + ".json"), True)
    c2 = Calculator()
    h_, out = cli(c2, f"load {sp}")
    check("load command", h_ is True and "loaded" in out and c2.variables["A"] == 9, True)
    h_, out = cli(c2, f"load {_os.path.join(d_, 'missing')}")
    check("load of a missing file is reported", h_ is True and "cannot use" in out, True)
    with open(sp + ".json", "w", encoding="utf-8") as fh:
        fh.write("{oops")
    h_, out = cli(c2, f"load {sp}")
    check("load of a broken file is reported", h_ is True and "valid JSON" in out and c2.variables["A"] == 9, True)
    h_, out = cli(c2, f"save {_os.path.join(d_, 'no_such_dir', 'x')}")
    check("save to a bad place is reported", h_ is True and "cannot use" in out, True)
    _os.unlink(sp + ".json"); _os.rmdir(d_)
    h_, out = cli(c2, "frac mixed"); check("frac command", c2.frac_display == "mixed" and "mixed" in out, True)
    h_, out = cli(c2, "frac nonsense"); check("frac command refuses nonsense", c2.frac_display == "mixed" and "use:" in out, True)
    h_, out = cli(c2, "frac off"); check("frac off", c2.frac_display is None, True)
    h_, out = cli(c2, "eng 4"); check("eng command", c2.display == ("eng", 4), True)
    h_, out = cli(c2, "eng 99"); check("eng command range", c2.display == ("eng", 4) and "use:" in out, True)
    c2.reset(); check("reset clears the new settings", c2.frac_display is None and c2.display == ("norm", 2) and not c2.user_functions, True)
    # ---- constants browser
    h_, out = cli(Calculator(), "constants")
    check("constants lists the categories", all(c_ in out for c_ in ("Physics", "Maths", "Astronomy", "Chemistry", "Units & Everyday")), True)
    h_, out = cli(Calculator(), "constants hartree")
    check("constants search by name", "const_hartree_ev" in out and "const_hartree_kjmol" in out, True)
    h_, out = cli(Calculator(), "constants lemniscate")
    check("constants search by alias or description", "const_lemniscate" in out, True)
    h_, out = cli(Calculator(), "constants planet zzzz")
    check("constants search with no match", "no constant matches" in out, True)
    h_, out = cli(Calculator(), "constants maths")
    check("constants search by category", out.count("\n") >= 56, True)
    h_, out = cli(Calculator(), "const const_gauss_c")
    check("const details", "0.8346268416740731" in out and "gauss_const" in out and "Constants: Maths" in out, True)
    h_, out = cli(Calculator(), "const pi")
    check("const details for pi", "3.14159" in out, True)
    h_, out = cli(Calculator(), "const gauss")
    check("const suggests names", "did you mean" in out and "const_gauss" in out, True)
    h_, out = cli(Calculator(), "const zzzz")
    check("const unknown name", "no constant named" in out, True)
    h_, out = cli(Calculator(), "help")
    check("help mentions the new commands", all(w in out for w in ("eng 1-10", "frac improper", "save <file>", "constants [word]", "f(x)=x^2+1")), True)
    return {"_json": _json, "cli": cli}
