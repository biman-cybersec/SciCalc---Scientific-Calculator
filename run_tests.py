"""Test one module (or one topic) of SCICALC on its own.

    python run_tests.py                      list every module with its function count and test topics
    python run_tests.py lib_trig             test one module
    python run_tests.py lib_trig lib_units   test several
    python run_tests.py --topic trig         run one test topic only (names are listed by --topics)
    python run_tests.py --topics             list the test topics
    python run_tests.py --all                test every module and print one table
    python run_tests.py --full               the complete self-test (same as: python calculator.py --selftest --quiet)

For a module the script reports three things:
    import     the module (and every module before it) loads without an error
    examples   every function registered by this module: its  example="expr => result"  must come out true
    checks     the independent cross-checks and bad-input tests of the topics that belong to this module
               (scicalc/tests/test_<topic>.py).  A problem line names the exact check that failed.
Exit code 0 means everything passed.
"""
import importlib
import sys

# the load order of the modules (same as scicalc/MODULES.md)
MODULES = [
    "errors", "registry", "arithmetic", "display", "parser", "engine", "lib_trig", "lib_powers_rounding",
    "lib_numtheory_basic", "lib_constants_basic", "lib_geometry_daily", "lib_finance_stats_basic",
    "lib_vectors_solver_basen", "lib_science_basic", "lib_expansion_basic", "lib_special_functions",
    "lib_distributions", "lib_regression", "lib_inference", "lib_numerical", "lib_units",
    "lib_numtheory_sprint3", "lib_algebra", "menu", "cli", "lib_geometry_extras", "lib_calculus", "lib_basen",
    "lib_complex_c", "lib_vectors_matrices", "lib_physics", "lib_finance_calendar", "lib_lists_matrices",
    "lib_chemistry", "lib_complex_type", "lib_equations_tables", "lib_engineering", "lib_electronics", "lib_ml",
    "lib_health", "lib_astronomy_geodesy", "lib_cooking_home", "lib_type_extensions", "constants_expansion",
    "api", "selftest", "app",
]

# which test topics (scicalc/tests/test_<topic>.py) exercise which module
TOPICS = {
    "errors": ["bad_input"],
    "registry": [],
    "arithmetic": ["lists_matrices", "complex_type"],
    "display": ["display_sessions", "symbolic_output"],
    "parser": ["input_features"],
    "engine": ["engine_behaviour", "input_features", "display_sessions"],
    "lib_trig": ["trig"],
    "lib_powers_rounding": ["powers_rounding"],
    "lib_numtheory_basic": ["number_theory"],
    "lib_constants_basic": ["constants"],
    "lib_geometry_daily": ["geometry", "finance_daily"],
    "lib_finance_stats_basic": ["finance_daily", "statistics"],
    "lib_vectors_solver_basen": ["vectors_complex_text", "basen", "calculus"],
    "lib_science_basic": ["science_misc"],
    "lib_expansion_basic": ["science_misc"],
    "lib_special_functions": ["special_functions"],
    "lib_distributions": ["distributions"],
    "lib_regression": ["statistics"],
    "lib_inference": ["inference"],
    "lib_numerical": ["calculus"],
    "lib_units": ["units"],
    "lib_numtheory_sprint3": ["number_theory"],
    "lib_algebra": ["algebra"],
    "menu": [],
    "cli": ["display_sessions", "engine_behaviour"],
    "lib_geometry_extras": ["geometry_extras"],
    "lib_calculus": ["calculus"],
    "lib_basen": ["basen"],
    "lib_complex_c": ["complex_c"],
    "lib_vectors_matrices": ["matrices"],
    "lib_physics": ["physics"],
    "lib_finance_calendar": ["finance_calendar"],
    "lib_lists_matrices": ["lists_matrices"],
    "lib_chemistry": ["chemistry"],
    "lib_complex_type": ["complex_type"],
    "lib_equations_tables": ["equations_tables"],
    "lib_engineering": ["engineering"],
    "lib_electronics": ["electronics"],
    "lib_ml": ["machine_learning"],
    "lib_health": ["health"],
    "lib_astronomy_geodesy": ["astronomy_geodesy"],
    "lib_cooking_home": ["cooking_home"],
    "lib_type_extensions": ["type_extensions"],
    "constants_expansion": ["constants", "symbolic_output"],
    "selftest": [],
    "app": [],
    "api": ["api"],
}


class Report:
    def __init__(self):
        self.total = 0
        self.problems = []

    def check(self, label, got, want):
        self.total += 1
        if got != want:
            self.problems.append(f"{label}: got {got!r}, wanted {want!r}")


