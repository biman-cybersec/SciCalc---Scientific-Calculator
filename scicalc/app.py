"""print_docs() and main()

Module 47 of 47.  Taken from lines 18793-18839 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "app"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import sys

from .menu import menu_main
from .cli import calc_main
from .selftest import selftest

def print_docs():
    print("""
======================================================================
 SCICALC - TECHNICAL DOCUMENTATION & REFERENCE
======================================================================
 ARCHITECTURE:
   - Centralized REGISTRY object with @register decorators.
   - High-precision math handled via Python's decimal & math libraries.
   - ar_normalize manages floating-point noise and precision.

 COMMAND-LINE USAGE:
   python calculator.py                     Interactive Casio prompt
   python calculator.py "expr"              Evaluate single expression
   python calculator.py --menu              Numbered helper menu
   python calculator.py --selftest          Run complete test suite, listing every function
                                            (long: redirect it, e.g.  > examples.txt)
   python calculator.py --selftest --quiet  Same tests, only the 4-line summary
   python calculator.py --docs              Show this documentation guide

 INSIDE PROMPT COMMANDS:
   help [name], list [cat], listall, listconstants, search <word>,
   graph <expr> [min] [max], mode deg|rad|grad, norm|fix|sci|eng|custom,
   frac, sym, base, dms, complex, table, funcs, delfunc, constants, const,
   save <file>, load <file>, vars, history, full, stats, reset, menu, quit
======================================================================
    """)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("--menu", "menu"):
        menu_main()
        return 0
    if argv and argv[0] == "--examples":
        return selftest(show_examples=True)
    if argv and argv[0] == "--selftest":
        return selftest(show_examples="--quiet" not in argv[1:])
    if argv and argv[0] == "--quiet":
        return selftest(show_examples=False)
    if argv and argv[0] == "--coverage":
        return selftest(show_uncovered=True, show_examples=False)
    if argv and argv[0] in ("--docs", "docs"):
        print_docs()
        return 0
    return calc_main(argv)
