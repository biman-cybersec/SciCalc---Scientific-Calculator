"""Checks: engineering.  Run alone with  python run_tests.py engineering"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "engineering"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_engineering_31(check, ev, near, ex):
    """Phase 3: engineering and materials"""
    # ================= Phase 3: engineering and materials =================
    G0 = 9.80665
    pi8 = math.pi
    near("stress", "stress(1000,0.002)", 500000)
    near("strain/stress/E chain", "youngs_modulus(stress(1000,0.002),strain(0.001,1))", (1000 / 0.002) / 0.001)
    # beams against the integrated Euler-Bernoulli equation (numerical double integration of M/EI)
    def beam_mid(F, L, E, I):
        n = 2000
        h = L / n
        # simply supported, central load: M(x)=F x/2 for x<=L/2 ; deflection by integrating curvature twice
        xs = [k * h for k in range(n + 1)]
        M = [F * x / 2 if x <= L / 2 else F * (L - x) / 2 for x in xs]
        th = [0.0]
        for k in range(n):
            th.append(th[-1] + (M[k] + M[k + 1]) / 2 / (E * I) * h)
        y = [0.0]
        for k in range(n):
            y.append(y[-1] + (th[k] + th[k + 1]) / 2 * h)
        slope0 = -y[n] / L                       # make deflection zero at the far support
        return -(y[n // 2] + slope0 * xs[n // 2])
    near("beam_deflection_simple by integration", "beam_deflection_simple(1000,2,200e9,8e-6)", beam_mid(1000, 2, 200e9, 8e-6), 1e-4)
    near("cantilever = 16 x simple (same F, L, E, I)", "beam_deflection_cantilever(7,2,3e9,1e-5)", 16 * ev("beam_deflection_simple(7,2,3e9,1e-5)"))
    near("udl against 5/384 formula", "beam_deflection_udl(2000,3,200e9,1e-5)", 5 * 2000 * 3 ** 4 / (384 * 200e9 * 1e-5))
    near("udl equals point load of same total at 5/8 ratio", "beam_deflection_udl(1000,2,1e9,1e-5)", ev("beam_deflection_simple(2000,2,1e9,1e-5)") * 5 * 48 / (384 * 1), 1e-9)
    near("moment", "beam_moment_simple(1000,4)", 1000)
    near("I rect by integration", "second_moment_rect(0.1,0.2)", sum(0.1 * ((k + 0.5) * 0.2 / 4000 - 0.1) ** 2 * 0.2 / 4000 for k in range(4000)), 1e-6)
    near("I circle = polar/2", "second_moment_circle(0.1)", ev("polar_moment_circle(0.1)") / 2)
    near("polar J circle by integration", "polar_moment_circle(0.1)", sum(2 * pi8 * ((k + 0.5) * 0.05 / 4000) ** 3 * 0.05 / 4000 for k in range(4000)), 1e-6)
    near("hydrostatic 10 m water", "hydrostatic_pressure(1000,10)", 98066.5)
    near("buoyancy = weight of displaced water", "buoyancy(1000,0.5)", 0.5 * 1000 * G0)
    near("drag", "drag_force(1.225,30,0.3,2)", 0.5 * 1.225 * 900 * 0.3 * 2)
    near("terminal velocity balances weight and drag", "drag_force(1.225,terminal_velocity(80,1.225,1,0.7),1,0.7)", 80 * G0, 1e-9)
    near("bernoulli returns v1 when pressure is equal", "bernoulli_v(1e5,3,1e5,1000)", 3)
    near("bernoulli energy balance", "0.5*1000*bernoulli_v(2e5,2,1e5,1000)^2+1e5", 0.5 * 1000 * 4 + 2e5)
    near("darcy", "darcy_pressure_drop(0.02,50,0.1,1000,2)", 0.02 * 50 / 0.1 * 0.5 * 1000 * 4)
    near("pump power", "pump_power(0.01,20,1000,0.7)", 0.01 * 20 * 1000 * G0 / 0.7)
    near("gear ratio", "gear_ratio(60,20)", 3)
    # belt: integrate the geometry numerically: wrap angle on each pulley plus the two straight spans
    D, d_, C = 0.3, 0.1, 1.0
    a = math.asin((D - d_) / 2 / C)
    near("belt_length geometry", "belt_length(0.3,0.1,1)", 2 * C * math.cos(a) + D * (pi8 / 2 + a) + d_ * (pi8 / 2 - a))
    near("belt equal pulleys", "belt_length(0.2,0.2,1)", 2 + pi8 * 0.2)
    near("belt argument order free", "belt_length(0.1,0.3,1)", ev("belt_length(0.3,0.1,1)"))
    near("belt approximation for long spans", "belt_length(0.3,0.1,100)", 2 * 100 + pi8 * 0.2 + 0.04 / 400, 1e-6)
    near("torque / power round trip", "power_from_torque(torque_from_power(1000,1500),1500)", 1000)
    near("torque from power", "torque_from_power(1000,1500)", 1000 / (1500 * 2 * pi8 / 60))
    near("roof pitch", "roof_pitch(4,12)", 4)
    near("roof angle 6 in 12", "roof_angle(6,12)", math.degrees(math.atan(0.5)))
    near("rafter", "rafter_length(4,3)", 5)
    near("rafter from angle", "rafter_length(10,roof_angle(5,10)*0+5)", math.hypot(10, 5))
    near("stair riser", "stair_rise(2.7,15)", 0.18)
    ex("stair count", "stair_count(2.7,0.18)", 15)
    ex("stair count rounds up", "stair_count(2.7,0.17)", 16)
    near("stair run rule", "stair_run(175)", 280)
    near("slab", "concrete_volume_slab(5,4,0.1)", 2)
    near("column", "concrete_volume_column(0.4,3)", pi8 * 0.2 ** 2 * 3)
    near("paint", "paint_coverage(40,2,10)", 8)
    near("rebar 12 mm per metre ~ d^2/162", "rebar_weight(12,1)", 12 ** 2 / 162.2, 2e-3)
    near("thermal growth", "thermal_growth(12e-6,10,40)", 0.0048)
    near("thermal stress = E x strain", "thermal_stress(200e9,12e-6,50)", 200e9 * (12e-6 * 50))
    near("poisson", "poisson_lateral_strain(0.3,0.002)", -0.0006)
    near("shear modulus", "shear_modulus(200e9,0.3)", 200e9 / 2.6)
    near("bulk modulus", "bulk_modulus(200e9,0.25)", 200e9 / 1.5)
    near("elastic constants: E = 9KG/(3K+G)", "9*bulk_modulus(200e9,0.3)*shear_modulus(200e9,0.3)/(3*bulk_modulus(200e9,0.3)+shear_modulus(200e9,0.3))", 200e9, 1e-9)
    near("spring rate", "spring_rate_wire(79e9,0.002,0.02,10)", 79e9 * 0.002 ** 4 / (8 * 0.02 ** 3 * 10))
    near("euler fixed is 4x pinned", "euler_buckling(200e9,8e-6,3,0.5)", 4 * ev("euler_buckling(200e9,8e-6,3,1)"))
    near("euler value", "euler_buckling(200e9,8e-6,3,1)", pi8 ** 2 * 200e9 * 8e-6 / 9)
    near("hoop", "hoop_stress(2e6,0.5,0.01)", 1e8)
    near("torsion", "torsion_shear(500,0.025,polar_moment_circle(0.05))", 500 * 0.025 / (pi8 * 0.05 ** 4 / 32), 1e-9)
    near("flywheel", "flywheel_energy(2,3000)", 0.5 * 2 * (3000 * 2 * pi8 / 60) ** 2)
    near("lever", "lever_effort(100,0.2,1)", 20)
    near("incline 30 degrees", "incline_force(30,10)", 10 * G0 / 2, 1e-9)
    near("pipe velocity", "pipe_velocity(0.01,0.1)", 0.01 / (pi8 * 0.05 ** 2))
    for e in ["stress(1,0)", "stress(1,-1)", "strain(1,0)", "youngs_modulus(1,0)", "beam_deflection_simple(1,0,1,1)",
              "beam_deflection_simple(1,1,0,1)", "beam_deflection_cantilever(1,1,1,0)", "beam_deflection_udl(1,-1,1,1)",
              "beam_moment_simple(1,0)", "second_moment_rect(0,1)", "second_moment_circle(-1)", "polar_moment_circle(0)",
              "hydrostatic_pressure(0,1)", "hydrostatic_pressure(1,-1)", "buoyancy(-1,1)", "drag_force(0,1,1,1)", "terminal_velocity(0,1,1,1)",
              "terminal_velocity(1,1,1,0)", "bernoulli_v(0,0,1,1000)", "bernoulli_v(1,1,1,0)", "darcy_pressure_drop(1,1,0,1,1)",
              "pump_power(1,1,1,0)", "pump_power(1,1,1,1.5)", "gear_ratio(1,0)", "belt_length(1,1,0)", "belt_length(1,0,1)",
              "belt_length(3,1,0.5)", "torque_from_power(1,0)", "roof_pitch(1,0)", "roof_angle(1,0)", "rafter_length(-1,1)",
              "stair_rise(1,0)", "stair_rise(1,2.5)", "stair_count(1,0)", "stair_count(-1,1)", "stair_run(400)", "concrete_volume_slab(1,1,0)",
              "concrete_volume_column(0,1)", "paint_coverage(1,1,0)", "rebar_weight(0,1)", "thermal_growth(1,0,1)", "thermal_stress(0,1,1)",
              "poisson_lateral_strain(0.6,1)", "shear_modulus(1,-1)", "bulk_modulus(1,0.5)", "spring_rate_wire(1,1,0,1)",
              "euler_buckling(1,1,0,1)", "euler_buckling(1,1,1,0)", "hoop_stress(1,1,0)", "torsion_shear(1,1,0)", "flywheel_energy(0,1)",
              "lever_effort(1,1,0)", "incline_force(30,-1)", "pipe_velocity(1,0)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
