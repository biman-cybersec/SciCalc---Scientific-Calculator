"""SCICALC - an offline, Casio-style scientific calculator, split into modules.

Importing the package loads the library modules in the order below (the order matters: it is the order in which
functions and constants are registered).  Every module imports explicitly what it uses from the module that
defines it, so editors such as VS Code / Pylance can follow every name.  See MODULES.md for the list.
"""

from . import (  # noqa: F401  (loaded for their side effect: registering functions and constants)
    errors,
    registry,
    arithmetic,
    display,
    parser,
    engine,
    lib_trig,
    lib_powers_rounding,
    lib_numtheory_basic,
    lib_constants_basic,
    lib_geometry_daily,
    lib_finance_stats_basic,
    lib_vectors_solver_basen,
    lib_science_basic,
    lib_expansion_basic,
    lib_special_functions,
    lib_distributions,
    lib_regression,
    lib_inference,
    lib_numerical,
    lib_units,
    lib_numtheory_sprint3,
    lib_algebra,
    menu,
    cli,
    lib_geometry_extras,
    lib_calculus,
    lib_basen,
    lib_complex_c,
    lib_vectors_matrices,
    lib_physics,
    lib_finance_calendar,
    lib_lists_matrices,
    lib_chemistry,
    lib_complex_type,
    lib_equations_tables,
    lib_engineering,
    lib_electronics,
    lib_ml,
    lib_health,
    lib_astronomy_geodesy,
    lib_cooking_home,
    lib_type_extensions,
    constants_expansion,
    api,
)
from .api import Engine, dispatch, shared_engine
from .arithmetic import Cx, Lst, Mat
from .engine import Calculator, Result
from .errors import ArgumentError, CalcError, CalcSyntaxError, MathError
from .registry import REGISTRY

__all__ = [
    "ArgumentError", "CalcError", "CalcSyntaxError", "Calculator", "Cx", "Engine", "Lst", "Mat", "MathError",
    "REGISTRY", "Result", "dispatch", "shared_engine",
]
