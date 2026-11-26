"""Display modes: Norm / Fix / Sci / Eng, fractions, symbolic text

Module 4 of 47.  Taken from lines 527-633 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "display"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from decimal import Context
from decimal import Decimal
from decimal import InvalidOperation
from decimal import ROUND_HALF_UP
from fractions import Fraction

from .arithmetic import Lst, Mat, _elem_text, ar_snap

# ======================================================================================
#  PART 4 : DISPLAY (Norm / Fix / Sci)
# ======================================================================================

# Turning values into text the way a Casio does (Norm 1/2, Fix n, Sci n).

_WIDE = Context(prec=80, rounding=ROUND_HALF_UP)


def to_decimal(v):
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, int):
        return Decimal(v)
    if isinstance(v, Fraction):
        return _WIDE.divide(Decimal(v.numerator), Decimal(v.denominator))
    return Decimal(v)


def _round_sig(d, n):
    return Context(prec=n, rounding=ROUND_HALF_UP).create_decimal(d)


def _digits(d):
    return "".join(map(str, d.as_tuple().digits))


def _sci_text(digits, exponent):
    mantissa = digits[0] + ("." + digits[1:] if len(digits) > 1 else "")
    return f"{mantissa}×10^{exponent}"


def format_number(v, fmt=("norm", 2)):
    kind, n = fmt
    d = to_decimal(v)
    if d == 0:
        return "0." + "0" * n if kind == "fix" and n else "0"
    sign = "-" if d < 0 else ""
    d = abs(d)

    if kind == "custom":
        # n represents decimal places formatted cleanly with comma separators or custom template
        try:
            return sign + format(d, f",.{n}f")
        except Exception:
            return sign + format(d, "f")
        
    if kind == "fix":
        try:
            r = _WIDE.quantize(d, Decimal(1).scaleb(-n))
            return ("" if r == 0 else sign) + format(r, "f")
        except InvalidOperation:
            kind, n = "norm", 2                    # too big for Fix: fall back to Norm

    if kind == "sci":
        r = _round_sig(d, n)
        return sign + _sci_text(_digits(r).ljust(n, "0")[:n], r.adjusted())

    if kind == "eng":                              # exponent a multiple of 3: 12345 -> 12.3×10^3 with 3 digits
        r = _round_sig(d, n)
        e = r.adjusted()
        e3 = (e // 3) * 3
        digits = _digits(r).ljust(n, "0")[:n]
        lead = e - e3 + 1
        digits = digits.ljust(lead, "0")
        text = digits[:lead] + ("." + digits[lead:] if len(digits) > lead else "")
        return sign + text + (f"×10^{e3}" if e3 else "")

    r = _round_sig(d, 10)                          # Norm 1 / Norm 2: 10 significant digits
    e = r.adjusted()
    if e < (-2 if n == 1 else -9) or e >= 10:
        return sign + _sci_text(_digits(r.normalize()).rstrip("0") or "0", e)
    return sign + format(r.normalize(), "f")


def _cx_text(z, fmt, polar=None):
    if polar:                                          # r∠θ with θ in the given angle unit
        r = math.hypot(z.real, z.imag)
        th = math.atan2(z.imag, z.real)
        th = {"deg": math.degrees(th), "rad": th, "grad": th * 200 / math.pi}[polar]
        return f"{format_number(ar_snap(r), fmt)}∠{format_number(ar_snap(th), fmt)}"
    re_, im_ = z.real, z.imag
    mag = format_number(abs(im_), fmt)
    mag = "" if mag == "1" else mag
    if re_ == 0:
        return ("-" if im_ < 0 else "") + mag + "i"
    return format_number(re_, fmt) + ("-" if im_ < 0 else "+") + mag + "i"


def format_result(value, fmt, polar=None):
    # 1. If it's a text string (like '0b101010' or '45°30\'0.0"'), return it with None
    if isinstance(value, str):
        return value, None
    if isinstance(value, complex):
        return _cx_text(value, fmt, polar), None
    if isinstance(value, Lst):
        return "{" + ", ".join(_elem_text(v, fmt) for v in value) + "}", None
    if isinstance(value, Mat):
        return "{" + ", ".join("{" + ", ".join(_elem_text(v, fmt) for v in row) + "}" for row in value) + "}", None
        
    # 2. If it's a normal number, format it and return a pair of values
    text = format_number(value, fmt)
    decimal_val = to_decimal(value) if isinstance(value, Fraction) else None   # floats have no "exact" decimal form
    return text, decimal_val
