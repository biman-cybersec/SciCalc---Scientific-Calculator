"""Checks: science misc.  Run alone with  python run_tests.py science_misc"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "science_misc"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_science_misc_16(ev, near):
    """physics, chemistry, astronomy, optics ..."""
    # ---------------------------------------------------------------- physics, chemistry, astronomy, optics ...
    near("momentum", "momentum(4,-2.5)", -10)
    near("kinetic_energy = p^2/2m", "kinetic_energy(4,3)", momentum_ref := (4 * 3) ** 2 / (2 * 4))
    near("grav_potential", "grav_potential(3,10)", 3 * 9.80665 * 10)
    near("centripetal_force", "centripetal_force(2,6,3)", 2 * 36 / 3)
    near("ohm V=IR", "ohm_voltage(ohm_current(12,4),4)", 12)
    near("ohm R=V/I", "ohm_resistance(12,ohm_current(12,4))", 4)
    near("electric_power", "electric_power(230,2)", 460)
    near("wave_speed", "wave_speed(440,0.78)", 343.2)
    near("spring_pe", "spring_pe(200,0.05)", 0.25)
    near("projectile_range symmetric", "projectile_range(20,30)", ev("projectile_range(20,60)"), 1e-9)
    near("projectile_range 45deg max", "projectile_range(20,45)", 400 / 9.80665, 1e-12)
    near("sound_speed_air", "sound_speed_air(20)", 331.3 * math.sqrt(293.15 / 273.15), 1e-12)
    near("ideal_pressure PV=nRT", "ideal_pressure(2,300,0.05)*0.05", 2 * 8.314462618 * 300, 1e-12)
    near("heat_transfer", "heat_transfer(2,4184,10)", 83680)
    near("thermal_expansion", "thermal_expansion(0.000012,2,50)", 0.0012, 1e-12)
    near("reynolds_number", "reynolds_number(1000,2,0.05,0.001)", 100000)
    near("blackbody_power Stefan-Boltzmann", "blackbody_power(2,300)", 5.670374419e-8 * 2 * 300 ** 4, 1e-12)
    near("escape = sqrt2 * orbital", "escape_velocity(5.972e24,6.371e6)/orbital_velocity(5.972e24,6.371e6)", math.sqrt(2), 1e-12)
    near("orbital_period = 2 pi r / v", "orbital_period(5.972e24,6.771e6)*orbital_velocity(5.972e24,6.771e6)", 2 * math.pi * 6.771e6, 1e-9)
    near("grav_force", "grav_force(5.972e24,7.348e22,3.844e8)", 6.6743e-11 * 5.972e24 * 7.348e22 / 3.844e8 ** 2, 1e-9)
    near("schwarzschild_radius sun", "schwarzschild_radius(1.98847e30)", 2953.25, 1e-3)
    near("au2km", "au2km(2)", 2 * 149597870.7, 1e-12)
    near("z_redshift", "z_redshift(656.3*1.5,656.3)", 0.5, 1e-9)
    near("synodic_period Earth-Mars", "synodic_period(365.25,687)", 1 / (1 / 365.25 - 1 / 687), 1e-9)
    near("snells_law", "sin(snells_law(1,1.5,30))*1.5", math.sin(math.radians(30)), 1e-12)
    near("critical_angle", "sin(critical_angle(1.5,1))*1.5", 1, 1e-12)
    near("photon_energy", "photon_energy(5e14)", 6.62607015e-34 * 5e14, 1e-12)
    near("sound_intensity_level", "sound_intensity_level(1e-6,1e-12)", 60)
    near("lensmaker", "lensmaker(1.5,20,-20)", 20, 1e-12)
    near("ph_calc", "ph_calc(1e-3)", 3, 1e-12)
    near("poh_calc", "poh_calc(1e-4)", 4, 1e-12)
    near("pH+pOH = 14", "ph_calc(2e-5)+poh_calc(5e-10)", 14, 1e-9)
    near("henderson_hasselbalch", "henderson_hasselbalch(4.76,0.2,0.1)", 4.76 + math.log10(2), 1e-12)
    near("molarity", "molarity(0.5,2)", 0.25)
    near("snr_db", "snr_db(1000,10)", 20)
    near("nyquist_frequency", "nyquist_frequency(48000)", 24000)
