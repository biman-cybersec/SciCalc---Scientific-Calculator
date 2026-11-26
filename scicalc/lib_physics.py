"""Sprint 6: physics

Module 31 of 47.  Taken from lines 9993-10576 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_physics"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import REGISTRY, register

# ======================================================================================
#  SPRINT 6 : PHYSICS (84)
#  SI units throughout (m, kg, s, N, J, W, K, A, V, ohm, F, H, T, C) unless a description says
#  otherwise.  Every angle argument and result is in DEGREES.  g = const_g0 = 9.80665 m/s^2.
#  Physical constants are read from the constants table so every function agrees with it.
# ======================================================================================
_PH = "Physics & Engineering"
_PO = "Acoustics & Optics"
_PA = "Astronomy & Orbital Mechanics"


def _K(name):
    return float(REGISTRY.constant(name).value)  # pyright: ignore[reportOptionalMemberAccess]


def _ppos(*vals):
    for v in vals:
        if not (v > 0) or math.isinf(v):
            raise MathError("this value must be positive")


def _pnn(*vals):
    for v in vals:
        if v < 0 or math.isinf(v) or math.isnan(v):
            raise MathError("this value must not be negative")


def _pang(deg, lo, hi):
    if not (lo <= deg <= hi):
        raise MathError(f"angle must be between {lo} and {hi} degrees")
    return math.radians(deg)


def _p(name, desc, args, example, cat=_PH):
    return register(name, cat, desc, args, example=example)


# ---------- kinematics and dynamics ----------
@_p("final_velocity", "Final velocity v = u + a*t (m/s): final_velocity(u, a, t)", 3, "final_velocity(5, 2, 3) => 11")
def final_velocity(u, a, t):
    return u + a * t


@_p("displacement", "Displacement s = u*t + a*t^2/2 (m): displacement(u, a, t)", 3, "displacement(5, 2, 3) => 24")
def displacement(u, a, t):
    return u * t + a * t * t / 2


@_p("velocity_sq", "Speed v from v^2 = u^2 + 2*a*s (m/s): velocity_sq(u, a, s)", 3, "velocity_sq(3, 2, 4) => 5")
def velocity_sq(u, a, s):
    v2 = u * u + 2 * a * s
    if v2 < 0:
        raise MathError("the body never reaches that displacement")
    return math.sqrt(v2)


@_p("accel_from", "Acceleration a = (v - u)/t (m/s^2): accel_from(u, v, t)", 3, "accel_from(5, 11, 3) => 2")
def accel_from(u, v, t):
    if t == 0:
        raise MathError("t must not be zero")
    return (v - u) / t


@_p("free_fall_time", "Time to fall from rest through height h (s): free_fall_time(h)", 1, "free_fall_time(4.903325) => 1")
def free_fall_time(h):
    _pnn(h)
    return math.sqrt(2 * h / _K("const_g0"))


@_p("free_fall_speed", "Impact speed after falling from rest through height h (m/s): free_fall_speed(h)", 1, "free_fall_speed(4.903325) => 9.80665")
def free_fall_speed(h):
    _pnn(h)
    return math.sqrt(2 * _K("const_g0") * h)


@_p("proj_max_height", "Maximum height of a projectile, launch speed v (m/s) at angle 0..90 degrees (m): proj_max_height(v, angle)", 2, "proj_max_height(9.80665, 90) => 4.903325")
def proj_max_height(v, angle):
    _pnn(v)
    return (v * math.sin(_pang(angle, 0, 90))) ** 2 / (2 * _K("const_g0"))


@_p("proj_time", "Time of flight of a projectile on level ground (s): proj_time(v, angle)", 2, "proj_time(9.80665, 90) => 2")
def proj_time(v, angle):
    _pnn(v)
    return 2 * v * math.sin(_pang(angle, 0, 90)) / _K("const_g0")


@_p("rpm2rads", "Revolutions per minute to rad/s: rpm2rads(x)", 1, "rpm2rads(60) => 6.283185307")
def rpm2rads(x):
    return x * 2 * math.pi / 60


@_p("rads2rpm", "rad/s to revolutions per minute: rads2rpm(x)", 1, "rads2rpm(2*pi) => 60")
def rads2rpm(x):
    return x * 60 / (2 * math.pi)


@_p("centripetal_acc", "Centripetal acceleration v^2/r (m/s^2): centripetal_acc(v, r)", 2, "centripetal_acc(10, 5) => 20")
def centripetal_acc(v, r):
    _ppos(r)
    return v * v / r


@_p("newton_force", "Force F = m*a (N): newton_force(m, a)", 2, "newton_force(4, 2.5) => 10")
def newton_force(m, a):
    _pnn(m)
    return m * a


@_p("weight_n", "Weight of a mass in newtons, W = m*g: weight_n(m)", 1, "weight_n(2) => 19.6133")
def weight_n(m):
    _pnn(m)
    return m * _K("const_g0")


@_p("friction_force", "Friction force mu*N (N): friction_force(mu, N)", 2, "friction_force(0.5, 40) => 20")
def friction_force(mu, N):
    _pnn(mu, N)
    return mu * N


@_p("incline_accel", "Acceleration down an incline of 0..90 degrees with friction coefficient mu (m/s^2); 0 if friction holds the body: incline_accel(angle, mu)", 2, "incline_accel(30, 0) => 4.903325")
def incline_accel(angle, mu):
    _pnn(mu)
    r = _pang(angle, 0, 90)
    return max(0.0, _K("const_g0") * (math.sin(r) - mu * math.cos(r)))


@_p("torque", "Torque F*r*sin(angle) (N.m), angle between force and lever arm in degrees: torque(F, r, angle)", 3, "torque(10, 2, 90) => 20")
def torque(F, r, angle):
    _pnn(r)
    return F * r * math.sin(math.radians(angle))


@_p("mi_disk", "Moment of inertia of a solid disc, m*r^2/2 (kg.m^2): mi_disk(m, r)", 2, "mi_disk(4, 3) => 18")
def mi_disk(m, r):
    _pnn(m, r)
    return m * r * r / 2


@_p("mi_rod", "Moment of inertia of a thin rod about its centre, m*L^2/12: mi_rod(m, L)", 2, "mi_rod(12, 2) => 4")
def mi_rod(m, L):
    _pnn(m, L)
    return m * L * L / 12


@_p("mi_sphere", "Moment of inertia of a solid sphere, 2*m*r^2/5: mi_sphere(m, r)", 2, "mi_sphere(5, 2) => 8")
def mi_sphere(m, r):
    _pnn(m, r)
    return 2 * m * r * r / 5


@_p("mi_hollow_sphere", "Moment of inertia of a hollow sphere, 2*m*r^2/3: mi_hollow_sphere(m, r)", 2, "mi_hollow_sphere(3, 2) => 8")
def mi_hollow_sphere(m, r):
    _pnn(m, r)
    return 2 * m * r * r / 3


@_p("ang_momentum", "Angular momentum L = I*w (kg.m^2/s): ang_momentum(I, w)", 2, "ang_momentum(2, 3) => 6")
def ang_momentum(I, w):
    return I * w


@_p("rot_ke", "Rotational kinetic energy I*w^2/2 (J): rot_ke(I, w)", 2, "rot_ke(2, 3) => 9")
def rot_ke(I, w):
    _pnn(I)
    return I * w * w / 2


@_p("work_done", "Work F*d*cos(angle) (J), angle in degrees: work_done(F, d, angle)", 3, "work_done(10, 5, 0) => 50")
def work_done(F, d, angle):
    return F * d * math.cos(math.radians(angle))


@_p("power_work", "Average power W/t (W): power_work(W, t)", 2, "power_work(100, 4) => 25")
def power_work(W, t):
    _ppos(t)
    return W / t


@_p("pendulum_period", "Period of a simple pendulum, 2*pi*sqrt(L/g) (s), small swings: pendulum_period(L)", 1, "pendulum_period(9.80665) => 6.283185307")
def pendulum_period(L):
    _pnn(L)
    return 2 * math.pi * math.sqrt(L / _K("const_g0"))


@_p("spring_period", "Period of a mass on a spring, 2*pi*sqrt(m/k) (s): spring_period(m, k)", 2, "spring_period(1, 4) => 3.141592654")
def spring_period(m, k):
    _ppos(m, k)
    return 2 * math.pi * math.sqrt(m / k)


@_p("hooke_force", "Restoring force of a spring, F = -k*x (N): hooke_force(k, x)", 2, "hooke_force(50, 0.2) => -10")
def hooke_force(k, x):
    _pnn(k)
    return -k * x


# ---------- waves and sound ----------
@_p("doppler_freq", "Doppler-shifted frequency f*(v + vo)/(v - vs) in air (v = 343 m/s); vs = source speed toward the observer, vo = observer speed toward the source: doppler_freq(f, vs, vo)", 3, "doppler_freq(440, 171.5, 0) => 880", _PO)
def doppler_freq(f, vs, vo):
    v = 343.0
    _pnn(f)
    if vs >= v:
        raise MathError("source speed must be below the speed of sound")
    if v + vo < 0:
        raise MathError("observer is receding faster than the sound")
    return f * (v + vo) / (v - vs)


@_p("beat_freq", "Beat frequency |f1 - f2| (Hz): beat_freq(f1, f2)", 2, "beat_freq(440, 443) => 3", _PO)
def beat_freq(f1, f2):
    return abs(f1 - f2)


@_p("string_freq", "Fundamental frequency of a string, sqrt(T/mu)/(2L) (Hz); L in m, T in N, mu in kg/m: string_freq(L, T, mu)", 3, "string_freq(0.5, 100, 0.01) => 100", _PO)
def string_freq(L, T, mu):
    _ppos(L, mu)
    _pnn(T)
    return math.sqrt(T / mu) / (2 * L)


# ---------- gases and heat ----------
@_p("boyle_p2", "Boyle's law: new pressure p1*v1/v2 (same units as p1): boyle_p2(p1, v1, v2)", 3, "boyle_p2(100, 2, 4) => 50")
def boyle_p2(p1, v1, v2):
    _ppos(v2)
    _pnn(p1, v1)
    return p1 * v1 / v2


@_p("charles_v2", "Charles's law: new volume v1*t2/t1 (temperatures in kelvin): charles_v2(v1, t1, t2)", 3, "charles_v2(2, 300, 600) => 4")
def charles_v2(v1, t1, t2):
    _ppos(t1)
    _pnn(v1, t2)
    return v1 * t2 / t1


@_p("gay_lussac_p2", "Gay-Lussac's law: new pressure p1*t2/t1 (temperatures in kelvin): gay_lussac_p2(p1, t1, t2)", 3, "gay_lussac_p2(100, 300, 450) => 150")
def gay_lussac_p2(p1, t1, t2):
    _ppos(t1)
    _pnn(p1, t2)
    return p1 * t2 / t1


@_p("combined_gas_p2", "Combined gas law: p2 = p1*v1*t2/(t1*v2) (kelvin): combined_gas_p2(p1, v1, t1, v2, t2)", 5, "combined_gas_p2(100, 2, 300, 4, 600) => 100")
def combined_gas_p2(p1, v1, t1, v2, t2):
    _ppos(t1, v2)
    _pnn(p1, v1, t2)
    return p1 * v1 * t2 / (t1 * v2)


@_p("carnot_eff", "Carnot efficiency 1 - Tc/Th as a fraction (kelvin, Th > 0, 0 <= Tc <= Th): carnot_eff(Th, Tc)", 2, "carnot_eff(400, 300) => 0.25")
def carnot_eff(Th, Tc):
    _ppos(Th)
    if not 0 <= Tc <= Th:
        raise MathError("need 0 <= Tc <= Th")
    return 1 - Tc / Th


@_p("entropy_change", "Entropy change Q/T (J/K) at constant temperature T in kelvin: entropy_change(Q, T)", 2, "entropy_change(600, 300) => 2")
def entropy_change(Q, T):
    _ppos(T)
    return Q / T


@_p("latent_heat", "Heat for a phase change m*L (J): latent_heat(m, L)", 2, "latent_heat(2, 334000) => 668000")
def latent_heat(m, L):
    _pnn(m)
    return m * L


@_p("conduction_rate", "Heat conduction rate k*A*dT/d (W): conduction_rate(k, A, dT, d)", 4, "conduction_rate(0.5, 2, 10, 0.1) => 100")
def conduction_rate(k, A, dT, d):
    _ppos(d)
    _pnn(k, A)
    return k * A * dT / d


@_p("wien_peak", "Peak wavelength of a black body, b/T (m), T in kelvin: wien_peak(T)", 1, "wien_peak(2897.771955) => 0.000001")
def wien_peak(T):
    _ppos(T)
    return _K("const_wien") / T


# ---------- circuits ----------
@_p("res_series2", "Two resistors in series (ohm): res_series2(r1, r2)", 2, "res_series2(100, 220) => 320")
def res_series2(r1, r2):
    _pnn(r1, r2)
    return r1 + r2


@_p("res_parallel2", "Two resistors in parallel (ohm): res_parallel2(r1, r2)", 2, "res_parallel2(100, 100) => 50")
def res_parallel2(r1, r2):
    _pnn(r1, r2)
    return 0.0 if r1 == 0 or r2 == 0 else r1 * r2 / (r1 + r2)


@_p("res_series3", "Three resistors in series (ohm): res_series3(r1, r2, r3)", 3, "res_series3(1, 2, 3) => 6")
def res_series3(r1, r2, r3):
    _pnn(r1, r2, r3)
    return r1 + r2 + r3


@_p("res_parallel3", "Three resistors in parallel (ohm): res_parallel3(r1, r2, r3)", 3, "res_parallel3(3, 6, 6) => 1.5")
def res_parallel3(r1, r2, r3):
    _pnn(r1, r2, r3)
    if 0 in (r1, r2, r3):
        return 0.0
    return 1 / (1 / r1 + 1 / r2 + 1 / r3)


@_p("cap_series2", "Two capacitors in series (F): cap_series2(c1, c2)", 2, "cap_series2(6, 3) => 2")
def cap_series2(c1, c2):
    _ppos(c1, c2)
    return c1 * c2 / (c1 + c2)


@_p("cap_parallel2", "Two capacitors in parallel (F): cap_parallel2(c1, c2)", 2, "cap_parallel2(6, 3) => 9")
def cap_parallel2(c1, c2):
    _ppos(c1, c2)
    return c1 + c2


@_p("rc_tau", "RC time constant R*C (s): rc_tau(R, C)", 2, "rc_tau(1000, 0.001) => 1")
def rc_tau(R, C):
    _pnn(R, C)
    return R * C


@_p("rl_tau", "RL time constant L/R (s): rl_tau(L, R)", 2, "rl_tau(0.5, 100) => 0.005")
def rl_tau(L, R):
    _pnn(L)
    _ppos(R)
    return L / R


@_p("lc_freq", "Resonant frequency 1/(2*pi*sqrt(L*C)) (Hz): lc_freq(L, C)", 2, "lc_freq(1, 1/(4*pi^2)) => 1")
def lc_freq(L, C):
    _ppos(L, C)
    return 1 / (2 * math.pi * math.sqrt(L * C))


@_p("impedance_rlc", "Series RLC impedance sqrt(R^2 + (2*pi*f*L - 1/(2*pi*f*C))^2) (ohm): impedance_rlc(R, L, C, f)", 4, "impedance_rlc(3, 5, 1, 1/(2*pi)) => 5")
def impedance_rlc(R, L, C, f):
    _pnn(R, L)
    _ppos(C, f)
    w = 2 * math.pi * f
    return math.hypot(R, w * L - 1 / (w * C))


@_p("power_factor", "Power factor R/Z (0..1): power_factor(R, Z)", 2, "power_factor(3, 5) => 0.6")
def power_factor(R, Z):
    _pnn(R)
    _ppos(Z)
    if R > Z:
        raise MathError("R cannot exceed Z")
    return R / Z


@_p("transformer_vs", "Secondary voltage Vp*Ns/Np (V): transformer_vs(Vp, Np, Ns)", 3, "transformer_vs(230, 1000, 50) => 11.5")
def transformer_vs(Vp, Np, Ns):
    _ppos(Np)
    _pnn(Ns)
    return Vp * Ns / Np


# ---------- electromagnetism ----------
@_p("coulomb_force", "Coulomb force k*q1*q2/r^2 (N); positive = repulsion: coulomb_force(q1, q2, r)", 3, "coulomb_force(0.001, 0.001, 1) => 8987.551792")
def coulomb_force(q1, q2, r):
    _ppos(r)
    return _K("const_ke") * q1 * q2 / (r * r)


@_p("electric_field", "Field of a point charge k*q/r^2 (V/m): electric_field(q, r)", 2, "electric_field(0.001, 10) => 89875.51792")
def electric_field(q, r):
    _ppos(r)
    return _K("const_ke") * q / (r * r)


@_p("electric_potential", "Potential of a point charge k*q/r (V): electric_potential(q, r)", 2, "electric_potential(0.001, 10) => 898755.1792")
def electric_potential(q, r):
    _ppos(r)
    return _K("const_ke") * q / r


@_p("plate_capacitance", "Parallel-plate capacitance k*eps0*A/d (F), area A in m^2, gap d in m, relative permittivity k: plate_capacitance(A, d, k)", 3, "plate_capacitance(1, 0.001, 1) => 0.000000008854187813")
def plate_capacitance(A, d, k):
    _ppos(A, d, k)
    return k * _K("const_eps0") * A / d


@_p("magnetic_force", "Magnetic force |q|*v*B*sin(angle) on a moving charge (N), angle 0..180 degrees: magnetic_force(q, v, B, angle)", 4, "magnetic_force(2, 3, 4, 90) => 24")
def magnetic_force(q, v, B, angle):
    _pnn(v, B)
    return abs(q) * v * B * math.sin(_pang(angle, 0, 180))


@_p("wire_field", "Magnetic field of a long straight wire mu0*I/(2*pi*r) (T): wire_field(I, r)", 2, "wire_field(10, 0.05) => 0.00004000000002")
def wire_field(I, r):
    _ppos(r)
    return _K("const_mu0") * I / (2 * math.pi * r)


@_p("solenoid_field", "Field inside a solenoid mu0*n*I (T), n = turns per metre: solenoid_field(n, I)", 2, "solenoid_field(1000, 2) => 0.002513274124")
def solenoid_field(n, I):
    _pnn(n)
    return _K("const_mu0") * n * I


@_p("faraday_emf", "Induced emf -N*dflux/dt (V): faraday_emf(N, dflux, dt)", 3, "faraday_emf(100, 0.02, 0.5) => -4")
def faraday_emf(N, dflux, dt):
    _pnn(N)
    _ppos(dt)
    return -N * dflux / dt


# ---------- optics ----------
@_p("lens_image_dist", "Thin-lens image distance di from 1/f = 1/do + 1/di (same length unit; negative = virtual image): lens_image_dist(f, do)", 2, "lens_image_dist(10, 30) => 15", _PO)
def lens_image_dist(f, do):
    _ppos(do)
    if f == 0 or f == do:
        raise MathError("no image forms at this distance")
    return 1 / (1 / f - 1 / do)


@_p("lens_magnification", "Magnification -di/do: lens_magnification(di, do)", 2, "lens_magnification(15, 30) => -0.5", _PO)
def lens_magnification(di, do):
    _ppos(do)
    return -di / do


@_p("mirror_focal", "Focal length of a spherical mirror R/2: mirror_focal(R)", 1, "mirror_focal(30) => 15", _PO)
def mirror_focal(R):
    return R / 2


@_p("brewster_angle", "Brewster angle atan(n2/n1) in degrees: brewster_angle(n1, n2)", 2, "brewster_angle(1, 1) => 45", _PO)
def brewster_angle(n1, n2):
    _ppos(n1, n2)
    return math.degrees(math.atan(n2 / n1))


@_p("grating_angle", "Diffraction-grating angle asin(m*lam/d) in degrees (lam and d in the same unit): grating_angle(m, lam, d)", 3, "grating_angle(1, 500, 1000) => 30", _PO)
def grating_angle(m, lam, d):
    _ppos(lam, d)
    x = m * lam / d
    if abs(x) > 1:
        raise MathError("this order does not exist")
    return math.degrees(math.asin(x))


# ---------- modern physics ----------
@_p("de_broglie", "de Broglie wavelength h/(m*v) (m), non-relativistic: de_broglie(m, v)", 2, "de_broglie(1, 1) => 6.62607015×10^-34")
def de_broglie(m, v):
    _ppos(m)
    if v == 0:
        raise MathError("v must not be zero")
    return _K("const_h") / (m * abs(v))


@_p("compton_shift", "Compton wavelength shift (h/(m_e*c))*(1 - cos(angle)) in m, scattering angle in degrees: compton_shift(angle)", 1, "compton_shift(180) => 4.852620477×10^-12")
def compton_shift(angle):
    r = _pang(angle, 0, 180)
    return _K("const_h") / (_K("const_me") * _K("const_c")) * (1 - math.cos(r))


@_p("bohr_energy", "Energy level of a hydrogen-like atom -13.605693123*Z^2/n^2 in eV (n whole): bohr_energy(n, Z)", 2, "bohr_energy(2, 1) => -3.401423281")
def bohr_energy(n, Z):
    _ppos(n, Z)
    if n != int(n):
        raise MathError("n must be a whole number")
    return -13.605693123 * Z * Z / (n * n)


@_p("rydberg_wavelength", "Wavelength of the hydrogen line n2 -> n1 (n2 > n1 >= 1, whole) in m: rydberg_wavelength(n1, n2)", 2, "rydberg_wavelength(1, 2) => 0.0000001215022734")
def rydberg_wavelength(n1, n2):
    if n1 != int(n1) or n2 != int(n2) or n1 < 1 or n2 <= n1:
        raise MathError("need whole numbers with n2 > n1 >= 1")
    return 1 / (_K("const_ryd") * (1 / n1 ** 2 - 1 / n2 ** 2))


@_p("mass_energy", "Rest energy m*c^2 (J): mass_energy(m)", 1, "mass_energy(1) => 8.987551787×10^16")
def mass_energy(m):
    _pnn(m)
    return m * _K("const_c") ** 2


def _gamma(v):
    c = _K("const_c")
    if abs(v) >= c:
        raise MathError("speed must be below the speed of light")
    return 1 / math.sqrt(1 - (v / c) ** 2)


@_p("lorentz_gamma", "Lorentz factor 1/sqrt(1 - v^2/c^2), v in m/s: lorentz_gamma(v)", 1, "lorentz_gamma(0.6*const_c) => 1.25")
def lorentz_gamma(v):
    return _gamma(v)


@_p("time_dilation", "Dilated time gamma*t (same unit as t): time_dilation(t, v)", 2, "time_dilation(10, 0.6*const_c) => 12.5")
def time_dilation(t, v):
    return _gamma(v) * t


@_p("length_contraction", "Contracted length L/gamma (same unit as L): length_contraction(L, v)", 2, "length_contraction(10, 0.6*const_c) => 8")
def length_contraction(L, v):
    return L / _gamma(v)


@_p("rel_momentum", "Relativistic momentum gamma*m*v (kg.m/s): rel_momentum(m, v)", 2, "rel_momentum(1, 0.6*const_c) => 224844343.5")
def rel_momentum(m, v):
    _pnn(m)
    return _gamma(v) * m * v


@_p("rel_energy", "Total relativistic energy gamma*m*c^2 (J): rel_energy(m, v)", 2, "rel_energy(1, 0.6*const_c) => 1.123443973×10^17")
def rel_energy(m, v):
    _pnn(m)
    return _gamma(v) * m * _K("const_c") ** 2


@_p("half_life_remaining", "Amount left after time t, N0*2^(-t/th) (t and th in the same unit): half_life_remaining(N0, t, th)", 3, "half_life_remaining(80, 10, 5) => 20")
def half_life_remaining(N0, t, th):
    _pnn(N0, t)
    _ppos(th)
    return N0 * 2.0 ** (-t / th)


@_p("decay_constant", "Decay constant ln(2)/th (per unit of th): decay_constant(th)", 1, "decay_constant(ln(2)) => 1")
def decay_constant(th):
    _ppos(th)
    return math.log(2) / th


@_p("activity", "Activity lambda*N, with lambda = ln(2)/th (decays per unit of th): activity(N, th)", 2, "activity(100, ln(2)) => 100")
def activity(N, th):
    _pnn(N)
    _ppos(th)
    return math.log(2) / th * N


# ---------- astronomy ----------
@_p("hill_sphere", "Hill sphere radius a*(m/(3*M))^(1/3), orbit radius a, small mass m, large mass M: hill_sphere(a, m, M)", 3, "hill_sphere(100, 3, 8) => 50", _PA)
def hill_sphere(a, m, M):
    _ppos(a, m, M)
    return a * (m / (3 * M)) ** (1 / 3)


@_p("roche_limit", "Fluid Roche limit 2.44*R*(rho_m/rho_s)^(1/3): R = radius of the large body, rho_m its density, rho_s the satellite's density: roche_limit(R, rho_m, rho_s)", 3, "roche_limit(1, 8, 1) => 4.88", _PA)
def roche_limit(R, rho_m, rho_s):
    _ppos(R, rho_m, rho_s)
    return 2.44 * R * (rho_m / rho_s) ** (1 / 3)


@_p("surface_gravity", "Surface gravity G*M/R^2 (m/s^2), M in kg, R in m: surface_gravity(M, R)", 2, "surface_gravity(5.972e24, 6.371e6) => 9.819973426", _PA)
def surface_gravity(M, R):
    _ppos(M, R)
    return _K("const_G") * M / (R * R)


@_p("parallax_distance", "Distance in parsecs from a parallax in arcseconds, 1/p: parallax_distance(arcsec)", 1, "parallax_distance(0.5) => 2", _PA)
def parallax_distance(arcsec):
    _ppos(arcsec)
    return 1 / arcsec


@_p("hubble_velocity", "Recession speed H0*d in km/s for a distance d in Mpc, with H0 = 70 km/s/Mpc: hubble_velocity(d)", 1, "hubble_velocity(100) => 7000", _PA)
def hubble_velocity(d):
    _pnn(d)
    return 70.0 * d


@_p("distance_modulus", "Distance in parsecs from apparent magnitude m and absolute magnitude M, 10^((m - M + 5)/5): distance_modulus(m, M)", 2, "distance_modulus(5, 0) => 100", _PA)
def distance_modulus(m, M):
    return 10.0 ** ((m - M + 5) / 5)


@_p("luminosity_bb", "Black-body luminosity 4*pi*R^2*sigma*T^4 (W), R in m, T in kelvin: luminosity_bb(R, T)", 2, "luminosity_bb(6.957e8, 5772) => 3.827990903×10^26", _PA)
def luminosity_bb(R, T):
    _ppos(R, T)
    return 4 * math.pi * R * R * _K("const_sigma") * T ** 4
