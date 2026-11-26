"""Checks: number theory.  Run alone with  python run_tests.py number_theory"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "number_theory"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .helpers import _err, _expr_error  # noqa: F401


def checks_number_theory_8(check, cov, ex, fn):
    """number theory (brute force)"""
    # ---------------------------------------------------------------- number theory (brute force)
    def is_p(n):
        return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))

    def divs(n):
        return [d for d in range(1, n + 1) if n % d == 0]

    def fac(n):
        out, d = [], 2
        while d * d <= n:
            while n % d == 0:
                out.append(d)
                n //= d
            d += 1
        if n > 1:
            out.append(n)
        return out

    primes = [q for q in range(2, 400) if is_p(q)]
    for n in range(1, 61):
        ex(f"isprime({n})", f"isprime({n})", int(is_p(n)))
        ex(f"totient({n})", f"totient({n})", sum(1 for k in range(1, n + 1) if math.gcd(k, n) == 1))
        ex(f"divisors_count({n})", f"divisors_count({n})", len(divs(n)))
        ex(f"divisors_sum({n})", f"divisors_sum({n})", sum(divs(n)))
        ex(f"aliquot_sum({n})", f"aliquot_sum({n})", sum(divs(n)) - n)
        ex(f"sigma_k(2,{n})", f"sigma_k(2,{n})", sum(d * d for d in divs(n)))
        ex(f"is_perfect({n})", f"is_perfect({n})", int(sum(divs(n)) - n == n))
        ex(f"is_abundant({n})", f"is_abundant({n})", int(sum(divs(n)) - n > n))
        ex(f"prime_pi({n})", f"prime_pi({n})", sum(1 for q in primes if q <= n))
        ex(f"next_prime({n})", f"next_prime({n})", next(q for q in primes if q > n))
        if n > 2:
            ex(f"prev_prime({n})", f"prev_prime({n})", max(q for q in primes if q < n))
        if n > 1:
            f_ = fac(n)
            ex(f"smallest_pf({n})", f"smallest_pf({n})", min(f_))
            ex(f"largest_pf({n})", f"largest_pf({n})", max(f_))
        f_ = fac(n)
        ex(f"distinct_pf({n})", f"distinct_pf({n})", len(set(f_)))
        ex(f"total_pf({n})", f"total_pf({n})", len(f_))
        rad = 1
        for q in set(f_):
            rad *= q
        ex(f"radical({n})", f"radical({n})", rad)
        mu = 0 if len(f_) != len(set(f_)) else (-1) ** len(f_)
        ex(f"mobius({n})", f"mobius({n})", mu)
        ex(f"is_square({n})", f"is_square({n})", int(math.isqrt(n) ** 2 == n))
        ex(f"is_cube({n})", f"is_cube({n})", int(any(c ** 3 == n for c in range(0, 5))))
        ex(f"is_pow2({n})", f"is_pow2({n})", int(bin(n).count("1") == 1))
        ex(f"is_palindrome({n})", f"is_palindrome({n})", int(str(n) == str(n)[::-1]))
        ex(f"is_armstrong({n})", f"is_armstrong({n})", int(sum(int(c) ** len(str(n)) for c in str(n)) == n))
        ex(f"digit_sum({n})", f"digit_sum({n})", sum(map(int, str(n))))
        ex(f"digit_count({n})", f"digit_count({n})", len(str(n)))
        ex(f"reverse_digits({n})", f"reverse_digits({n})", int(str(n)[::-1]))
        dr = n
        while dr > 9:
            dr = sum(map(int, str(dr)))
        ex(f"digital_root({n})", f"digital_root({n})", dr)
        c_, steps = n, 0
        while c_ != 1:
            c_ = c_ // 2 if c_ % 2 == 0 else 3 * c_ + 1
            steps += 1
        ex(f"collatz_steps({n})", f"collatz_steps({n})", steps)
        h_, seen = n, set()
        while h_ != 1 and h_ not in seen:
            seen.add(h_)
            h_ = sum(int(c) ** 2 for c in str(h_))
        ex(f"is_happy({n})", f"is_happy({n})", int(h_ == 1))
        ex(f"coprime({n},12)", f"coprime({n},12)", int(math.gcd(n, 12) == 1))
        ex(f"gcd({n},84)", f"gcd({n},84)", math.gcd(n, 84))
        ex(f"lcm({n},18)", f"lcm({n},18)", math.lcm(n, 18))
        ex(f"triangular_num({n})", f"triangular_num({n})", sum(range(n + 1)))
        ex(f"tetrahedral_num({n})", f"tetrahedral_num({n})", sum(k * (k + 1) // 2 for k in range(n + 1)))
        ex(f"polygonal_num(6,{n})", f"polygonal_num(6,{n})", n * (2 * n - 1))
    ex("nth_prime", "nth_prime(25)", primes[24])
    a_, b_ = 0, 1
    fibs = []
    for _ in range(40):
        fibs.append(a_)
        a_, b_ = b_, a_ + b_
    lu = [2, 1]
    for _ in range(38):
        lu.append(lu[-1] + lu[-2])
    pe = [0, 1]
    for _ in range(38):
        pe.append(2 * pe[-1] + pe[-2])
    tr = [0, 1, 1]
    for _ in range(38):
        tr.append(tr[-1] + tr[-2] + tr[-3])
    for n in range(0, 30):
        ex(f"fib({n})", f"fib({n})", fibs[n])
        ex(f"lucas({n})", f"lucas({n})", lu[n])
        ex(f"pell({n})", f"pell({n})", pe[n])
        ex(f"tribonacci({n})", f"tribonacci({n})", tr[n])
        ex(f"fib_mod({n},7)", f"fib_mod({n},7)", fibs[n] % 7)
        ex(f"catalan({n})", f"catalan({n})", math.comb(2 * n, n) // (n + 1))
        ex(f"central_binomial({n})", f"central_binomial({n})", math.comb(2 * n, n))
        ex(f"factorial({n})", f"factorial({n})", math.factorial(n))
        ex(f"double_factorial({n})", f"double_factorial({n})", math.prod(range(n, 0, -2)))
        der = sum((-1) ** k * math.factorial(n) // math.factorial(k) for k in range(n + 1))
        ex(f"derangements({n})", f"derangements({n})", der)
        ex(f"harmonic_number({n + 1})", f"harmonic_number({n + 1})", sum(Fraction(1, k) for k in range(1, n + 2)))
        ex(f"rising_factorial(3,{n})", f"rising_factorial(3,{n})", math.prod(range(3, 3 + n)))
        ex(f"falling_factorial(40,{n})", f"falling_factorial(40,{n})", math.prod(range(40, 40 - n, -1)))
    memo = {}

    def part(n, k):
        if n == 0:
            return 1
        if n < 0 or k == 0:
            return 0
        if (n, k) not in memo:
            memo[(n, k)] = part(n - k, k) + part(n, k - 1)
        return memo[(n, k)]

    def s2(n, k):
        return sum((-1) ** (k - j) * math.comb(k, j) * j ** n for j in range(k + 1)) // math.factorial(k)

    def s1(n, k):
        if n == k:
            return 1
        if n == 0 or k == 0:
            return 0
        return s1(n - 1, k - 1) + (n - 1) * s1(n - 1, k)

    for n in range(0, 16):
        ex(f"partitions({n})", f"partitions({n})", part(n, n))
        ex(f"bell({n})", f"bell({n})", sum(s2(n, k) for k in range(n + 1)))
    for n in range(1, 9):
        for k in range(0, n + 1):
            ex(f"stirling2({n},{k})", f"stirling2({n},{k})", s2(n, k) if k else 0)
            ex(f"stirling1({n},{k})", f"stirling1({n},{k})", s1(n, k))
    ex("multinomial", "multinomial(9,2,3,4)", math.factorial(9) // (math.factorial(2) * math.factorial(3) * math.factorial(4)))
    for n, r_ in [(5, 2), (8, 3), (10, 10), (12, 0)]:
        ex(f"ncr({n},{r_})", f"ncr({n},{r_})", math.comb(n, r_))
        ex(f"npr({n},{r_})", f"npr({n},{r_})", math.perm(n, r_))
    for p_ in (3, 5, 7, 11, 13, 17, 19, 23):
        root = primitive_root_ref = next(g for g in range(2, p_) if len({pow(g, e, p_) for e in range(1, p_)}) == p_ - 1)
        ex(f"primitive_root({p_})", f"primitive_root({p_})", root)
        for a in range(1, p_):
            qr = int(any((x * x - a) % p_ == 0 for x in range(1, p_)))
            ex(f"legendre({a},{p_})", f"legendre({a},{p_})", 1 if qr else -1)
        for a in (2, 3, 10):
            ord_ = next(k for k in range(1, p_ + 1) if pow(a, k, p_) == 1) if a % p_ else None
            if ord_:
                ex(f"order_mod({a},{p_})", f"order_mod({a},{p_})", ord_)
    for nn in (9, 15, 21, 35):
        for a in range(1, 12):
            # Jacobi symbol by factoring into Legendre symbols
            want = 1
            for q in fac(nn):
                if a % q == 0:
                    want = 0
                    break
                want *= 1 if any((x * x - a) % q == 0 for x in range(1, q)) else -1
            ex(f"jacobi({a},{nn})", f"jacobi({a},{nn})", want)
    for a, m in [(3, 11), (7, 40), (10, 17), (5, 12)]:
        ex(f"modinv({a},{m})", f"modinv({a},{m})", pow(a, -1, m))
    for b, e, m in [(2, 10, 1000), (7, 222, 13), (123, 45, 67)]:
        ex(f"modpow({b},{e},{m})", f"modpow({b},{e},{m})", pow(b, e, m))
    for a, b in [(35, 15), (240, 46), (17, 5), (99, 78)]:
        x = fn("egcd_x")(a, b)
        y = fn("egcd_y")(a, b)
        cov("egcd_x", "egcd_y")
        check(f"egcd identity {a},{b}", a * x + b * y, math.gcd(a, b))
    for a1, m1, a2, m2 in [(2, 3, 3, 5), (1, 4, 3, 9), (5, 7, 2, 11)]:
        sol = fn("crt2")(a1, m1, a2, m2)
        cov("crt2")
        check(f"crt2({a1},{m1},{a2},{m2}) satisfies both", (sol % m1, sol % m2), (a1 % m1, a2 % m2))
    ex("gcd of three", "gcd(12,18,30)", 6)
    ex("lcm of three", "lcm(4,6,10)", 60)
    ex("isprime big", "isprime(1000000007)", 1)
    ex("isprime Carmichael", "isprime(561)", 0)
