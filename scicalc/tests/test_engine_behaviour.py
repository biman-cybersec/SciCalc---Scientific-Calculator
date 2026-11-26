"""Checks: engine behaviour.  Run alone with  python run_tests.py engine_behaviour"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "engine_behaviour"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from .helpers import _err, _expr_error  # noqa: F401


def checks_engine_behaviour_41(covered, ex):
    """engine behaviour"""
    # ---------------------------------------------------------------- engine behaviour
    for expr, want in [("3+4*2", 11), ("(3+4)*2", 14), ("2^3^2", 512), ("-2^2", -4), ("7 mod 3", 1), ("5!", 120),
                       ("200*15%", 30), ("5 nCr 2", 10), ("5 nPr 2", 20)]:
        ex(f"engine {expr}", expr, want)
