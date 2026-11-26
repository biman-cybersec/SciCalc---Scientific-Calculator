"""Constants expansion (266 total) and sym_form

Module 44 of 47.  Taken from lines 14402-14646 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "constants_expansion"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import ArgumentError, MathError
from .registry import REGISTRY, register, register_constant
from .arithmetic import Lst, Mat
from .engine import sym_text

#  CONSTANTS EXPANSION  (CODATA 2018 values, to match the original table)
#  Sub-categories: Physics, Maths, Chemistry, Astronomy, Units & Everyday.
#  Where a constant follows from exact SI constants (h, c, e, k, N_A) it is computed from
#  them, so it cannot disagree with the table.  Measured values carry their CODATA 2018
#  digits.  Planet data are IAU/NASA mean values.  Everyday constants such as the specific
#  heat of water are textbook values and say so in their description.
# ======================================================================================
_H, _C, _QE, _KB, _NAV = 6.62607015e-34, 299792458.0, 1.602176634e-19, 1.380649e-23, 6.02214076e23
_RGAS = _KB * _NAV
_HBAR = _H / (2 * math.pi)
_ALPHA = 7.2973525693e-3
_RINF = 10973731.568160
_ME, _MP, _MN, _AMU = 9.1093837015e-31, 1.67262192369e-27, 1.67492749804e-27, 1.66053906660e-27
_EH = 2 * _RINF * _H * _C                                # Hartree energy


def _kc(category, rows):
    for name, value, desc, *al in rows:
        register_constant(name, value, desc, category=category, aliases=tuple(al[0]) if al else ())


_kc("Constants: Physics", [
    ("const_mmu", 1.883531627e-28, "Muon mass (kg)", ("m_muon", "m_mu")),
    ("const_mtau", 3.16754e-27, "Tau mass (kg)", ("m_tau",)),
    ("const_md", 3.3435837724e-27, "Deuteron mass (kg)", ("m_deuteron",)),
    ("const_mtriton", 5.0073567446e-27, "Triton mass (kg)", ("m_triton",)),
    ("const_mhelion", 5.0064127796e-27, "Helion (helium-3 nucleus) mass (kg)", ("m_helion",)),
    ("const_malpha", 6.6446573357e-27, "Alpha particle mass (kg)", ("m_alpha",)),
    ("const_me_mev", _ME * _C ** 2 / _QE / 1e6, "Electron rest energy (MeV)", ("electron_mev",)),
    ("const_mp_mev", _MP * _C ** 2 / _QE / 1e6, "Proton rest energy (MeV)", ("proton_mev",)),
    ("const_mn_mev", _MN * _C ** 2 / _QE / 1e6, "Neutron rest energy (MeV)", ("neutron_mev",)),
    ("const_amu_mev", _AMU * _C ** 2 / _QE / 1e6, "Atomic mass unit energy equivalent (MeV)", ("amu_mev",)),
    ("const_mn_mp", 1.00137841931, "Neutron-to-proton mass ratio", ("neutron_proton_ratio",)),
    ("const_md_me", 3670.48296788, "Deuteron-to-electron mass ratio", ("deuteron_electron_ratio",)),
    ("const_r_e", 2.8179403262e-15, "Classical electron radius (m)", ("classical_electron_radius",)),
    ("const_thomson", 6.6524587321e-29, "Thomson cross section (m^2)", ("thomson_xs",)),
    ("const_compton_p", 1.32140985539e-15, "Compton wavelength of the proton (m)", ("compton_proton",)),
    ("const_compton_n", 1.31959090581e-15, "Compton wavelength of the neutron (m)", ("compton_neutron",)),
    ("const_hartree", _EH, "Hartree energy (J)", ("hartree_j",)),
    ("const_hartree_ev", _EH / _QE, "Hartree energy (eV)", ("hartree_ev",)),
    ("const_rydberg_ev", _RINF * _H * _C / _QE, "Rydberg energy (eV)", ("rydberg_ev",)),
    ("const_hbar_ev", _HBAR / _QE, "Reduced Planck constant (eV s)", ("hbar_ev",)),
    ("const_planck_ev", _H / _QE, "Planck constant (eV s)", ("h_ev",)),
    ("const_hc_evnm", _H * _C / _QE * 1e9, "h c (eV nm): photon energy in eV is this / wavelength in nm", ("hc_ev_nm",)),
    ("const_kb_ev", _KB / _QE, "Boltzmann constant (eV/K)", ("kb_ev",)),
    ("const_ub_ev", _QE * _HBAR / (2 * _ME) / _QE, "Bohr magneton (eV/T)", ("bohr_m_ev",)),
    ("const_mu_n", 5.0507837461e-27, "Nuclear magneton (J/T)", ("nuclear_magneton",)),
    ("const_mu_e", -9.2847647043e-24, "Electron magnetic moment (J/T)", ("electron_moment",)),
    ("const_mu_p", 1.41060679736e-26, "Proton magnetic moment (J/T)", ("proton_moment",)),
    ("const_g_e", -2.00231930436256, "Electron g-factor", ("electron_g",)),
    ("const_gamma_e", 1.76085963023e11, "Electron gyromagnetic ratio (1/(s T))", ("gyro_electron",)),
    ("const_gamma_p", 2.6752218744e8, "Proton gyromagnetic ratio (1/(s T))", ("gyro_proton",)),
    ("const_josephson", 2 * _QE / _H, "Josephson constant 2e/h (Hz/V)", ("josephson",)),
    ("const_klitzing", _H / _QE ** 2, "von Klitzing constant h/e^2 (ohm)", ("klitzing",)),
    ("const_rad1", 2 * math.pi * _H * _C ** 2, "First radiation constant 2 pi h c^2 (W m^2)", ("radiation_c1",)),
    ("const_rad2", _H * _C / _KB, "Second radiation constant h c / k (m K)", ("radiation_c2",)),
    ("const_wien_freq", 2.821439372122078893 * _KB / _H, "Wien frequency displacement constant (Hz/K)", ("wien_hz",)),
    ("const_rad_density", 4 * 5.670374419e-8 / _C, "Radiation density constant a = 4 sigma / c (J m^-3 K^-4)", ("radiation_a",)),
    ("const_molar_planck", _NAV * _H, "Molar Planck constant (J s/mol)", ("molar_h",)),
    ("const_fermi", 1.1663787e-5, "Fermi coupling constant G_F/(hbar c)^3 (1/GeV^2)", ("fermi_coupling",)),
    ("const_sin2w", 0.22290, "Weak mixing angle sin^2(theta_W)", ("weak_mixing",)),
    ("const_au_time", 2.4188843265857e-17, "Atomic unit of time (s)", ("atomic_time",)),
    ("const_au_velocity", _ALPHA * _C, "Atomic unit of velocity alpha c (m/s)", ("atomic_velocity",)),
    ("const_p_std", 1e5, "Standard-state pressure, 1 bar (Pa)", ("p_standard",)),
    ("const_abs_zero", -273.15, "Absolute zero (degrees Celsius)", ("absolute_zero",)),
    ("const_inv_alpha", 1 / _ALPHA, "Inverse fine-structure constant", ("alpha_inv",)),
    ("const_cmb", 2.7255, "Cosmic microwave background temperature (K)", ("cmb_temp",)),
    ("const_hubble", 67.4, "Hubble constant, Planck 2018 (km/s/Mpc)", ("h0_hubble",)),
])

_kc("Constants: Chemistry", [
    ("const_vm_atm25", _RGAS * 298.15 / 101325 * 1000, "Molar volume of an ideal gas at 25 C and 1 atm (L/mol)", ("molar_volume_25c",)),
    ("const_vm_bar25", _RGAS * 298.15 / 1e5 * 1000, "Molar volume of an ideal gas at 25 C and 1 bar (L/mol)", ("molar_volume_bar",)),
    ("const_vm_stp_l", _RGAS * 273.15 / 101325 * 1000, "Molar volume of an ideal gas at 0 C and 1 atm (L/mol)", ("molar_volume_stp",)),
    ("const_r_latm", _RGAS / 101.325, "Gas constant (L atm/(mol K))", ("r_l_atm",)),
    ("const_r_barl", _RGAS / 100, "Gas constant (L bar/(mol K))", ("r_l_bar",)),
    ("const_r_cal", _RGAS / 4.184, "Gas constant (cal/(mol K))", ("r_cal",)),
    ("const_r_air", _RGAS / 0.0289647, "Specific gas constant of dry air (J/(kg K))", ("r_specific_air",)),
    ("const_m_air", 28.9647, "Molar mass of dry air (g/mol)", ("air_molar_mass",)),
    ("const_mu_molar", 0.99999999965e-3, "Molar mass constant (kg/mol)", ("molar_mass_const",)),
    ("const_kw", 1.0e-14, "Ion product of water at 25 C", ("water_ion_product",)),
    ("const_hartree_kjmol", _EH * _NAV / 1000, "Hartree energy (kJ/mol)", ("hartree_kjmol",)),
    ("const_kcalmol_ev", 4184 / _NAV / _QE, "One kcal/mol in electron volts", ("kcalmol_ev",)),
    ("const_ev_kjmol", _QE * _NAV / 1000, "One electron volt per particle (kJ/mol)", ("ev_kjmol",)),
    ("const_debye", 1e-21 / _C, "Debye unit of dipole moment (C m)", ("debye",)),
    ("const_angstrom", 1e-10, "Angstrom (m)", ("angstrom",)),
    ("const_cp_water", 4186.0, "Specific heat of liquid water, textbook value (J/(kg K))", ("water_heat_capacity",)),
    ("const_lf_water", 334000.0, "Latent heat of fusion of ice, textbook value (J/kg)", ("water_fusion",)),
    ("const_lv_water", 2.26e6, "Latent heat of vaporisation of water at 100 C, textbook value (J/kg)", ("water_vaporisation",)),
    ("const_rho_water", 999.975, "Maximum density of water at 3.98 C (kg/m^3)", ("water_density",)),
    ("const_t_std", 298.15, "Standard temperature, 25 C (K)", ("t_standard",)),
    ("const_t_stp", 273.15, "Freezing point of water (K)", ("t_stp",)),
    ("const_curie", 3.7e10, "Curie (decays per second)", ("curie",)),
    ("const_gas_gamma_air", 1.4, "Heat-capacity ratio of dry air", ("gamma_air",)),
])

_kc("Constants: Maths", [
    ("const_sqrt2", 1.4142135623730951, "Square root of 2 (Pythagoras' constant)", ("sqrt_two",)),
    ("const_sqrt3", 1.7320508075688772, "Square root of 3 (Theodorus' constant)", ("sqrt_three",)),
    ("const_sqrt5", 2.23606797749979, "Square root of 5", ("sqrt_five",)),
    ("const_cbrt2", 1.2599210498948732, "Cube root of 2 (the Delian constant)", ("delian",)),
    ("const_ln2", 0.6931471805599453, "Natural logarithm of 2", ("ln_two",)),
    ("const_ln10", 2.302585092994046, "Natural logarithm of 10", ("ln_ten",)),
    ("const_log10e", 0.4342944819032518, "Base-10 logarithm of e", ("log10_e",)),
    ("const_ln_phi", 0.48121182505960347, "Natural logarithm of the golden ratio", ("ln_golden",)),
    ("const_sqrt_pi", 1.7724538509055159, "Square root of pi (Gamma(1/2))", ("sqrt_pi",)),
    ("const_sqrt_2pi", 2.5066282746310002, "Square root of 2 pi (Stirling / normal-distribution constant)", ("sqrt_2pi",)),
    ("const_inv_sqrt_2pi", 0.3989422804014327, "1 / sqrt(2 pi) (peak of the standard normal density)", ("normal_peak",)),
    ("const_pi_sq", 9.869604401089358, "Pi squared", ("pi_squared",)),
    ("const_e_e", 15.154262241479262, "e to the power e", ("e_pow_e",)),
    ("const_gelfond", 23.140692632779267, "Gelfond's constant e^pi", ("e_pow_pi",)),
    ("const_gelfond_schneider", 2.665144142690225, "Gelfond-Schneider constant 2^sqrt(2)", ("two_pow_sqrt2",)),
    ("const_i_to_i", 0.20787957635076193, "i^i = e^(-pi/2)", ("i_pow_i",)),
    ("const_ramanujan", 2.6253741264076874e17, "Ramanujan's constant e^(pi sqrt(163)), almost an integer", ("ramanujan_c",)),
    ("const_gauss_c", 0.8346268416740731, "Gauss's constant 1/agm(1, sqrt 2)", ("gauss_const",)),
    ("const_lemniscate", 2.622057554292119, "Lemniscate constant (arc length of the lemniscate is 2 times this)", ("lemniscate",)),
    ("const_levy", 3.2758229187218111, "Levy's constant e^(pi^2/(12 ln 2))", ("levy_const",)),
    ("const_dottie", 0.7390851332151607, "Dottie number, the real fixed point of cos x", ("dottie",)),
    ("const_gompertz", 0.5963473623231940, "Euler-Gompertz constant, integral of e^-x/(1+x) from 0 to infinity", ("gompertz",)),
    ("const_parabolic", 2.29558714939263807, "Universal parabolic constant sqrt 2 + ln(1 + sqrt 2)", ("parabolic",)),
    ("const_erdos_borwein", 1.6066951524152917, "Erdos-Borwein constant, sum of 1/(2^n - 1)", ("erdos_borwein",)),
    ("const_recip_fib", 3.3598856662431775, "Reciprocal Fibonacci constant, sum of 1/F(n)", ("reciprocal_fibonacci",)),
    ("const_thue_morse", 0.4124540336401076, "Prouhet-Thue-Morse constant", ("thue_morse",)),
    ("const_champernowne", 0.12345678910111213, "Champernowne constant 0.123456789101112...", ("champernowne",)),
    ("const_cahen", 0.6434105462883380, "Cahen's constant", ("cahen",)),
    ("const_mills", 1.3063778838630806, "Mills' constant: floor(A^(3^n)) is prime for every n", ("mills",)),
    ("const_lieb", 1.5396007178390020, "Lieb's square ice constant 8 sqrt(3) / 9", ("lieb_ice",)),
    ("const_golden_angle", 2.399963229728653, "Golden angle (radians), 137.5077...", ("golden_angle",)),
    ("const_rad_deg", 57.29577951308232, "Degrees in one radian", ("deg_per_rad",)),
    ("const_deg_rad", 0.017453292519943295, "Radians in one degree", ("rad_per_deg",)),
    ("const_arcsec", 4.84813681109536e-6, "Radians in one arc-second", ("arcsec_rad",)),
])

_kc("Constants: Astronomy", [
    ("const_mmercury", 3.3011e23, "Mass of Mercury (kg)", ("mercury_mass",)),
    ("const_mvenus", 4.8675e24, "Mass of Venus (kg)", ("venus_mass",)),
    ("const_mmars", 6.4171e23, "Mass of Mars (kg)", ("mars_mass",)),
    ("const_msaturn", 5.6834e26, "Mass of Saturn (kg)", ("saturn_mass",)),
    ("const_muranus", 8.6810e25, "Mass of Uranus (kg)", ("uranus_mass",)),
    ("const_mneptune", 1.02413e26, "Mass of Neptune (kg)", ("neptune_mass",)),
    ("const_mpluto", 1.303e22, "Mass of Pluto (kg)", ("pluto_mass",)),
    ("const_rmercury", 2.4397e6, "Mean radius of Mercury (m)", ("mercury_radius",)),
    ("const_rvenus", 6.0518e6, "Mean radius of Venus (m)", ("venus_radius",)),
    ("const_rmars", 3.3895e6, "Mean radius of Mars (m)", ("mars_radius",)),
    ("const_rsaturn", 5.8232e7, "Mean radius of Saturn (m)", ("saturn_radius",)),
    ("const_ruranus", 2.5362e7, "Mean radius of Uranus (m)", ("uranus_radius",)),
    ("const_rneptune", 2.4622e7, "Mean radius of Neptune (m)", ("neptune_radius",)),
    ("const_rpluto", 1.1883e6, "Mean radius of Pluto (m)", ("pluto_radius",)),
    ("const_rsun", 6.957e8, "Nominal solar radius, IAU (m)", ("solar_radius", "r_sun")),
    ("const_tsun", 5772.0, "Nominal solar effective temperature, IAU (K)", ("solar_temp",)),
    ("const_mpc", 3.0856775814913673e22, "Megaparsec (m)", ("megaparsec",)),
    ("const_moon_dist", 3.84399e8, "Mean Earth-Moon distance (m)", ("moon_distance",)),
    ("const_earth_a", 6378137.0, "Equatorial radius of Earth, WGS-84 (m)", ("earth_equatorial_radius",)),
    ("const_earth_b", 6356752.314245, "Polar radius of Earth, WGS-84 (m)", ("earth_polar_radius",)),
    ("const_earth_flat", 1 / 298.257223563, "Flattening of Earth, WGS-84", ("earth_flattening",)),
    ("const_earth_omega", 7.2921150e-5, "Earth's rotation rate (rad/s)", ("earth_rotation",)),
    ("const_day_sidereal", 86164.0905, "Sidereal day (s)", ("sidereal_day",)),
    ("const_year_julian", 31557600.0, "Julian year, 365.25 days (s)", ("julian_year",)),
    ("const_year_tropical", 31556925.2, "Tropical year (s)", ("tropical_year",)),
    ("const_year_sidereal", 31558149.8, "Sidereal year (s)", ("sidereal_year",)),
    ("const_month_synodic", 29.530588853 * 86400, "Synodic month (s)", ("synodic_month",)),
    ("const_jansky", 1e-26, "Jansky (W m^-2 Hz^-1)", ("jansky",)),
    ("const_chandrasekhar", 1.4 * 1.98847e30, "Chandrasekhar limit, 1.4 solar masses (kg)", ("chandrasekhar",)),
    ("const_light_second", 299792458.0, "Light-second (m)", ("light_second",)),
])

_kc("Constants: Units & Everyday", [
    ("const_inch", 0.0254, "Inch (m, exact)", ("inch_m",)),
    ("const_foot", 0.3048, "Foot (m, exact)", ("foot_m",)),
    ("const_yard", 0.9144, "Yard (m, exact)", ("yard_m",)),
    ("const_mile", 1609.344, "Statute mile (m, exact)", ("mile_m",)),
    ("const_nmi", 1852.0, "Nautical mile (m, exact)", ("nautical_mile",)),
    ("const_furlong", 201.168, "Furlong (m, exact)", ("furlong_m",)),
    ("const_fathom", 1.8288, "Fathom (m, exact)", ("fathom_m",)),
    ("const_acre", 4046.8564224, "Acre (m^2, exact)", ("acre_m2",)),
    ("const_hectare", 1e4, "Hectare (m^2)", ("hectare_m2",)),
    ("const_lb", 0.45359237, "Avoirdupois pound (kg, exact)", ("pound_kg",)),
    ("const_oz", 0.028349523125, "Avoirdupois ounce (kg, exact)", ("ounce_kg",)),
    ("const_stone", 6.35029318, "Stone (kg, exact)", ("stone_kg",)),
    ("const_ton_short", 907.18474, "Short ton (kg, exact)", ("short_ton_kg",)),
    ("const_ton_long", 1016.0469088, "Long ton (kg, exact)", ("long_ton_kg",)),
    ("const_grain", 6.479891e-5, "Grain (kg, exact)", ("grain_kg",)),
    ("const_carat", 2e-4, "Metric carat (kg)", ("carat_kg",)),
    ("const_gallon_us", 3.785411784e-3, "US liquid gallon (m^3, exact)", ("us_gallon",)),
    ("const_gallon_uk", 4.54609e-3, "Imperial gallon (m^3, exact)", ("uk_gallon",)),
    ("const_floz_us", 2.95735295625e-5, "US fluid ounce (m^3, exact)", ("us_fluid_ounce",)),
    ("const_cup_us", 2.365882365e-4, "US cup (m^3, exact)", ("us_cup",)),
    ("const_tbsp_us", 1.478676478125e-5, "US tablespoon (m^3, exact)", ("us_tablespoon",)),
    ("const_tsp_us", 4.92892159375e-6, "US teaspoon (m^3, exact)", ("us_teaspoon",)),
    ("const_litre", 1e-3, "Litre (m^3)", ("litre_m3",)),
    ("const_lbf", 4.4482216152605, "Pound-force (N, exact)", ("pound_force",)),
    ("const_dyne", 1e-5, "Dyne (N)", ("dyne",)),
    ("const_erg", 1e-7, "Erg (J)", ("erg",)),
    ("const_cal", 4.184, "Thermochemical calorie (J, exact)", ("calorie_th",)),
    ("const_cal_it", 4.1868, "International Table calorie (J, exact)", ("calorie_it",)),
    ("const_btu", 1055.05585262, "British thermal unit, IT (J)", ("btu_it",)),
    ("const_kwh", 3.6e6, "Kilowatt-hour (J, exact)", ("kilowatt_hour",)),
    ("const_tnt", 4.184e9, "Ton of TNT (J, exact)", ("ton_tnt",)),
    ("const_hp", 745.6998715822702, "Mechanical horsepower, 550 ft lbf/s (W)", ("horsepower",)),
    ("const_hp_metric", 735.49875, "Metric horsepower (W, exact)", ("horsepower_metric",)),
    ("const_bar", 1e5, "Bar (Pa)", ("bar_pa",)),
    ("const_torr", 101325 / 760, "Torr (Pa)", ("torr_pa",)),
    ("const_psi", 6894.757293168361, "Pound per square inch (Pa)", ("psi_pa",)),
    ("const_mmhg", 133.322387415, "Millimetre of mercury, conventional (Pa)", ("mmhg_pa",)),
    ("const_knot", 1852 / 3600, "Knot (m/s)", ("knot_ms",)),
    ("const_mph", 0.44704, "Mile per hour (m/s, exact)", ("mph_ms",)),
    ("const_gauss", 1e-4, "Gauss (T)", ("gauss_t",)),
    ("const_barn", 1e-28, "Barn (m^2)", ("barn_m2",)),
    ("const_roentgen", 2.58e-4, "Roentgen (C/kg)", ("roentgen",)),
    ("const_day", 86400.0, "Day (s)", ("day_s",)),
    ("const_rho_air", 1.225, "Density of air, ISA sea level (kg/m^3)", ("air_density",)),
    ("const_c_sound", 340.294, "Speed of sound in air, ISA sea level 15 C (m/s)", ("speed_of_sound",)),
    ("const_t_isa", 288.15, "ISA sea-level temperature (K)", ("isa_temp",)),
])


# ---- file the original constants into the same sub-categories
_MATH_OLD = {"pi", "e", "tau", "phi", "GOLDEN_RATIO", "EULER_MASCHERONI", "const_apery", "const_khinchin", "const_omega", "const_glaisher",
             "const_feigenbaum_delta", "const_feigenbaum_alpha", "const_catalan", "const_mm", "const_twin_prime", "const_silver_ratio",
             "const_plastic", "const_brun", "const_golomb", "const_fransen", "const_supergolden", "const_landau_ramanujan"}
_ASTRO_OLD = {"const_au", "const_ly", "const_pc", "const_msun", "const_mearth", "const_rearth", "const_lsun", "const_gme", "const_gms",
              "const_solar_irradiance", "const_mmass", "const_mradius", "const_jmass", "const_jradius"}
_CHEM_OLD = {"const_NA", "const_R", "const_F", "const_atm", "const_tpwater", "const_vm", "const_loschmidt", "AVOGADRO_CONST", "GAS_CONSTANT",
             "FARADAY_CONST"}
for _k in REGISTRY.constants():
    if _k.category == "Constants":
        _cat = ("Constants: Maths" if _k.name in _MATH_OLD else "Constants: Astronomy" if _k.name in _ASTRO_OLD
                else "Constants: Chemistry" if _k.name in _CHEM_OLD else "Constants: Physics")
        object.__setattr__(_k, "category", _cat)


@register("sym_form", "Display & Formatting", "Exact form of a number when it is simple (p/q, a fraction of pi, or a multiple of a square root), as text", 1,
          exact=True, example="sym_form(sqrt(12)) => 2√3")
def sym_form(x):
    if isinstance(x, (Lst, Mat, str, complex)) or isinstance(x, bool):
        raise ArgumentError("sym_form takes one real number")
    if isinstance(x, (int, Fraction)):
        return sym_text(x)
    t = sym_text(float(x))
    if t is None:
        raise MathError("no simple exact form")
    return t


# ======================================================================================
