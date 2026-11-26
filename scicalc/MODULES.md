# SCICALC modules

47 modules in `scicalc/`, loaded top to bottom. Every module imports explicitly, by name, what it uses from the module that defines it (so VS Code / Pylance can follow every name). `scicalc/__init__.py` imports the modules in this order, which is also the order functions and constants are registered.

Run `python run_tests.py <module>` to test one of them, or `python run_tests.py` for this list.

| # | module | what it holds | lines | functions | test topics |
|--:|---|---|--:|--:|---|
| 1 | `errors.py` | Error types (Math ERROR, Syntax ERROR, Argument ERROR) | 55 |  | bad_input |
| 2 | `registry.py` | Function registry: @register and register_constant | 180 |  |  |
| 3 | `arithmetic.py` | Exact fractions + clean floats, Lst/Mat/Cx value types | 312 |  | lists_matrices, complex_type |
| 4 | `display.py` | Display modes: Norm / Fix / Sci / Eng, fractions, symbolic text | 127 |  | display_sessions, symbolic_output |
| 5 | `parser.py` | Tokenizer and parser | 378 |  | input_features |
| 6 | `engine.py` | The Calculator class: state, evaluator, sessions | 711 |  | engine_behaviour, input_features, display_sessions |
| 7 | `lib_trig.py` | Trigonometry, inverse trig, hyperbolic, angle conversions | 283 | 43 | trig |
| 8 | `lib_powers_rounding.py` | Powers, roots, exp/log, rounding, integers, random | 245 | 28 | powers_rounding |
| 9 | `lib_numtheory_basic.py` | Factorials, permutations, gcd/lcm, primes, number theory | 199 | 16 | number_theory |
| 10 | `lib_constants_basic.py` | First batch of named constants | 140 |  | constants |
| 11 | `lib_geometry_daily.py` | Daily life helpers, 2-D and 3-D geometry | 369 | 46 | geometry, finance_daily |
| 12 | `lib_finance_stats_basic.py` | First financial helpers and basic statistics | 205 | 24 | finance_daily, statistics |
| 13 | `lib_vectors_solver_basen.py` | Vectors, equation solver, unit helpers, DMS, base-N | 246 | 28 | vectors_complex_text, basen, calculus |
| 14 | `lib_science_basic.py` | Physics, complex numbers, matrices (first versions) | 273 | 28 | science_misc |
| 15 | `lib_expansion_basic.py` | Astronomy, ML, thermodynamics, acoustics, expansions 1-6 | 551 | 58 | science_misc |
| 16 | `lib_special_functions.py` | Sprint 1A: special functions | 580 | 22 | special_functions |
| 17 | `lib_distributions.py` | Sprint 1B: probability distributions | 372 | 30 | distributions |
| 18 | `lib_regression.py` | Sprint 1C: statistics and regression | 430 | 37 | statistics |
| 19 | `lib_inference.py` | Sprint 1D/1E: inference, hypothesis tests, non-parametric tests | 680 | 49 | inference |
| 20 | `lib_numerical.py` | Sprint 2A: numerical methods and differential equations | 332 | 13 | calculus |
| 21 | `lib_units.py` | Unit conversion table and convert() | 175 | 77 | units |
| 22 | `lib_numtheory_sprint3.py` | Sprint 3A: number theory and combinatorics | 611 | 49 | number_theory |
| 23 | `lib_algebra.py` | Sprint 3B: algebra, equations and sequences | 370 | 37 | algebra |
| 24 | `menu.py` | Old numbered menu (menu_main) | 576 |  |  |
| 25 | `cli.py` | HELP text and the interactive prompt (calc_main) | 527 |  | display_sessions, engine_behaviour |
| 26 | `lib_geometry_extras.py` | Sprint 4: geometry extras | 501 | 61 | geometry_extras |
| 27 | `lib_calculus.py` | Sprint 5A: calculus and numerical analysis | 416 | 21 | calculus |
| 28 | `lib_basen.py` | Sprint 5B: base-N and bit operations | 236 | 24 | basen |
| 29 | `lib_complex_c.py` | Sprint 5C: c_* complex functions | 172 | 23 | complex_c |
| 30 | `lib_vectors_matrices.py` | Sprint 5D: vectors and 3x3/4x4 matrices | 328 | 29 | matrices |
| 31 | `lib_physics.py` | Sprint 6: physics | 604 | 84 | physics |
| 32 | `lib_finance_calendar.py` | Sprint 7: finance, calendar, navigation | 663 | 63 | finance_calendar |
| 33 | `lib_lists_matrices.py` | Sprint 8: list and matrix types | 414 | 43 | lists_matrices |
| 34 | `lib_chemistry.py` | Phase 3: chemistry | 509 | 46 | chemistry |
| 35 | `lib_complex_type.py` | Complex numbers as a value type | 73 | 5 | complex_type |
| 36 | `lib_equations_tables.py` | Equation and table modes | 363 | 7 | equations_tables |
| 37 | `lib_engineering.py` | Phase 3: engineering and materials | 347 | 44 | engineering |
| 38 | `lib_electronics.py` | Phase 3: electronics and signals | 273 | 36 | electronics |
| 39 | `lib_ml.py` | Phase 3: machine learning and data science | 405 | 44 | machine_learning |
| 40 | `lib_health.py` | Phase 3: health and fitness | 267 | 28 | health |
| 41 | `lib_astronomy_geodesy.py` | Phase 3: astronomy and geodesy | 279 | 26 | astronomy_geodesy |
| 42 | `lib_cooking_home.py` | Phase 3: cooking and home | 166 | 16 | cooking_home |
| 43 | `lib_type_extensions.py` | List/matrix statistics and solve_all | 331 | 17 | type_extensions |
| 44 | `constants_expansion.py` | Constants expansion (266 total) and sym_form | 268 | 1 | constants, symbolic_output |
| 45 | `api.py` | Plain-data API for apps (web, desktop, phone) | 223 |  | api |
| 46 | `selftest.py` | selftest() runner | 111 |  |  |
| 47 | `app.py` | print_docs() and main() | 68 |  |  |

