"""The self-test suite, split by topic.

SECTIONS lists every check section in the order the full self-test runs them:
    (number, title, topic module, function name, names it needs from the shared helpers)
A section that needs a helper another section defines gets it from S (the dict of shared names).
"""
import importlib
import inspect

from .helpers import make_helpers

SECTIONS = [
    (1, 'unit conversions', 'units', 'checks_units_1', ('check', 'cov', 'near')),
    (2, 'one-variable statistics', 'statistics', 'checks_statistics_2', ('near', 'csv', 'st')),
    (3, 'two-variable statistics', 'statistics', 'checks_statistics_3', ('near', 'csv', 'st')),
    (4, 'distributions', 'distributions', 'checks_distributions_4', ('check', 'ev', 'near', 'simpson')),
    (5, 'inference', 'inference', 'checks_inference_5', ('near', 'text')),
    (6, 'non-parametric / ANOVA (by definition)', 'inference', 'checks_inference_6', ('near', 'csv')),
    (7, 'special functions', 'special_functions', 'checks_special_functions_7', ('near', 'simpson')),
    (8, 'number theory (brute force)', 'number_theory', 'checks_number_theory_8', ('check', 'cov', 'ex', 'fn')),
    (9, 'algebra and sequences', 'algebra', 'checks_algebra_9', ('check', 'ev', 'near', 'csv')),
    (10, 'trigonometry and hyperbolic', 'trig', 'checks_trig_10', ('check', 'run', 'near')),
    (11, 'powers, logs, rounding', 'powers_rounding', 'checks_powers_rounding_11', ('check', 'ev', 'near', 'ex')),
    (12, 'geometry', 'geometry', 'checks_geometry_12', ('near', 'simpson')),
    (13, 'finance and daily life', 'finance_daily', 'checks_finance_daily_13', ('check', 'ev', 'near')),
    (14, 'vectors, matrices, complex, text results', 'vectors_complex_text', 'checks_vectors_complex_text_14', ('check', 'run', 'ev', 'near', 'text', 'cmath')),
    (15, 'bases and bit operations', 'basen', 'checks_basen_15', ('ex', 'text')),
    (16, 'physics, chemistry, astronomy, optics ...', 'science_misc', 'checks_science_misc_16', ('ev', 'near')),
    (17, 'calculus, numerical methods, machine learning', 'calculus', 'checks_calculus_17', ('near',)),
    (18, 'Sprint 4 geometry extras', 'geometry_extras', 'checks_geometry_extras_18', ('check', 'ev', 'near', 'ex', 'simpson')),
    (19, 'Sprint 5 : calculus (RAD mode, closed forms)', 'calculus', 'checks_calculus_19', ('check', 'run', 'ev', 'ex')),
    (20, 'Sprint 5 : base-N and bits (brute force)', 'basen', 'checks_basen_20', ('check', 'run', 'ex', 'text')),
    (21, 'Sprint 5 : complex numbers', 'complex_c', 'checks_complex_c_21', ('check', 'run', 'ev', 'near', 'ex', 'text', 'cx')),
    (22, 'Sprint 5 : matrices and vectors', 'matrices', 'checks_matrices_22', ('check', 'ev', 'near', 'ex', 'mtext')),
    (23, 'Sprint 6 : physics', 'physics', 'checks_physics_23', ('check', 'ev', 'near', 'simpson')),
    (24, 'Sprint 7: finance, calendar, trig and navigation', 'finance_calendar', 'checks_finance_calendar_24', ('check', 'ev', 'near', 'ex', 'fn', 'nearr')),
    (25, 'Sprint 8: list and matrix types', 'lists_matrices', 'checks_lists_matrices_25', ('check', 'run', 'ev', 'near', 'ex', 'text')),
    (26, 'Phase 3: chemistry', 'chemistry', 'checks_chemistry_26', ('check', 'ev', 'near', 'ex', 'text', 're')),
    (27, 'complex numbers as a value type', 'complex_type', 'checks_complex_type_27', ('check', 'run', 'ev', 'ex', 'text', 'cmath', 'rg8')),
    (28, 'old matrix functions now return real matrices/lists', 'lists_matrices', 'checks_lists_matrices_28', ('check', 'near', 'ex', 'flat8', 'leibniz8', 'lit', 'rg8', 'rnd', 'val8')),
    (29, 'equation and table modes', 'equations_tables', 'checks_equations_tables_29', ('check', 'run', 'near', 'ex', 'text', '_Fr', '_it', 'bisect8', 'leibniz8', 'lit', 'nl', 'rg8', 'rnd', 'val8')),
    (30, 'input features', 'input_features', 'checks_input_features_30', ('check', 'run', 'near', 'text')),
    (31, 'Phase 3: engineering and materials', 'engineering', 'checks_engineering_31', ('check', 'ev', 'near', 'ex')),
    (32, 'Phase 3: electronics and signals', 'electronics', 'checks_electronics_32', ('check', 'ev', 'near', 'ex')),
    (33, 'Phase 3: machine learning and data science', 'machine_learning', 'checks_machine_learning_33', ('check', 'ev', 'near', 'ex', 'fn', 'lit', 'rg8')),
    (34, 'Phase 3: health and fitness', 'health', 'checks_health_34', ('check', 'near', 'ex')),
    (35, 'Phase 3: more astronomy and geodesy', 'astronomy_geodesy', 'checks_astronomy_geodesy_35', ('check', 'ev', 'near', 'ex')),
    (36, 'Phase 3: cooking and home', 'cooking_home', 'checks_cooking_home_36', ('check', 'ev', 'near', 'ex')),
    (37, 'type extensions: statistics returning lists, solve_all', 'type_extensions', 'checks_type_extensions_37', ('check', 'run', 'ev', 'near', 'fn', 'lit', 'rg8')),
    (38, 'constants expansion', 'constants', 'checks_constants_38', ('check', 'run', 'ev', 'near')),
    (39, 'ENG display, fraction display, sessions, constants browser', 'display_sessions', 'checks_display_sessions_39', ('check', 'text', 'rg8')),
    (40, 'symbolic-looking output', 'symbolic_output', 'checks_symbolic_output_40', ('check', 'run', 'text', '_json', 'cli', 'rg8')),
    (41, 'engine behaviour', 'engine_behaviour', 'checks_engine_behaviour_41', ('covered', 'ex')),
    (42, 'application programming interface', 'api', 'checks_api_42', ('check',)),
]


