"""Sprint 1B: probability distributions

Module 17 of 47.  Taken from lines 4557-4907 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_distributions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .registry import register
from .lib_numtheory_basic import ncr
from .lib_special_functions import beta_inc, erf_inv, gamma_inc_p

# ==============================================================================
# SPRINT 1 - BATCH 1B: PROBABILITY DISTRIBUTIONS (30 Functions)
# ==============================================================================

CAT_PROB_DIST = "Probability Distributions"


@register("norm_inv", CAT_PROB_DIST, "Inverse normal CDF (quantile function / PPF) for given probability p in (0,1)", args=3, example="norm_inv(0.5, 0, 1) => 0")
def norm_inv(p, mean=0.0, stdev=1.0):
    p, mean, stdev = float(p), float(mean), float(stdev)
    if p <= 0.0 or p >= 1.0 or stdev <= 0.0:
        raise ValueError("Math ERROR")
    return mean + stdev * math.sqrt(2.0) * erf_inv(2.0 * p - 1.0)


@register("norm_between", CAT_PROB_DIST, "Probability P(a <= X <= b) for normal distribution", args=4, example="norm_between(-1, 1, 0, 1) => 0.6826894921")
def norm_between(a, b, mean=0.0, stdev=1.0):
    a, b, mean, stdev = float(a), float(b), float(mean), float(stdev)
    if stdev <= 0.0:
        raise ValueError("Math ERROR")
    if a > b:
        a, b = b, a
    cdf_b = 0.5 * (1.0 + math.erf((b - mean) / (stdev * math.sqrt(2.0))))
    cdf_a = 0.5 * (1.0 + math.erf((a - mean) / (stdev * math.sqrt(2.0))))
    return cdf_b - cdf_a


@register("binom_pmf", CAT_PROB_DIST, "Binomial PMF P(X = k) for n trials and success probability p", args=3, example="binom_pmf(3, 5, 0.5) => 0.3125")
def binom_pmf(k, n, p):
    k, n, p = int(k), int(n), float(p)
    if n < 0 or k < 0 or k > n or p < 0.0 or p > 1.0:
        raise ValueError("Math ERROR")
    return ncr(n, k) * (p ** k) * ((1.0 - p) ** (n - k))


@register("binom_cdf", CAT_PROB_DIST, "Binomial CDF P(X <= k) for n trials and success probability p", args=3, example="binom_cdf(3, 5, 0.5) => 0.8125")
def binom_cdf(k, n, p):
    k, n, p = int(k), int(n), float(p)
    if n < 0 or k < 0 or p < 0.0 or p > 1.0:
        raise ValueError("Math ERROR")
    if k >= n:
        return 1.0
    total = 0.0
    for i in range(0, min(k, n) + 1):
        total += ncr(n, i) * (p ** i) * ((1.0 - p) ** (n - i))
    return total


@register("geom_pmf", CAT_PROB_DIST, "Geometric PMF P(X = k) for success probability p", args=2, example="geom_pmf(3, 0.5) => 0.125")
def geom_pmf(k, p):
    k, p = int(k), float(p)
    if k < 1 or p <= 0.0 or p > 1.0:
        raise ValueError("Math ERROR")
    return ((1.0 - p) ** (k - 1)) * p


@register("geom_cdf", CAT_PROB_DIST, "Geometric CDF P(X <= k) for success probability p", args=2, example="geom_cdf(3, 0.5) => 0.875")
def geom_cdf(k, p):
    k, p = int(k), float(p)
    if k < 1 or p <= 0.0 or p > 1.0:
        raise ValueError("Math ERROR")
    return 1.0 - ((1.0 - p) ** k)


@register("poisson_cdf", CAT_PROB_DIST, "Poisson CDF P(X <= k) for rate lambda", args=2, example="poisson_cdf(3, 2) => 0.8571234605")
def poisson_cdf(k, lam):
    k, lam = int(k), float(lam)
    if k < 0 or lam <= 0.0:
        raise ValueError("Math ERROR")
    total = 0.0
    for i in range(k + 1):
        total += (lam ** i) * math.exp(-lam) / math.factorial(i)
    return total


@register("hypergeom_pmf", CAT_PROB_DIST, "Hypergeometric PMF P(X = k) given population N, successes K, draws n", args=4, example="hypergeom_pmf(2, 10, 5, 4) => 0.4761904762")
def hypergeom_pmf(k, N, K, n):
    k, N, K, n = int(k), int(N), int(K), int(n)
    if N < 0 or K < 0 or n < 0 or K > N or n > N or k < 0 or k > n:
        raise ValueError("Math ERROR")
    if k > K or (n - k) > (N - K):
        return 0.0
    return (ncr(K, k) * ncr(N - K, n - k)) / ncr(N, n)


@register("hypergeom_cdf", CAT_PROB_DIST, "Hypergeometric CDF P(X <= k) given N, K, n", args=4, example="hypergeom_cdf(2, 10, 5, 4) => 0.7380952381")
def hypergeom_cdf(k, N, K, n):
    k, N, K, n = int(k), int(N), int(K), int(n)
    if N < 0 or K < 0 or n < 0 or K > N or n > N or k < 0:
        raise ValueError("Math ERROR")
    low = max(0, n - (N - K))
    high = min(k, K, n)
    if low > high:
        return 0.0 if k >= low else 0.0
    total = 0.0
    denom = ncr(N, n)
    for i in range(low, min(k, high) + 1):
        total += (ncr(K, i) * ncr(N - K, n - i)) / denom
    return total


@register("exp_pdf", CAT_PROB_DIST, "Exponential distribution PDF for rate lambda", args=2, example="exp_pdf(1, 2) => 0.2706705665")
def exp_pdf(x, lam):
    x, lam = float(x), float(lam)
    if lam <= 0.0 or x < 0.0:
        return 0.0
    return lam * math.exp(-lam * x)


@register("exp_cdf", CAT_PROB_DIST, "Exponential distribution CDF for rate lambda", args=2, example="exp_cdf(1, 2) => 0.8646647168")
def exp_cdf(x, lam):
    x, lam = float(x), float(lam)
    if lam <= 0.0 or x < 0.0:
        return 0.0
    return 1.0 - math.exp(-lam * x)


@register("uniform_pdf", CAT_PROB_DIST, "Continuous Uniform distribution PDF on [a, b]", args=3, example="uniform_pdf(2, 0, 5) => 0.2")
def uniform_pdf(x, a, b):
    x, a, b = float(x), float(a), float(b)
    if a >= b:
        raise ValueError("Math ERROR")
    if a <= x <= b:
        return 1.0 / (b - a)
    return 0.0


@register("uniform_cdf", CAT_PROB_DIST, "Continuous Uniform distribution CDF on [a, b]", args=3, example="uniform_cdf(2, 0, 5) => 0.4")
def uniform_cdf(x, a, b):
    x, a, b = float(x), float(a), float(b)
    if a >= b:
        raise ValueError("Math ERROR")
    if x < a:
        return 0.0
    if x > b:
        return 1.0
    return (x - a) / (b - a)


@register("t_pdf", CAT_PROB_DIST, "Student's t-distribution PDF for df degrees of freedom", args=2, example="t_pdf(1, 5) => 0.2196797974")
def t_pdf(x, df):
    x, df = float(x), float(df)
    if df <= 0.0:
        raise ValueError("Math ERROR")
    num = math.gamma((df + 1.0) / 2.0)
    den = math.sqrt(df * math.pi) * math.gamma(df / 2.0)
    return (num / den) * ((1.0 + (x * x) / df) ** (-(df + 1.0) / 2.0))


@register("t_cdf", CAT_PROB_DIST, "Student's t-distribution CDF for df degrees of freedom", args=2, example="t_cdf(1, 5) => 0.8183912662")
def t_cdf(x, df):
    x, df = float(x), float(df)
    if df <= 0.0:
        raise ValueError("Math ERROR")
    x2 = x * x
    val = 0.5 * beta_inc(df / 2.0, 0.5, df / (df + x2))
    return 1.0 - val if x >= 0 else val


@register("t_inv", CAT_PROB_DIST, "Student's t-distribution inverse CDF (quantile function) for probability p and df", args=2, example="t_inv(0.975, 5) => 2.570581836")
def t_inv(p, df):
    p, df = float(p), float(df)
    if p <= 0.0 or p >= 1.0 or df <= 0.0:
        raise ValueError("Math ERROR")
    # Bisection search
    low, high = -100.0, 100.0
    for _ in range(100):
        mid = 0.5 * (low + high)
        if t_cdf(mid, df) < p:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


@register("chisq_pdf", CAT_PROB_DIST, "Chi-square distribution PDF for df degrees of freedom", args=2, example="chisq_pdf(3, 2) => 0.1115650801")
def chisq_pdf(x, df):
    x, df = float(x), float(df)
    if df <= 0.0 or x < 0.0:
        return 0.0
    if x == 0.0:
        if df == 2.0:
            return 0.5
        elif df < 2.0:
            return float('inf')
        else:
            return 0.0
    return (x ** (df / 2.0 - 1.0) * math.exp(-x / 2.0)) / ((2.0 ** (df / 2.0)) * math.gamma(df / 2.0))


@register("chisq_cdf", CAT_PROB_DIST, "Chi-square distribution CDF for df degrees of freedom", args=2, example="chisq_cdf(3, 2) => 0.7768698399")
def chisq_cdf(x, df):
    x, df = float(x), float(df)
    if df <= 0.0 or x < 0.0:
        raise ValueError("Math ERROR")
    if x == 0.0:
        return 0.0
    return gamma_inc_p(df / 2.0, x / 2.0)


@register("chisq_inv", CAT_PROB_DIST, "Chi-square inverse CDF for probability p and df degrees of freedom", args=2, example="chisq_inv(0.95, 2) => 5.991464547")
def chisq_inv(p, df):
    p, df = float(p), float(df)
    if p <= 0.0 or p >= 1.0 or df <= 0.0:
        raise ValueError("Math ERROR")
    low, high = 0.0, max(10.0, df * 10.0)
    for _ in range(100):
        mid = 0.5 * (low + high)
        if chisq_cdf(mid, df) < p:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


@register("f_pdf", CAT_PROB_DIST, "F-distribution PDF for df1 and df2 degrees of freedom", args=3, example="f_pdf(1, 5, 5) => 0.4244131816")
def f_pdf(x, df1, df2):
    x, df1, df2 = float(x), float(df1), float(df2)
    if df1 <= 0.0 or df2 <= 0.0 or x < 0.0:
        return 0.0
    num = (math.gamma((df1 + df2) / 2.0) * ((df1 / df2) ** (df1 / 2.0)) * (x ** (df1 / 2.0 - 1.0)))
    den = (math.gamma(df1 / 2.0) * math.gamma(df2 / 2.0) * ((1.0 + (df1 / df2) * x) ** ((df1 + df2) / 2.0)))
    return num / den


@register("f_cdf", CAT_PROB_DIST, "F-distribution CDF for df1 and df2 degrees of freedom", args=3, example="f_cdf(1, 5, 5) => 0.5")
def f_cdf(x, df1, df2):
    x, df1, df2 = float(x), float(df1), float(df2)
    if df1 <= 0.0 or df2 <= 0.0 or x < 0.0:
        raise ValueError("Math ERROR")
    if x == 0.0:
        return 0.0
    z = (df1 * x) / (df1 * x + df2)
    return beta_inc(df1 / 2.0, df2 / 2.0, z)


@register("f_inv", CAT_PROB_DIST, "F-distribution inverse CDF (quantile function) for probability p and df1, df2", args=3, example="f_inv(0.5, 5, 5) => 1")
def f_inv(p, df1, df2):
    p, df1, df2 = float(p), float(df1), float(df2)
    if p <= 0.0 or p >= 1.0 or df1 <= 0.0 or df2 <= 0.0:
        raise ValueError("Math ERROR")
    low, high = 0.0, 100.0
    while f_cdf(high, df1, df2) < p:
        high *= 2.0
    for _ in range(100):
        mid = 0.5 * (low + high)
        if f_cdf(mid, df1, df2) < p:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


@register("gamma_pdf", CAT_PROB_DIST, "Gamma distribution PDF with shape alpha and rate beta", args=3, example="gamma_pdf(2, 2, 1) => 0.2706705665")
def gamma_pdf(x, alpha, beta_rate):
    x, alpha, beta_rate = float(x), float(alpha), float(beta_rate)
    if alpha <= 0.0 or beta_rate <= 0.0 or x < 0.0:
        return 0.0
    if x == 0.0:
        if alpha == 1.0:
            return beta_rate
        elif alpha < 1.0:
            return float('inf')
        else:
            return 0.0
    return ((beta_rate ** alpha) / math.gamma(alpha)) * (x ** (alpha - 1.0)) * math.exp(-beta_rate * x)


@register("gamma_cdf", CAT_PROB_DIST, "Gamma distribution CDF with shape alpha and rate beta", args=3, example="gamma_cdf(2, 2, 1) => 0.5939941503")
def gamma_cdf(x, alpha, beta_rate):
    x, alpha, beta_rate = float(x), float(alpha), float(beta_rate)
    if alpha <= 0.0 or beta_rate <= 0.0 or x < 0.0:
        raise ValueError("Math ERROR")
    if x == 0.0:
        return 0.0
    return gamma_inc_p(alpha, beta_rate * x)


@register("beta_pdf", CAT_PROB_DIST, "Beta distribution PDF with parameters alpha and beta on [0, 1]", args=3, example="beta_pdf(0.5, 2, 2) => 1.5")
def beta_pdf(x, alpha, beta_param):
    x, alpha, beta_param = float(x), float(alpha), float(beta_param)
    if alpha <= 0.0 or beta_param <= 0.0 or x < 0.0 or x > 1.0:
        return 0.0
    if x == 0.0 or x == 1.0:
        if alpha == 1.0 and beta_param == 1.0:
            return 1.0
        if (x == 0.0 and alpha < 1.0) or (x == 1.0 and beta_param < 1.0):
            return float('inf')
        return 0.0
    beta_val = math.exp(math.lgamma(alpha) + math.lgamma(beta_param) - math.lgamma(alpha + beta_param))
    return (x ** (alpha - 1.0)) * ((1.0 - x) ** (beta_param - 1.0)) / beta_val


@register("beta_cdf", CAT_PROB_DIST, "Beta distribution CDF with parameters alpha and beta on [0, 1]", args=3, example="beta_cdf(0.5, 2, 2) => 0.5")
def beta_cdf(x, alpha, beta_param):
    x, alpha, beta_param = float(x), float(alpha), float(beta_param)
    if alpha <= 0.0 or beta_param <= 0.0 or x < 0.0 or x > 1.0:
        raise ValueError("Math ERROR")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    return beta_inc(alpha, beta_param, x)


@register("weibull_pdf", CAT_PROB_DIST, "Weibull distribution PDF with shape k and scale lambda", args=3, example="weibull_pdf(1, 2, 1) => 0.7357588823")
def weibull_pdf(x, k, lam):
    x, k, lam = float(x), float(k), float(lam)
    if k <= 0.0 or lam <= 0.0 or x < 0.0:
        return 0.0
    if x == 0.0:
        if k == 1.0:
            return 1.0 / lam
        elif k < 1.0:
            return float('inf')
        else:
            return 0.0
    return (k / lam) * ((x / lam) ** (k - 1.0)) * math.exp(-((x / lam) ** k))


@register("weibull_cdf", CAT_PROB_DIST, "Weibull distribution CDF with shape k and scale lambda", args=3, example="weibull_cdf(1, 2, 1) => 0.6321205588")
def weibull_cdf(x, k, lam):
    x, k, lam = float(x), float(k), float(lam)
    if k <= 0.0 or lam <= 0.0 or x < 0.0:
        raise ValueError("Math ERROR")
    if x == 0.0:
        return 0.0
    return 1.0 - math.exp(-((x / lam) ** k))


@register("lognorm_pdf", CAT_PROB_DIST, "Log-normal distribution PDF with mean mu and stdev sigma of underlying normal", args=3, example="lognorm_pdf(1, 0, 1) => 0.3989422804")
def lognorm_pdf(x, mu=0.0, sigma=1.0):
    x, mu, sigma = float(x), float(mu), float(sigma)
    if sigma <= 0.0 or x <= 0.0:
        return 0.0
    ln_x = math.log(x)
    return (1.0 / (x * sigma * math.sqrt(2.0 * math.pi))) * math.exp(-((ln_x - mu) ** 2) / (2.0 * sigma * sigma))


@register("lognorm_cdf", CAT_PROB_DIST, "Log-normal distribution CDF with mean mu and stdev sigma", args=3, example="lognorm_cdf(1, 0, 1) => 0.5")
def lognorm_cdf(x, mu=0.0, sigma=1.0):
    x, mu, sigma = float(x), float(mu), float(sigma)
    if sigma <= 0.0:
        raise ValueError("Math ERROR")
    if x <= 0.0:
        return 0.0
    ln_x = math.log(x)
    z = (ln_x - mu) / sigma
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
