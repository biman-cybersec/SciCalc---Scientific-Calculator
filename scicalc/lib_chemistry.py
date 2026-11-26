"""Phase 3: chemistry

Module 34 of 47.  Taken from lines 11613-12100 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_chemistry"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
import re

from .errors import ArgumentError, MathError
from .registry import register
from .arithmetic import _is_scalar, ar_snap
from .lib_powers_rounding import _whole
from .lib_physics import _K
from .lib_lists_matrices import _S

# ======================================================================================
#  PHASE 3 : CHEMISTRY (46)
#  Offline table of the 118 elements: symbol, name, standard atomic weight (abridged IUPAC
#  values; for elements without a stable isotope the mass number of a long-lived isotope,
#  the bracketed value in the usual tables) and Pauling electronegativity (blank where no
#  single accepted value exists: He, Ne, Ar, Pm, Eu, Yb, Fr, Rn, Lr and heavier).
#  Every function that takes an element accepts the atomic number or the symbol/name in
#  quotes: atomic_mass(26) = atomic_mass('Fe').  Formulas are written like 'Ca(OH)2',
#  'Al2(SO4)3', 'K4[Fe(CN)6]' or with water of crystallisation 'CuSO4.5H2O'.
#  Units: grams, moles, litres, kelvin, joules, kPa; pH uses 10^-14 for Kw.
# ======================================================================================
_CHM = "Chemistry"
_ELEMENTS = (
    # Z, symbol, name, atomic weight, Pauling electronegativity (0 = none)
    (1, "H", "Hydrogen", 1.008, 2.20), (2, "He", "Helium", 4.0026, 0), (3, "Li", "Lithium", 6.94, 0.98),
    (4, "Be", "Beryllium", 9.0122, 1.57), (5, "B", "Boron", 10.81, 2.04), (6, "C", "Carbon", 12.011, 2.55),
    (7, "N", "Nitrogen", 14.007, 3.04), (8, "O", "Oxygen", 15.999, 3.44), (9, "F", "Fluorine", 18.998, 3.98),
    (10, "Ne", "Neon", 20.180, 0), (11, "Na", "Sodium", 22.990, 0.93), (12, "Mg", "Magnesium", 24.305, 1.31),
    (13, "Al", "Aluminium", 26.982, 1.61), (14, "Si", "Silicon", 28.085, 1.90), (15, "P", "Phosphorus", 30.974, 2.19),
    (16, "S", "Sulfur", 32.06, 2.58), (17, "Cl", "Chlorine", 35.45, 3.16), (18, "Ar", "Argon", 39.95, 0),
    (19, "K", "Potassium", 39.098, 0.82), (20, "Ca", "Calcium", 40.078, 1.00), (21, "Sc", "Scandium", 44.956, 1.36),
    (22, "Ti", "Titanium", 47.867, 1.54), (23, "V", "Vanadium", 50.942, 1.63), (24, "Cr", "Chromium", 51.996, 1.66),
    (25, "Mn", "Manganese", 54.938, 1.55), (26, "Fe", "Iron", 55.845, 1.83), (27, "Co", "Cobalt", 58.933, 1.88),
    (28, "Ni", "Nickel", 58.693, 1.91), (29, "Cu", "Copper", 63.546, 1.90), (30, "Zn", "Zinc", 65.38, 1.65),
    (31, "Ga", "Gallium", 69.723, 1.81), (32, "Ge", "Germanium", 72.630, 2.01), (33, "As", "Arsenic", 74.922, 2.18),
    (34, "Se", "Selenium", 78.971, 2.55), (35, "Br", "Bromine", 79.904, 2.96), (36, "Kr", "Krypton", 83.798, 3.00),
    (37, "Rb", "Rubidium", 85.468, 0.82), (38, "Sr", "Strontium", 87.62, 0.95), (39, "Y", "Yttrium", 88.906, 1.22),
    (40, "Zr", "Zirconium", 91.224, 1.33), (41, "Nb", "Niobium", 92.906, 1.6), (42, "Mo", "Molybdenum", 95.95, 2.16),
    (43, "Tc", "Technetium", 97, 1.9), (44, "Ru", "Ruthenium", 101.07, 2.2), (45, "Rh", "Rhodium", 102.91, 2.28),
    (46, "Pd", "Palladium", 106.42, 2.20), (47, "Ag", "Silver", 107.87, 1.93), (48, "Cd", "Cadmium", 112.41, 1.69),
    (49, "In", "Indium", 114.82, 1.78), (50, "Sn", "Tin", 118.71, 1.96), (51, "Sb", "Antimony", 121.76, 2.05),
    (52, "Te", "Tellurium", 127.60, 2.1), (53, "I", "Iodine", 126.90, 2.66), (54, "Xe", "Xenon", 131.29, 2.6),
    (55, "Cs", "Caesium", 132.91, 0.79), (56, "Ba", "Barium", 137.33, 0.89), (57, "La", "Lanthanum", 138.91, 1.10),
    (58, "Ce", "Cerium", 140.12, 1.12), (59, "Pr", "Praseodymium", 140.91, 1.13), (60, "Nd", "Neodymium", 144.24, 1.14),
    (61, "Pm", "Promethium", 145, 0), (62, "Sm", "Samarium", 150.36, 1.17), (63, "Eu", "Europium", 151.96, 0),
    (64, "Gd", "Gadolinium", 157.25, 1.20), (65, "Tb", "Terbium", 158.93, 1.1), (66, "Dy", "Dysprosium", 162.50, 1.22),
    (67, "Ho", "Holmium", 164.93, 1.23), (68, "Er", "Erbium", 167.26, 1.24), (69, "Tm", "Thulium", 168.93, 1.25),
    (70, "Yb", "Ytterbium", 173.05, 0), (71, "Lu", "Lutetium", 174.97, 1.27), (72, "Hf", "Hafnium", 178.49, 1.3),
    (73, "Ta", "Tantalum", 180.95, 1.5), (74, "W", "Tungsten", 183.84, 2.36), (75, "Re", "Rhenium", 186.21, 1.9),
    (76, "Os", "Osmium", 190.23, 2.2), (77, "Ir", "Iridium", 192.22, 2.20), (78, "Pt", "Platinum", 195.08, 2.28),
    (79, "Au", "Gold", 196.97, 2.54), (80, "Hg", "Mercury", 200.59, 2.00), (81, "Tl", "Thallium", 204.38, 1.62),
    (82, "Pb", "Lead", 207.2, 2.33), (83, "Bi", "Bismuth", 208.98, 2.02), (84, "Po", "Polonium", 209, 2.0),
    (85, "At", "Astatine", 210, 2.2), (86, "Rn", "Radon", 222, 0), (87, "Fr", "Francium", 223, 0),
    (88, "Ra", "Radium", 226, 0.9), (89, "Ac", "Actinium", 227, 1.1), (90, "Th", "Thorium", 232.04, 1.3),
    (91, "Pa", "Protactinium", 231.04, 1.5), (92, "U", "Uranium", 238.03, 1.38), (93, "Np", "Neptunium", 237, 1.36),
    (94, "Pu", "Plutonium", 244, 1.28), (95, "Am", "Americium", 243, 1.3), (96, "Cm", "Curium", 247, 1.3),
    (97, "Bk", "Berkelium", 247, 1.3), (98, "Cf", "Californium", 251, 1.3), (99, "Es", "Einsteinium", 252, 1.3),
    (100, "Fm", "Fermium", 257, 1.3), (101, "Md", "Mendelevium", 258, 1.3), (102, "No", "Nobelium", 259, 1.3),
    (103, "Lr", "Lawrencium", 266, 0), (104, "Rf", "Rutherfordium", 267, 0), (105, "Db", "Dubnium", 268, 0),
    (106, "Sg", "Seaborgium", 267, 0), (107, "Bh", "Bohrium", 270, 0), (108, "Hs", "Hassium", 271, 0),
    (109, "Mt", "Meitnerium", 278, 0), (110, "Ds", "Darmstadtium", 281, 0), (111, "Rg", "Roentgenium", 282, 0),
    (112, "Cn", "Copernicium", 285, 0), (113, "Nh", "Nihonium", 286, 0), (114, "Fl", "Flerovium", 289, 0),
    (115, "Mc", "Moscovium", 290, 0), (116, "Lv", "Livermorium", 293, 0), (117, "Ts", "Tennessine", 294, 0),
    (118, "Og", "Oganesson", 294, 0),
)
_EL_BY_SYMBOL = {e[1]: e for e in _ELEMENTS}
_EL_BY_NAME = {e[2].lower(): e for e in _ELEMENTS}
_EL_BY_NAME.update({"aluminum": _ELEMENTS[12], "cesium": _ELEMENTS[54], "sulphur": _ELEMENTS[15]})
_PERIOD_ENDS = (2, 10, 18, 36, 54, 86, 118)


def _el(x):
    """An element given as its atomic number or its symbol/name in quotes."""
    if isinstance(x, str):
        e = _EL_BY_SYMBOL.get(x.strip()) or _EL_BY_NAME.get(x.strip().lower())
        if e is None:
            raise MathError(f"unknown element '{x}'")
        return e
    z = _whole(_S(x), "atomic number")
    if not 1 <= z <= 118:
        raise MathError("atomic number must be between 1 and 118")
    return _ELEMENTS[z - 1]


def _cn(x):
    """A plain number (not a list or text) as a float."""
    if not _is_scalar(x):
        raise ArgumentError("this needs a number")
    return float(x)


def _chm(name, desc, args, example, exact=False):
    return register(name, _CHM, desc, args, exact=exact, example=example)


@_chm("atomic_mass", "Atomic weight in g/mol of an element given by number or symbol: atomic_mass(26) or atomic_mass('Fe')", 1, "atomic_mass('Fe') => 55.845", exact=True)
def atomic_mass(e):
    return _el(e)[3]


@_chm("electronegativity", "Pauling electronegativity of an element (Math ERROR where there is no accepted value): electronegativity('O')", 1, "electronegativity('O') => 3.44", exact=True)
def electronegativity(e):
    v = _el(e)[4]
    if not v:
        raise MathError("no electronegativity value for this element")
    return v


@_chm("atomic_number", "Atomic number from a symbol or name: atomic_number('Fe')", 1, "atomic_number('Fe') => 26", exact=True)
def atomic_number(e):
    return _el(e)[0]


@_chm("element_symbol", "Symbol of an element: element_symbol(26)", 1, "element_symbol(26) => Fe", exact=True)
def element_symbol(e):
    return _el(e)[1]


@_chm("element_name", "Name of an element: element_name(26)", 1, "element_name(26) => Iron", exact=True)
def element_name(e):
    return _el(e)[2]


@_chm("element_period", "Row (period) of the periodic table, 1 to 7: element_period('Fe')", 1, "element_period('Fe') => 4", exact=True)
def element_period(e):
    z = _el(e)[0]
    return next(i + 1 for i, end in enumerate(_PERIOD_ENDS) if z <= end)


@_chm("element_group", "Group (column) 1 to 18; the f-block (lanthanides and actinides, Z 57-71 and 89-103) has none: element_group('Fe')", 1, "element_group('Fe') => 8", exact=True)
def element_group(e):
    z = _el(e)[0]
    if 57 <= z <= 71 or 89 <= z <= 103:
        raise MathError("the f-block elements have no group number")
    if z <= 2:
        return 1 if z == 1 else 18
    if z <= 18:
        k = z - (2 if z <= 10 else 10)
        return k if k <= 2 else k + 10
    if z <= 54:
        return z - (18 if z <= 36 else 36)
    if z <= 86:
        return z - 54 if z <= 56 else z - 68
    return z - 86 if z <= 88 else z - 100


_FORMULA_MAX = 200


def _formula(f):
    """'Ca(OH)2' -> {'Ca': 1, 'O': 2, 'H': 2}. Brackets and hydrate dots allowed."""
    if not isinstance(f, str):
        raise ArgumentError("this needs a formula in quotes, such as 'H2O'")
    f = f.strip()
    if not f or len(f) > _FORMULA_MAX:
        raise MathError("not a usable formula")
    total = {}
    for part in re.split(r"[.·*•]", f):
        if not part:
            raise MathError("empty part in the formula")
        i, n = 0, len(part)

        def number():
            nonlocal i
            j = i
            while j < n and part[j].isdigit() and part[j].isascii():
                j += 1
            if j == i:
                return 1
            k = int(part[i:j])
            i = j
            if k < 1 or k > 100000:
                raise MathError("subscript out of range")
            return k
        coef = number()
        stack, closers = [{}], []
        while i < n:
            c = part[i]
            if c in "([":
                stack.append({})
                closers.append(")" if c == "(" else "]")
                i += 1
            elif c in ")]":
                if not closers or closers.pop() != c:
                    raise MathError("unbalanced brackets")
                i += 1
                k = number()
                grp = stack.pop()
                for sym, v in grp.items():
                    stack[-1][sym] = stack[-1].get(sym, 0) + v * k
            elif c.isascii() and c.isupper():
                sym = c
                if i + 1 < n and part[i + 1].isascii() and part[i + 1].islower():
                    sym = part[i:i + 2]
                    i += 1
                i += 1
                if sym not in _EL_BY_SYMBOL:
                    raise MathError(f"unknown element '{sym}'")
                stack[-1][sym] = stack[-1].get(sym, 0) + number()
            else:
                raise MathError(f"unexpected '{c}' in the formula")
        if closers or len(stack) != 1:
            raise MathError("unbalanced brackets")
        for sym, v in stack[0].items():
            total[sym] = total.get(sym, 0) + v * coef
    if not total:
        raise MathError("empty formula")
    if sum(total.values()) > 10 ** 9:
        raise MathError("formula too large")
    return total


def _fmass(f):
    return math.fsum(_EL_BY_SYMBOL[s][3] * k for s, k in _formula(f).items())


@_chm("molar_mass", "Molar mass in g/mol of a formula: molar_mass('Ca(OH)2'), also 'CuSO4.5H2O'", 1, "molar_mass('H2O') => 18.015", exact=True)
def molar_mass(f):
    return ar_snap(_fmass(f))


@_chm("atom_count", "Number of atoms of one element in a formula: atom_count('Al2(SO4)3', 'O')", 2, "atom_count('Al2(SO4)3', 'O') => 12", exact=True)
def atom_count(f, e):
    return _formula(f).get(_el(e)[1], 0)


@_chm("formula_atoms", "Total number of atoms in one formula unit: formula_atoms('H2O')", 1, "formula_atoms('Ca(OH)2') => 5", exact=True)
def formula_atoms(f):
    return sum(_formula(f).values())


@_chm("mass_percent", "Percentage of an element in a compound by mass: mass_percent('H2O', 'O')", 2, "mass_percent('H2O', 'O') => 88.80933", exact=True)
def mass_percent(f, e):
    sym = _el(e)[1]
    n = _formula(f).get(sym, 0)
    return ar_snap(round(n * _EL_BY_SYMBOL[sym][3] / _fmass(f) * 100, 5))


def _molar(m):
    """A molar mass given as a number or as a formula in quotes."""
    v = _fmass(m) if isinstance(m, str) else _cn(m)
    if not v > 0:
        raise MathError("molar mass must be positive")
    return v


@_chm("moles_from_mass", "Moles = mass (g) / molar mass; the molar mass may be a number or a formula: moles_from_mass(36.03, 'H2O')", 2, "moles_from_mass(36.03, 'H2O') => 2", exact=True)
def moles_from_mass(mass, m):
    mass = _cn(mass)
    if mass < 0:
        raise MathError("mass must not be negative")
    return mass / _molar(m)


@_chm("mass_from_moles", "Mass (g) = moles * molar mass (number or formula): mass_from_moles(2, 'H2O')", 2, "mass_from_moles(2, 'H2O') => 36.03", exact=True)
def mass_from_moles(n, m):
    n = _cn(n)
    if n < 0:
        raise MathError("moles must not be negative")
    return n * _molar(m)


@_chm("molecules_from_moles", "Number of particles = moles * Avogadro's number: molecules_from_moles(0.5)", 1, "molecules_from_moles(1) => 6.02214076×10^23")
def molecules_from_moles(n):
    if n < 0:
        raise MathError("moles must not be negative")
    return n * _K("const_NA")


@_chm("moles_from_molecules", "Moles = number of particles / Avogadro's number: moles_from_molecules(3.011e23)", 1, "moles_from_molecules(6.02214076e23) => 1")
def moles_from_molecules(count):
    if count < 0:
        raise MathError("the number of particles must not be negative")
    return count / _K("const_NA")


@_chm("percent_yield", "Percent yield = actual / theoretical * 100: percent_yield(actual, theoretical)", 2, "percent_yield(8, 10) => 80")
def percent_yield(actual, theoretical):
    if actual < 0 or not theoretical > 0:
        raise MathError("need actual >= 0 and theoretical > 0")
    return actual / theoretical * 100


@_chm("dilution_v2", "Final volume after diluting: V2 = C1*V1/C2: dilution_v2(c1, v1, c2)", 3, "dilution_v2(2, 50, 0.5) => 200")
def dilution_v2(c1, v1, c2):
    if c1 < 0 or v1 < 0 or not c2 > 0:
        raise MathError("need c1, v1 >= 0 and c2 > 0")
    return c1 * v1 / c2


@_chm("dilution_c2", "Final concentration after diluting: C2 = C1*V1/V2: dilution_c2(c1, v1, v2)", 3, "dilution_c2(2, 50, 200) => 0.5")
def dilution_c2(c1, v1, v2):
    if c1 < 0 or v1 < 0 or not v2 > 0:
        raise MathError("need c1, v1 >= 0 and v2 > 0")
    return c1 * v1 / v2


@_chm("molality", "Molality = moles of solute / kg of solvent: molality(1, 0.5)", 2, "molality(1, 0.5) => 2")
def molality(n, kg):
    if n < 0 or not kg > 0:
        raise MathError("need moles >= 0 and kg > 0")
    return n / kg


@_chm("mole_fraction", "Mole fraction = n / n_total: mole_fraction(1, 4)", 2, "mole_fraction(1, 4) => 0.25")
def mole_fraction(n, total):
    if n < 0 or not total > 0 or n > total:
        raise MathError("need 0 <= n <= total and total > 0")
    return n / total


@_chm("percent_by_mass", "Mass percent of solute in a solution: percent_by_mass(solute_g, solution_g)", 2, "percent_by_mass(5, 50) => 10")
def percent_by_mass(solute, solution):
    if solute < 0 or not solution > 0 or solute > solution:
        raise MathError("need 0 <= solute <= solution and solution > 0")
    return solute / solution * 100


@_chm("ppm", "Parts per million by mass: ppm(solute_g, solution_g)", 2, "ppm(0.002, 1000) => 2")
def ppm(solute, solution):
    if solute < 0 or not solution > 0 or solute > solution:
        raise MathError("need 0 <= solute <= solution and solution > 0")
    return solute / solution * 1e6


@_chm("normality", "Normality = molarity * equivalents per mole: normality(0.5, 2)", 2, "normality(0.5, 2) => 1")
def normality(m, eq):
    if m < 0 or not eq > 0:
        raise MathError("need molarity >= 0 and equivalents > 0")
    return m * eq


_KW = 1e-14


@_chm("ph_strong_acid", "pH of a strong monoprotic acid of concentration c (mol/L), including the water correction for very dilute acid: ph_strong_acid(c)", 1, "ph_strong_acid(0.01) => 2")
def ph_strong_acid(c):
    if not c > 0:
        raise MathError("concentration must be positive")
    h = (c + math.sqrt(c * c + 4 * _KW)) / 2
    return ar_snap(-math.log10(h))


@_chm("ph_strong_base", "pH of a strong monohydroxide base of concentration c (mol/L): ph_strong_base(c)", 1, "ph_strong_base(0.01) => 12")
def ph_strong_base(c):
    if not c > 0:
        raise MathError("concentration must be positive")
    oh = (c + math.sqrt(c * c + 4 * _KW)) / 2
    return ar_snap(-math.log10(_KW / oh))


@_chm("ph_weak_acid", "pH of a weak acid (concentration c mol/L, acid constant Ka), solving x^2/(c-x) = Ka exactly: ph_weak_acid(c, Ka)", 2, "ph_weak_acid(0.1, 1e-5) => 3.002171463")
def ph_weak_acid(c, ka):
    if not c > 0 or not ka > 0:
        raise MathError("c and Ka must be positive")
    x = (-ka + math.sqrt(ka * ka + 4 * ka * c)) / 2
    return round(-math.log10(x), 9)


@_chm("ph_weak_base", "pH of a weak base (concentration c mol/L, base constant Kb): ph_weak_base(c, Kb)", 2, "ph_weak_base(0.1, 1e-5) => 10.99782854")
def ph_weak_base(c, kb):
    if not c > 0 or not kb > 0:
        raise MathError("c and Kb must be positive")
    x = (-kb + math.sqrt(kb * kb + 4 * kb * c)) / 2
    return round(14 + math.log10(x), 9)


@_chm("buffer_ph", "pH of a buffer from the acid constant Ka and the acid and base (conjugate) concentrations: buffer_ph(Ka, c_acid, c_base)", 3, "buffer_ph(1e-5, 0.1, 0.1) => 5")
def buffer_ph(ka, acid, base):
    if not (ka > 0 and acid > 0 and base > 0):
        raise MathError("all three values must be positive")
    return ar_snap(-math.log10(ka) + math.log10(base / acid))


@_chm("pka_from_ka", "pKa = -log10(Ka): pka_from_ka(1e-5)", 1, "pka_from_ka(1e-5) => 5")
def pka_from_ka(ka):
    if not ka > 0:
        raise MathError("Ka must be positive")
    return ar_snap(-math.log10(ka))


@_chm("ka_from_pka", "Ka = 10^-pKa: ka_from_pka(5)", 1, "ka_from_pka(5) => 0.00001")
def ka_from_pka(pka):
    if not -300 < pka < 300:
        raise MathError("pKa out of range")
    return ar_snap(10.0 ** -pka)


@_chm("nernst", "Cell potential E = E0 - (R T / n F) ln Q in volts (T in kelvin, default 298.15): nernst(E0, n, Q [, T])", (3, 4), "nernst(1.1, 2, 1) => 1.1")
def nernst(e0, n, q, t=298.15):
    if not (n > 0 and q > 0 and t > 0):
        raise MathError("need n > 0, Q > 0 and T > 0")
    return e0 - _K("const_R") * t / (n * _K("const_F")) * math.log(q)


@_chm("gibbs", "Gibbs energy change dG = dH - T dS (J/mol, J/(mol K), K): gibbs(dH, T, dS)", 3, "gibbs(-100000, 300, -100) => -70000")
def gibbs(dh, t, ds):
    if t < 0:
        raise MathError("temperature must not be negative")
    return dh - t * ds


@_chm("gibbs_from_k", "dG = -R T ln K in J/mol: gibbs_from_k(T, K)", 2, "gibbs_from_k(298.15, 1) => 0")
def gibbs_from_k(t, k):
    if not (t > 0 and k > 0):
        raise MathError("T and K must be positive")
    return -_K("const_R") * t * math.log(k)


@_chm("k_from_gibbs", "Equilibrium constant K = exp(-dG / R T): k_from_gibbs(dG, T)", 2, "k_from_gibbs(0, 300) => 1")
def k_from_gibbs(dg, t):
    if not t > 0:
        raise MathError("T must be positive")
    return math.exp(-dg / (_K("const_R") * t))


@_chm("cell_gibbs", "dG = -n F E in J/mol: cell_gibbs(n, E)", 2, "cell_gibbs(2, 1.1) => -212267.7307")
def cell_gibbs(n, e):
    if not n > 0:
        raise MathError("n must be positive")
    return -n * _K("const_F") * e


@_chm("arrhenius", "Rate constant k = A exp(-Ea / R T), Ea in J/mol: arrhenius(A, Ea, T)", 3, "arrhenius(1000, 0, 300) => 1000")
def arrhenius(a, ea, t):
    if not (a >= 0 and ea >= 0 and t > 0):
        raise MathError("need A >= 0, Ea >= 0 and T > 0")
    return a * math.exp(-ea / (_K("const_R") * t))


@_chm("arrhenius_ea", "Activation energy (J/mol) from rate constants k1 at T1 and k2 at T2: arrhenius_ea(k1, T1, k2, T2)", 4, "arrhenius_ea(1, 300, 1, 350) => 0")
def arrhenius_ea(k1, t1, k2, t2):
    if not (k1 > 0 and k2 > 0 and t1 > 0 and t2 > 0) or t1 == t2:
        raise MathError("need positive k and T values with T1 different from T2")
    return _K("const_R") * math.log(k2 / k1) / (1 / t1 - 1 / t2)


@_chm("osmotic_pressure", "Osmotic pressure in kPa = i M R T (M in mol/L, T in K, van 't Hoff factor i default 1): osmotic_pressure(M, T [, i])", (2, 3), "osmotic_pressure(0.1, 300) => 249.4338785")
def osmotic_pressure(m, t, i=1):
    if m < 0 or not t > 0 or not i > 0:
        raise MathError("need M >= 0, T > 0 and i > 0")
    return i * m * _K("const_R") * t


@_chm("boiling_elevation", "Boiling point rise dT = i Kb m: boiling_elevation(Kb, molality [, i])", (2, 3), "boiling_elevation(0.512, 2) => 1.024")
def boiling_elevation(kb, m, i=1):
    if kb < 0 or m < 0 or not i > 0:
        raise MathError("need Kb >= 0, molality >= 0 and i > 0")
    return i * kb * m


@_chm("freezing_depression", "Freezing point drop dT = i Kf m: freezing_depression(Kf, molality [, i])", (2, 3), "freezing_depression(1.86, 0.5, 2) => 1.86")
def freezing_depression(kf, m, i=1):
    if kf < 0 or m < 0 or not i > 0:
        raise MathError("need Kf >= 0, molality >= 0 and i > 0")
    return i * kf * m


@_chm("first_order_conc", "Concentration after time t in a first-order reaction: c0 exp(-k t): first_order_conc(c0, k, t)", 3, "first_order_conc(1, ln(2), 1) => 0.5")
def first_order_conc(c0, k, t):
    if c0 < 0 or k < 0 or t < 0:
        raise MathError("values must not be negative")
    return c0 * math.exp(-k * t)


@_chm("half_life_first_order", "Half-life of a first-order reaction, ln 2 / k: half_life_first_order(k)", 1, "half_life_first_order(ln(2)) => 1")
def half_life_first_order(k):
    if not k > 0:
        raise MathError("k must be positive")
    return math.log(2) / k


@_chm("second_order_conc", "Concentration after time t in a second-order reaction: c0 / (1 + k c0 t): second_order_conc(c0, k, t)", 3, "second_order_conc(2, 0.5, 1) => 1")
def second_order_conc(c0, k, t):
    if c0 < 0 or k < 0 or t < 0:
        raise MathError("values must not be negative")
    return c0 / (1 + k * c0 * t)


@_chm("graham_ratio", "Graham's law: rate of gas 1 / rate of gas 2 = sqrt(M2 / M1); M may be a number or a formula: graham_ratio('H2', 'O2')", 2, "graham_ratio(2, 32) => 4", exact=True)
def graham_ratio(m1, m2):
    return math.sqrt(_molar(m2) / _molar(m1))


@_chm("raoult_pressure", "Vapour pressure of a solution = mole fraction of solvent * pure vapour pressure: raoult_pressure(x_solvent, p0)", 2, "raoult_pressure(0.9, 100) => 90")
def raoult_pressure(x, p0):
    if not 0 <= x <= 1 or p0 < 0:
        raise MathError("need 0 <= x <= 1 and p0 >= 0")
    return x * p0


@_chm("isotope_avg_mass", "Average atomic mass of two isotopes: masses m1, m2 and abundance of the first in percent: isotope_avg_mass(m1, m2, pct1)", 3, "isotope_avg_mass(10.013, 11.009, 19.9) => 10.810796")
def isotope_avg_mass(m1, m2, pct1):
    if not (m1 > 0 and m2 > 0 and 0 <= pct1 <= 100):
        raise MathError("need positive masses and 0 <= percent <= 100")
    return (m1 * pct1 + m2 * (100 - pct1)) / 100