def _functions_of(module):
    import scicalc
    return [f for f in scicalc.REGISTRY.functions() if getattr(f.fn, "__module__", "") == f"scicalc.{module}"]


def _run_examples(funcs):
    import scicalc
    rep = Report()
    for f in funcs:
        expr, _, want = f.example.partition(" => ")
        try:
            got = scicalc.Calculator().evaluate(expr).text
        except scicalc.CalcError as err:
            got = err.message
        rep.check(f"example of {f.name}", "ok" if want.startswith("<") and "ERROR" not in got else got,
                  "ok" if want.startswith("<") else want)
    return rep


def _run_topics(topics):
    """Run the check sections of these topics; returns (Report, covered-function-names)."""
    from scicalc import tests
    rep = Report()
    covered = tests.run_sections(rep.check, set(topics)) if topics else set()
    if "bad_input" in topics:
        from scicalc.tests.test_bad_input import _bad_input_checks
        _bad_input_checks(rep.check)
    return rep, covered


def test_module(name, verbose=True):
    """Returns (ok, summary-dict)."""
    out = {"module": name, "import": "ok", "functions": 0, "examples": "-", "checks": "-", "problems": []}
    try:
        importlib.import_module(f"scicalc.{name}")
    except Exception as exc:                                     # an import error stops here
        out["import"] = f"FAILED: {type(exc).__name__}: {exc}"
        out["problems"].append(out["import"])
        return False, out
    funcs = _functions_of(name)
    out["functions"] = len(funcs)
    if funcs:
        rep = _run_examples(funcs)
        out["examples"] = f"{rep.total - len(rep.problems)}/{rep.total}"
        out["problems"] += rep.problems
    topics = TOPICS.get(name, [])
    if topics:
        rep, covered = _run_topics(topics)
        out["checks"] = f"{rep.total} checks"
        out["problems"] += rep.problems
        mine = {f.name for f in funcs}
        if mine:
            out["cross-checked"] = f"{len(mine & covered)}/{len(mine)} functions have an independent check in the topics above"
    return not out["problems"], out


def print_module(ok, out):
    print(f"== {out['module']}   ({out['functions']} functions)   topics: {', '.join(TOPICS.get(out['module'], [])) or '-'}")
    print(f"   import ...... {out['import']}")
    print(f"   examples .... {out['examples']}")
    print(f"   checks ...... {out['checks']}" + (f"  [{out['cross-checked']}]" if 'cross-checked' in out else ""))
    for p in out["problems"][:40]:
        print("   PROBLEM:", p)
    if len(out["problems"]) > 40:
        print(f"   ... and {len(out['problems']) - 40} more")
    print("   " + ("OK" if ok else "FAILED"))


def main(argv):
    if not argv:
        print(__doc__)
        print(f"{'module':<28}{'functions':>9}  test topics")
        for m in MODULES:
            print(f"{m:<28}{len(_functions_of(m)):>9}  {', '.join(TOPICS.get(m, [])) or '-'}")
        return 0
    if argv[0] == "--topics":
        from scicalc import tests
        for t in tests.topics():
            print(t)
        return 0
    if argv[0] == "--topic":
        rep, _ = _run_topics(argv[1:])
        print(f"{rep.total} checks, {len(rep.problems)} problem(s)")
        for p in rep.problems[:50]:
            print("PROBLEM:", p)
        return 1 if rep.problems else 0
    if argv[0] == "--full":
        from scicalc.app import main as app_main
        return app_main(["--selftest", "--quiet"])
    names = MODULES if argv[0] == "--all" else argv
    bad = [n for n in names if n not in MODULES]
    if bad:
        print("unknown module(s):", ", ".join(bad), "\nrun  python run_tests.py  to list them")
        return 2
    failed = []
    rows = []
    for n in names:
        ok, out = test_module(n)
        rows.append(out)
        if argv[0] != "--all":
            print_module(ok, out)
        if not ok:
            failed.append(n)
    if argv[0] == "--all":
        print(f"{'module':<28}{'import':<8}{'functions':>9}  {'examples':<10}{'checks':<14}result")
        for o in rows:
            res = "OK" if not o["problems"] else f"{len(o['problems'])} PROBLEM(S)"
            print(f"{o['module']:<28}{o['import'][:6]:<8}{o['functions']:>9}  {o['examples']:<10}{o['checks']:<14}{res}")
        for o in rows:
            for p in o["problems"][:5]:
                print(f"  [{o['module']}] {p}")
    print(("\nALL PASSED" if not failed else f"\nFAILED: {', '.join(failed)}"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
