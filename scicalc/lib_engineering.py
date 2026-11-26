"""Phase 3: engineering and materials

Module 37 of 47.  Taken from lines 12495-12818 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_engineering"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .lib_vectors_matrices import _fr

# ======================================================================================
#  PHASE 3 : ENGINEERING AND MATERIALS (44)
#  SI units throughout (metres, kilograms, seconds, newtons, pascals, watts) unless a
#  description says otherwise (mm for rebar and the stair rule). g = 9.80665 m/s^2.
#  Beam formulas are the standard textbook cases: simply supported (central point load or
#  uniform load) and cantilever (end load).
# ======================================================================================
_ENG = "Engineering & Materials"
_G0 = 9.80665


def _eng(name, desc, args, example, **kw):
    return register(name, _ENG, desc, args, example=example, **kw)


def _epos(x, what="value"):
    """A finite number greater than zero."""
    x = float(x)
    if not math.isfinite(x) or x <= 0:
        raise MathError(f"{what} must be positive")
    return x


def _enn(x, what="value"):
    """A finite number that is not negative."""
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise MathError(f"{what} cannot be negative")
    return x


def _efin(x, what="value"):
    x = float(x)
    if not math.isfinite(x):
        raise MathError(f"{what} is not a finite number")
    return x


@_eng("stress", "Normal stress in Pa: stress(force_N, area_m2)", 2, "stress(1000, 0.002) => 500000")
def stress(f, a):
    return _efin(f) / _epos(a, "area")


@_eng("strain", "Strain (no unit): strain(extension, original_length)", 2, "strain(0.002, 2) => 0.001")
def strain(dl, l):
    return _efin(dl) / _epos(l, "length")


@_eng("youngs_modulus", "Young's modulus in Pa: youngs_modulus(stress_Pa, strain)", 2, "youngs_modulus(200e6, 0.001) => 2×10^11")
def youngs_modulus(s, e):
    e = _efin(e)
    if e == 0:
        raise MathError("strain cannot be zero")
    return _efin(s) / e


@_eng("beam_deflection_simple", "Mid-span deflection (m) of a simply supported beam with a central point load: F, L, E, I", 4,
      "beam_deflection_simple(1000, 2, 200e9, 8e-6) => 0.0001041666667")
def beam_deflection_simple(f, l, e, i):
    return _efin(f) * _epos(l, "length") ** 3 / (48 * _epos(e, "modulus") * _epos(i, "second moment"))


@_eng("beam_deflection_cantilever", "Tip deflection (m) of a cantilever with an end load: F, L, E, I", 4,
      "beam_deflection_cantilever(500, 1.5, 70e9, 4e-6) => 0.002008928571", )
def beam_deflection_cantilever(f, l, e, i):
    return _efin(f) * _epos(l, "length") ** 3 / (3 * _epos(e, "modulus") * _epos(i, "second moment"))


@_eng("beam_deflection_udl", "Mid-span deflection (m) of a simply supported beam under a uniform load w (N/m): w, L, E, I", 4,
      "beam_deflection_udl(2000, 3, 200e9, 1e-5) => 0.0010546875")
def beam_deflection_udl(w, l, e, i):
    return 5 * _efin(w) * _epos(l, "length") ** 4 / (384 * _epos(e, "modulus") * _epos(i, "second moment"))


@_eng("beam_moment_simple", "Maximum bending moment (N m) of a simply supported beam with a central point load: F, L", 2,
      "beam_moment_simple(1000, 4) => 1000")
def beam_moment_simple(f, l):
    return _efin(f) * _epos(l, "length") / 4


@_eng("second_moment_rect", "Second moment of area (m^4) of a rectangle about its centroidal axis: b (width), h (height)", 2,
      "second_moment_rect(0.1, 0.2) => 0.00006666666667")
def second_moment_rect(b, h):
    return _epos(b, "width") * _epos(h, "height") ** 3 / 12


@_eng("second_moment_circle", "Second moment of area (m^4) of a solid circle: second_moment_circle(diameter)", 1,
      "second_moment_circle(0.1) => 0.000004908738521")
def second_moment_circle(d):
    return math.pi * _epos(d, "diameter") ** 4 / 64


@_eng("polar_moment_circle", "Polar moment of area (m^4) of a solid circular shaft: polar_moment_circle(diameter)", 1,
      "polar_moment_circle(0.1) => 0.000009817477042")
def polar_moment_circle(d):
    return math.pi * _epos(d, "diameter") ** 4 / 32


@_eng("hydrostatic_pressure", "Gauge pressure (Pa) at depth h in a fluid of density rho: hydrostatic_pressure(rho, h)", 2,
      "hydrostatic_pressure(1000, 10) => 98066.5")
def hydrostatic_pressure(rho, h):
    return _epos(rho, "density") * _G0 * _enn(h, "depth")


@_eng("buoyancy", "Buoyant force (N) on a displaced volume V (m^3) in a fluid of density rho: buoyancy(rho, V)", 2,
      "buoyancy(1000, 0.5) => 4903.325")
def buoyancy(rho, v):
    return _epos(rho, "density") * _G0 * _enn(v, "volume")


@_eng("drag_force", "Drag force (N): drag_force(rho, v, Cd, A) = 1/2 rho v^2 Cd A", 4,
      "drag_force(1.225, 30, 0.3, 2) => 330.75")
def drag_force(rho, v, cd, a):
    return 0.5 * _epos(rho, "density") * _efin(v) ** 2 * _enn(cd, "drag coefficient") * _enn(a, "area")


@_eng("terminal_velocity", "Terminal velocity (m/s) of a falling body: terminal_velocity(mass, rho, Cd, A)", 4,
      "terminal_velocity(80, 1.225, 1, 0.7) => 42.77630471")
def terminal_velocity(m, rho, cd, a):
    return math.sqrt(2 * _epos(m, "mass") * _G0 / (_epos(rho, "density") * _epos(cd, "drag coefficient") * _epos(a, "area")))


@_eng("bernoulli_v", "Speed v2 (m/s) after a pressure change at equal height: bernoulli_v(p1, v1, p2, rho)", 4,
      "bernoulli_v(200000, 2, 100000, 1000) => 14.28285686")
def bernoulli_v(p1, v1, p2, rho):
    inside = _efin(v1) ** 2 + 2 * (_efin(p1) - _efin(p2)) / _epos(rho, "density")
    if inside < 0:
        raise MathError("the fluid cannot have this pressure change")
    return math.sqrt(inside)


@_eng("darcy_pressure_drop", "Pressure drop (Pa) in a pipe, Darcy-Weisbach: darcy_pressure_drop(f, L, D, rho, v)", 5,
      "darcy_pressure_drop(0.02, 50, 0.1, 1000, 2) => 20000")
def darcy_pressure_drop(f, l, d, rho, v):
    return _enn(f, "friction factor") * _enn(l, "length") / _epos(d, "diameter") * _epos(rho, "density") * _efin(v) ** 2 / 2


@_eng("pump_power", "Shaft power (W) needed to lift Q (m^3/s) through a head (m): pump_power(Q, head, rho, efficiency 0-1)", 4,
      "pump_power(0.01, 20, 1000, 0.7) => 2801.9")
def pump_power(q, head, rho, eff):
    eff = _epos(eff, "efficiency")
    if eff > 1:
        raise MathError("efficiency is between 0 and 1")
    return _epos(rho, "density") * _G0 * _enn(q, "flow") * _enn(head, "head") / eff


@_eng("gear_ratio", "Gear ratio driven/driver teeth: gear_ratio(driven_teeth, driver_teeth)", 2, "gear_ratio(60, 20) => 3")
def gear_ratio(driven, driver):
    return _epos(driven, "teeth") / _epos(driver, "teeth")


@_eng("belt_length", "Length (m) of an open belt round two pulleys: belt_length(D, d, centre_distance)", 3,
      "belt_length(0.3, 0.1, 1) => 2.638326889")
def belt_length(big, small, c):
    big, small, c = _epos(big, "diameter"), _epos(small, "diameter"), _epos(c, "centre distance")
    if big < small:
        big, small = small, big
    half = (big - small) / 2
    if c <= half:
        raise MathError("the pulleys overlap")
    return 2 * math.sqrt(c * c - half * half) + math.pi * (big + small) / 2 + (big - small) * math.asin(half / c)


@_eng("torque_from_power", "Torque (N m) from power (W) and speed (rpm): torque_from_power(P, rpm)", 2,
      "torque_from_power(1000, 1500) => 6.366197724")
def torque_from_power(p, rpm):
    return _efin(p) / (2 * math.pi * _epos(rpm, "speed") / 60)


@_eng("power_from_torque", "Power (W) from torque (N m) and speed (rpm): power_from_torque(T, rpm)", 2,
      "power_from_torque(6.366197724, 1500) => 1000")
def power_from_torque(t, rpm):
    return _efin(t) * 2 * math.pi * _efin(rpm) / 60


@_eng("roof_pitch", "Pitch as 'rise per 12 run': roof_pitch(rise, run)", 2, "roof_pitch(4, 12) => 4")
def roof_pitch(rise, run):
    return _efin(rise) / _epos(run, "run") * 12


@_eng("roof_angle", "Roof slope angle in the current angle mode: roof_angle(rise, run)", 2, "roof_angle(1, 1) => 45", angle_out=True)
def roof_angle(rise, run):
    return math.atan2(_enn(rise, "rise"), _epos(run, "run"))


@_eng("rafter_length", "Rafter length: rafter_length(run, rise)", 2, "rafter_length(4, 3) => 5")
def rafter_length(run, rise):
    return math.hypot(_enn(run, "run"), _enn(rise, "rise"))


@_eng("stair_rise", "Height of each riser: stair_rise(total_height, number_of_risers)", 2, "stair_rise(2.7, 15) => 0.18")
def stair_rise(h, n):
    n = _epos(n, "number of risers")
    if n != int(n):
        raise MathError("the number of risers must be a whole number")
    return _epos(h, "height") / n


@_eng("stair_count", "Fewest risers that keep each at or below max_rise: stair_count(total_height, max_rise)", 2,
      "stair_count(2.7, 0.18) => 15", exact=True)
def stair_count(h, r):
    h, r = _fr(h), _fr(r)
    if h <= 0 or r <= 0:
        raise MathError("height and riser must be positive")
    n = h / r
    return int(n) if n.denominator == 1 else int(n) + 1


@_eng("stair_run", "Tread depth (mm) from the rule 2 x riser + tread = 630: stair_run(riser_mm)", 1, "stair_run(175) => 280")
def stair_run(riser):
    riser = _enn(riser, "riser")
    if riser >= 315:
        raise MathError("the riser is too high for this rule")
    return 630 - 2 * riser


@_eng("concrete_volume_slab", "Volume (m^3) of a rectangular slab: concrete_volume_slab(length, width, thickness)", 3,
      "concrete_volume_slab(5, 4, 0.1) => 2")
def concrete_volume_slab(l, w, t):
    return _epos(l, "length") * _epos(w, "width") * _epos(t, "thickness")


@_eng("concrete_volume_column", "Volume (m^3) of a round column: concrete_volume_column(diameter, height)", 2,
      "concrete_volume_column(0.4, 3) => 0.3769911184")
def concrete_volume_column(d, h):
    return math.pi * _epos(d, "diameter") ** 2 / 4 * _epos(h, "height")


@_eng("paint_coverage", "Litres of paint: paint_coverage(area_m2, coats, m2_per_litre)", 3, "paint_coverage(40, 2, 10) => 8")
def paint_coverage(area, coats, rate):
    return _epos(area, "area") * _epos(coats, "coats") / _epos(rate, "coverage")


@_eng("rebar_weight", "Mass (kg) of steel bar (7850 kg/m^3): rebar_weight(diameter_mm, length_m)", 2,
      "rebar_weight(12, 6) => 5.326884503")
def rebar_weight(d, l):
    return math.pi / 4 * (_epos(d, "diameter") / 1000) ** 2 * 7850 * _epos(l, "length")


@_eng("thermal_growth", "Change in length: thermal_growth(alpha_per_K, length, delta_T)", 3,
      "thermal_growth(12e-6, 10, 40) => 0.0048")
def thermal_growth(alpha, l, dt):
    return _efin(alpha) * _epos(l, "length") * _efin(dt)


@_eng("thermal_stress", "Stress (Pa) when thermal expansion is prevented: thermal_stress(E, alpha, delta_T)", 3,
      "thermal_stress(200e9, 12e-6, 50) => 120000000")
def thermal_stress(e, alpha, dt):
    return _epos(e, "modulus") * _efin(alpha) * _efin(dt)


@_eng("poisson_lateral_strain", "Lateral strain = -nu x axial strain: poisson_lateral_strain(nu, axial_strain)", 2,
      "poisson_lateral_strain(0.3, 0.002) => -0.0006")
def poisson_lateral_strain(nu, e):
    nu = _efin(nu)
    if not -1 < nu <= 0.5:
        raise MathError("Poisson's ratio is between -1 and 0.5")
    return -nu * _efin(e)


@_eng("shear_modulus", "Shear modulus G = E / (2(1+nu)): shear_modulus(E, nu)", 2, "shear_modulus(200e9, 0.3) => 7.692307692×10^10")
def shear_modulus(e, nu):
    nu = _efin(nu)
    if not -1 < nu <= 0.5:
        raise MathError("Poisson's ratio is between -1 and 0.5")
    return _epos(e, "modulus") / (2 * (1 + nu))


@_eng("bulk_modulus", "Bulk modulus K = E / (3(1-2nu)): bulk_modulus(E, nu)", 2, "bulk_modulus(200e9, 0.25) => 1.333333333×10^11")
def bulk_modulus(e, nu):
    nu = _efin(nu)
    if not -1 < nu < 0.5:
        raise MathError("Poisson's ratio must be below 0.5 here")
    return _epos(e, "modulus") / (3 * (1 - 2 * nu))


@_eng("spring_rate_wire", "Stiffness (N/m) of a coil spring: spring_rate_wire(G, wire_d, coil_D, active_turns)", 4,
      "spring_rate_wire(79e9, 0.002, 0.02, 10) => 1975")
def spring_rate_wire(g, d, big_d, n):
    return _epos(g, "modulus") * _epos(d, "wire diameter") ** 4 / (8 * _epos(big_d, "coil diameter") ** 3 * _epos(n, "turns"))


@_eng("euler_buckling", "Critical buckling load (N): euler_buckling(E, I, L, K) with K = 1 pinned, 0.5 fixed, 2 cantilever", 4,
      "euler_buckling(200e9, 8e-6, 3, 1) => 1754596.338")
def euler_buckling(e, i, l, k):
    return math.pi ** 2 * _epos(e, "modulus") * _epos(i, "second moment") / (_epos(k, "K") * _epos(l, "length")) ** 2


@_eng("hoop_stress", "Hoop stress (Pa) in a thin-walled cylinder: hoop_stress(pressure, radius, wall)", 3,
      "hoop_stress(2e6, 0.5, 0.01) => 100000000")
def hoop_stress(p, r, t):
    return _efin(p) * _epos(r, "radius") / _epos(t, "wall thickness")


@_eng("torsion_shear", "Shear stress (Pa) in a twisted shaft: torsion_shear(T, r, J)", 3, "torsion_shear(500, 0.025, 6.14e-7) => 20358306.19")
def torsion_shear(t, r, j):
    return _efin(t) * _enn(r, "radius") / _epos(j, "polar moment")


@_eng("flywheel_energy", "Kinetic energy (J) of a spinning body: flywheel_energy(I, rpm)", 2,
      "flywheel_energy(2, 3000) => 98696.04401")
def flywheel_energy(i, rpm):
    return 0.5 * _epos(i, "inertia") * (2 * math.pi * _efin(rpm) / 60) ** 2


@_eng("lever_effort", "Effort force to balance a load on a lever: lever_effort(load, load_arm, effort_arm)", 3,
      "lever_effort(100, 0.2, 1) => 20")
def lever_effort(load, la, ea):
    return _efin(load) * _enn(la, "arm") / _epos(ea, "effort arm")


@_eng("incline_force", "Force (N) along a frictionless slope to hold a mass: incline_force(slope_angle, mass)", 2,
      "incline_force(30, 10) => 49.03325", angle_in=True)
def incline_force(a, m):
    return _enn(m, "mass") * _G0 * math.sin(a)


@_eng("pipe_velocity", "Mean speed (m/s) in a round pipe: pipe_velocity(Q_m3_per_s, diameter_m)", 2,
      "pipe_velocity(0.01, 0.1) => 1.273239545")
def pipe_velocity(q, d):
    return _enn(q, "flow") / (math.pi * _epos(d, "diameter") ** 2 / 4)


# ======================================================================================
