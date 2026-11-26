"""Sprint 1A: special functions

Module 16 of 47.  Taken from lines 3998-4556 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_special_functions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import ArgumentError
from .registry import register

# ==============================================================================
# SPRINT 1 - BATCH 1A: SPECIAL FUNCTIONS (22 Functions)
# ==============================================================================

CAT_SPECIAL = "Special Functions"


def _gamma_inc_p(a, x):
    """Regularized lower incomplete gamma P(a, x) = gamma(a, x) / Gamma(a)."""
    if a <= 0 or x < 0:
        raise ValueError("Math ERROR")
    if x == 0:
        return 0.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap = a
        total = 1.0 / a
        delta = total
        for _ in range(300):
            ap += 1.0
            delta *= x / ap
            total += delta
            if abs(delta) < abs(total) * 1e-15:
                break
        return total * math.exp(-x + a * math.log(x) - gln)
    else:
        fpmin = 1e-300
        b = x + 1.0 - a
        c = 1.0 / fpmin
        d = 1.0 / b
        h = d
        for i in range(1, 300):
            an = -i * (i - a)
            b += 2.0
            d = an * d + b
            if abs(d) < fpmin:
                d = fpmin
            c = b + an / c
            if abs(c) < fpmin:
                c = fpmin
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-15:
                break
        q = math.exp(-x + a * math.log(x) - gln) * h
        return max(0.0, min(1.0, 1.0 - q))


def _betacf(a, b, x):
    """Continued fraction evaluation for regularized incomplete beta."""
    fpmin = 1e-300
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin:
        d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin:
            d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin:
            c = fpmin
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def _beta_inc(a, b, x):
    """Regularized incomplete beta function I_x(a, b)."""
    if a <= 0 or b <= 0 or x < 0 or x > 1:
        raise ValueError("Math ERROR")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    else:
        return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


@register("gamma_inc_p", CAT_SPECIAL, "Regularized lower incomplete gamma P(a, x) for a > 0, x >= 0", args=2, example="gamma_inc_p(2, 1) => 0.2642411177")
def gamma_inc_p(a, x):
    return _gamma_inc_p(float(a), float(x))


@register("beta_inc", CAT_SPECIAL, "Regularized incomplete beta I_x(a, b) for a > 0, b > 0, 0 <= x <= 1", args=3, example="beta_inc(2, 3, 0.5) => 0.6875")
def beta_inc(a, b, x):
    return _beta_inc(float(a), float(b), float(x))


@register("erf_comp", CAT_SPECIAL, "Complementary error function erfc(x) = 1 - erf(x)", args=1, example="erf_comp(0) => 1")
def erf_comp(x):
    return math.erfc(float(x))


@register("erf_inv", CAT_SPECIAL, "Inverse error function erfinv(y) for -1 < y < 1", args=1, example="erf_inv(0.5) => 0.4769362762")
def erf_inv(y):
    y = float(y)
    if y <= -1.0 or y >= 1.0:
        raise ValueError("Math ERROR")
    if y == 0.0:
        return 0.0
    a = 0.147
    sgn = -1.0 if y < 0 else 1.0
    ln_term = math.log(1.0 - y * y)
    t1 = 2.0 / (math.pi * a) + ln_term / 2.0
    x = sgn * math.sqrt(math.sqrt(t1 * t1 - ln_term / a) - t1)
    two_over_sqrt_pi = 2.0 / math.sqrt(math.pi)
    for _ in range(6):
        err = math.erf(x) - y
        deriv_val = two_over_sqrt_pi * math.exp(-x * x)
        x -= err / (deriv_val * (1.0 + x * err / deriv_val))
    return x


@register("expm1", CAT_SPECIAL, "Compute e^x - 1 accurately even for very small x", args=1, example="expm1(0) => 0")
def expm1_(x):
    return math.expm1(float(x))


@register("log1p", CAT_SPECIAL, "Compute ln(1 + x) accurately for small x (x > -1)", args=1, example="log1p(0) => 0")
def log1p_(x):
    x = float(x)
    if x <= -1.0:
        raise ValueError("Math ERROR")
    return math.log1p(x)


@register("lambertw", CAT_SPECIAL, "Principal branch of Lambert W function W_0(x) solving w*e^w = x for x >= -1/e", args=1, example="lambertw(0) => 0")
def lambertw(x):
    x = float(x)
    min_x = -1.0 / math.e
    if x < min_x - 1e-15:
        raise ValueError("Math ERROR")
    if abs(x - min_x) <= 1e-15:
        return -1.0
    if x == 0.0:
        return 0.0
    if x < 1.0:
        w = x if x > -0.3 else -1.0 + math.sqrt(2.0 * (math.e * x + 1.0))
    else:
        w = math.log(x) - math.log(math.log(x)) if x > 3.0 else 0.6 * math.log1p(x)
    for _ in range(50):
        ew = math.exp(w)
        wew = w * ew
        f = wew - x
        fp = ew * (w + 1.0)
        if fp == 0.0:
            break
        denom = fp - (w + 2.0) * f / (2.0 * w + 2.0)
        dw = f / denom
        w -= dw
        if abs(dw) < 1e-15 * (1.0 + abs(w)):
            break
    return w


@register("digamma", CAT_SPECIAL, "Digamma function psi(x) = d/dx ln Gamma(x) for x not a non-positive integer", args=1, example="digamma(1) => -0.5772156649")
def digamma(x):
    x = float(x)
    if x <= 0.0 and x == int(x):
        raise ValueError("Math ERROR")
    res = 0.0
    if x < 0.0:
        res -= math.pi / math.tan(math.pi * x)
        x = 1.0 - x
    while x < 10.0:
        res -= 1.0 / x
        x += 1.0
    inv_x2 = 1.0 / (x * x)
    res += (
        math.log(x)
        - 0.5 / x
        - inv_x2 * (
            1.0 / 12.0
            - inv_x2 * (
                1.0 / 120.0
                - inv_x2 * (1.0 / 252.0 - inv_x2 / 240.0)
            )
        )
    )
    return res


@register("zeta", CAT_SPECIAL, "Riemann zeta function zeta(s) for real s != 1", args=1, example="zeta(2) => 1.644934067")
def zeta(s):
    s = float(s)
    if s == 1.0:
        raise ValueError("Math ERROR")
    if s == 0.0:
        return -0.5
    if s < 0.0:
        if s == int(s) and int(s) % 2 == 0:
            return 0.0
        return (
            (2.0 ** s)
            * (math.pi ** (s - 1.0))
            * math.sin(0.5 * math.pi * s)
            * math.gamma(1.0 - s)
            * zeta(1.0 - s)
        )
    n = 30
    d = [0.0] * (n + 1)
    d[0] = 1.0
    for i in range(1, n + 1):
        term = 1.0
        s_acc = 1.0
        for j in range(1, i + 1):
            term = term * (n + j - 1) * (n - j + 1) * 4.0 / ((2 * j - 1) * (2 * j))
            s_acc += term
        d[i] = s_acc
    dn = d[n]
    total = 0.0
    for k in range(n):
        sgn = -1.0 if (k % 2 == 1) else 1.0
        total += sgn * (d[k] - dn) / ((k + 1) ** s)
    eta = -total / dn
    return eta / (1.0 - (2.0 ** (1.0 - s)))


def _bessel_j_int(n, x):
    """Bessel function of the first kind J_n(x) for integer n >= 0."""
    if x == 0.0:
        return 1.0 if n == 0 else 0.0
    ax = abs(x)
    sgn = -1.0 if (x < 0 and n % 2 == 1) else 1.0
    if ax < 15.0 or ax < n + 5:
        half_x = 0.5 * ax
        term = (half_x ** n) / math.gamma(n + 1.0)
        total = term
        x2 = -0.25 * ax * ax
        for k in range(1, 200):
            term *= x2 / (k * (n + k))
            total += term
            if abs(term) < abs(total) * 1e-16:
                break
        return sgn * total
    else:
        chi = ax - (0.5 * n + 0.25) * math.pi
        mu = 4.0 * n * n
        z8 = 8.0 * ax
        p = 1.0 - (mu - 1.0) * (mu - 9.0) / (2.0 * z8 * z8) + (mu - 1.0) * (mu - 9.0) * (mu - 25.0) * (mu - 49.0) / (24.0 * (z8 ** 4))
        q = (mu - 1.0) / z8 - (mu - 1.0) * (mu - 9.0) * (mu - 25.0) / (6.0 * (z8 ** 3))
        return sgn * math.sqrt(2.0 / (math.pi * ax)) * (p * math.cos(chi) - q * math.sin(chi))


@register("bessel_j", CAT_SPECIAL, "Bessel function of the first kind J_n(x) for integer order n", args=2, example="bessel_j(0, 0) => 1")
def bessel_j(n, x):
    n_f = float(n)
    if n_f != int(n_f):
        raise ArgumentError("order n must be an integer")
    ni = int(n_f)
    x = float(x)
    if ni < 0:
        val = _bessel_j_int(-ni, x)
        return -val if ((-ni) % 2 == 1) else val
    return _bessel_j_int(ni, x)


def _bessel_y0(x):
    """Neumann function Y_0(x) for x > 0."""
    euler_gamma = 0.5772156649015328606
    if x < 12.0:
        j0 = _bessel_j_int(0, x)
        total = 0.0
        term = 1.0
        h_k = 0.0
        x2 = -0.25 * x * x
        for k in range(1, 200):
            term *= x2 / (k * k)
            h_k += 1.0 / k
            add = term * h_k
            total += add
            if abs(add) < 1e-16:
                break
        return (2.0 / math.pi) * ((math.log(0.5 * x) + euler_gamma) * j0 - total)
    else:
        chi = x - 0.25 * math.pi
        z8 = 8.0 * x
        p = 1.0 - 9.0 / (2.0 * z8 * z8) + 9.0 * 25.0 * 49.0 / (24.0 * (z8 ** 4))
        q = -1.0 / z8 + 9.0 * 25.0 / (6.0 * (z8 ** 3))
        return math.sqrt(2.0 / (math.pi * x)) * (p * math.sin(chi) + q * math.cos(chi))


def _bessel_y1(x):
    """Neumann function Y_1(x) for x > 0."""
    if x < 12.0:
        j0 = _bessel_j_int(0, x)
        j1 = _bessel_j_int(1, x)
        y0 = _bessel_y0(x)
        return (j1 * y0 - 2.0 / (math.pi * x)) / j0
    else:
        chi = x - 0.75 * math.pi
        mu = 4.0
        z8 = 8.0 * x
        p = 1.0 - (mu - 1.0) * (mu - 9.0) / (2.0 * z8 * z8) + (mu - 1.0) * (mu - 9.0) * (mu - 25.0) * (mu - 49.0) / (24.0 * (z8 ** 4))
        q = (mu - 1.0) / z8 - (mu - 1.0) * (mu - 9.0) * (mu - 25.0) / (6.0 * (z8 ** 3))
        return math.sqrt(2.0 / (math.pi * x)) * (p * math.sin(chi) + q * math.cos(chi))


@register("bessel_y", CAT_SPECIAL, "Bessel function of the second kind Y_n(x) for integer n and x > 0", args=2, example="bessel_y(0, 1) => 0.08825696422")
def bessel_y(n, x):
    n_f = float(n)
    x = float(x)
    if n_f != int(n_f):
        raise ArgumentError("order n must be an integer")
    if x <= 0.0:
        raise ValueError("Math ERROR")
    ni = int(n_f)
    neg = ni < 0
    m = abs(ni)
    if m == 0:
        res = _bessel_y0(x)
    elif m == 1:
        res = _bessel_y1(x)
    else:
        y_prev = _bessel_y0(x)
        y_curr = _bessel_y1(x)
        for k in range(1, m):
            y_next = (2.0 * k / x) * y_curr - y_prev
            y_prev, y_curr = y_curr, y_next
        res = y_curr
    return -res if (neg and m % 2 == 1) else res


@register("elliptic_k", CAT_SPECIAL, "Complete elliptic integral of the first kind K(m) for parameter m < 1", args=1, example="elliptic_k(0) => 1.570796327")
def elliptic_k(m):
    m = float(m)
    if m >= 1.0:
        raise ValueError("Math ERROR")
    a = 1.0
    b = math.sqrt(1.0 - m)
    for _ in range(50):
        if abs(a - b) < 1e-16 * a:
            break
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return math.pi / (2.0 * a)


@register("elliptic_e", CAT_SPECIAL, "Complete elliptic integral of the second kind E(m) for parameter m <= 1", args=1, example="elliptic_e(0) => 1.570796327")
def elliptic_e(m):
    m = float(m)
    if m > 1.0:
        raise ValueError("Math ERROR")
    if m == 1.0:
        return 1.0
    a = 1.0
    b = math.sqrt(1.0 - m)
    c_sq = m
    power_two = 1.0
    sum_c = c_sq
    for _ in range(50):
        if abs(a - b) < 1e-16 * a:
            break
        a_next = 0.5 * (a + b)
        b_next = math.sqrt(a * b)
        c = 0.5 * (a - b)
        power_two *= 2.0
        sum_c += power_two * c * c
        a, b = a_next, b_next
    k_val = math.pi / (2.0 * a)
    return k_val * (1.0 - 0.5 * sum_c)


@register("sine_integral", CAT_SPECIAL, "Sine integral Si(x) = integral_0^x (sin(t)/t) dt", args=1, example="sine_integral(0) => 0")
def sine_integral(x):
    x = float(x)
    if x == 0.0:
        return 0.0
    sgn = -1.0 if x < 0 else 1.0
    ax = abs(x)
    if ax <= 16.0:
        term = ax
        total = term
        x2 = -ax * ax
        for k in range(1, 200):
            term *= x2 / ((2 * k) * (2 * k + 1))
            add = term / (2 * k + 1)
            total += add
            if abs(add) < abs(total) * 1e-16:
                break
        return sgn * total
    else:
        inv_x = 1.0 / ax
        inv_x2 = inv_x * inv_x
        f = inv_x * (1.0 - 2.0 * inv_x2 + 24.0 * (inv_x2 ** 2) - 720.0 * (inv_x2 ** 3))
        g = inv_x2 * (1.0 - 6.0 * inv_x2 + 120.0 * (inv_x2 ** 2) - 5040.0 * (inv_x2 ** 3))
        return sgn * (0.5 * math.pi - f * math.cos(ax) - g * math.sin(ax))


@register("cosine_integral", CAT_SPECIAL, "Cosine integral Ci(x) = gamma + ln(x) + integral_0^x ((cos(t)-1)/t) dt for x > 0", args=1, example="cosine_integral(1) => 0.3374039229")
def cosine_integral(x):
    x = float(x)
    if x <= 0.0:
        raise ValueError("Math ERROR")
    euler_gamma = 0.5772156649015328606
    if x <= 16.0:
        term = 1.0
        total = 0.0
        x2 = -x * x
        for k in range(1, 200):
            term *= x2 / ((2 * k - 1) * (2 * k))
            add = term / (2 * k)
            total += add
            if abs(add) < 1e-16:
                break
        return euler_gamma + math.log(x) + total
    else:
        inv_x = 1.0 / x
        inv_x2 = inv_x * inv_x
        f = inv_x * (1.0 - 2.0 * inv_x2 + 24.0 * (inv_x2 ** 2) - 720.0 * (inv_x2 ** 3))
        g = inv_x2 * (1.0 - 6.0 * inv_x2 + 120.0 * (inv_x2 ** 2) - 5040.0 * (inv_x2 ** 3))
        return f * math.sin(x) - g * math.cos(x)


@register("fresnel_s", CAT_SPECIAL, "Normalized Fresnel sine integral S(x) = integral_0^x sin(pi*t^2 / 2) dt", args=1, example="fresnel_s(0) => 0")
def fresnel_s(x):
    x = float(x)
    if x == 0.0:
        return 0.0
    sgn = -1.0 if x < 0 else 1.0
    ax = abs(x)
    if ax <= 3.5:
        u = 0.5 * math.pi * ax * ax
        term = u
        total = ax * term / 3.0
        u2 = -u * u
        for k in range(1, 150):
            term *= u2 / ((2 * k) * (2 * k + 1))
            add = ax * term / (4 * k + 3)
            total += add
            if abs(add) < abs(total) * 1e-16:
                break
        return sgn * total
    else:
        z = math.pi * ax * ax
        inv_z = 1.0 / z
        inv_z2 = inv_z * inv_z
        f = (1.0 - 3.0 * inv_z2 + 105.0 * (inv_z2 ** 2)) / (math.pi * ax)
        g = (inv_z - 15.0 * inv_z * inv_z2) / (math.pi * ax)
        half_z = 0.5 * z
        return sgn * (0.5 - f * math.cos(half_z) - g * math.sin(half_z))


@register("fresnel_c", CAT_SPECIAL, "Normalized Fresnel cosine integral C(x) = integral_0^x cos(pi*t^2 / 2) dt", args=1, example="fresnel_c(0) => 0")
def fresnel_c(x):
    x = float(x)
    if x == 0.0:
        return 0.0
    sgn = -1.0 if x < 0 else 1.0
    ax = abs(x)
    if ax <= 3.5:
        u = 0.5 * math.pi * ax * ax
        term = 1.0
        total = ax
        u2 = -u * u
        for k in range(1, 150):
            term *= u2 / ((2 * k - 1) * (2 * k))
            add = ax * term / (4 * k + 1)
            total += add
            if abs(add) < abs(total) * 1e-16:
                break
        return sgn * total
    else:
        z = math.pi * ax * ax
        inv_z = 1.0 / z
        inv_z2 = inv_z * inv_z
        f = (1.0 - 3.0 * inv_z2 + 105.0 * (inv_z2 ** 2)) / (math.pi * ax)
        g = (inv_z - 15.0 * inv_z * inv_z2) / (math.pi * ax)
        half_z = 0.5 * z
        return sgn * (0.5 + f * math.sin(half_z) - g * math.cos(half_z))


@register("hyp2f1", CAT_SPECIAL, "Gauss hypergeometric function 2F1(a, b; c; z) for |z| < 1 and c not a non-positive integer", args=4, example="hyp2f1(1, 2, 3, 0.5) => 1.545177444")
def hyp2f1(a, b, c, z):
    a, b, c, z = float(a), float(b), float(c), float(z)
    if c <= 0.0 and c == int(c):
        raise ValueError("Math ERROR")
    if abs(z) >= 1.0:
        raise ValueError("Math ERROR")
    total = 1.0
    term = 1.0
    for k in range(1, 1000):
        term *= ((a + k - 1.0) * (b + k - 1.0) * z) / ((c + k - 1.0) * k)
        total += term
        if abs(term) < abs(total) * 1e-16:
            break
    return total


@register("sum_n2", CAT_SPECIAL, "Sum of squares 1^2 + 2^2 + ... + n^2 for integer n >= 0", args=1, exact=True, example="sum_n2(5) => 55")
def sum_n2(n):
    nf = float(n)
    if nf != int(nf) or nf < 0:
        raise ArgumentError("n must be a non-negative integer")
    ni = int(nf)
    return ni * (ni + 1) * (2 * ni + 1) // 6


@register("sum_n3", CAT_SPECIAL, "Sum of cubes 1^3 + 2^3 + ... + n^3 for integer n >= 0", args=1, exact=True, example="sum_n3(4) => 100")
def sum_n3(n):
    nf = float(n)
    if nf != int(nf) or nf < 0:
        raise ArgumentError("n must be a non-negative integer")
    ni = int(nf)
    s = ni * (ni + 1) // 2
    return s * s


@register("sum_odd", CAT_SPECIAL, "Sum of the first n odd positive integers (1 + 3 + ... + (2n-1) = n^2) for integer n >= 0", args=1, exact=True, example="sum_odd(5) => 25")
def sum_odd(n):
    nf = float(n)
    if nf != int(nf) or nf < 0:
        raise ArgumentError("n must be a non-negative integer")
    ni = int(nf)
    return ni * ni


@register("linrec2", CAT_SPECIAL, "n-th term of 2nd-order linear recurrence x(n) = a*x(n-1) + b*x(n-2) given x0, x1 and n >= 0", args=5, exact=True, example="linrec2(1, 1, 0, 1, 10) => 55")
def linrec2(a, b, x0, x1, n):
    nf = float(n)
    if nf != int(nf) or nf < 0:
        raise ArgumentError("n must be a non-negative integer")
    ni = int(nf)
    if ni == 0:
        return x0
    if ni == 1:
        return x1
    prev2, prev1 = x0, x1
    for _ in range(2, ni + 1):
        prev2, prev1 = prev1, a * prev1 + b * prev2
    return prev1
