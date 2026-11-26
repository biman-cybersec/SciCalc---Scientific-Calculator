"""Error types (Math ERROR, Syntax ERROR, Argument ERROR)

Module 1 of 47.  Taken from lines 41-77 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "errors"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

# ======================================================================================
#  PART 1 : ERRORS
# ======================================================================================

# Errors, named and worded like a Casio display so the UI can just print `.message`.


class CalcError(Exception):
    def __init__(self, message, pos=None, detail=""):
        super().__init__(message)
        self.message = message      # e.g. "Math ERROR"
        self.pos = pos              # character position in the typed text (or None)
        self.detail = detail        # short explanation for the curious

    def __str__(self):
        return f"{self.message} ({self.detail})" if self.detail else self.message


class MathError(CalcError):
    """The maths itself is impossible: 1/0, sqrt(-1), tan(90), number too large..."""
    def __init__(self, detail="", pos=None):
        super().__init__("Math ERROR", pos, detail)


class CalcSyntaxError(CalcError):
    """The typed text cannot be understood."""
    def __init__(self, detail="", pos=None):
        super().__init__("Syntax ERROR", pos, detail)


class ArgumentError(CalcError):
    """A function got the wrong number (or kind) of arguments."""
    def __init__(self, detail="", pos=None):
        super().__init__("Argument ERROR", pos, detail)
