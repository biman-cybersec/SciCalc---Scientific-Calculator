"""Checks: constants.  Run alone with  python run_tests.py constants"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "constants"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..registry import REGISTRY

from .helpers import _err, _expr_error  # noqa: F401


def checks_constants_38(check, run, ev, near):
    """constants expansion"""
    # ================= constants expansion =================
    new_cats = ("Constants: Physics", "Constants: Chemistry", "Constants: Maths", "Constants: Astronomy", "Constants: Units & Everyday")
    new_consts = [k for k in REGISTRY.constants() if k.category in new_cats]
    check("new constants registered", len(new_consts) >= 170, True)
    for k in new_consts:                              # every name and alias evaluates to the stored value
        for nm in (k.name,) + tuple(k.aliases):
            got = run(nm).value
            check(f"constant {nm} evaluates", math.isclose(float(got), float(k.value), rel_tol=1e-14) and math.isfinite(float(got)), True)
        check(f"constant {k.name} has a description", len(k.desc) >= 3, True)
    near("constant inside an expression", "2*const_sqrt2", 2 * math.sqrt(2), 1e-14)
    near("constant names ignore case", "CONST_SQRT2", math.sqrt(2), 1e-14)
    # ---- physics: published CODATA 2018 values against the values the table derives from exact SI constants
    pub = {"const_me_mev": 0.51099895000, "const_mp_mev": 938.27208816, "const_mn_mev": 939.56542052, "const_amu_mev": 931.49410242,
           "const_hartree": 4.3597447222071e-18, "const_hartree_ev": 27.211386245988, "const_rydberg_ev": 13.605693122994,
           "const_hbar_ev": 6.582119569e-16, "const_planck_ev": 4.135667696e-15, "const_hc_evnm": 1239.841984, "const_kb_ev": 8.617333262e-5,
           "const_ub_ev": 5.7883818060e-5, "const_josephson": 483597.8484e9, "const_klitzing": 25812.80745, "const_rad1": 3.741771852e-16,
           "const_rad2": 1.438776877e-2, "const_wien_freq": 5.878925757e10, "const_rad_density": 7.5657332e-16,
           "const_molar_planck": 3.990312712e-10, "const_au_velocity": 2187691.26364, "const_inv_alpha": 137.035999084,
           "const_vm_stp_l": 22.41396954, "const_vm_bar25": 24.78957, "const_r_latm": 0.082057366080960, "const_r_cal": 1.98720425864083,
           "const_hartree_kjmol": 2625.4996394799, "const_kcalmol_ev": 0.043364104, "const_ev_kjmol": 96.48533212, "const_debye": 3.33564e-30,
           "const_r_air": 287.05502}
    for nm, want in pub.items():
        near(f"{nm} against the published value", nm, want, 2e-8)
    near("Planck constant from h/(2 pi) and hbar in eV", "const_hbar_ev*2*pi", ev("const_planck_ev"), 1e-12)
    near("Josephson times Klitzing is 2/e", "const_josephson*const_klitzing", 2 / 1.602176634e-19, 1e-12)
    near("c2 = h c / k", "const_rad2", 6.62607015e-34 * 299792458 / 1.380649e-23, 1e-12)
    near("c1 = 2 pi h c^2", "const_rad1", 2 * math.pi * 6.62607015e-34 * 299792458 ** 2, 1e-12)
    near("molar volume agrees with the old table value", "const_vm_stp_l/1000", ev("const_vm"), 2e-8)
    near("R in L atm and Pa m3 agree", "const_r_latm*101.325", ev("gas_R"), 1e-9)
    near("R in cal", "const_r_cal*4.184", ev("gas_R"), 1e-9)
    near("Hartree is twice the Rydberg energy", "const_hartree_ev", 2 * ev("const_rydberg_ev"), 1e-10)
    near("Bohr magneton in eV/T agrees with J/T", "const_ub_ev*1.602176634e-19", ev("bohr_m"), 1e-9)
    near("electron rest energy from m c^2", "const_me_mev", ev("m_e") * 299792458 ** 2 / 1.602176634e-19 / 1e6, 1e-12)
    near("proton / neutron mass ratio", "const_mn_mp", ev("m_n") / ev("m_p"), 2e-9)
    near("deuteron / electron mass ratio", "const_md_me", ev("const_md") / ev("m_e"), 2e-9)
    near("alpha particle is about 4 u", "const_malpha/amu", 4.001506179127, 2e-9)
    near("deuteron is about 2 u", "const_md/amu", 2.013553212745, 2e-9)
    near("classical electron radius = alpha^2 a0", "const_r_e", ev("fine_alpha") ** 2 * ev("bohr_r"), 2e-9)
    near("Thomson cross section = 8 pi r^2 / 3", "const_thomson", 8 * math.pi / 3 * ev("const_r_e") ** 2, 2e-9)
    near("proton Compton wavelength = h/(m c)", "const_compton_p", 6.62607015e-34 / (ev("m_p") * 299792458), 2e-9)
    near("neutron Compton wavelength = h/(m c)", "const_compton_n", 6.62607015e-34 / (ev("m_n") * 299792458), 2e-9)
    near("nuclear magneton = e hbar / 2 m_p", "const_mu_n", 1.602176634e-19 * 1.054571817e-34 / (2 * ev("m_p")), 2e-9)
    near("proton moment is 2.7928 nuclear magnetons", "const_mu_p/const_mu_n", 2.79284734463, 2e-9)
    near("electron moment is -1.0011596 Bohr magnetons", "const_mu_e/bohr_m", -1.00115965218128, 2e-9)
    near("gyromagnetic ratio = |moment|*2/hbar ", "const_gamma_e", 2 * abs(ev("const_mu_e")) / 1.054571817e-34, 5e-9)
    near("proton gyromagnetic ratio", "const_gamma_p", 2 * ev("const_mu_p") / 1.054571817e-34, 5e-9)
    near("sin^2 theta_W", "const_sin2w", 0.2229, 1e-12)
    near("atomic time = hbar / Hartree", "const_au_time", 1.054571817e-34 / ev("const_hartree"), 2e-9)
    near("absolute zero", "const_abs_zero+const_t_stp", 0, 1e-12)
    near("CMB temperature", "const_cmb", 2.7255, 1e-12)
    # ---- chemistry
    near("1 atm molar volume at 25 C", "const_vm_atm25", 24.4655, 5e-5)
    near("molar volumes scale with 1/p", "const_vm_atm25*101325/100000", ev("const_vm_bar25"), 1e-12)
    near("molar volumes scale with T", "const_vm_stp_l*298.15/273.15", ev("const_vm_atm25"), 1e-12)
    near("dry air density from the gas law", "101325/(const_r_air*const_t_isa)", ev("const_rho_air"), 5e-5)
    near("speed of sound in air", "sqrt(const_gas_gamma_air*const_r_air*const_t_isa)", ev("const_c_sound"), 5e-5)
    near("air molar mass in R", "gas_R/(const_m_air/1000)", ev("const_r_air"), 1e-9)
    near("Kw", "const_kw", 1e-14, 1e-12)
    near("kcal/mol in eV from the calorie", "4184/avogadro/e_charge", ev("const_kcalmol_ev"), 1e-12)
    near("eV per particle in kJ/mol", "e_charge*avogadro/1000", ev("const_ev_kjmol"), 1e-12)
    near("Hartree per mole in kJ", "const_hartree*avogadro/1000", ev("const_hartree_kjmol"), 1e-12)
    near("Debye from the speed of light", "const_debye*299792458", 1e-21, 1e-12)
    near("Angstrom", "const_angstrom", 1e-10, 1e-12)
    near("water heat capacity is close to the calorie definition", "const_cp_water/(const_cal*1000)", 1, 1e-3)
    near("heat to melt 1 kg of ice vs the heat to boil it", "const_lv_water/const_lf_water", 6.77, 2e-2)
    near("water density", "const_rho_water", 999.975, 1e-9)
    near("molar mass constant", "const_mu_molar*1000", 1, 1e-9)
    near("standard temperature", "const_t_std-const_t_stp", 25, 1e-12)
    near("curie", "const_curie", 3.7e10, 1e-12)
    # ---- maths: each value against an independent computation
    def agm(a, b):
        for _ in range(60):
            a, b = (a + b) / 2, math.sqrt(a * b)
        return a
    near("sqrt2", "const_sqrt2", 2 ** 0.5, 1e-13)
    near("sqrt3", "const_sqrt3", 3 ** 0.5, 1e-13)
    near("sqrt5 = 2 phi - 1", "const_sqrt5", 2 * ev("phi") - 1, 1e-13)
    near("cube root of 2 cubed", "const_cbrt2^3", 2, 1e-13)
    near("ln2", "const_ln2", math.log(2), 1e-13)
    near("ln10", "const_ln10", math.log(10), 1e-13)
    near("log10(e) is 1/ln10", "const_log10e*const_ln10", 1, 1e-13)
    near("ln phi", "const_ln_phi", math.log((1 + math.sqrt(5)) / 2), 1e-13)
    near("sqrt pi = Gamma(1/2)", "const_sqrt_pi", math.gamma(0.5), 1e-13)
    near("sqrt 2 pi", "const_sqrt_2pi", math.sqrt(2 * math.pi), 1e-13)
    near("normal peak is 1/sqrt(2 pi)", "const_inv_sqrt_2pi*const_sqrt_2pi", 1, 1e-13)
    near("pi squared", "const_pi_sq", math.pi ** 2, 1e-13)
    near("e^e", "const_e_e", math.e ** math.e, 1e-13)
    near("e^pi", "const_gelfond", math.exp(math.pi), 1e-13)
    near("2^sqrt2", "const_gelfond_schneider", 2 ** math.sqrt(2), 1e-13)
    near("i^i is real", "const_i_to_i", (1j ** 1j).real, 1e-13)
    near("i^i = e^(-pi/2)", "const_i_to_i", math.exp(-math.pi / 2), 1e-13)
    near("Ramanujan's constant", "const_ramanujan", math.exp(math.pi * math.sqrt(163)), 1e-12)
    check("Ramanujan's constant is almost an integer", abs(ev("const_ramanujan") - (640320 ** 3 + 744)) < 1e3, True)
    near("Gauss's constant", "const_gauss_c", 1 / agm(1, math.sqrt(2)), 1e-13)
    near("lemniscate constant", "const_lemniscate", math.pi / agm(1, math.sqrt(2)), 1e-13)
    near("Levy's constant", "const_levy", math.exp(math.pi ** 2 / (12 * math.log(2))), 1e-13)
    z = 1.0
    for _ in range(500):
        z = math.cos(z)
    near("Dottie number", "const_dottie", z, 1e-13)
    near("cos(Dottie) = Dottie", "cos(const_dottie*180/pi)-const_dottie", 0, 1e-13)
    # Euler-Gompertz: e * E1(1), with E1(1) = -gamma + sum_{k>=1} (-1)^(k+1) / (k k!)
    e1 = -0.5772156649015329 + sum((-1) ** (k + 1) / (k * math.factorial(k)) for k in range(1, 40))
    near("Euler-Gompertz constant", "const_gompertz", math.e * e1, 1e-13)
    near("universal parabolic constant", "const_parabolic", math.sqrt(2) + math.log(1 + math.sqrt(2)), 1e-13)
    near("Erdos-Borwein", "const_erdos_borwein", sum(1 / (2 ** n - 1) for n in range(1, 80)), 1e-13)
    fibs = [1, 1]
    while len(fibs) < 120:
        fibs.append(fibs[-1] + fibs[-2])
    near("reciprocal Fibonacci", "const_recip_fib", sum(1 / f for f in fibs), 1e-13)
    tm = sum((bin(n).count("1") % 2) / 2 ** (n + 1) for n in range(60))
    near("Thue-Morse constant", "const_thue_morse", tm, 1e-13)
    near("Champernowne", "const_champernowne", float("0." + "".join(str(n) for n in range(1, 30))), 1e-13)
    s_, cah = 2, 0.0                                   # Sylvester sequence 2, 3, 7, 43, ...
    for k in range(8):
        cah += (-1) ** k / (s_ - 1)
        s_ = s_ * s_ - s_ + 1
    near("Cahen's constant", "const_cahen", cah, 1e-13)
    import decimal as _dec
    _dec.getcontext().prec = 80
    mills_long = _dec.Decimal("1.306377883863080690468614492602605712916784585156713644368")    # enough digits for A^81
    check("Mills constant matches its long form", abs(float(mills_long) - ev("const_mills")) < 1e-13, True)
    for nth, prime in [(1, 2), (2, 11), (3, 1361), (4, 2521008887)]:
        check(f"Mills prime {nth}", int(mills_long ** (3 ** nth)) == prime and all(prime % q for q in range(2, int(prime ** 0.5) + 1)), True)
    near("Lieb's square ice constant", "const_lieb", 8 * math.sqrt(3) / 9, 1e-13)
    near("golden angle", "const_golden_angle", math.pi * (3 - math.sqrt(5)), 1e-13)
    near("degrees per radian", "const_rad_deg", 180 / math.pi, 1e-13)
    near("radians per degree", "const_deg_rad*const_rad_deg", 1, 1e-13)
    near("arc-second", "const_arcsec", math.pi / 648000, 1e-13)
    # ---- astronomy
    near("megaparsec", "const_mpc", 1e6 * ev("parsec"), 1e-12)
    near("Moon distance from the existing Moon data is 60 Earth radii", "const_moon_dist/const_rearth", 60.3, 5e-3)
    near("polar radius from flattening", "const_earth_a*(1-const_earth_flat)", ev("const_earth_b"), 1e-9)
    near("WGS-84 flattening", "1/const_earth_flat", 298.257223563, 1e-12)
    near("sidereal day from the rotation rate", "2*pi/const_earth_omega", ev("const_day_sidereal"), 1e-6)
    near("Julian year", "const_year_julian", 365.25 * 86400, 1e-14)
    near("tropical year is 365.2422 days", "const_year_tropical/86400", 365.2422, 1e-6)
    near("sidereal year is 365.2564 days", "const_year_sidereal/86400", 365.25636, 1e-6)
    near("synodic month in days", "const_month_synodic/86400", 29.530588853, 1e-12)
    near("sidereal day is shorter than a solar day by a year ratio", "const_day_sidereal*(1+1/365.2422)", 86400, 1e-4)
    for nm, g in [("mercury", 3.70), ("venus", 8.87), ("mars", 3.71), ("saturn", 11.19), ("uranus", 8.87), ("neptune", 11.15), ("pluto", 0.62)]:
        near(f"surface gravity of {nm}", f"G_grav*{nm}_mass/{nm}_radius^2", g, 0.02)
    near("Sun's luminosity from radius and temperature", "4*pi*solar_radius^2*stefan_sigma*solar_temp^4", ev("solar_luminosity"), 0.01)
    near("jansky", "jansky", 1e-26, 1e-12)
    near("Chandrasekhar mass", "chandrasekhar/solar_mass", 1.4, 1e-3)
    near("light-second", "light_second", ev("c_light"), 1e-15)
    # ---- units: exact relations between the exact definitions
    near("foot = 12 inches", "inch_m*12", ev("foot_m"), 1e-14)
    near("yard = 3 feet", "foot_m*3", ev("yard_m"), 1e-14)
    near("mile = 1760 yards", "yard_m*1760", ev("mile_m"), 1e-14)
    near("furlong = 220 yards", "yard_m*220", ev("furlong_m"), 1e-14)
    near("fathom = 2 yards", "yard_m*2", ev("fathom_m"), 1e-14)
    near("acre = 43560 square feet", "foot_m^2*43560", ev("acre_m2"), 1e-12)
    near("ounce = pound / 16", "pound_kg/16", ev("ounce_kg"), 1e-12)
    near("stone = 14 pounds", "pound_kg*14", ev("stone_kg"), 1e-12)
    near("short ton = 2000 pounds", "pound_kg*2000", ev("short_ton_kg"), 1e-12)
    near("long ton = 2240 pounds", "pound_kg*2240", ev("long_ton_kg"), 1e-12)
    near("grain = pound / 7000", "pound_kg/7000", ev("grain_kg"), 1e-7)
    near("gallon = 231 cubic inches", "inch_m^3*231", ev("us_gallon"), 1e-9)
    near("cup = gallon / 16", "us_gallon/16", ev("us_cup"), 1e-9)
    near("fluid ounce = gallon / 128", "us_gallon/128", ev("us_fluid_ounce"), 1e-9)
    near("tablespoon = fluid ounce / 2", "us_fluid_ounce/2", ev("us_tablespoon"), 1e-9)
    near("teaspoon = tablespoon / 3", "us_tablespoon/3", ev("us_teaspoon"), 1e-9)
    near("imperial gallon is 4.54609 litres", "uk_gallon/litre_m3", 4.54609, 1e-12)
    near("pound-force = pound x g", "pound_kg*g_accel", ev("pound_force"), 1e-9)
    near("psi = lbf per square inch", "pound_force/inch_m^2", ev("psi_pa"), 1e-9)
    near("horsepower = 550 ft lbf/s", "550*foot_m*pound_force", ev("horsepower"), 1e-9)
    near("metric horsepower = 75 kgf m/s", "75*g_accel", ev("horsepower_metric"), 1e-12)
    near("torr", "atm/760", ev("torr_pa"), 1e-12)
    near("mmHg is almost one torr", "mmhg_pa/torr_pa", 1, 1e-6)
    near("bar", "bar_pa", 1e5, 1e-12)
    near("knot", "nautical_mile/3600", ev("knot_ms"), 1e-12)
    near("mph", "mile_m/3600", ev("mph_ms"), 1e-12)
    near("kilowatt-hour", "1000*3600", ev("kilowatt_hour"), 1e-12)
    near("ton of TNT", "const_tnt", 4.184e9, 1e-12)
    near("two calories", "calorie_it/calorie_th", 4.1868 / 4.184, 1e-9)
    near("BTU about 252 calories", "btu_it/calorie_it", 252, 2e-3)
    near("erg = dyne x centimetre", "dyne*0.01", ev("erg"), 1e-12)
    near("gauss", "gauss_t", 1e-4, 1e-12)
    near("barn", "barn_m2", 1e-28, 1e-12)
    near("day", "day_s", 86400, 1e-14)
    near("carat", "carat_kg", 2e-4, 1e-14)
    near("hectare", "hectare_m2", 100 * 100, 1e-14)
    near("roentgen", "roentgen", 2.58e-4, 1e-12)
    near("air density at ISA sea level", "air_density", 1.225, 1e-12)
    # no value is NaN, infinite or zero, and the registry has no duplicated names
    check("all constants finite", all(math.isfinite(float(k.value)) and float(k.value) != 0 for k in REGISTRY.constants()), True)
    names = [n for k in REGISTRY.constants() for n in (k.name,) + tuple(k.aliases)]
    check("constant names are unique", len(names) == len({n.lower() for n in names}), True)
    check("constants do not shadow function names", all(REGISTRY.function(n) is None for n in names), True)
