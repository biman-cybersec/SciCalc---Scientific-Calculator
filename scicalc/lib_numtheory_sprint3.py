"""Sprint 3A: number theory and combinatorics

Module 22 of 47.  Taken from lines 6440-7029 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_numtheory_sprint3"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import MathError
from .registry import register
from .lib_powers_rounding import _whole
from .lib_numtheory_basic import CAT_COMB, isprime

# --- SPRINT 3: PART A - NUMBER THEORY & COMBINATORICS ---

@register("prime_pi", CAT_COMB, "Number of primes <= n", 1, exact=True, example="prime_pi(10) => 4")
def func_prime_pi(n):
    nv = _whole(n, "prime_pi")
    if nv < 0:
        raise MathError("prime_pi requires n >= 0")
    count = 0
    sieve = [True] * (nv + 1)
    if nv >= 2:
        sieve[0] = sieve[1] = False
        for p in range(2, int(math.isqrt(nv)) + 1):
            if sieve[p]:
                for i in range(p * p, nv + 1, p):
                    sieve[i] = False
        count = sum(1 for x in sieve if x)
    return count

@register("nth_prime", CAT_COMB, "n-th prime (1-indexed)", 1, exact=True, example="nth_prime(5) => 11")
def func_nth_prime(n):
    nv = _whole(n, "nth_prime")
    if nv < 1:
        raise MathError("nth_prime requires n >= 1")
    primes = []
    limit = max(15, int(nv * (math.log(nv) + math.log(math.log(nv)) if nv > 5 else 2)))
    while len(primes) < nv:
        sieve = [True] * (limit + 1)
        sieve[0] = sieve[1] = False
        for p in range(2, int(math.isqrt(limit)) + 1):
            if sieve[p]:
                for i in range(p * p, limit + 1, p):
                    sieve[i] = False
        primes = [i for i, is_p in enumerate(sieve) if is_p]
        if len(primes) < nv:
            limit *= 2
    return primes[nv - 1]

@register("prev_prime", CAT_COMB, "Largest prime strictly below n", 1, exact=True, example="prev_prime(10) => 7")
def func_prev_prime(n):
    nv = _whole(n, "prev_prime")
    if nv <= 2:
        raise MathError("No prime below 2")
    for x in range(nv - 1, 1, -1):
        if isprime(x):
            return x
    raise MathError("No prime found")

@register("smallest_pf", CAT_COMB, "Smallest prime factor", 1, exact=True, example="smallest_pf(35) => 5")
def func_smallest_pf(n):
    nv = _whole(n, "smallest_pf")
    if nv < 2:
        raise MathError("smallest_pf requires n >= 2")
    for i in range(2, int(math.isqrt(nv)) + 1):
        if nv % i == 0:
            return i
    return nv

@register("largest_pf", CAT_COMB, "Largest prime factor", 1, exact=True, example="largest_pf(35) => 7")
def func_largest_pf(n):
    nv = _whole(n, "largest_pf")
    if nv < 2:
        raise MathError("largest_pf requires n >= 2")
    temp = nv
    largest = 2
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            largest = d
            temp //= d
        d += 1
    if temp > 1:
        largest = temp
    return largest

@register("distinct_pf", CAT_COMB, "Number of distinct prime factors", 1, exact=True, example="distinct_pf(72) => 2")
def func_distinct_pf(n):
    nv = _whole(n, "distinct_pf")
    if nv < 1:
        raise MathError("distinct_pf requires n >= 1")
    if nv == 1:
        return 0
    temp = nv
    count = 0
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            count += 1
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count

@register("total_pf", CAT_COMB, "Total prime factors with repetition", 1, exact=True, example="total_pf(72) => 5")
def func_total_pf(n):
    nv = _whole(n, "total_pf")
    if nv < 1:
        raise MathError("total_pf requires n >= 1")
    if nv == 1:
        return 0
    temp = nv
    count = 0
    d = 2
    while d * d <= temp:
        while temp % d == 0:
            count += 1
            temp //= d
        d += 1
    if temp > 1:
        count += 1
    return count

@register("radical", CAT_COMB, "Product of distinct prime factors", 1, exact=True, example="radical(72) => 6")
def func_radical(n):
    nv = _whole(n, "radical")
    if nv < 1:
        raise MathError("radical requires n >= 1")
    if nv == 1:
        return 1
    temp = nv
    rad = 1
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            rad *= d
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        rad *= temp
    return rad

@register("aliquot_sum", CAT_COMB, "Sum of proper divisors", 1, exact=True, example="aliquot_sum(6) => 6")
def func_aliquot_sum(n):
    nv = _whole(n, "aliquot_sum")
    if nv < 1:
        raise MathError("aliquot_sum requires n >= 1")
    if nv == 1:
        return 0
    s = 1
    for i in range(2, int(math.isqrt(nv)) + 1):
        if nv % i == 0:
            s += i
            if i * i != nv:
                s += nv // i
    return s

@register("sigma_k", CAT_COMB, "Sum of k-th powers of divisors", 2, exact=True, example="sigma_k(1, 6) => 12")
def func_sigma_k(k, n):
    kv = _whole(k, "sigma_k")
    nv = _whole(n, "sigma_k")
    if nv < 1:
        raise MathError("sigma_k requires n >= 1")
    s = 0
    for i in range(1, int(math.isqrt(nv)) + 1):
        if nv % i == 0:
            s += i ** kv
            other = nv // i
            if other != i:
                s += other ** kv
    return s

@register("is_perfect", CAT_COMB, "1 if perfect number", 1, exact=True, example="is_perfect(6) => 1")
def func_is_perfect(n):
    nv = _whole(n, "is_perfect")
    return 1 if nv > 0 and func_aliquot_sum(nv) == nv else 0

@register("is_abundant", CAT_COMB, "1 if abundant number", 1, exact=True, example="is_abundant(12) => 1")
def func_is_abundant(n):
    nv = _whole(n, "is_abundant")
    return 1 if nv > 0 and func_aliquot_sum(nv) > nv else 0

@register("is_square", CAT_COMB, "1 if perfect square", 1, exact=True, example="is_square(25) => 1")
def func_is_square(n):
    nv = _whole(n, "is_square")
    if nv < 0:
        return 0
    r = int(math.isqrt(nv))
    return 1 if r * r == nv else 0

@register("is_cube", CAT_COMB, "1 if perfect cube", 1, exact=True, example="is_cube(27) => 1")
def func_is_cube(n):
    nv = _whole(n, "is_cube")
    r = int(round(abs(nv) ** (1/3)))
    cubed = (r ** 3) if nv >= 0 else (- (r ** 3))
    return 1 if cubed == nv else 0

@register("is_pow2", CAT_COMB, "1 if power of 2", 1, exact=True, example="is_pow2(8) => 1")
def func_is_pow2(n):
    nv = _whole(n, "is_pow2")
    return 1 if nv > 0 and (nv & (nv - 1)) == 0 else 0

@register("is_palindrome", CAT_COMB, "1 if decimal palindrome", 1, exact=True, example="is_palindrome(121) => 1")
def func_is_palindrome(n):
    nv = _whole(n, "is_palindrome")
    if nv < 0:
        return 0
    s = str(nv)
    return 1 if s == s[::-1] else 0

@register("is_happy", CAT_COMB, "1 if happy number", 1, exact=True, example="is_happy(19) => 1")
def func_is_happy(n):
    nv = _whole(n, "is_happy")
    if nv < 1:
        return 0
    seen = set()
    curr = nv
    while curr != 1 and curr not in seen:
        seen.add(curr)
        curr = sum(int(c)**2 for c in str(curr))
    return 1 if curr == 1 else 0

@register("is_armstrong", CAT_COMB, "1 if Armstrong number", 1, exact=True, example="is_armstrong(153) => 1")
def func_is_armstrong(n):
    nv = _whole(n, "is_armstrong")
    if nv < 0:
        return 0
    s = str(nv)
    k = len(s)
    total = sum(int(c) ** k for c in s)
    return 1 if total == nv else 0

@register("digit_sum", CAT_COMB, "Sum of digits", 1, exact=True, example="digit_sum(123) => 6")
def func_digit_sum(n):
    nv = _whole(n, "digit_sum")
    return sum(int(c) for c in str(abs(nv)))

@register("digit_count", CAT_COMB, "Number of digits", 1, exact=True, example="digit_count(123) => 3")
def func_digit_count(n):
    nv = _whole(n, "digit_count")
    return len(str(abs(nv)))

@register("digital_root", CAT_COMB, "Repeated digit sum", 1, exact=True, example="digital_root(99) => 9")
def func_digital_root(n):
    nv = _whole(n, "digital_root")
    if nv == 0:
        return 0
    val = abs(nv) % 9
    return 9 if val == 0 else val

@register("reverse_digits", CAT_COMB, "Digits reversed", 1, exact=True, example="reverse_digits(123) => 321")
def func_reverse_digits(n):
    nv = _whole(n, "reverse_digits")
    sign = -1 if nv < 0 else 1
    s = str(abs(nv))[::-1]
    return sign * int(s)

@register("collatz_steps", CAT_COMB, "Steps to reach 1 in Collatz", 1, exact=True, example="collatz_steps(6) => 8")
def func_collatz_steps(n):
    nv = _whole(n, "collatz_steps")
    if nv < 1:
        raise MathError("collatz_steps requires n >= 1")
    steps = 0
    curr = nv
    while curr != 1:
        if curr % 2 == 0:
            curr //= 2
        else:
            curr = 3 * curr + 1
        steps += 1
    return steps

@register("lucas", CAT_COMB, "n-th Lucas number", 1, exact=True, example="lucas(3) => 4")
def func_lucas(n):
    nv = _whole(n, "lucas")
    if nv < 0:
        raise MathError("lucas requires n >= 0")
    a, b = 2, 1
    for _ in range(nv):
        a, b = b, a + b
    return a

@register("tribonacci", CAT_COMB, "n-th Tribonacci number", 1, exact=True, example="tribonacci(4) => 4")
def func_tribonacci(n):
    nv = _whole(n, "tribonacci")
    if nv < 0:
        raise MathError("tribonacci requires n >= 0")
    if nv == 0: return 0
    if nv <= 2: return 1
    a, b, c = 0, 1, 1
    for _ in range(nv - 2):
        a, b, c = b, c, a + b + c
    return c

@register("pell", CAT_COMB, "n-th Pell number", 1, exact=True, example="pell(3) => 5")
def func_pell(n):
    nv = _whole(n, "pell")
    if nv < 0:
        raise MathError("pell requires n >= 0")
    a, b = 0, 1
    for _ in range(nv):
        a, b = b, 2 * b + a
    return a

@register("harmonic_number", CAT_COMB, "n-th harmonic number as exact fraction", 1, exact=True, example="harmonic_number(3) => 1.833333333")
def func_harmonic_number(n):
    nv = _whole(n, "harmonic_number")
    if nv < 1:
        raise MathError("harmonic_number requires n >= 1")
    total = Fraction(0, 1)
    for i in range(1, nv + 1):
        total += Fraction(1, i)
    return total

@register("fib_mod", CAT_COMB, "Fibonacci mod m", 2, exact=True, example="fib_mod(10, 7) => 6")
def func_fib_mod(n, m):
    nv = _whole(n, "fib_mod")
    mv = _whole(m, "fib_mod")
    if nv < 0 or mv < 1:
        raise MathError("Invalid arguments for fib_mod")
    if mv == 1: return 0
    a, b = 0, 1
    for _ in range(nv):
        a, b = b, (a + b) % mv
    return a

@register("jacobi", CAT_COMB, "Jacobi symbol (a/n)", 2, exact=True, example="jacobi(2, 15) => 1")
def func_jacobi(a, n):
    av = _whole(a, "jacobi")
    nv = _whole(n, "jacobi")
    if nv < 1 or nv % 2 == 0:
        raise MathError("jacobi requires n to be positive and odd")
    av %= nv
    t = 1
    while av != 0:
        while av % 2 == 0:
            av //= 2
            r = nv % 8
            if r in (3, 5):
                t = -t
        av, nv = nv, av
        if av % 4 == 3 and nv % 4 == 3:
            t = -t
        av %= nv
    return t if nv == 1 else 0

@register("legendre", CAT_COMB, "Legendre symbol (a/p)", 2, exact=True, example="legendre(2, 7) => 1")
def func_legendre(a, p):
    return func_jacobi(a, p)

@register("primitive_root", CAT_COMB, "Smallest primitive root mod p", 1, exact=True, example="primitive_root(7) => 3")
def func_primitive_root(p):
    pv = _whole(p, "primitive_root")
    if pv < 2:
        raise MathError("primitive_root requires p >= 2")
    phi = pv - 1
    factors = []
    temp = phi
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    
    for r in range(2, pv):
        if pow(r, phi, pv) != 1:
            continue
        ok = True
        for f in factors:
            if pow(r, phi // f, pv) == 1:
                ok = False
                break
        if ok:
            return r
    raise MathError("No primitive root found")

@register("order_mod", CAT_COMB, "Multiplicative order of a mod n", 2, exact=True, example="order_mod(2, 7) => 3")
def func_order_mod(a, n):
    av = _whole(a, "order_mod")
    nv = _whole(n, "order_mod")
    if math.gcd(av, nv) != 1:
        raise MathError("a and n must be coprime for order_mod")
    k = 1
    curr = av % nv
    while curr != 1:
        curr = (curr * av) % nv
        k += 1
        if k > nv:
            raise MathError("Order exceeds n")
    return k

@register("crt2", CAT_COMB, "Chinese Remainder Theorem for two equations", 4, exact=True, example="crt2(2, 3, 3, 5) => 8")
def func_crt2(a1, m1, a2, m2):
    a1v, m1v = _whole(a1, "crt2"), _whole(m1, "crt2")
    a2v, m2v = _whole(a2, "crt2"), _whole(m2, "crt2")
    g = math.gcd(m1v, m2v)
    if (a1v - a2v) % g != 0:
        raise MathError("No solution exists for CRT")
    m = m1v * m2v // g
    def egcd(a, b):
        if a == 0: return b, 0, 1
        g, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y
    _, x, _ = egcd(m1v, m2v)
    sol = (a1v + m1v * (a2v - a1v) // g * x) % m
    return sol

@register("egcd_x", CAT_COMB, "x in ax + by = gcd(a,b)", 2, exact=True, example="egcd_x(35, 15) => 1")
def func_egcd_x(a, b):
    av, bv = _whole(a, "egcd_x"), _whole(b, "egcd_x")
    def egcd(a, b):
        if a == 0: return b, 0, 1
        g, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y
    _, x, _ = egcd(av, bv)
    return x

@register("egcd_y", CAT_COMB, "y in ax + by = gcd(a,b)", 2, exact=True, example="egcd_y(35, 15) => -2")
def func_egcd_y(a, b):
    av, bv = _whole(a, "egcd_x"), _whole(b, "egcd_x")
    def egcd(a, b):
        if a == 0: return b, 0, 1
        g, x1, y1 = egcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return g, x, y
    _, _, y = egcd(av, bv)
    return y

@register("coprime", CAT_COMB, "1 if gcd is 1", 2, exact=True, example="coprime(8, 9) => 1")
def func_coprime(a, b):
    return 1 if math.gcd(_whole(a, "coprime"), _whole(b, "coprime")) == 1 else 0

@register("partitions", CAT_COMB, "Number of integer partitions", 1, exact=True, example="partitions(5) => 7")
def func_partitions(n):
    nv = _whole(n, "partitions")
    if nv < 0:
        raise MathError("partitions requires n >= 0")
    if nv == 0: return 1
    p = [0] * (nv + 1)
    p[0] = 1
    for i in range(1, nv + 1):
        j = 1
        while True:
            pent1 = j * (3 * j - 1) // 2
            pent2 = j * (3 * j + 1) // 2
            sign = -1 if j % 2 == 0 else 1
            added = False
            if pent1 <= i:
                p[i] += sign * p[i - pent1]
                added = True
            if pent2 <= i:
                p[i] += sign * p[i - pent2]
                added = True
            if not added:
                break
            j += 1
    return p[nv]

@register("stirling1", CAT_COMB, "Stirling number of the first kind", 2, exact=True, example="stirling1(4, 2) => 11")
def func_stirling1(n, k):
    nv = _whole(n, "stirling1")
    kv = _whole(k, "stirling1")
    if nv < 0 or kv < 0 or kv > nv:
        return 0
    dp = [[0] * (kv + 1) for _ in range(nv + 1)]
    dp[0][0] = 1
    for i in range(1, nv + 1):
        for j in range(1, min(i, kv) + 1):
            dp[i][j] = dp[i-1][j-1] + (i - 1) * dp[i-1][j]
    return dp[nv][kv]

@register("stirling2", CAT_COMB, "Stirling number of the second kind", 2, exact=True, example="stirling2(4, 2) => 7")
def func_stirling2(n, k):
    nv = _whole(n, "stirling2")
    kv = _whole(k, "stirling2")
    if nv < 0 or kv < 0 or kv > nv:
        return 0
    dp = [[0] * (kv + 1) for _ in range(nv + 1)]
    dp[0][0] = 1
    for i in range(1, nv + 1):
        for j in range(1, min(i, kv) + 1):
            dp[i][j] = j * dp[i-1][j] + dp[i-1][j-1]
    return dp[nv][kv]

@register("bell", CAT_COMB, "Bell number", 1, exact=True, example="bell(3) => 5")
def func_bell(n):
    nv = _whole(n, "bell")
    if nv < 0:
        raise MathError("bell requires n >= 0")
    bell_tri = [[0] * (nv + 1) for _ in range(nv + 1)]
    if nv == 0: return 1
    bell_tri[0][0] = 1
    for i in range(1, nv + 1):
        bell_tri[i][0] = bell_tri[i-1][i-1]
        for j in range(1, i + 1):
            bell_tri[i][j] = bell_tri[i-1][j-1] + bell_tri[i][j-1]
    return bell_tri[nv][0]

@register("derangements", CAT_COMB, "Number of derangements", 1, exact=True, example="derangements(3) => 2")
def func_derangements(n):
    nv = _whole(n, "derangements")
    if nv < 0:
        raise MathError("derangements requires n >= 0")
    if nv == 0: return 1
    if nv == 1: return 0
    dprev2, dprev1 = 1, 0
    res = 0
    for i in range(2, nv + 1):
        res = (i - 1) * (dprev1 + dprev2)
        dprev2, dprev1 = dprev1, res
    return res

@register("multinomial", CAT_COMB, "Multinomial coefficient", (2, None), exact=True, example="multinomial(4, 2, 2) => 6")
def func_multinomial(n, *ks):
    nv = _whole(n, "multinomial")
    kvals = [_whole(k, "multinomial") for k in ks]
    if sum(kvals) != nv:
        raise MathError("Multinomial parts must sum to n")
    ans = math.factorial(nv)
    for kv in kvals:
        ans //= math.factorial(kv)
    return ans

@register("central_binomial", CAT_COMB, "Central binomial coefficient C(2n, n)", 1, exact=True, example="central_binomial(3) => 20")
def func_central_binomial(n):
    nv = _whole(n, "central_binomial")
    if nv < 0:
        raise MathError("central_binomial requires n >= 0")
    return math.comb(2 * nv, nv)

@register("double_factorial", CAT_COMB, "Double factorial n!!", 1, exact=True, example="double_factorial(5) => 15")
def func_double_factorial(n):
    nv = _whole(n, "double_factorial")
    if nv < -1:
        raise MathError("double_factorial domain error")
    if nv in (-1, 0, 1): return 1
    ans = 1
    for i in range(nv, 0, -2):
        ans *= i
    return ans

@register("rising_factorial", CAT_COMB, "Rising factorial (x)_n", 2, exact=True, example="rising_factorial(2, 3) => 24")
def func_rising_factorial(x, n):
    nv = _whole(n, "rising_factorial")
    if nv < 0:
        raise MathError("rising_factorial requires n >= 0")
    xv = x if isinstance(x, (int, Fraction)) and not isinstance(x, bool) else float(x)
    ans = 1
    for i in range(nv):
        ans *= (xv + i)
    if isinstance(ans, Fraction) and ans.denominator == 1:
        return int(ans)
    return int(ans) if isinstance(ans, float) and ans.is_integer() else ans

@register("falling_factorial", CAT_COMB, "Falling factorial (x)_n", 2, exact=True, example="falling_factorial(5, 2) => 20")
def func_falling_factorial(x, n):
    nv = _whole(n, "falling_factorial")
    if nv < 0:
        raise MathError("falling_factorial requires n >= 0")
    xv = x if isinstance(x, (int, Fraction)) and not isinstance(x, bool) else float(x)
    ans = 1
    for i in range(nv):
        ans *= (xv - i)
    if isinstance(ans, Fraction) and ans.denominator == 1:
        return int(ans)
    return int(ans) if isinstance(ans, float) and ans.is_integer() else ans

@register("triangular_num", CAT_COMB, "n-th triangular number", 1, exact=True, example="triangular_num(4) => 10")
def func_triangular_num(n):
    nv = _whole(n, "triangular_num")
    if nv < 0:
        raise MathError("triangular_num requires n >= 0")
    return nv * (nv + 1) // 2

@register("polygonal_num", CAT_COMB, "n-th s-gonal number", 2, exact=True, example="polygonal_num(5, 4) => 22")
def func_polygonal_num(s, n):
    sv = _whole(s, "polygonal_num")
    nv = _whole(n, "polygonal_num")
    if sv < 3 or nv < 0:
        raise MathError("polygonal_num requires s >= 3 and n >= 0")
    return ((sv - 2) * nv * nv - (sv - 4) * nv) // 2

@register("tetrahedral_num", CAT_COMB, "n-th tetrahedral number", 1, exact=True, example="tetrahedral_num(4) => 20")
def func_tetrahedral_num(n):
    nv = _whole(n, "tetrahedral_num")
    if nv < 0:
        raise MathError("tetrahedral_num requires n >= 0")
    return nv * (nv + 1) * (nv + 2) // 6
