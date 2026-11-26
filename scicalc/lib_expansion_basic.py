"""Astronomy, ML, thermodynamics, acoustics, expansions 1-6

Module 15 of 47.  Taken from lines 3469-3997 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_expansion_basic"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .arithmetic import Mat
from .lib_powers_rounding import _whole
from .lib_numtheory_basic import isprime

# ---------- 7t. Astronomy & Orbital Mechanics ----------

CAT_ASTRO = "Astronomy & Orbital Mechanics"

# Standard CODATA constants for self-contained accuracy
_G_CONST = 6.67430e-11       # Gravitational constant (m^3 kg^-1 s^-2)
_C_CONST = 299792458.0       # Speed of light in vacuum (m/s)
_AU_METERS = 149597870700.0  # Astronomical Unit (m)


@register("grav_force", CAT_ASTRO, "Newton's universal gravitational force (N): grav_force(m1, m2, distance)", args=3, example="grav_force(1e10, 1e10, 100) => 667430")
def grav_force(m1, m2, distance):
    if m1 < 0 or m2 < 0 or distance <= 0:
        raise MathError("masses must be non-negative and distance must be positive")
    return (_G_CONST * m1 * m2) / (distance ** 2)


@register("escape_velocity", CAT_ASTRO, "Escape velocity from a celestial body (m/s): escape_velocity(mass, radius)", args=2, example="escape_velocity(5.972e24, 6371000) => 11185.97789")
def escape_velocity(mass, radius):
    if mass < 0 or radius <= 0:
        raise MathError("mass must be non-negative and radius must be positive")
    return math.sqrt((2.0 * _G_CONST * mass) / radius)


@register("orbital_velocity", CAT_ASTRO, "Circular orbital speed at radius r (m/s): orbital_velocity(mass, radius)", args=2, example="orbital_velocity(5.972e24, 6771000) => 7672.490413")
def orbital_velocity(mass, radius):
    if mass < 0 or radius <= 0:
        raise MathError("mass must be non-negative and radius must be positive")
    return math.sqrt((_G_CONST * mass) / radius)


@register("orbital_period", CAT_ASTRO, "Orbital period via Kepler's Third Law (seconds): orbital_period(mass, radius)", args=2, example="orbital_period(5.972e24, 6771000) => 5544.933317")
def orbital_period(mass, radius):
    if mass <= 0 or radius <= 0:
        raise MathError("mass and radius must be positive")
    return 2.0 * math.pi * math.sqrt((radius ** 3) / (_G_CONST * mass))


@register("schwarzschild_radius", CAT_ASTRO, "Event horizon radius of a non-rotating black hole (m): schwarzschild_radius(mass)", args=1, example="schwarzschild_radius(1.9885e30) => 2953.383939")
def schwarzschild_radius(mass):
    if mass < 0:
        raise MathError("mass cannot be negative")
    return (2.0 * _G_CONST * mass) / (_C_CONST ** 2)


@register("au2km", CAT_ASTRO, "Convert Astronomical Units (AU) to kilometers: au2km(au)", args=1, example="au2km(1) => 149597870.7")
def au2km(au):
    return (au * _AU_METERS) / 1000.0


# ---------- 7u. Machine Learning & Special Math ----------

CAT_ML = "Machine Learning & Special Math"


@register("sigmoid", CAT_ML, "Sigmoid activation function 1 / (1 + e^-x): sigmoid(x)", args=1, example="sigmoid(0) => 0.5")
def sigmoid(x):
    if x < -709:
        return 0.0
    if x > 709:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


@register("relu", CAT_ML, "Rectified Linear Unit (ReLU) max(0, x): relu(x)", args=1, exact=True, example="relu(5) => 5")
def relu(x):
    res = max(0.0, x)
    return int(res) if float(res).is_integer() else res


@register("leaky_relu", CAT_ML, "Leaky ReLU max(alpha*x, x) with default alpha=0.01: leaky_relu(x)", args=1, example="leaky_relu(-5) => -0.05")
def leaky_relu(x, alpha=0.01):
    return alpha * x if x < 0 else x


@register("sinc", CAT_ML, "Unnormalized sinc function sin(x)/x (x in radians): sinc(x)", args=1, example="sinc(0) => 1")
def sinc(x):
    if x == 0:
        return 1.0
    return math.sin(x) / x if x != 0 else 1.0


@register("logistic_growth", CAT_ML, "Logistic growth curve L / (1 + k*e^(-r*t)): logistic_growth(L, k, r, t)", args=4, example="logistic_growth(100, 9, 1, 0) => 10")
def logistic_growth(L, k, r, t):
    exponent = -r * t
    if exponent > 709:
        return 0.0
    return L / (1.0 + k * math.exp(exponent))


# ---------- 7v. Advanced Statistics & Probability ----------

CAT_ADV_STATS = "Advanced Statistics & Probability"


@register("sample_variance", CAT_ADV_STATS, "Sample variance of a dataset: sample_variance(x1, x2, ...)", args=(1, 100), example="sample_variance(2, 4, 4, 4, 5, 5, 7, 9) => 4.571428571")
def sample_variance(*args):
    if len(args) < 2:
        raise MathError("sample variance requires at least 2 values")
    mean_val = sum(args) / len(args)
    sq_diff_sum = sum((x - mean_val) ** 2 for x in args)
    return sq_diff_sum / (len(args) - 1)


@register("sample_stdev", CAT_ADV_STATS, "Sample standard deviation of a dataset: sample_stdev(x1, x2, ...)", args=(1, 100), example="sample_stdev(2, 4, 4, 4, 5, 5, 7, 9) => 2.138089935")
def sample_stdev(*args):
    return math.sqrt(sample_variance(*args))


@register("standard_error", CAT_ADV_STATS, "Standard error of the mean: standard_error(x1, x2, ...)", args=(1, 100), example="standard_error(2, 4, 4, 4, 5, 5, 7, 9) => 0.755928946")
def standard_error(*args):
    n = len(args)
    if n == 0:
        raise MathError("standard error requires at least 1 value")
    if n < 2:
        raise MathError("standard error requires at least 2 values")
    return sample_stdev(*args) / math.sqrt(n)


@register("z_score", CAT_ADV_STATS, "Z-score of value x given mean and stdev: z_score(x, mean, stdev)", args=3, exact=True, example="z_score(85, 75, 5) => 2")
def z_score(x, mean, stdev):
    if stdev == 0:
        raise MathError("standard deviation cannot be zero")
    res = (x - mean) / stdev
    return int(res) if float(res).is_integer() else res


@register("binomial_pmf", CAT_ADV_STATS, "Binomial probability P(X = k): binomial_pmf(n, k, p)", args=3, example="binomial_pmf(10, 3, 0.5) => 0.1171875")
def binomial_pmf(n, k, p):
    if not (0 <= p <= 1):
        raise MathError("probability p must be between 0 and 1")
    if not (0 <= k <= n):
        return 0.0
    comb = math.comb(int(n), int(k))
    return comb * (p ** k) * ((1.0 - p) ** (n - k))


# ---------- 7w. Financial & Actuarial Expansions ----------

CAT_FIN_ADV = "Financial & Actuarial"


@register("continuous_compounding", CAT_FIN_ADV, "Continuous compounding future value P*e^(r*t): continuous_compounding(principal, rate, time)", args=3, example="continuous_compounding(1000, 0.05, 2) => 1105.170918")
def continuous_compounding(principal, rate, time):
    if principal < 0 or time < 0:
        raise MathError("principal and time must be non-negative")
    return principal * math.exp(rate * time)


@register("annuity_fv", CAT_FIN_ADV, "Future value of an ordinary annuity: annuity_fv(pmt, rate, periods)", args=3, example="annuity_fv(100, 0.05, 10) => 1257.789254")
def annuity_fv(pmt, r, n):
    if r == 0:
        return pmt * n
    if n < 0:
        raise MathError("periods cannot be negative")
    return pmt * (((1.0 + r) ** n - 1.0) / r)


@register("annuity_pv", CAT_FIN_ADV, "Present value of an ordinary annuity: annuity_pv(pmt, rate, periods)", args=3, example="annuity_pv(100, 0.05, 10) => 772.1734929")
def annuity_pv(pmt, r, n):
    if r == 0:
        return pmt * n
    if n < 0:
        raise MathError("periods cannot be negative")
    return pmt * ((1.0 - (1.0 + r) ** (-n)) / r)


# ---------- 7x. Signal Processing & Fourier Helpers ----------

CAT_SIGNAL = "Signal Processing & Fourier"


@register("snr_db", CAT_SIGNAL, "Signal-to-Noise Ratio in decibels (dB): snr_db(signal_power, noise_power)", args=2, example="snr_db(100, 1) => 20")
def snr_db(signal, noise):
    if signal <= 0 or noise <= 0:
        raise MathError("signal and noise power must be positive")
    res = 10.0 * math.log10(signal / noise)
    return int(res) if float(res).is_integer() else res


@register("nyquist_frequency", CAT_SIGNAL, "Nyquist frequency given sample rate: nyquist_frequency(sample_rate)", args=1, example="nyquist_frequency(44100) => 22050")
def nyquist_frequency(sample_rate):
    if sample_rate < 0:
        raise MathError("sample rate cannot be negative")
    res = sample_rate / 2.0
    return int(res) if float(res).is_integer() else res


# ---------- 7y. Thermodynamics & Fluid Mechanics ----------

CAT_THERMO = "Thermodynamics & Fluids"

# Universal Gas Constant R in J/(mol·K)
_R_GAS_CONST = 8.314462618


@register("ideal_pressure", CAT_THERMO, "Calculate pressure using Ideal Gas Law P = nRT/V: ideal_pressure(n, T, V)", args=3, example="ideal_pressure(1, 300, 0.0224) => 111354.4101")
def ideal_pressure(n, T, V):
    if n < 0 or T < 0 or V <= 0:
        raise MathError("moles and temperature must be non-negative, volume must be positive")
    res = (n * _R_GAS_CONST * T) / V
    return int(res) if float(res).is_integer() else res


@register("reynolds_number", CAT_THERMO, "Calculate Reynolds number Re = (rho * v * L) / mu: reynolds_number(density, velocity, length, viscosity)", args=4, example="reynolds_number(998, 2, 0.1, 0.001) => 199600")
def reynolds_number(density, velocity, length, viscosity):
    if density < 0 or velocity < 0 or length < 0 or viscosity <= 0:
        raise MathError("density, velocity, length must be non-negative; dynamic viscosity must be positive")
    res = (density * velocity * length) / viscosity
    return int(res) if float(res).is_integer() else res


@register("heat_transfer", CAT_THERMO, "Calculate heat energy Q = m * c * dT: heat_transfer(mass, specific_heat, delta_temp)", args=3, example="heat_transfer(2, 4184, 50) => 418400")
def heat_transfer(mass, specific_heat, delta_temp):
    if mass < 0 or specific_heat < 0:
        raise MathError("mass and specific heat capacity must be non-negative")
    res = mass * specific_heat * delta_temp
    return int(res) if float(res).is_integer() else res


@register("thermal_expansion", CAT_THERMO, "Linear thermal expansion dL = alpha * L0 * dT: thermal_expansion(alpha, length, delta_temp)", args=3, example="thermal_expansion(0.0000231, 1, 50) => 0.001155")
def thermal_expansion(alpha, length, delta_temp):
    if length < 0:
        raise MathError("initial length must be non-negative")
    return alpha * length * delta_temp


@register("sound_speed_air", CAT_THERMO, "Approximate speed of sound in air at temperature T (Celsius): sound_speed_air(temp_c)", args=1, example="sound_speed_air(20) => 343.2146227")
def sound_speed_air(temp_c):
    if temp_c < -273.15:
        raise MathError("temperature cannot be below absolute zero (-273.15 C)")
    return 331.3 * math.sqrt(1.0 + (temp_c / 273.15))


# ---------- 7z. Probability Distributions & Statistical Inference ----------

CAT_PROB = "Probability & Statistics"

@register("norm_pdf", CAT_PROB, "Normal probability density function: norm_pdf(x, mean, stdev)", args=3, example="norm_pdf(0, 0, 1) => 0.3989422804")
def norm_pdf(x, mean, stdev):
    if stdev <= 0:
        raise MathError("standard deviation must be positive")
    variance = stdev ** 2
    coef = 1.0 / (stdev * math.sqrt(2.0 * math.pi))
    exponent = -((x - mean) ** 2) / (2.0 * variance)
    return coef * math.exp(exponent)

@register("norm_cdf", CAT_PROB, "Normal cumulative distribution function: norm_cdf(x, mean, stdev)", args=3, example="norm_cdf(0, 0, 1) => 0.5")
def norm_cdf(x, mean, stdev):
    if stdev <= 0:
        raise MathError("standard deviation must be positive")
    return 0.5 * (1.0 + math.erf((x - mean) / (stdev * math.sqrt(2.0))))

@register("poisson_pmf", CAT_PROB, "Poisson probability P(X = k): poisson_pmf(lambda, k)", args=2, exact=True, example="poisson_pmf(3, 2) => 0.2240418077")
def poisson_pmf(lam, k):
    k_val = _whole(k, "k")
    if lam <= 0 or k_val < 0:
        raise MathError("lambda must be positive and k must be non-negative")
    return (math.exp(-lam) * (lam ** k_val)) / math.factorial(k_val)

@register("z_test_stat", CAT_PROB, "One-sample z-test statistic: z_test_stat(sample_mean, pop_mean, pop_stdev, n)", args=4, example="z_test_stat(102, 100, 15, 30) => 0.7302967433")
def z_test_stat(sample_mean, pop_mean, pop_stdev, n):
    if pop_stdev <= 0 or n <= 0:
        raise MathError("population stdev and sample size n must be positive")
    return (sample_mean - pop_mean) / (pop_stdev / math.sqrt(n))


# ---------- 7aa. Advanced Matrix & Linear Algebra Expansions ----------

CAT_MATRIX_ADV = "Advanced Matrix & Linear Algebra"

@register("det3", CAT_MATRIX_ADV, "Determinant of a 3x3 matrix: det3(a11, a12, a13, a21, a22, a23, a31, a32, a33)", args=9, exact=True, example="det3(1, 2, 3, 0, 1, 4, 5, 6, 0) => 1")
def det3(a, b, c, d, e, f, g, h, i):
    res = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    return int(res) if float(res).is_integer() else res

@register("mat_inv2", CAT_MATRIX_ADV, "Inverse of a 2x2 matrix {{a, b}, {c, d}}: mat_inv2(a, b, c, d)", args=4, example="mat_inv2(4, 7, 2, 6) => {{0.6, -0.7}, {-0.2, 0.4}}")
def mat_inv2(a, b, c, d):
    det = a * d - b * c
    if det == 0:
        raise MathError("matrix is singular and non-invertible")
    inv_det = 1.0 / det
    ra = d * inv_det
    rb = -b * inv_det
    rc = -c * inv_det
    rd = a * inv_det
    
    return Mat(((ra, rb), (rc, rd)))

@register("vector_projection", CAT_MATRIX_ADV, "Vector projection of u onto v (returns scalar component factor or length): vector_projection(ux, uy, vx, vy)", args=4, example="vector_projection(3, 4, 1, 0) => 3")
def vector_projection(ux, uy, vx, vy):
    dot = ux * vx + uy * vy
    mag_v_sq = vx * vx + vy * vy
    if mag_v_sq == 0:
        raise MathError("cannot project onto zero vector")
    res = dot / mag_v_sq
    return int(res) if float(res).is_integer() else res


# ---------- 7ab. Acoustics, Optics & Photonics ----------

CAT_OPTICS = "Acoustics & Optics"

@register("snells_law", CAT_OPTICS, "Calculate refraction angle theta2 (in current angle mode): snells_law(n1, n2, theta1)", args=3, angle_out=True, example="snells_law(1.0, 1.5, 30) => 19.47122063")
def snells_law(n1, n2, theta1_deg):
    if n2 <= 0:
        raise MathError("refractive index n2 must be positive")
    rad1 = math.radians(theta1_deg)
    sin_theta2 = (n1 / n2) * math.sin(rad1)
    if abs(sin_theta2) > 1.0:
        raise MathError("total internal reflection occurs (no refraction angle)")
    return math.asin(sin_theta2)

@register("critical_angle", CAT_OPTICS, "Critical angle for total internal reflection (in current angle mode): critical_angle(n1, n2)", args=2, angle_out=True, example="critical_angle(1.5, 1.0) => 41.8103149")
def critical_angle(n1, n2):
    if n1 <= 0 or n2 <= 0:
        raise MathError("refractive indices must be positive")
    ratio = n2 / n1
    if ratio > 1.0:
        raise MathError("no critical angle when n1 <= n2")
    return math.asin(ratio)

@register("photon_energy", CAT_OPTICS, "Photon energy E = h * f: photon_energy(frequency)", args=1, example="photon_energy(5e14) => 3.313035075×10^-19")
def photon_energy(freq):
    if freq < 0:
        raise MathError("frequency cannot be negative")
    return freq * 6.62607015e-34

@register("sound_intensity_level", CAT_OPTICS, "Sound intensity level in decibels (dB): sound_intensity_level(intensity, reference_intensity)", args=2, example="sound_intensity_level(1e-6, 1e-12) => 60")
def sound_intensity_level(I, I0=1e-12):
    if I <= 0 or I0 <= 0:
        raise MathError("intensities must be positive")
    res = 10.0 * math.log10(I / I0)
    return int(res) if float(res).is_integer() else res


# ---------- 7ac. Chemical & Environmental Engineering ----------

CAT_CHEM = "Chemical & Environmental"

@register("ph_calc", CAT_CHEM, "Calculate pH from hydronium ion concentration [H+]: ph_calc(h_conc)", args=1, example="ph_calc(1e-7) => 7")
def ph_calc(h_conc):
    if h_conc <= 0:
        raise MathError("concentration must be positive")
    res = -math.log10(h_conc)
    return int(res) if float(res).is_integer() else res

@register("poh_calc", CAT_CHEM, "Calculate pOH from hydroxide ion concentration [OH-]: poh_calc(oh_conc)", args=1, example="poh_calc(1e-7) => 7")
def poh_calc(oh_conc):
    if oh_conc <= 0:
        raise MathError("concentration must be positive")
    res = -math.log10(oh_conc)
    return int(res) if float(res).is_integer() else res

@register("henderson_hasselbalch", CAT_CHEM, "Henderson-Hasselbalch equation for buffer pH: henderson_hasselbalch(pka, base_conc, acid_conc)", args=3, example="henderson_hasselbalch(4.76, 0.1, 0.1) => 4.76")
def henderson_hasselbalch(pka, base, acid):
    if base <= 0 or acid <= 0:
        raise MathError("concentrations must be positive")
    return pka + math.log10(base / acid)

@register("molarity", CAT_CHEM, "Calculate solution molarity: molarity(moles_solute, volume_liters)", args=2, example="molarity(2, 0.5) => 4")
def molarity(moles, volume):
    if moles < 0 or volume <= 0:
        raise MathError("moles must be non-negative and volume must be positive")
    res = moles / volume
    return int(res) if float(res).is_integer() else res


# ---------- Additional Expansion: Categories 1 to 6 ----------

# 1. Physics, Mechanics & Astronomy
@register("kinetic_energy", "Physics & Engineering", "Kinetic energy KE = 0.5 * m * v^2: kinetic_energy(mass, velocity)", args=2, example="kinetic_energy(10, 5) => 125")
def kinetic_energy(mass, velocity):
    if mass < 0 or velocity < 0:
        raise MathError("mass and velocity cannot be negative")
    return 0.5 * mass * (velocity ** 2)


@register("spring_pe", "Physics & Engineering", "Elastic potential energy in a spring PE = 0.5 * k * x^2: spring_pe(k, displacement)", args=2, example="spring_pe(100, 0.1) => 0.5")
def spring_pe(k, displacement):
    if k < 0:
        raise MathError("spring constant cannot be negative")
    return 0.5 * k * (displacement ** 2)


@register("projectile_range", "Physics & Engineering", "Horizontal projectile range: projectile_range(velocity, angle_deg)", args=2, example="projectile_range(20, 45) => 40.78864852")
def projectile_range(v, angle_deg):
    if v < 0:
        raise MathError("velocity cannot be negative")
    rad = math.radians(angle_deg)
    return (v ** 2 * math.sin(2 * rad)) / 9.80665


@register("z_redshift", "Astronomy & Orbital Mechanics", "Cosmological redshift z = (obs - emit) / emit: z_redshift(observed, emitted)", args=2, example="z_redshift(600, 500) => 0.2")
def z_redshift(obs, emit):
    if emit <= 0:
        raise MathError("emitted wavelength must be positive")
    return (obs - emit) / emit


@register("synodic_period", "Astronomy & Orbital Mechanics", "Synodic period between two orbiting bodies: synodic_period(p1, p2)", args=2, example="synodic_period(365.25, 687) => 779.8811189")
def synodic_period(p1, p2):
    if p1 == 0 or p2 == 0:
        raise MathError("periods cannot be zero")
    return abs(1.0 / ((1.0 / p1) - (1.0 / p2)))


# 2. Advanced Mathematics & Number Theory
@register("mobius", "Combinatorics & Number Theory", "Möbius function mu(n): returns -1, 0, or 1", args=1, exact=True, example="mobius(30) => -1")
def mobius(n):
    n = _whole(n, "n")
    if n <= 0:
        raise MathError("n must be positive")
    if n == 1:
        return 1
    p, count, temp = 2, 0, n
    while p * p <= temp:
        if temp % p == 0:
            temp //= p
            count += 1
            if temp % p == 0:
                return 0
        p += 1
    if temp > 1:
        count += 1
    return -1 if count % 2 == 1 else 1


@register("next_prime", "Combinatorics & Number Theory", "Smallest prime number strictly greater than n", args=1, exact=True, example="next_prime(10) => 11")
def next_prime(n):
    n = _whole(n, "n")
    candidate = n + 1
    while isprime(candidate) == 0:
        candidate += 1
    return candidate


@register("erf", "Machine Learning & Special Math", "Gauss error function erf(x)", args=1, example="erf(1) => 0.8427007929")
def erf(x):
    return math.erf(x)


@register("soft_plus", "Machine Learning & Special Math", "Softplus activation function ln(1 + e^x): soft_plus(x)", args=1, example="soft_plus(0) => 0.6931471806")
def soft_plus(x):
    if x > 709:
        return x
    if x < -709:
        return 0.0
    return math.log(1.0 + math.exp(x))


# 3. Complex Numbers & Linear Algebra
@register("c_div", "Complex Numbers", "Complex division (a+bi) / (c+di): c_div(a, b, c, d)", args=4, example="c_div(1, 2, 3, 4) => 0.44+0.08i")
def c_div(a, b, c, d):
    from .lib_complex_c import _cstr  # imported here because lib_complex_c is loaded after this module
    denom = c*c + d*d
    if denom == 0:
        raise MathError("division by zero complex number")
    return _cstr(complex((a*c + b*d) / denom, (b*c - a*d) / denom))


@register("vector_proj3", "Advanced Matrix & Linear Algebra", "3D vector projection of u onto v: vector_proj3(ux, uy, uz, vx, vy, vz)", args=6, example="vector_proj3(1, 2, 3, 1, 0, 0) => 1")
def vector_proj3(ux, uy, uz, vx, vy, vz):
    dot = ux*vx + uy*vy + uz*vz
    mag_v_sq = vx*vx + vy*vy + vz*vz
    if mag_v_sq == 0:
        raise MathError("cannot project onto zero vector")
    res = dot / mag_v_sq
    return int(res) if float(res).is_integer() else res


# 4. Statistics, Probability & Finance
@register("skewness", "Statistics", "Sample skewness of dataset: skewness(x1, x2, ...)", args=(3, 100), example="skewness(1, 2, 3, 4, 10) => 1.697056275")
def skewness(*xs):
    n = len(xs)
    if n < 3:
        raise MathError("skewness requires at least 3 values")
    m = sum(xs) / n
    s = sample_stdev(*xs)
    if s == 0:
        return 0.0
    return (n / ((n - 1) * (n - 2))) * sum(((x - m) / s) ** 3 for x in xs)


@register("npv", "Financial", "Net Present Value: npv(discount_rate_pct, cf0, cf1, cf2, ...)", args=(2, 100), example="npv(10, -1000, 300, 400, 500) => -21.03681443")
def npv(rate, *cashflows):
    r = rate / 100.0
    total = 0.0
    for t, cf in enumerate(cashflows):
        total += cf / ((1.0 + r) ** t)
    return total


# 5. Optics, Acoustics & Thermodynamics
@register("lensmaker", "Acoustics & Optics", "Lensmaker's equation for focal length f: lensmaker(n, r1, r2)", args=3, example="lensmaker(1.5, 10, -10) => 10")
def lensmaker(n, r1, r2):
    if r1 == 0 or r2 == 0 or n <= 0:
        raise MathError("radii cannot be zero and refractive index must be positive")
    inv_f = (n - 1.0) * ((1.0 / r1) - (1.0 / r2))
    if inv_f == 0:
        raise MathError("focal length is infinite")
    return 1.0 / inv_f


@register("blackbody_power", "Thermodynamics & Fluids", "Total Stefan-Boltzmann radiative power P = sigma * A * T^4: blackbody_power(area, temp_k)", args=2, example="blackbody_power(1, 1000) => 56703.74419")
def blackbody_power(area, temp):
    if area < 0 or temp < 0:
        raise MathError("area and temperature cannot be negative")
    sigma = 5.670374419e-8
    return sigma * area * (temp ** 4)


# 6. Navigation & Everyday Calculations
@register("haversine_dist", "Daily Life", "Great-circle distance between two GPS coordinates (km): haversine_dist(lat1, lon1, lat2, lon2)", args=4, example="haversine_dist(51.5074, -0.1278, 48.8566, 2.3522) => 343.5560603")
def haversine_dist(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


@register("tip", "Daily Life", "Calculate tip amount given bill and tip percentage: tip(bill, tip_pct)", args=2, example="tip(50, 15) => 7.5")
def tip(bill, pct):
    if bill < 0 or pct < 0:
        raise MathError("bill and tip percentage cannot be negative")
    return bill * (pct / 100.0)
