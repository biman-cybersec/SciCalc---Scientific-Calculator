"""Checks: chemistry.  Run alone with  python run_tests.py chemistry"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "chemistry"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..lib_chemistry import _ELEMENTS

from .helpers import _err, _expr_error  # noqa: F401


def checks_chemistry_26(check, ev, near, ex, text, re):
    """Phase 3: chemistry"""
    # ================= Phase 3: chemistry =================
    # --- the element table against Madelung's filling rule (an independent derivation)
    order = sorted(((n, l) for n in range(1, 9) for l in range(0, min(n, 4))), key=lambda t: (t[0] + t[1], t[0]))
    def ideal_config(z):
        left, cfg = z, []
        for n, l in order:
            take = min(left, 2 * (2 * l + 1))
            if take:
                cfg.append((n, l, take))
            left -= take
            if not left:
                break
        return cfg
    group_bad, period_bad = [], []
    for z in range(1, 119):
        cfg = ideal_config(z)
        period = max(n for n, l, k in cfg)
        if ev(f"element_period({z})") != period:
            period_bad.append(z)
        n, l, k = cfg[-1]
        if 57 <= z <= 71 or 89 <= z <= 103:
            check(f"f-block element {z} has no group", _err(f"element_group({z})"), "Math ERROR")
            continue
        if z == 2:
            want = 18
        elif l == 0:
            want = k
        elif l == 1:
            want = 12 + k
        else:
            want = 2 + k
        if ev(f"element_group({z})") != want:
            group_bad.append((z, want))
    check("element_period matches Madelung filling for all 118", period_bad, [])
    check("element_group matches Madelung filling for all 118", group_bad, [])
    for sym, z, name in [("H", 1, "Hydrogen"), ("Fe", 26, "Iron"), ("Au", 79, "Gold"), ("Og", 118, "Oganesson"), ("U", 92, "Uranium"), ("Pb", 82, "Lead")]:
        ex(f"atomic_number('{sym}')", f"atomic_number('{sym}')", z)
        ex(f"element_symbol({z})", f"element_symbol({z})", sym)
        ex(f"element_name({z})", f"element_name({z})", name)
        ex(f"atomic_number by name {name}", f"atomic_number('{name.lower()}')", z)
    ex("a list of atomic numbers maps element by element", "atomic_mass({1,6,8})", (1.008, 12.011, 15.999))
    ex("a list of symbols is not a number", "atomic_number({1,2})", (1, 2))
    ex("US spelling aluminum", "atomic_number('aluminum')", 13)
    ex("US spelling cesium", "atomic_number('cesium')", 55)
    ex("table has 118 rows", "atomic_number('Og')", 118)
    syms = [row[1] for row in _ELEMENTS]
    check("118 elements", len(_ELEMENTS), 118)
    check("symbols unique", len(set(syms)), 118)
    check("names unique", len({row[2] for row in _ELEMENTS}), 118)
    check("atomic numbers consecutive", [row[0] for row in _ELEMENTS], list(range(1, 119)))
    check("symbols are Xx", all(re.fullmatch(r"[A-Z][a-z]?", s) for s in syms), True)
    check("mass per proton between 1 and 2.6", all(1.0 <= row[3] / row[0] <= 2.6 for row in _ELEMENTS), True)
    for sym, mass in [("H", 1.008), ("C", 12.011), ("N", 14.007), ("O", 15.999), ("Na", 22.990), ("Cl", 35.45), ("Fe", 55.845), ("Cu", 63.546), ("Ag", 107.87), ("Au", 196.97), ("Pb", 207.2), ("U", 238.03), ("Tc", 97)]:
        near(f"atomic_mass('{sym}')", f"atomic_mass('{sym}')", mass, 1e-12)
    near("atomic_mass by number", "atomic_mass(8)", 15.999, 1e-12)
    for sym, en in [("F", 3.98), ("O", 3.44), ("Cl", 3.16), ("C", 2.55), ("H", 2.20), ("Na", 0.93), ("Cs", 0.79), ("Au", 2.54)]:
        near(f"electronegativity('{sym}')", f"electronegativity('{sym}')", en, 1e-12)
    ens = [ev(f"electronegativity({z})") for z in range(3, 10)]
    check("electronegativity rises across period 2", ens == sorted(ens), True)
    hal = [ev(f"electronegativity('{s}')") for s in ("F", "Cl", "Br", "I")]
    check("electronegativity falls down the halogens", hal == sorted(hal, reverse=True), True)
    for z in (2, 10, 18, 61, 63, 70, 87, 86, 103, 118):
        text(f"no electronegativity for {z}", f"electronegativity({z})", "Math ERROR")
    # --- formulas against hand sums
    near("molar_mass H2O", "molar_mass('H2O')", 2 * 1.008 + 15.999, 1e-12)
    near("molar_mass CO2", "molar_mass('CO2')", 12.011 + 2 * 15.999, 1e-12)
    near("molar_mass NaCl", "molar_mass('NaCl')", 22.990 + 35.45, 1e-12)
    near("molar_mass glucose", "molar_mass('C6H12O6')", 6 * 12.011 + 12 * 1.008 + 6 * 15.999, 1e-12)
    near("molar_mass H2SO4", "molar_mass('H2SO4')", 2 * 1.008 + 32.06 + 4 * 15.999, 1e-12)
    near("molar_mass Ca(OH)2", "molar_mass('Ca(OH)2')", 40.078 + 2 * (15.999 + 1.008), 1e-12)
    near("molar_mass Al2(SO4)3", "molar_mass('Al2(SO4)3')", 2 * 26.982 + 3 * (32.06 + 4 * 15.999), 1e-12)
    near("molar_mass K4[Fe(CN)6]", "molar_mass('K4[Fe(CN)6]')", 4 * 39.098 + 55.845 + 6 * (12.011 + 14.007), 1e-12)
    near("molar_mass CuSO4.5H2O", "molar_mass('CuSO4.5H2O')", 63.546 + 32.06 + 4 * 15.999 + 5 * (2 * 1.008 + 15.999), 1e-12)
    near("molar_mass with middle dot", "molar_mass('CuSO4·5H2O')", ev("molar_mass('CuSO4.5H2O')"), 1e-12)
    near("molar_mass Ca3(PO4)2", "molar_mass('Ca3(PO4)2')", 3 * 40.078 + 2 * (30.974 + 4 * 15.999), 1e-12)
    near("molar_mass nested", "molar_mass('(NH4)2[Fe(SO4)2]')", 2 * (14.007 + 4 * 1.008) + 55.845 + 2 * (32.06 + 4 * 15.999), 1e-12)
    near("CO is not Co", "molar_mass('CO')", 12.011 + 15.999, 1e-12)
    near("Co is cobalt", "molar_mass('Co')", 58.933, 1e-12)
    ex("atom_count O in Al2(SO4)3", "atom_count('Al2(SO4)3', 'O')", 12)
    ex("atom_count S in Al2(SO4)3", "atom_count('Al2(SO4)3', 'S')", 3)
    ex("atom_count by number", "atom_count('H2O', 1)", 2)
    ex("atom_count absent element", "atom_count('H2O', 'Fe')", 0)
    ex("atom_count in hydrate", "atom_count('CuSO4.5H2O', 'O')", 9)
    ex("atom_count in K4[Fe(CN)6]", "atom_count('K4[Fe(CN)6]', 'N')", 6)
    ex("formula_atoms Ca(OH)2", "formula_atoms('Ca(OH)2')", 5)
    ex("formula_atoms hydrate", "formula_atoms('CuSO4.5H2O')", 21)
    ex("formula_atoms glucose", "formula_atoms('C6H12O6')", 24)
    near("mass_percent O in water", "mass_percent('H2O','O')", 15.999 / 18.015 * 100, 1e-6)
    near("mass percents sum to 100", "mass_percent('C6H12O6','C')+mass_percent('C6H12O6','H')+mass_percent('C6H12O6','O')", 100, 1e-6)
    near("mass_percent absent element", "mass_percent('NaCl','O')", 0, 1e-12)
    near("moles_from_mass with a number", "moles_from_mass(36, 18)", 2, 1e-12)
    near("moles_from_mass with a formula", "moles_from_mass(58.44, 'NaCl')", 58.44 / 58.44, 1e-9)
    near("mass_from_moles with a formula", "mass_from_moles(0.5, 'C6H12O6')", 0.5 * 180.156, 1e-12)
    near("mass and moles round trip", "moles_from_mass(mass_from_moles(3.7,'CO2'),'CO2')", 3.7, 1e-12)
    near("moles_from_molecules inverts molecules_from_moles", "moles_from_molecules(molecules_from_moles(2.5))", 2.5, 1e-12)
    near("molecules in a mole", "molecules_from_moles(1)", 6.02214076e23, 1e-12)
    near("percent_yield", "percent_yield(7.5,12.5)", 60, 1e-12)
    # --- solutions
    near("dilution conserves moles", "dilution_v2(3,20,0.5)*0.5", 3 * 20, 1e-12)
    near("dilution_c2 inverts dilution_v2", "dilution_c2(3,20,dilution_v2(3,20,0.5))", 0.5, 1e-12)
    near("molality hand", "molality(0.75,1.5)", 0.5, 1e-12)
    near("mole_fraction hand", "mole_fraction(3,12)", 0.25, 1e-12)
    near("percent_by_mass hand", "percent_by_mass(12,80)", 15, 1e-12)
    near("ppm hand", "ppm(0.0005,250)", 2, 1e-9)
    near("normality hand", "normality(0.2,3)", 0.6, 1e-12)
    # --- acids and bases against bisection of the defining equations
    def bisect8(f, lo, hi):
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(lo) * f(mid) <= 0:
                hi = mid
            else:
                lo = mid
        return (lo + hi) / 2
    for c in (1.0, 0.1, 0.01, 1e-3, 1e-6, 1e-8):
        h = bisect8(lambda h: h - 1e-14 / h - c, 1e-14, 10)       # charge balance [H+] = c + Kw/[H+]
        near(f"ph_strong_acid({c})", f"ph_strong_acid({c})", -math.log10(h), 1e-9)
        near(f"ph_strong_base({c}) mirrors the acid", f"ph_strong_base({c})", 14 - ev(f"ph_strong_acid({c})"), 1e-9)
    near("ph_strong_acid 0.01", "ph_strong_acid(0.01)", 2, 1e-9)
    near("very dilute acid stays just below 7", "ph_strong_acid(1e-8)", 6.97829431354289, 1e-9)
    for c, ka in [(0.1, 1e-5), (1.0, 1.8e-5), (0.001, 6.3e-8), (0.5, 0.01), (1e-4, 1e-3)]:
        x = bisect8(lambda x: x * x - ka * (c - x), 0, c)
        near(f"ph_weak_acid({c},{ka}) solves x^2/(c-x)=Ka", f"ph_weak_acid({c},{ka})", -math.log10(x), 1e-8)
        near(f"ph_weak_base({c},{ka}) is 14 - pH", f"ph_weak_base({c},{ka})", 14 + math.log10(x), 1e-8)
    near("ph_weak_acid approximation", "ph_weak_acid(0.1,1e-9)", -0.5 * math.log10(1e-9 * 0.1), 1e-4)
    near("buffer at equal concentrations is pKa", "buffer_ph(1.8e-5,0.2,0.2)", -math.log10(1.8e-5), 1e-12)
    near("buffer hand value", "buffer_ph(1e-5,0.1,1)", 6, 1e-12)
    near("pka_from_ka", "pka_from_ka(1e-5)", 5, 1e-12)
    near("ka_from_pka inverts", "ka_from_pka(pka_from_ka(3.2e-7))", 3.2e-7, 1e-9)
    # --- thermo, electro, kinetics
    R8, F8 = 8.314462618, 96485.33212
    near("nernst at Q=10", "nernst(1.1,1,10)", 1.1 - R8 * 298.15 / F8 * math.log(10), 1e-12)
    near("nernst with temperature", "nernst(0.8,2,0.01,350)", 0.8 - R8 * 350 / (2 * F8) * math.log(0.01), 1e-12)
    near("nernst slope is 59.16 mV per decade", "nernst(0,1,1)-nernst(0,1,10)", 0.05916, 1e-4)
    near("gibbs hand", "gibbs(-92000,298,-199)", -92000 + 298 * 199, 1e-12)
    near("gibbs_from_k hand", "gibbs_from_k(300,100)", -R8 * 300 * math.log(100), 1e-12)
    near("k_from_gibbs inverts gibbs_from_k", "k_from_gibbs(gibbs_from_k(310,42),310)", 42, 1e-9)
    near("cell_gibbs hand", "cell_gibbs(2,0.5)", -2 * F8 * 0.5, 1e-12)
    near("cell_gibbs and nernst agree (K from E0)", "k_from_gibbs(cell_gibbs(2,0.2),298.15)", math.exp(2 * F8 * 0.2 / (R8 * 298.15)), 1e-9)
    near("arrhenius hand", "arrhenius(1e13,80000,300)", 1e13 * math.exp(-80000 / (R8 * 300)), 1e-12)
    near("arrhenius_ea recovers Ea", "arrhenius_ea(arrhenius(5e10,65000,300),300,arrhenius(5e10,65000,340),340)", 65000, 1e-9)
    near("osmotic pressure hand", "osmotic_pressure(0.25,310)", 0.25 * R8 * 310, 1e-12)
    near("osmotic pressure with i", "osmotic_pressure(0.25,310,2)", 2 * 0.25 * R8 * 310, 1e-12)
    near("boiling_elevation hand", "boiling_elevation(0.512,1.5,2)", 1.536, 1e-12)
    near("freezing_depression hand", "freezing_depression(1.86,0.25)", 0.465, 1e-12)
    near("first order half-life leaves half", "first_order_conc(0.8,0.05,half_life_first_order(0.05))", 0.4, 1e-12)
    near("half_life_first_order hand", "half_life_first_order(0.1)", math.log(2) / 0.1, 1e-12)
    near("first order after 3 half-lives", "first_order_conc(1,0.2,3*half_life_first_order(0.2))", 1 / 8, 1e-12)
    near("second order half time is 1/(k c0)", "second_order_conc(0.5,0.2,1/(0.2*0.5))", 0.25, 1e-12)
    near("second order at t=0", "second_order_conc(0.5,0.2,0)", 0.5, 1e-12)
    near("graham H2 vs O2", "graham_ratio('H2','O2')", math.sqrt(31.998 / 2.016), 1e-12)
    near("graham with numbers", "graham_ratio(4,16)", 2, 1e-12)
    near("raoult hand", "raoult_pressure(0.8,23.8)", 0.8 * 23.8, 1e-12)
    near("isotope_avg_mass pure first", "isotope_avg_mass(10.013,11.009,100)", 10.013, 1e-12)
    near("isotope_avg_mass boron", "isotope_avg_mass(10.0129,11.0093,19.9)", 10.0129 * 0.199 + 11.0093 * 0.801, 1e-12)
    # --- bad input
    for e in ["atomic_mass(0)", "atomic_mass(119)", "atomic_mass(1.5)", "atomic_mass('Xx')", "atomic_mass('')", "atomic_mass('fe')", "atomic_mass(-1)",
              "electronegativity(0)", "element_symbol(200)", "element_name('Zz')", "element_period(0)", "element_group(0)", "element_group('La')",
              "atomic_number('Q')", "molar_mass('')", "molar_mass('H2O)')", "molar_mass('(H2O')", "molar_mass('[H2O)')", "molar_mass('Xx2')",
              "molar_mass('h2o')", "molar_mass('H2O!')", "molar_mass('2')", "molar_mass('H0')", "molar_mass('H2.')", "molar_mass(18)", "molar_mass('H99999999')",
              "molar_mass('()')", "atom_count('H2O','Xx')", "atom_count(5,'H')", "formula_atoms('')", "formula_atoms(3)", "mass_percent('H2O','Qq')",
              "moles_from_mass(-1,18)", "moles_from_mass(5,0)", "moles_from_mass(5,'Zz')", "moles_from_mass('a',18)", "mass_from_moles(-1,18)", "mass_from_moles(1,-5)",
              "molecules_from_moles(-1)", "moles_from_molecules(-1)", "percent_yield(5,0)", "percent_yield(-1,5)", "dilution_v2(1,1,0)", "dilution_v2(-1,1,1)",
              "dilution_c2(1,1,0)", "molality(1,0)", "molality(-1,1)", "mole_fraction(5,4)", "mole_fraction(1,0)", "percent_by_mass(6,5)", "percent_by_mass(1,0)",
              "ppm(2,1)", "ppm(1,0)", "normality(1,0)", "normality(-1,2)", "ph_strong_acid(0)", "ph_strong_acid(-1)", "ph_strong_base(0)", "ph_weak_acid(0,1e-5)",
              "ph_weak_acid(1,0)", "ph_weak_base(-1,1e-5)", "ph_weak_base(1,0)", "buffer_ph(0,1,1)", "buffer_ph(1e-5,0,1)", "buffer_ph(1e-5,1,0)", "pka_from_ka(0)",
              "pka_from_ka(-1)", "ka_from_pka(1e308)", "nernst(1,0,1)", "nernst(1,1,0)", "nernst(1,1,1,0)", "gibbs(1,-5,1)", "gibbs_from_k(0,1)", "gibbs_from_k(300,0)",
              "k_from_gibbs(1,0)", "cell_gibbs(0,1)", "arrhenius(-1,1,300)", "arrhenius(1,-1,300)", "arrhenius(1,1,0)", "arrhenius_ea(1,300,1,300)", "arrhenius_ea(0,300,1,350)",
              "arrhenius_ea(1,0,1,350)", "osmotic_pressure(-1,300)", "osmotic_pressure(1,0)", "osmotic_pressure(1,300,0)", "boiling_elevation(-1,1)", "boiling_elevation(1,-1)",
              "boiling_elevation(1,1,0)", "freezing_depression(-1,1)", "freezing_depression(1,1,-1)", "first_order_conc(-1,1,1)", "first_order_conc(1,-1,1)", "first_order_conc(1,1,-1)",
              "half_life_first_order(0)", "half_life_first_order(-1)", "second_order_conc(1,1,-1)", "second_order_conc(-1,1,1)", "graham_ratio(0,1)", "graham_ratio('Zz','H2')",
              "raoult_pressure(1.5,10)", "raoult_pressure(0.5,-1)", "isotope_avg_mass(10,11,101)", "isotope_avg_mass(0,11,50)", "isotope_avg_mass(10,11,-1)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
    return {"bisect8": bisect8}
