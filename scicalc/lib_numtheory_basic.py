"""Factorials, permutations, gcd/lcm, primes, number theory

Module 9 of 47.  Taken from lines 2168-2346 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_numtheory_basic"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .arithmetic import ar_factorial
from .lib_powers_rounding import _whole

# ---------- 7d. Combinatorics and number theory ----------

# Factorials, permutations, combinations, gcd, lcm and primes.


CAT_COMB = "Combinatorics & Number Theory"
MAX_N = 5000


@register("factorial", CAT_COMB, "Factorial n! (n up to 1500)", exact=True, aliases=("fact",),
          example="factorial(5) => 120")
def factorial(n):
    return ar_factorial(n)


def _n_r(n, r):
    n, r = _whole(n, "n"), _whole(r, "r")
    if not 0 <= r <= n or n > MAX_N:
        raise MathError(f"needs 0 <= r <= n <= {MAX_N}")
    return n, r


@register("npr", CAT_COMB, "Permutations nPr: ordered choices of r from n", args=2, exact=True,
          example="npr(5,2) => 20")
def npr(n, r):
    return math.perm(*_n_r(n, r))


@register("ncr", CAT_COMB, "Combinations nCr: unordered choices of r from n", args=2, exact=True,
          example="ncr(5,2) => 10")
def ncr(n, r):
    return math.comb(*_n_r(n, r))


@register("gcd", CAT_COMB, "Greatest common divisor", args=(2, None), exact=True, example="gcd(12,18) => 6")
def gcd(*xs):
    return math.gcd(*[_whole(x, "values") for x in xs])


@register("lcm", CAT_COMB, "Least common multiple", args=(2, None), exact=True, example="lcm(4,6) => 12")
def lcm(*xs):
    return math.lcm(*[_whole(x, "values") for x in xs])


@register("isprime", CAT_COMB, "1 if the number is prime, otherwise 0 (up to 3x10^24)", exact=True,
          example="isprime(97) => 1")
def isprime(n):
    n = _whole(n, "n")
    if n < 2:
        return 0
    if n > 3 * 10 ** 24:
        raise MathError("number too large for the prime test")
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return int(n == p)
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):      # deterministic below 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return 0
    return 1


# --- Number Theory Expansion ---

@register("totient", CAT_COMB, "Euler's totient function phi(n): counts integers 1..n coprime to n", exact=True, aliases=("phi_func",), example="totient(12) => 4")
def totient(n):
    n = _whole(n, "n")
    if n <= 0:
        raise MathError("n must be positive")
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result


@register("divisors_count", CAT_COMB, "Count total positive divisors of n", exact=True, aliases=("tau_func",), example="divisors_count(12) => 6")
def divisors_count(n):
    n = _whole(n, "n")
    if n <= 0:
        raise MathError("n must be positive")
    count = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            count += 1 if i * i == n else 2
    return count


@register("divisors_sum", CAT_COMB, "Sum of positive divisors of n", exact=True, aliases=("sigma_func",), example="divisors_sum(12) => 28")
def divisors_sum(n):
    n = _whole(n, "n")
    if n <= 0:
        raise MathError("n must be positive")
    total = 0
    for i in range(1, int(math.isqrt(n)) + 1):
        if n % i == 0:
            total += i if i * i == n else (i + n // i)
    return total


@register("modpow", CAT_COMB, "Modular exponentiation: modpow(base, exp, mod) = (base^exp) % mod", args=3, exact=True, example="modpow(2,10,1000) => 24")
def modpow(b, e, m):
    b, e, m = _whole(b, "base"), _whole(e, "exp"), _whole(m, "mod")
    if m <= 0:
        raise MathError("modulus must be positive")
    if e < 0:
        raise MathError("exponent cannot be negative")
    return pow(b, e, m)


@register("modinv", CAT_COMB, "Modular multiplicative inverse of a mod m: modinv(a, m)", args=2, exact=True, example="modinv(3,11) => 4")
def modinv(a, m):
    a, m = _whole(a, "a"), _whole(m, "m")
    if m <= 0:
        raise MathError("modulus must be positive")
    try:
        return pow(a, -1, m)
    except ValueError:
        raise MathError("modular inverse does not exist (gcd != 1)")


@register("fib", CAT_COMB, "n-th Fibonacci number (fib(0)=0, fib(1)=1)", exact=True, aliases=("fibonacci",), example="fib(10) => 55")
def fib(n):
    n = _whole(n, "n")
    if n < 0 or n > 1000:
        raise MathError("n must be between 0 and 1000")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@register("catalan", CAT_COMB, "n-th Catalan number: C_n = (2n)! / ((n+1)! n!)", exact=True, example="catalan(4) => 14")
def catalan(n):
    n = _whole(n, "n")
    if n < 0 or n > 500:
        raise MathError("n must be between 0 and 500")
    return math.comb(2 * n, n) // (n + 1)


@register("gamma", CAT_COMB, "Gamma function Γ(x)", example="gamma(5) => 24")
def gamma_(x):
    if x <= 0 and float(x).is_integer():
        raise MathError("gamma is undefined at zero and negative integers")
    return math.gamma(x)


@register("lgamma", CAT_COMB, "Natural log of absolute Gamma function: ln(|Γ(x)|)", example="lgamma(5) => 3.17805383")
def lgamma_(x):
    if x <= 0 and float(x).is_integer():
        raise MathError("lgamma is undefined at zero and negative integers")
    return math.lgamma(x)


@register("beta", CAT_COMB, "Euler Beta function: beta(x, y)", args=2, example="beta(3,4) => 0.01666666667")
def beta_(x, y):
    if x <= 0 or y <= 0:
        raise MathError("arguments must be positive")
    return math.exp(math.lgamma(x) + math.lgamma(y) - math.lgamma(x + y))