def _load(group, name):
    return getattr(importlib.import_module(f"{__name__}.test_{group}"), name)


def run_sections(check, topics=None):
    """Run the sections (all, or only those whose topic is in `topics`) and return the set of covered function names.

    Sections of other topics still run first if the chosen one needs a helper they define, but their results are
    thrown away.
    """
    S = make_helpers(check)
    provides = {}
    for num, title, group, name, params in SECTIONS:
        pass
    for num, title, group, name, params in SECTIONS:
        wanted = topics is None or group in topics
        f = _load(group, name)
        local = S if wanted else dict(S, check=lambda *a, **k: None)
        if not wanted and not _needed_later(num, topics):
            continue
        args = {p: local[p] for p in inspect.signature(f).parameters}
        out = f(**args)
        if isinstance(out, dict):
            S.update(out)
    return S["covered"]


def _needed_later(num, topics):
    """True if a later wanted section needs a name defined by this (unwanted) section."""
    for n2, _t, g2, _f, params in SECTIONS:
        if n2 > num and g2 in topics and any(p in EXPORTS.get(num, ()) for p in params):
            return True
    return False


EXPORTS = {
    14: ('cx', 'mtext'),
    19: ('nearr',),
    25: ('_Fr', '_it', 'flat8', 'leibniz8', 'lit', 'nl', 'rg8', 'rnd', 'val8'),
    26: ('bisect8',),
    39: ('_json', 'cli'),
}


def topics():
    seen = []
    for _n, _t, g, _f, _p in SECTIONS:
        if g not in seen:
            seen.append(g)
    return seen