## Other files

- `calculator.py` - the main executor (starts `scicalc.app.main()`); every command line option still works: `python calculator.py`, `"expr"`, `--menu`, `--selftest [--quiet]`, `--examples`, `--coverage`, `--docs`.
- `run_tests.py` - test one module or one topic on its own.
- `scicalc/tests/` - the self-test suite split by topic (`test_trig.py`, `test_units.py` ...). `tests/helpers.py` holds the shared helpers; `tests/__init__.py` lists every section in the order the full self-test runs them.

## Rules for editing

- A new function goes in the library module that fits it. A new `lib_*.py` file must be (1) added to `MODULES` in `run_tests.py`, (2) added to the import list in `scicalc/__init__.py` (the order there is the registration order), and (3) import what it uses, e.g. `from .registry import register`.
- Importing a name from another module is explicit: `from .lib_calculus import _make_fn`. Underscore names can be imported like any other.
- A function that needs something defined in a LATER module imports it inside the function (`from .display import format_number`); five modules do this.
- Do not give two modules the same top-level name: the later one would not replace the earlier one for code already loaded. (The original file had two such clashes, `_DIGITS` and `_NAV`; they were renamed.)
- You CAN run any single file (VS Code "Run Python File", or `python scicalc/lib_trig.py`): it tests that module and prints the result, the same as `python run_tests.py lib_trig`. (Before, running a module file directly failed with "attempted relative import with no known parent package", because the modules import each other with relative imports; the guard at the top of each file fixes that.)
- Do not start a module with `python -m scicalc.NAME` (it would register its functions twice). Use `python run_tests.py NAME`, or `python -c "import scicalc.NAME"` to see only an import error.
- A module that imports fine but fails a check: `python run_tests.py <module>` names the failing check.
