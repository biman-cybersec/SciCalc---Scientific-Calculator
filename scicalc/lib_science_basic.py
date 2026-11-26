"""Physics, complex numbers, matrices (first versions)

Module 14 of 47.  Taken from lines 3220-3468 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_science_basic"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .arithmetic import Lst, Mat, ar_div, ar_mul
from .lib_powers_rounding import _whole, sq

# ---------- 7q. Physics, Mechanics & Electronics ----------

CAT_PHYSICS = "Physics & Engineering"


@register("momentum", CAT_PHYSICS, "Linear momentum: momentum(mass, velocity)", args=2, exact=True, example="momentum(10, 5) => 50")
def momentum(mass, velocity):
    if mass < 0:
        raise MathError("mass cannot be negative")
    return ar_mul(mass, velocity)


@register("grav_potential", CAT_PHYSICS, "Gravitational potential energy: grav_potential(mass, height)", args=2, example="grav_potential(10, 10) => 980.665")
def grav_potential(mass, height):
    if mass < 0 or height < 0:
        raise MathError("mass and height cannot be negative")
    # Uses standard gravity const_g0 (9.80665)
    return ar_mul(ar_mul(mass, 9.80665), height)


@register("centripetal_force", CAT_PHYSICS, "Centripetal force: centripetal_force(mass, velocity, radius)", args=3, example="centripetal_force(2, 3, 1) => 18")
def centripetal_force(mass, velocity, radius):
    if mass < 0 or radius <= 0:
        raise MathError("invalid mass or radius")
    return ar_div(ar_mul(mass, sq(velocity)), radius)


@register("ohm_current", CAT_PHYSICS, "Ohm's Law - Current (I = V / R): ohm_current(voltage, resistance)", args=2, example="ohm_current(12, 4) => 3")
def ohm_current(voltage, resistance):
    if resistance == 0:
        raise MathError("resistance cannot be zero")
    return ar_div(voltage, resistance)


@register("ohm_voltage", CAT_PHYSICS, "Ohm's Law - Voltage (V = I * R): ohm_voltage(current, resistance)", args=2, exact=True, example="ohm_voltage(2, 6) => 12")
def ohm_voltage(current, resistance):
    return ar_mul(current, resistance)


@register("ohm_resistance", CAT_PHYSICS, "Ohm's Law - Resistance (R = V / I): ohm_resistance(voltage, current)", args=2, example="ohm_resistance(12, 3) => 4")
def ohm_resistance(voltage, current):
    if current == 0:
        raise MathError("current cannot be zero")
    return ar_div(voltage, current)


@register("electric_power", CAT_PHYSICS, "Electrical power (P = V * I): electric_power(voltage, current)", args=2, example="electric_power(12, 2) => 24")
def electric_power(voltage, current):
    return ar_mul(voltage, current)


@register("wave_speed", CAT_PHYSICS, "Wave speed (v = f * lambda): wave_speed(frequency, wavelength)", args=2, example="wave_speed(50, 2) => 100")
def wave_speed(frequency, wavelength):
    if frequency < 0 or wavelength < 0:
        raise MathError("frequency and wavelength cannot be negative")
    return ar_mul(frequency, wavelength)


# ---------- 7r. Complex Numbers & Polar Coordinates ----------

CAT_COMPLEX = "Complex Numbers"


@register("c_mag", CAT_COMPLEX, "Magnitude (absolute value) of complex number a+bi: c_mag(a, b)", args=2, example="c_mag(3, 4) => 5")
def c_mag(a, b):
    return math.hypot(a, b)


@register("c_arg", CAT_COMPLEX, "Argument (angle) of complex number a+bi in current angle mode: c_arg(a, b)", args=2, angle_out=True, example="c_arg(1, 1) => 45")
def c_arg(a, b):
    if a == 0 and b == 0:
        raise MathError("argument of 0+0i is undefined")
    return math.atan2(b, a)


@register("c_conj", CAT_COMPLEX, "Complex conjugate of a+bi: c_conj(a, b)", args=2, exact=True, example="c_conj(3, 4) => 3-4i")
def c_conj(a, b):
    from .lib_complex_c import _cstr  # imported here because lib_complex_c is loaded after this module
    return _cstr(complex(a, -b))


@register("c_add", CAT_COMPLEX, "Add two complex numbers (a+bi) + (c+di): c_add(a, b, c, d)", args=4, exact=True, example="c_add(1, 2, 3, 4) => 4+6i")
def c_add(a, b, c, d):
    from .lib_complex_c import _cstr  # imported here because lib_complex_c is loaded after this module
    return _cstr(complex(a + c, b + d))


@register("c_mul", CAT_COMPLEX, "Multiply two complex numbers (a+bi)*(c+di): c_mul(a, b, c, d)", args=4, exact=True, example="c_mul(1, 2, 3, 4) => -5+10i")
def c_mul(a, b, c, d):
    from .lib_complex_c import _cstr  # imported here because lib_complex_c is loaded after this module
    return _cstr(complex(a * c - b * d, a * d + b * c))


@register("polar2rect_re", CAT_COMPLEX, "Real part from polar coordinates (r, theta): polar2rect_re(r, theta)", args=2, example="polar2rect_re(5, 53.13010235) => 3")
def polar2rect_re(r, theta):
    rad = math.radians(theta)
    return r * math.cos(rad)


@register("polar2rect_im", CAT_COMPLEX, "Imaginary part from polar coordinates (r, theta): polar2rect_im(r, theta)", args=2, example="polar2rect_im(5, 53.13010235) => 4")
def polar2rect_im(r, theta):
    rad = math.radians(theta)
    return r * math.sin(rad)

# ---------- 7s. Advanced Matrix & Linear Algebra ----------

CAT_MATRIX = "Advanced Matrix & Linear Algebra"


@register("mat_mul2", CAT_MATRIX, "Multiply two 2x2 matrices: mat_mul2(a, b, c, d, e, f, g, h) for [[a,b],[c,d]] * [[e,f],[g,h]]", args=8, exact=True, example="mat_mul2(1, 2, 3, 4, 5, 6, 7, 8) => {{19, 22}, {43, 50}}")
def mat_mul2(a, b, c, d, e, f, g, h):
    # Matrix 1: [[a, b], [c, d]]
    # Matrix 2: [[e, f], [g, h]]
    r1c1 = a * e + b * g
    r1c2 = a * f + b * h
    r2c1 = c * e + d * g
    r2c2 = c * f + d * h
    
    return Mat(((r1c1, r1c2), (r2c1, r2c2)))


@register("trace2", CAT_MATRIX, "Trace of a 2x2 matrix (sum of main diagonal): trace2(a, b, c, d) for [[a,b],[c,d]]", args=4, exact=True, example="trace2(1, 2, 3, 4) => 5")
def trace2(a, b, c, d):
    res = a + d
    return int(res) if float(res).is_integer() else res


@register("cross3", CAT_MATRIX, "Cross product of two 3D vectors u x v: cross3(ux, uy, uz, vx, vy, vz)", args=6, exact=True, example="cross3(1, 0, 0, 0, 1, 0) => {0, 0, 1}")
def cross3(ux, uy, uz, vx, vy, vz):
    cx = uy * vz - uz * vy
    cy = uz * vx - ux * vz
    cz = ux * vy - uy * vx
    
    return Lst((cx, cy, cz))


@register("angle_vectors2", CAT_MATRIX, "Angle between two 2D vectors in current angle mode: angle_vectors2(ux, uy, vx, vy)", args=4, angle_out=True, example="angle_vectors2(1, 0, 0, 1) => 90")
def angle_vectors2(ux, uy, vx, vy):
    dot_prod = ux * vx + uy * vy
    mag_u = math.hypot(ux, uy)
    mag_v = math.hypot(vx, vy)
    
    if mag_u == 0 or mag_v == 0:
        raise MathError("cannot find angle with a zero vector")
        
    cos_theta = max(-1.0, min(1.0, dot_prod / (mag_u * mag_v)))
    return math.acos(cos_theta)


# ---------- Advanced Matrix & Linear Algebra Expansions ----------

@register("mat_transpose2", CAT_MATRIX, "Transpose of a 2x2 matrix: mat_transpose2(a, b, c, d)", args=4, exact=True, example="mat_transpose2(1, 2, 3, 4) => {{1, 3}, {2, 4}}")
def mat_transpose2(a, b, c, d):
    return Mat(((a, c), (b, d)))


@register("mat_add2", CAT_MATRIX, "Add two 2x2 matrices: mat_add2(a11, a12, a21, a22, b11, b12, b21, b22)", args=8, exact=True, example="mat_add2(1, 2, 3, 4, 5, 6, 7, 8) => {{6, 8}, {10, 12}}")
def mat_add2(a11, a12, a21, a22, b11, b12, b21, b22):
    r1c1, r1c2 = a11 + b11, a12 + b12
    r2c1, r2c2 = a21 + b21, a22 + b22
    return Mat(((r1c1, r1c2), (r2c1, r2c2)))


@register("mat_scalar_mul2", CAT_MATRIX, "Scalar multiplication of a 2x2 matrix: mat_scalar_mul2(k, a, b, c, d)", args=5, exact=True, example="mat_scalar_mul2(2, 1, 2, 3, 4) => {{2, 4}, {6, 8}}")
def mat_scalar_mul2(k, a, b, c, d):
    ra, rb, rc, rd = k * a, k * b, k * c, k * d
    return Mat(((ra, rb), (rc, rd)))


@register("mat_pow2", CAT_MATRIX, "Power of a 2x2 matrix A^n: mat_pow2(a, b, c, d, n)", args=5, exact=True, example="mat_pow2(1, 1, 0, 1, 3) => {{1, 3}, {0, 1}}")
def mat_pow2(a, b, c, d, n):
    n_val = _whole(n, "n")
    if n_val < 0:
        raise MathError("matrix power cannot be negative in this implementation")
    
    # Identity matrix for n = 0
    res_a, res_b, res_c, res_d = 1, 0, 0, 1
    curr_a, curr_b, curr_c, curr_d = a, b, c, d
    
    for _ in range(n_val):
        ra = res_a * curr_a + res_b * curr_c
        rb = res_a * curr_b + res_b * curr_d
        rc = res_c * curr_a + res_d * curr_c
        rd = res_c * curr_b + res_d * curr_d
        res_a, res_b, res_c, res_d = ra, rb, rc, rd
        
    return Mat(((res_a, res_b), (res_c, res_d)))


@register("mat_rank2", CAT_MATRIX, "Rank of a 2x2 matrix: mat_rank2(a, b, c, d)", args=4, exact=True, example="mat_rank2(1, 2, 2, 4) => 1")
def mat_rank2(a, b, c, d):
    det = a * d - b * c
    if det != 0:
        return 2
    if a != 0 or b != 0 or c != 0 or d != 0:
        return 1
    return 0


@register("eigenvalues2", CAT_MATRIX, "Eigenvalues of a 2x2 matrix: eigenvalues2(a, b, c, d)", args=4, example="eigenvalues2(4, 1, 2, 3) => 5")
def eigenvalues2(a, b, c, d):
    trace = a + d
    det = a * d - b * c
    disc = trace ** 2 - 4 * det
    if disc < 0:
        raise MathError("eigenvalues are complex")
    lam1 = (trace + math.sqrt(disc)) / 2
    lam2 = (trace - math.sqrt(disc)) / 2
    res = max(lam1, lam2) # returns principal / max eigenvalue for simple check or display
    return int(res) if float(res).is_integer() else res


@register("spectral_radius2", CAT_MATRIX, "Spectral radius of a 2x2 matrix: spectral_radius2(a, b, c, d)", args=4, example="spectral_radius2(4, 1, 2, 3) => 5")
def spectral_radius2(a, b, c, d):
    trace = a + d
    det = a * d - b * c
    disc = trace ** 2 - 4 * det
    if disc < 0:
        # Magnitude of complex conjugate eigenvalues sqrt(det)
        sr = math.sqrt(abs(det))
    else:
        lam1 = abs((trace + math.sqrt(disc)) / 2)
        lam2 = abs((trace - math.sqrt(disc)) / 2)
        sr = max(lam1, lam2)
    return int(sr) if float(sr).is_integer() else sr


@register("is_idempotent2", CAT_MATRIX, "Check if 2x2 matrix is idempotent (A^2 = A): is_idempotent2(a, b, c, d)", args=4, exact=True, example="is_idempotent2(3, -6, 1, -2) => 1")
def is_idempotent2(a, b, c, d):
    # A^2 = A
    a2 = a * a + b * c
    b2 = a * b + b * d
    c2 = c * a + d * c
    d2 = c * b + d * d
    tolerance = 1e-9
    if abs(a2 - a) < tolerance and abs(b2 - b) < tolerance and abs(c2 - c) < tolerance and abs(d2 - d) < tolerance:
        return 1
    return 0


@register("is_nilpotent2", CAT_MATRIX, "Check if 2x2 matrix is nilpotent (A^2 = 0): is_nilpotent2(a, b, c, d)", args=4, exact=True, example="is_nilpotent2(1, -1, 1, -1) => 1")
def is_nilpotent2(a, b, c, d):
    a2 = a * a + b * c
    b2 = a * b + b * d
    c2 = c * a + d * c
    d2 = c * b + d * d
    tolerance = 1e-9
    if abs(a2) < tolerance and abs(b2) < tolerance and abs(c2) < tolerance and abs(d2) < tolerance:
        return 1
    return 0
