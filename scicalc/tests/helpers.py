"""Shared test helpers: run/ev/near/ex/text/fn/simpson/csv, plus _err and _expr_error."""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topics"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import ast
import cmath
import re
import statistics as st

from ..errors import CalcError
from ..registry import REGISTRY
from ..engine import Calculator


def _expr_error(calc, expr):
    try:
        calc.evaluate(expr)
        return ""
    except CalcError as err:
        return err.message


def _err(expr):
    """The error name an expression produces ('' if it works)."""
    try:
        Calculator().evaluate(expr)
        return ""
    except CalcError as err:
        return err.message


def make_helpers(check):
    """Build the helpers the check sections share; everything reports into `check`."""
    covered = set()
    words = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")

    def cov(*names):
        for w in names:
            f = REGISTRY.function(w)
            if f:
                covered.add(f.name)

    def run(expr, calc=None):
        for w in words.findall(expr):
            cov(w)
        return (calc or Calculator()).evaluate(expr)

    def ev(expr):
        v = run(expr).value
        return float(v)

    def near(label, expr, want, tol=1e-9):
        try:
            got = ev(expr)
        except CalcError as err:
            got = err.message
        ok = isinstance(got, float) and abs(got - want) <= tol * max(1.0, abs(want))
        check(label, "ok" if ok else got, "ok" if ok else want)

    def ex(label, expr, want):
        try:
            got = run(expr).value
        except CalcError as err:
            got = err.message
        check(label, got, want)

    def text(label, expr, want):
        try:
            got = run(expr).text
        except CalcError as err:
            got = err.message
        check(label, got, want)

    def fn(name):
        return REGISTRY.function(name).fn  # pyright: ignore[reportOptionalMemberAccess]

    def simpson(f, a, b, n=400):
        h = (b - a) / n
        total = f(a) + f(b)
        for i in range(1, n):
            total += (4 if i % 2 else 2) * f(a + i * h)
        return total * h / 3

    def csv(xs):
        return ",".join(repr(x) for x in xs)
    return {"check": check, "covered": covered, "words": words, "cov": cov, "run": run, "ev": ev, "near": near, "ex": ex,
            "text": text, "fn": fn, "simpson": simpson, "csv": csv, "ast": ast, "cmath": cmath, "re": re, "st": st}
