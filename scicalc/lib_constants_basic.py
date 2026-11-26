"""First batch of named constants

Module 10 of 47.  Taken from lines 2347-2465 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_constants_basic"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .registry import register_constant

# ---------- 7e. Constants ----------

# --- Mathematical & Golden Ratio ---
register_constant("pi", math.pi, "Ratio of a circle's circumference to its diameter")
register_constant("e", math.e, "Euler's number, the base of natural logarithms")
register_constant("tau", math.tau, "Tau = 2*pi, one full turn in radians")
register_constant("phi", (1 + math.sqrt(5)) / 2, "The golden ratio")

# --- Universal & Relativistic Constants ---
register_constant("const_c", 299792458, "Speed of light in vacuum (m/s)", aliases=("c_light", "c"))
register_constant("const_h", 6.62607015e-34, "Planck constant (J.s)", aliases=("h_planck",))
register_constant("const_hbar", 1.054571817e-34, "Reduced Planck constant h/(2*pi) (J.s)", aliases=("hbar",))
register_constant("const_G", 6.67430e-11, "Newtonian constant of gravitation (m^3/(kg.s^2))", aliases=("G_grav", "big_g"))
register_constant("const_g0", 9.80665, "Standard acceleration of gravity (m/s^2)", aliases=("g_accel", "g"))

# --- Electromagnetism ---
register_constant("const_e", 1.602176634e-19, "Elementary charge (C)", aliases=("e_charge", "qe"))
register_constant("const_eps0", 8.8541878128e-12, "Vacuum electric permittivity (F/m)", aliases=("eps0", "ep0"))
register_constant("const_mu0", 1.25663706212e-6, "Vacuum magnetic permeability (N/A^2)", aliases=("mu0",))
register_constant("const_ke", 8.9875517923e9, "Coulomb constant 1/(4*pi*eps0) (N.m^2/C^2)", aliases=("ke_coulomb", "ke"))
register_constant("const_z0", 376.730313668, "Characteristic impedance of vacuum (ohm)", aliases=("z0_vac", "z0"))

# --- Atomic, Quantum & Nuclear ---
register_constant("const_me", 9.1093837015e-31, "Electron rest mass (kg)", aliases=("m_electron", "m_e"))
register_constant("const_mp", 1.67262192369e-27, "Proton rest mass (kg)", aliases=("m_proton", "m_p"))
register_constant("const_mn", 1.67492749804e-27, "Neutron rest mass (kg)", aliases=("m_neutron", "m_n"))
register_constant("const_u", 1.66053906660e-27, "Atomic mass unit / dalton (kg)", aliases=("amu", "m_u"))
register_constant("const_a0", 5.29177210903e-11, "Bohr radius (m)", aliases=("a0_bohr", "bohr_r"))
register_constant("const_ryd", 10973731.568160, "Rydberg constant (1/m)", aliases=("rydberg",))
register_constant("const_alpha", 7.2973525693e-3, "Fine-structure constant", aliases=("fine_alpha", "alpha_fs"))
register_constant("const_ub", 9.2740100783e-24, "Bohr magneton (J/T)", aliases=("bohr_m",))
register_constant("const_un", 5.0507837461e-27, "Nuclear magneton (J/T)", aliases=("nuclear_m",))

# --- Physico-Chemical & Thermodynamics ---
register_constant("const_NA", 6.02214076e23, "Avogadro constant (1/mol)", aliases=("avogadro", "n_a"))
register_constant("const_kB", 1.380649e-23, "Boltzmann constant (J/K)", aliases=("k_boltzmann", "k_b"))
register_constant("const_R", 8.314462618, "Molar ideal gas constant (J/(mol.K))", aliases=("gas_R", "r_gas"))
register_constant("const_F", 96485.33212, "Faraday constant (C/mol)", aliases=("faraday",))
register_constant("const_sigma", 5.670374419e-8, "Stefan-Boltzmann constant (W/(m^2.K^4))", aliases=("stefan_sigma", "stefan"))
register_constant("const_atm", 101325, "Standard atmospheric pressure (Pa)", aliases=("std_atm", "atm"))
register_constant("const_wien", 2.897771955e-3, "Wien displacement law constant (m.K)", aliases=("wien_b",))
register_constant("const_ev", 1.602176634e-19, "Electronvolt in Joules (J)", aliases=("ev",))

# --- Astronomy & Astrophysics ---
register_constant("const_au", 149597870700, "Astronomical unit (m)", aliases=("au",))
register_constant("const_ly", 9.4607304725808e15, "Light-year (m)", aliases=("lightyear", "ly"))
register_constant("const_pc", 3.08567758149137e16, "Parsec (m)", aliases=("parsec", "pc"))

# --- Constants Expansion Batch ---
register_constant("PLANCK_CONST", 6.62607015e-34, "Planck's constant h (J·s)")
register_constant("REDUCED_PLANCK", 1.054571817e-34, "Reduced Planck's constant h-bar (J·s)")
register_constant("ELEM_CHARGE", 1.602176634e-19, "Elementary charge e (C)")
register_constant("ELEC_MASS", 9.1093837015e-31, "Electron rest mass m_e (kg)")
register_constant("PROTON_MASS", 1.67262192369e-27, "Proton rest mass m_p (kg)")
register_constant("NEUTRON_MASS", 1.67492749804e-27, "Neutron rest mass m_n (kg)")
register_constant("AVOGADRO_CONST", 6.02214076e23, "Avogadro constant N_A (mol^-1)")
register_constant("BOLTZMANN_CONST", 1.380649e-23, "Boltzmann constant k_B (J/K)")
register_constant("GAS_CONSTANT", 8.314462618, "Molar gas constant R (J/(mol·K))")
register_constant("STEFAN_BOLTZMANN", 5.670374419e-8, "Stefan-Boltzmann constant sigma (W/(m^2·K^4))")
register_constant("COULOMB_CONST", 8.9875517923e9, "Coulomb constant k_e (N·m^2/C^2)")
register_constant("FARADAY_CONST", 96485.33212, "Faraday constant F (C/mol)")
register_constant("BOHR_RADIUS", 5.29177210903e-11, "Bohr radius a_0 (m)")
register_constant("GOLDEN_RATIO", 1.618033988749895, "Golden ratio phi")
register_constant("EULER_MASCHERONI", 0.577215664901532, "Euler-Mascheroni constant gamma")

# --- Advanced Mathematical & Astrophysical Batch ---
register_constant("const_apery", 1.202056903159594, "Apéry's constant ζ(3)", aliases=("apery",))
register_constant("const_khinchin", 2.685452001065306, "Khinchin's constant", aliases=("khinchin",))
register_constant("const_omega", 0.5671432904097838, "Omega constant W(1)", aliases=("omega",))

# --- Advanced Mathematical Constants ---
register_constant("const_glaisher", 1.2824271291006226, "Glaisher-Kinkelin constant", aliases=("glaisher",))

# --- Astrophysical & Planetary Constants ---
register_constant("const_msun", 1.98847e30, "Solar mass M_☉ (kg)", aliases=("solar_mass", "m_sun"))
register_constant("const_mearth", 5.97219e24, "Earth mass M_⊕ (kg)", aliases=("earth_mass", "m_earth"))
register_constant("const_rearth", 6371000.0, "Mean Earth radius R_⊕ (m)", aliases=("earth_radius", "r_earth"))
register_constant("const_lsun", 3.828e26, "Solar luminosity L_☉ (W)", aliases=("solar_luminosity", "l_sun"))

# --- Physical & Thermodynamic Constants Extensions ---
register_constant("const_tpwater", 273.16, "Triple point of water temperature (K)", aliases=("triple_point",))
register_constant("const_vm", 0.022413969, "Molar volume of ideal gas at STP (m³/mol)", aliases=("molar_volume",))
register_constant("const_compton", 2.42631023867e-12, "Compton wavelength of electron (m)", aliases=("compton_electron",))

# --- Additional Physics, Cosmology & Mathematics Constants ---
register_constant("const_feigenbaum_delta", 4.6692016091, "Feigenbaum bifurcation constant delta", aliases=("feigenbaum_d",))
register_constant("const_feigenbaum_alpha", 2.50290787509, "Feigenbaum scaling constant alpha", aliases=("feigenbaum_a",))
register_constant("const_gme", 3.986004418e14, "Earth standard gravitational parameter μ (m³/s²)", aliases=("earth_gm",))
register_constant("const_gms", 1.32712440018e20, "Sun standard gravitational parameter μ (m³/s²)", aliases=("sun_gm",))
register_constant("const_proton_electron_ratio", 1836.15267343, "Proton-to-electron mass ratio", aliases=("mp_me_ratio",))
register_constant("const_loschmidt", 2.6867811e25, "Loschmidt constant at STP (m⁻³)", aliases=("loschmidt",))
register_constant("const_magnetic_flux_quantum", 2.067833848e-15, "Magnetic flux quantum Φ₀ (Wb)", aliases=("flux_quantum",))
register_constant("const_conductance_quantum", 7.7480917293e-5, "Conductance quantum G₀ (S)", aliases=("conductance_quantum",))
register_constant("const_planck_length", 1.616255e-35, "Planck length l_P (m)", aliases=("planck_length",))
register_constant("const_planck_time", 5.391247e-44, "Planck time t_P (s)", aliases=("planck_time",))
register_constant("const_planck_mass", 2.176434e-8, "Planck mass m_P (kg)", aliases=("planck_mass",))
register_constant("const_planck_temp", 1.416784e32, "Planck temperature T_P (K)", aliases=("planck_temp",))


# --- Additional Mathematical & Number Theory Constants ---
register_constant("const_catalan", 0.915965594177219, "Catalan's constant", aliases=("catalan_const",))
register_constant("const_mm", 0.261497212847646, "Meissel–Mertens constant", aliases=("meissel_mertens",))
register_constant("const_twin_prime", 0.660161815846869, "Twin prime constant (Brun's constant related)", aliases=("twin_prime_c",))
register_constant("const_silver_ratio", 2.414213562373095, "Silver ratio 1 + sqrt(2)", aliases=("silver_ratio",))
register_constant("const_plastic", 1.324717957244746, "Plastic constant (rho)", aliases=("plastic_constant",))
register_constant("const_brun", 1.902160583104, "Brun's constant for twin primes", aliases=("brun_constant",))
register_constant("const_golomb", 0.6243299885435508, "Golomb–Dickman constant", aliases=("golomb_dickman",))
register_constant("const_fransen", 2.807770242028519, "Fransén–Robinson constant", aliases=("fransen_robinson",))
register_constant("const_supergolden", 1.465571231876768, "Supergolden ratio (psi)", aliases=("supergolden_ratio",))
register_constant("const_landau_ramanujan", 0.76422365358922, "Landau–Ramanujan constant", aliases=("landau_ramanujan",))

# --- Additional Planetary, Lunar & Solar Constants ---
register_constant("const_solar_irradiance", 1361.0, "Total solar irradiance / Solar constant at 1 AU (W/m^2)", aliases=("solar_constant",))
register_constant("const_mmass", 7.342e22, "Lunar mass M_moon (kg)", aliases=("moon_mass",))
register_constant("const_mradius", 1737400.0, "Mean lunar radius R_moon (m)", aliases=("moon_radius",))
register_constant("const_jmass", 1.8982e27, "Jupiter mass M_jup (kg)", aliases=("jupiter_mass",))
register_constant("const_jradius", 69911000.0, "Mean Jupiter volumetric radius R_jup (m)", aliases=("jupiter_radius",))
