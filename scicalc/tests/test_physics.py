"""Checks: physics.  Run alone with  python run_tests.py physics"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "physics"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..registry import REGISTRY

from .helpers import _err, _expr_error  # noqa: F401


def checks_physics_23(check, ev, near, simpson):
    """Sprint 6 : physics"""
    # ---------------------------------------------------------------- Sprint 6 : physics
    K = lambda nm: float(REGISTRY.constant(nm).value)  # pyright: ignore[reportOptionalMemberAccess]
    g0 = K("const_g0")
    c0, h0_, G0, e0 = K("const_c"), K("const_h"), K("const_G"), 1.602176634e-19

    # kinematics: identities, numerical integration and round trips
    for u, a, t in [(0, 9.8, 2), (5, 2, 3), (-4, 3, 6), (12, -1.5, 7), (0.5, 0.25, 40)]:
        tag = f"{u},{a},{t}"
        near(f"final_velocity({tag})", f"final_velocity({tag})", u + a * t)
        near(f"displacement({tag}) = integral of velocity", f"displacement({tag})", simpson(lambda s: u + a * s, 0, t, 20), 1e-9)
        near(f"displacement({tag}) = average velocity * t", f"displacement({tag})", (u + (u + a * t)) / 2 * t)
        near(f"accel_from recovers a ({tag})", f"accel_from({u},final_velocity({tag}),{t})", a)
        near(f"velocity_sq({tag}) is |v|", f"velocity_sq({u},{a},displacement({tag}))", abs(u + a * t), 1e-9)
    for h in (0.5, 4.903325, 20, 100):
        tfall = ev(f"free_fall_time({h})")
        near(f"free_fall_time({h}): s = g t^2/2", f"displacement(0,const_g0,free_fall_time({h}))", h)
        near(f"free_fall_speed({h}) = g * t", f"free_fall_speed({h})", g0 * tfall)
        near(f"free_fall_speed({h}) by velocity_sq", f"free_fall_speed({h})", ev(f"velocity_sq(0,const_g0,{h})"))
    for v, ang in [(20, 30), (20, 45), (50, 60), (9.80665, 90), (15, 0)]:
        tf = ev(f"proj_time({v},{ang})")
        vy = v * math.sin(math.radians(ang))
        near(f"proj_time({v},{ang}) returns to the ground", f"displacement({vy!r},-const_g0,{tf!r})", 0, 1e-9)
        near(f"proj_max_height({v},{ang}) at half the flight time", f"proj_max_height({v},{ang})", ev(f"displacement({vy!r},-const_g0,{tf / 2!r})"), 1e-9)
        near(f"proj_max_height({v},{ang}) by energy", f"proj_max_height({v},{ang})", vy * vy / (2 * g0), 1e-9)
        near(f"projectile range from time ({v},{ang})", f"projectile_range({v},{ang})", v * math.cos(math.radians(ang)) * tf, 1e-9)
    for x in (0, 1, 60, 1000, -30):
        near(f"rpm2rads({x}) = revolutions * 2pi / 60", f"rpm2rads({x})", x / 60 * 2 * math.pi)
        near(f"rads2rpm(rpm2rads({x})) round trip", f"rads2rpm(rpm2rads({x}))", x, 1e-12)
    near("rpm2rads(60) is one revolution per second", "rpm2rads(60)", 2 * math.pi)
    for v, r in [(10, 5), (3, 0.5), (30, 100)]:
        near(f"centripetal_acc({v},{r}) = w^2 r", f"centripetal_acc({v},{r})", (v / r) ** 2 * r)
    near("newton_force", "newton_force(4,2.5)", 10)
    near("weight_n", "weight_n(70)", 70 * 9.80665)
    near("weight_n = newton_force(m,g)", "weight_n(12)", ev("newton_force(12,const_g0)"))
    near("friction_force", "friction_force(0.3,50)", 15)
    for ang, mu in [(30, 0), (30, 0.2), (45, 0.5), (60, 0.8), (10, 0.5), (45, 1)]:
        m_ = 3.0
        net = (m_ * g0 * math.sin(math.radians(ang)) - ev(f"friction_force({mu},weight_n({m_})*cos({ang}))")) / m_
        near(f"incline_accel({ang},{mu}) from force balance", f"incline_accel({ang},{mu})", max(0.0, net), 1e-9)
    near("incline_accel frictionless 90 deg is free fall", "incline_accel(90,0)", g0, 1e-12)
    near("incline_accel stuck block", "incline_accel(10,0.5)", 0)
    for F, r, ang in [(10, 2, 90), (10, 2, 30), (5, 0.4, 150), (7, 1, 0)]:
        Fx, Fy = F * math.cos(math.radians(ang)), F * math.sin(math.radians(ang))
        near(f"torque({F},{r},{ang}) = r x F (z component)", f"torque({F},{r},{ang})", r * Fy - 0 * Fx, 1e-9)
        near(f"work_done({F},{r},{ang}) = F . d", f"work_done({F},{r},{ang})", Fx * r, 1e-9)
    near("work and torque swap sin and cos", "work_done(8,3,40)", ev("torque(8,3,50)"), 1e-9)
    # moments of inertia from numerical integration of r^2 dm
    for m_, r_ in [(4, 3), (1, 1), (2.5, 0.4)]:
        near(f"mi_disk({m_},{r_}) integral", f"mi_disk({m_},{r_})", simpson(lambda x: x * x * (m_ / (math.pi * r_ ** 2)) * 2 * math.pi * x, 0, r_, 200), 1e-9)
        rho = m_ / (4 / 3 * math.pi * r_ ** 3)
        near(f"mi_sphere({m_},{r_}) integral over shells", f"mi_sphere({m_},{r_})", simpson(lambda x: (2 / 3) * x * x * rho * 4 * math.pi * x * x, 0, r_, 200), 1e-9)
        near(f"mi_hollow_sphere({m_},{r_}) = shell at r", f"mi_hollow_sphere({m_},{r_})", (2 / 3) * m_ * r_ * r_, 1e-12)
        near(f"mi ordering hollow > disc > solid sphere ({m_},{r_})", f"mi_hollow_sphere({m_},{r_})-mi_sphere({m_},{r_})", (2 / 3 - 2 / 5) * m_ * r_ * r_, 1e-12)
    for m_, L_ in [(12, 2), (1, 1), (0.3, 5)]:
        near(f"mi_rod({m_},{L_}) integral", f"mi_rod({m_},{L_})", simpson(lambda x: x * x * m_ / L_, -L_ / 2, L_ / 2, 200), 1e-9)
    near("parallel-axis theorem for the rod", "mi_rod(2,3)+2*(1.5)^2", 2 * 3 * 3 / 3, 1e-12)
    near("ang_momentum", "ang_momentum(2.5,4)", 10)
    near("rot_ke = L w / 2", "rot_ke(2.5,4)", ev("ang_momentum(2.5,4)*4/2"))
    near("rot_ke vs translational analogue", "rot_ke(mi_disk(2,0.5),10)", 0.5 * (0.5 * 2 * 0.25) * 100)
    near("power_work", "power_work(500,20)", 25)
    for L in (0.25, 1, 9.80665, 2.5):
        near(f"pendulum_period({L}) = SHM period with k = m g / L", f"pendulum_period({L})", ev(f"spring_period(3,3*const_g0/{L})"), 1e-12)
    # simulate a mass on a spring and measure the period (leapfrog) -- independent of the formula
    for m_, k_ in [(1, 4), (2, 50), (0.1, 3)]:
        dt, x, v, tt = 1e-5, 1.0, 0.0, 0.0
        a_ = -k_ / m_ * x
        crossings = []
        prev = x
        while len(crossings) < 2 and tt < 20:
            v += 0.5 * dt * a_
            x += dt * v
            a_ = -k_ / m_ * x
            v += 0.5 * dt * a_
            tt += dt
            if prev > 0 >= x or prev < 0 <= x:
                crossings.append(tt)
            prev = x
        near(f"spring_period({m_},{k_}) by simulation", f"spring_period({m_},{k_})", 2 * (crossings[1] - crossings[0]), 1e-4)
    near("hooke_force", "hooke_force(40,-0.5)", 20)
    check("hooke work equals spring energy", abs(-simpson(lambda x: ev(f"hooke_force(50,{x!r})"), 0, 0.2, 10) - 0.5 * 50 * 0.2 ** 2) < 1e-9, True)

    # waves and sound
    for f_, vs_, vo_ in [(440, 0, 0), (440, 30, 0), (440, 0, 10), (1000, -20, -5), (500, 100, 50)]:
        lam = (343.0 - vs_) / f_                 # wavelength in front of a moving source
        near(f"doppler_freq({f_},{vs_},{vo_}) by wavelength", f"doppler_freq({f_},{vs_},{vo_})", (343.0 + vo_) / lam, 1e-12)
    near("doppler_freq with nothing moving", "doppler_freq(440,0,0)", 440)
    near("beat_freq symmetric", "beat_freq(443,440)", 3)
    near("beat_freq", "beat_freq(440,443)", 3)
    for L_, T_, mu_ in [(0.5, 100, 0.01), (0.65, 70, 0.0004), (1, 9.80665, 0.001)]:
        near(f"string_freq({L_},{T_},{mu_}) = v / (2L)", f"string_freq({L_},{T_},{mu_})", math.sqrt(T_ / mu_) / 2 / L_, 1e-12)
    near("string_freq doubles when the length halves", "string_freq(0.25,50,0.01)/string_freq(0.5,50,0.01)", 2, 1e-12)

    # gases and heat
    for p1, v1, t1, v2, t2 in [(100, 2, 300, 4, 600), (101325, 1, 273.15, 0.5, 300), (5, 10, 250, 20, 250), (2, 3, 400, 3, 500)]:
        p2 = ev(f"combined_gas_p2({p1},{v1},{t1},{v2},{t2})")
        near(f"combined gas ({p1},{v1},{t1},{v2},{t2}): pV/T is conserved", f"{p2!r}*{v2}/{t2}", p1 * v1 / t1, 1e-12)
        near("boyle then Gay-Lussac equals the combined law", f"gay_lussac_p2(boyle_p2({p1},{v1},{v2}),{t1},{t2})", p2, 1e-12)
        near(f"boyle_p2 keeps pV ({p1},{v1},{v2})", f"boyle_p2({p1},{v1},{v2})*{v2}", p1 * v1, 1e-12)
        near(f"charles_v2 keeps V/T ({v1},{t1},{t2})", f"charles_v2({v1},{t1},{t2})/{t2}", v1 / t1, 1e-12)
        near(f"gay_lussac_p2 keeps p/T ({p1},{t1},{t2})", f"gay_lussac_p2({p1},{t1},{t2})/{t2}", p1 / t1, 1e-12)
    for Th, Tc in [(400, 300), (1000, 300), (373.15, 273.15), (500, 0)]:
        near(f"carnot_eff({Th},{Tc}) = 1 - Qc/Qh with Qc/Qh = Tc/Th", f"carnot_eff({Th},{Tc})", (Th - Tc) / Th, 1e-12)
        near(f"carnot_eff({Th},{Tc}) from entropy balance", f"carnot_eff({Th},{Tc})", 1 - ev(f"entropy_change(1000,{Th})*{Tc}") / 1000 if Tc else 1, 1e-12)
    near("entropy_change", "entropy_change(600,300)", 2)
    near("entropy of melting ice", "entropy_change(latent_heat(1,334000),273.15)", 334000 / 273.15, 1e-12)
    near("latent_heat", "latent_heat(0.5,2260000)", 1130000)
    near("conduction_rate", "conduction_rate(0.5,2,10,0.1)", 100)
    near("conduction_rate halves when the wall doubles", "conduction_rate(0.8,3,20,0.2)/conduction_rate(0.8,3,20,0.1)", 0.5, 1e-12)
    # Wien's law against the maximum of Planck's curve (golden-section search)
    def planck(lam, T):
        x = h0_ * c0 / (lam * K("const_kB") * T)
        return 1.0 / (lam ** 5 * math.expm1(x))
    for T_ in (3000, 5772, 10000):
        lo, hi = 1e-8, 1e-5
        for _ in range(200):
            m1, m2 = lo + (hi - lo) * 0.381966, lo + (hi - lo) * 0.618034
            if planck(m1, T_) > planck(m2, T_):
                hi = m2
            else:
                lo = m1
        near(f"wien_peak({T_}) is where the Planck curve peaks", f"wien_peak({T_})", (lo + hi) / 2, 1e-6)
    near("wien_peak(5772) is green (about 502 nm)", "wien_peak(5772)", 5.0204e-7, 1e-3)

    # circuits
    for r1, r2, r3 in [(100, 220, 330), (1, 1, 1), (3, 6, 6), (1000, 47, 4.7)]:
        near(f"res_parallel2({r1},{r2}) by conductance", f"res_parallel2({r1},{r2})", 1 / (1 / r1 + 1 / r2), 1e-12)
        near(f"res_parallel3({r1},{r2},{r3}) by conductance", f"res_parallel3({r1},{r2},{r3})", 1 / (1 / r1 + 1 / r2 + 1 / r3), 1e-12)
        near("res_parallel3 = nested res_parallel2", f"res_parallel3({r1},{r2},{r3})", ev(f"res_parallel2(res_parallel2({r1},{r2}),{r3})"), 1e-12)
        near(f"res_series3({r1},{r2},{r3})", f"res_series3({r1},{r2},{r3})", r1 + r2 + r3)
        near("res_series3 = nested res_series2", f"res_series3({r1},{r2},{r3})", ev(f"res_series2(res_series2({r1},{r2}),{r3})"))
        check(f"parallel < smallest branch ({r1},{r2},{r3})", ev(f"res_parallel3({r1},{r2},{r3})") < min(r1, r2, r3), True)
        near(f"cap_series2({r1},{r2}) by 1/C", f"cap_series2({r1},{r2})", 1 / (1 / r1 + 1 / r2), 1e-12)
        near(f"cap_parallel2({r1},{r2})", f"cap_parallel2({r1},{r2})", r1 + r2)
        near(f"capacitors are the dual of resistors ({r1},{r2})", f"cap_series2({r1},{r2})", ev(f"res_parallel2({r1},{r2})"), 1e-12)
    near("res_parallel2 with a short circuit", "res_parallel2(0,50)", 0)
    near("res_parallel3 with a short circuit", "res_parallel3(0,5,7)", 0)
    # RC charging reaches 1 - 1/e after one time constant (simulated)
    for R_, C_ in [(1000, 0.001), (470, 2.2e-6), (1e6, 1e-6)]:
        tau = ev(f"rc_tau({R_},{C_})")
        v, dt, tt = 0.0, tau / 20000, 0.0
        while tt < tau - 1e-18:
            v += dt * (1 - v) / tau
            tt += dt
        near(f"rc_tau({R_},{C_}): charge after tau is 63.2%", f"{v!r}", 1 - math.exp(-1), 1e-3)
        near(f"rc_tau({R_},{C_})", f"rc_tau({R_},{C_})", R_ * C_, 1e-12)
    near("rl_tau", "rl_tau(0.5,100)", 0.005)
    near("rl_tau as the dual of rc_tau", "rl_tau(2,4)", 0.5, 1e-12)
    for L_, C_ in [(1, 1 / (4 * math.pi ** 2)), (0.01, 1e-6), (2e-3, 5e-9)]:
        f0 = ev(f"lc_freq({L_!r},{C_!r})")
        near(f"lc_freq({L_},{C_}) is where the reactances cancel", f"2*pi*{f0!r}*{L_!r}-1/(2*pi*{f0!r}*{C_!r})", 0, 1e-8)
        near(f"impedance_rlc at resonance equals R ({L_},{C_})", f"impedance_rlc(12,{L_!r},{C_!r},{f0!r})", 12, 1e-8)
    for R_, L_, C_, f_ in [(3, 5, 1, 1 / (2 * math.pi)), (100, 0.1, 1e-5, 50), (10, 0.02, 2e-4, 400)]:
        w = 2 * math.pi * f_
        near(f"impedance_rlc({R_},{L_},{C_},{f_}) as a complex impedance", f"impedance_rlc({R_},{L_},{C_},{f_!r})", abs(complex(R_, w * L_ - 1 / (w * C_))), 1e-9)
        Z = abs(complex(R_, w * L_ - 1 / (w * C_)))
        near(f"power_factor = cos(phase) ({R_},{L_},{C_},{f_})", f"power_factor({R_},impedance_rlc({R_},{L_},{C_},{f_!r}))", R_ / Z, 1e-9)
    near("power_factor 3-4-5", "power_factor(3,5)", 0.6)
    for Vp, Np, Ns in [(230, 1000, 50), (11000, 500, 20), (12, 100, 800)]:
        Vs = ev(f"transformer_vs({Vp},{Np},{Ns})")
        near(f"transformer_vs({Vp},{Np},{Ns}) conserves power for an ideal load", f"{Vs!r}*({Vp}/{Vs!r}*5)", Vp * 5, 1e-12)
        near(f"transformer volts per turn ({Vp},{Np},{Ns})", f"{Vs!r}/{Ns}", Vp / Np, 1e-12)

    # electromagnetism
    for q1, q2, r in [(0.001, 0.001, 1), (1e-6, -2e-6, 0.3), (5e-9, 5e-9, 0.02)]:
        k_ = 1 / (4 * math.pi * K("const_eps0"))
        near(f"coulomb_force({q1},{q2},{r}) with k = 1/(4 pi eps0)", f"coulomb_force({q1},{q2},{r})", k_ * q1 * q2 / r ** 2, 1e-8)
        near(f"coulomb_force = field * charge ({q1},{q2},{r})", f"coulomb_force({q1},{q2},{r})", ev(f"electric_field({q1},{r})") * q2, 1e-12)
        near("coulomb_force is symmetric in the charges", f"coulomb_force({q2},{q1},{r})", ev(f"coulomb_force({q1},{q2},{r})"), 1e-12)
        near(f"coulomb inverse-square law ({r})", f"coulomb_force({q1},{q2},{r})/coulomb_force({q1},{q2},{2 * r})", 4, 1e-12)
        h = r * 1e-4
        near(f"electric_field({q1},{r}) = -dV/dr (numerical)", f"electric_field({q1},{r})", -(ev(f"electric_potential({q1},{r + h!r})") - ev(f"electric_potential({q1},{r - h!r})")) / (2 * h), 1e-6)
        near(f"electric_potential({q1},{r}) = work to bring a unit charge in", f"electric_potential({q1},{r})",
             simpson(lambda x: ev(f"electric_field({q1},{x!r})"), r, 2000 * r, 20000) + ev(f"electric_potential({q1},{2000 * r!r})"), 1e-4)
    for A_, d_, k_ in [(1, 0.001, 1), (0.02, 1e-4, 80), (0.5, 0.01, 2.2)]:
        near(f"plate_capacitance({A_},{d_},{k_})", f"plate_capacitance({A_},{d_},{k_})", k_ * K("const_eps0") * A_ / d_, 1e-12)
        near("plate_capacitance halves with twice the gap", f"plate_capacitance({A_},{2 * d_!r},{k_})/plate_capacitance({A_},{d_},{k_})", 0.5, 1e-12)
        near("two plates in parallel add (plate area doubles)", f"plate_capacitance({2 * A_!r},{d_},{k_})", ev(f"cap_parallel2(plate_capacitance({A_},{d_},{k_}),plate_capacitance({A_},{d_},{k_}))"), 1e-12)
    for q, v, B, ang in [(2, 3, 4, 90), (1.6e-19, 1e6, 0.5, 30), (-3, 2, 5, 150), (1, 1, 1, 0)]:
        vv = (v, 0.0, 0.0)
        Bv = (B * math.cos(math.radians(ang)), B * math.sin(math.radians(ang)), 0.0)
        cr = (vv[1] * Bv[2] - vv[2] * Bv[1], vv[2] * Bv[0] - vv[0] * Bv[2], vv[0] * Bv[1] - vv[1] * Bv[0])
        near(f"magnetic_force({q},{v},{B},{ang}) = |q v x B|", f"magnetic_force({q},{v},{B},{ang})", abs(q) * math.sqrt(sum(c * c for c in cr)), 1e-9)
    # wire: Biot-Savart integral over the whole wire, with z = r tan(t)
    for I_, r_ in [(10, 0.05), (1, 1), (100, 0.2)]:
        integral = simpson(lambda t: math.cos(t), -math.pi / 2 + 1e-9, math.pi / 2 - 1e-9, 2000)
        near(f"wire_field({I_},{r_}) by Biot-Savart", f"wire_field({I_},{r_})", K("const_mu0") * I_ / (4 * math.pi * r_) * integral, 1e-8)
        near(f"wire_field({I_},{r_}) falls as 1/r", f"wire_field({I_},{r_})/wire_field({I_},{2 * r_!r})", 2, 1e-12)
    near("solenoid_field", "solenoid_field(1000,2)", K("const_mu0") * 2000, 1e-12)
    near("solenoid_field with mu0 = 4 pi e-7", "solenoid_field(1000,2)", 4e-7 * math.pi * 2000, 1e-8)
    near("solenoid is wire_field times 2 pi r * n", "solenoid_field(500,3)", ev("wire_field(500*3,0.5/pi)"), 1e-9)
    for N_ in (1, 100, 2500):
        near(f"faraday_emf({N_}) from the mean of dPhi/dt", f"faraday_emf({N_},{0.3 * 1.5 ** 2 + 0.1 * 1.5 - (0.3 + 0.1)!r},0.5)",
             -N_ * ev("mean_value('0.6*x+0.1',1,1.5)"), 1e-7)
    near("faraday_emf sign (Lenz)", "faraday_emf(10,0.5,2)", -2.5)

    # optics
    for f_, do in [(10, 30), (10, 15), (-20, 40), (5, 7.5), (10, 5)]:
        di = ev(f"lens_image_dist({f_},{do})")
        near(f"lens_image_dist({f_},{do}) satisfies 1/f = 1/do + 1/di", f"1/{do}+1/{di!r}", 1 / f_, 1e-12)
        A_ = 1 - di / f_
        near(f"ray-transfer matrix: B element vanishes at the image ({f_},{do})", f"{do}+{di!r}-{do}*{di!r}/{f_}", 0, 1e-9)
        near(f"lens_magnification({di:.6g},{do}) = matrix A element", f"lens_magnification({di!r},{do})", -di / do, 1e-12)
        near(f"ray matrix A equals the magnification ({f_},{do})", f"1-{di!r}/{f_}", ev(f"lens_magnification({di!r},{do})"), 1e-9)
    near("object at 2f is imaged at 2f", "lens_image_dist(10,20)", 20)
    near("virtual image of a diverging lens", "lens_image_dist(-10,10)", -5)
    near("lens_magnification", "lens_magnification(15,30)", -0.5)
    for R_ in (30, 100, 0.5):
        h = R_ * 1e-4                                  # paraxial ray at height h reflects and crosses the axis here
        th = math.asin(h / R_)
        cross = R_ - R_ / (2 * math.cos(th))
        near(f"mirror_focal({R_}) by tracing a paraxial ray", f"mirror_focal({R_})", cross, 1e-6)
    near("mirror_focal negative for convex", "mirror_focal(-40)", -20)
    for n1, n2 in [(1, 1.5), (1, 1.33), (1.5, 1), (1, 2.4)]:
        tb = ev(f"brewster_angle({n1},{n2})")
        near(f"brewster_angle({n1},{n2}): reflected and refracted rays are perpendicular", f"{n1}*sin({tb!r})-{n2}*sin(90-{tb!r})", 0, 1e-9)
    near("brewster_angle of glass", "brewster_angle(1,1.5)", 56.30993247, 1e-8)
    for m_, lam, d_ in [(1, 500, 1000), (2, 400, 3000), (-1, 600, 2000), (0, 500, 1000)]:
        th = ev(f"grating_angle({m_},{lam},{d_})")
        near(f"grating equation d sin(theta) = m lambda ({m_},{lam},{d_})", f"{d_}*sin({th!r})", m_ * lam, 1e-9)
    near("grating_angle first order", "grating_angle(1,500,1000)", 30, 1e-9)

    # modern physics
    for m_, v_ in [(9.1093837015e-31, 1e6), (1.67e-27, 3000), (0.145, 40)]:
        near(f"de_broglie({m_},{v_}) = h/p", f"de_broglie({m_},{v_})", h0_ / (m_ * v_), 1e-12)
        E_ = 0.5 * m_ * v_ ** 2
        near(f"de_broglie({m_},{v_}) from the kinetic energy", f"de_broglie({m_},{v_})", h0_ / math.sqrt(2 * m_ * E_), 1e-9)
    near("de_broglie of a 1 eV electron (1.23 nm)", "de_broglie(const_me,sqrt(2*1.602176634e-19/const_me))", 1.2264e-9, 1e-3)
    lam_c = h0_ / (K("const_me") * c0)
    near("compton_shift(90) is the Compton wavelength", "compton_shift(90)", lam_c, 1e-12)
    near("compton_shift(180) is twice that", "compton_shift(180)", 2 * lam_c, 1e-12)
    near("compton_shift(0) is zero", "compton_shift(0)", 0, 1e-12)
    for th in (30, 60, 120, 175):
        E1 = 100e3 * e0                                          # 100 keV photon
        E2 = 1 / (1 / E1 + (1 - math.cos(math.radians(th))) / (K("const_me") * c0 ** 2))
        near(f"compton_shift({th}) from the scattered-photon energy", f"compton_shift({th})", h0_ * c0 / E2 - h0_ * c0 / E1, 1e-9)
    ryd_ev = 0.5 * K("const_me") * c0 ** 2 * K("const_alpha") ** 2 / e0
    for n, Z in [(1, 1), (2, 1), (3, 1), (1, 2), (4, 3), (10, 1)]:
        near(f"bohr_energy({n},{Z}) from m c^2 alpha^2 / 2", f"bohr_energy({n},{Z})", -ryd_ev * Z * Z / (n * n), 1e-6)
    near("bohr_energy ground state of hydrogen", "bohr_energy(1,1)", -13.605693123, 1e-9)
    for n1, n2 in [(1, 2), (2, 3), (2, 4), (3, 5), (1, 100)]:
        dE = (-ryd_ev / n1 ** 2 + ryd_ev / n2 ** 2) * -1 * e0
        near(f"rydberg_wavelength({n1},{n2}) = hc / (E2 - E1)", f"rydberg_wavelength({n1},{n2})", h0_ * c0 / ((ryd_ev / n1 ** 2 - ryd_ev / n2 ** 2) * e0), 1e-6)
        near(f"rydberg_wavelength({n1},{n2}) from bohr_energy", f"rydberg_wavelength({n1},{n2})", h0_ * c0 / ((ev(f'bohr_energy({n2},1)') - ev(f'bohr_energy({n1},1)')) * e0), 1e-6)
    near("H-alpha is 656 nm", "rydberg_wavelength(2,3)", 6.5611e-7, 1e-4)
    near("Lyman limit is 91.1 nm", "rydberg_wavelength(1,1000000)", 9.1127e-8, 1e-3)
    near("mass_energy of one gram", "mass_energy(0.001)", 0.001 * c0 ** 2, 1e-12)
    for v_ in (0.1, 0.5, 0.6, 0.8, 0.99):
        beta = v_
        vv = f"{v_}*const_c"
        gam = 1 / math.sqrt(1 - beta ** 2)
        near(f"lorentz_gamma({v_}c)", f"lorentz_gamma({vv})", gam, 1e-12)
        near(f"gamma^2 - (gamma*beta)^2 = 1 at {v_}c", f"lorentz_gamma({vv})^2-(lorentz_gamma({vv})*{beta})^2", 1, 1e-9)
        near(f"time_dilation(10, {v_}c)", f"time_dilation(10,{vv})", 10 * gam, 1e-12)
        near(f"length_contraction(10, {v_}c)", f"length_contraction(10,{vv})", 10 / gam, 1e-12)
        near(f"time dilation and length contraction cancel ({v_}c)", f"time_dilation(7,{vv})*length_contraction(3,{vv})", 21, 1e-12)
        E_ = ev(f"rel_energy(2,{vv})")
        p_ = ev(f"rel_momentum(2,{vv})")
        near(f"energy-momentum relation E^2 = (pc)^2 + (mc^2)^2 at {v_}c", f"{E_!r}^2", (p_ * c0) ** 2 + (2 * c0 ** 2) ** 2, 1e-9)
        near(f"rel_energy / mass_energy = gamma at {v_}c", f"rel_energy(2,{vv})/mass_energy(2)", gam, 1e-12)
        near(f"rel_momentum({v_}c) = E v / c^2", f"rel_momentum(2,{vv})", E_ * (v_ * c0) / c0 ** 2, 1e-9)
    near("low-speed limit of the kinetic energy", "rel_energy(1,1000)-mass_energy(1)", 0.5 * 1 * 1000 ** 2, 1e-5)
    near("low-speed limit of the momentum", "rel_momentum(2,300)", 600, 1e-9)
    near("negative velocity gives negative momentum", "rel_momentum(1,-0.6*const_c)", -ev("rel_momentum(1,0.6*const_c)"), 1e-12)
    for N0, t, th in [(80, 10, 5), (1000, 3, 12), (1, 0, 4), (5e6, 2.5, 0.5)]:
        near(f"half_life_remaining({N0},{t},{th}) = N0 e^(-lambda t)", f"half_life_remaining({N0},{t},{th})", N0 * math.exp(-math.log(2) / th * t), 1e-9)
        near(f"decay_constant({th})", f"decay_constant({th})", math.log(2) / th, 1e-12)
    near("one half-life leaves half", "half_life_remaining(64,5730,5730)", 32, 1e-12)
    near("three half-lives leave an eighth", "half_life_remaining(64,3,1)", 8, 1e-12)
    for N0, th in [(1000, 5), (2e6, 30.1), (1, 1)]:
        want = -ev(f"deriv('{N0}*2^(-x/{th})', 0)")
        near(f"activity({N0},{th}) = -dN/dt at t=0 (numerical derivative)", f"activity({N0},{th})", want, 1e-6)
    near("activity", "activity(100,ln(2))", 100, 1e-12)

    # astronomy
    near("hill_sphere of the Earth (about 1.5 million km)", "hill_sphere(1.496e11,5.972e24,1.989e30)", 1.4964e9, 1e-3)
    near("hill_sphere cube check", "(hill_sphere(2,1,6)/2)^3*3*6", 1, 1e-12)
    near("hill_sphere scales with the orbit", "hill_sphere(10,1,5)/hill_sphere(1,1,5)", 10, 1e-12)
    near("hill_sphere scales as m^(1/3)", "hill_sphere(1,8,3)/hill_sphere(1,1,3)", 2, 1e-12)
    near("roche_limit Earth-Moon (about 18,400 km)", "roche_limit(6.371e6,5514,3344)", 1.8366e7, 1e-3)
    near("roche_limit of equal densities", "roche_limit(1,3,3)", 2.44, 1e-12)
    near("roche_limit scales with the cube root of the density ratio", "roche_limit(1,8,1)/roche_limit(1,1,1)", 2, 1e-12)
    near("surface_gravity Earth", "surface_gravity(5.972e24,6.371e6)", 9.82, 1e-3)
    near("surface_gravity Moon", "surface_gravity(7.342e22,1.7374e6)", 1.62, 1e-2)
    near("surface_gravity Sun", "surface_gravity(1.98847e30,6.957e8)", 274, 5e-3)
    near("surface_gravity by Newton's law", "surface_gravity(5.972e24,6.371e6)*5", ev("grav_force(5.972e24,5,6.371e6)"), 1e-9)
    near("parallax_distance of Proxima Centauri (1.30 pc)", "parallax_distance(0.7687)", 1.3009, 1e-3)
    near("parallax_distance is its own inverse", "parallax_distance(parallax_distance(0.37))", 0.37, 1e-12)
    near("hubble_velocity", "hubble_velocity(100)", 7000)
    near("hubble_velocity at 1 Gpc", "hubble_velocity(1000)", 70000)
    near("distance_modulus of the Sun (1 AU in parsecs)", "distance_modulus(-26.74,4.83)", 4.848e-6, 3e-3)
    for mm, MM in [(5, 0), (10, 5), (-1, 3), (12.3, 4.1)]:
        d_pc = ev(f"distance_modulus({mm},{MM})")
        near(f"distance_modulus({mm},{MM}) round trip through the magnitude formula", f"5*log({d_pc!r})-5", mm - MM, 1e-9)
    near("luminosity_bb of the Sun", "luminosity_bb(6.957e8,5772)", 3.828e26, 1e-3)
    near("luminosity_bb scales as T^4", "luminosity_bb(1,200)/luminosity_bb(1,100)", 16, 1e-12)
    near("luminosity_bb scales as R^2", "luminosity_bb(3,1000)/luminosity_bb(1,1000)", 9, 1e-12)
    near("luminosity_bb agrees with blackbody_power", "luminosity_bb(2,300)", ev("blackbody_power(4*pi*4,300)"), 1e-9)
