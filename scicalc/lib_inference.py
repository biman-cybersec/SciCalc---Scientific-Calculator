"""Sprint 1D/1E: inference, hypothesis tests, non-parametric tests

Module 19 of 47.  Taken from lines 5317-5975 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_inference"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import REGISTRY, register
from .arithmetic import Lst, ar_add, ar_div
from .lib_special_functions import beta_inc, gamma_inc_p
from .lib_distributions import CAT_PROB_DIST, binom_cdf, chisq_inv, norm_inv, t_cdf, t_inv
from .lib_regression import (
    CAT_STAT_REG,
    _parse_numeric_args,
    _split_bivariate_args,
    coefficient_of_variation,
    percentile,
    quartile2,
)

# ==============================================================================
# SPRINT 1 - BATCH 1D: STATISTICAL INFERENCE & HYPOTHESIS TESTING (17 Functions)
# ==============================================================================

CAT_INFERENCE = "Statistical Inference"


@register("critical_z", CAT_INFERENCE, "Calculate critical z-value for significance level alpha (two-tailed by default)", args=(1, 2), example="critical_z(0.05) => 1.959963985")
def critical_z(alpha, tails=2):
    alpha, tails = float(alpha), int(tails)
    if alpha <= 0.0 or alpha >= 1.0 or tails not in (1, 2):
        raise ValueError("Math ERROR")
    p = 1.0 - (alpha / tails)
    return norm_inv(p, 0.0, 1.0)


@register("critical_t", CAT_INFERENCE, "Calculate critical t-value for df degrees of freedom and significance level alpha", args=(2, 3), example="critical_t(0.05, 10) => 2.228138852")
def critical_t(alpha, df, tails=2):
    alpha, df, tails = float(alpha), float(df), int(tails)
    if alpha <= 0.0 or alpha >= 1.0 or df <= 0.0 or tails not in (1, 2):
        raise ValueError("Math ERROR")
    p = 1.0 - (alpha / tails)
    return t_inv(p, df)


@register("critical_chi2", CAT_INFERENCE, "Calculate critical chi-square value for df degrees of freedom and significance level alpha", args=(2, 2), example="critical_chi2(0.05, 5) => 11.07049769")
def critical_chi2(alpha, df):
    alpha, df = float(alpha), float(df)
    if alpha <= 0.0 or alpha >= 1.0 or df <= 0.0:
        raise ValueError("Math ERROR")
    return chisq_inv(1.0 - alpha, df)


@register("ci_z_mean", CAT_INFERENCE, "Calculate z-based confidence interval for population mean given mean, stdev, sample size n, and confidence level", args=(4, 4), example="ci_z_mean(50, 5, 30, 0.95) => {48.21080586, 51.78919414}")
def ci_z_mean(mean_val, stdev, n, confidence=0.95):
    mean_val, stdev, n, confidence = float(mean_val), float(stdev), int(n), float(confidence)
    if stdev <= 0.0 or n <= 0 or not (0.0 < confidence < 1.0):
        raise ValueError("Math ERROR")
    alpha = 1.0 - confidence
    z_val = critical_z(alpha, tails=2)
    margin = z_val * (stdev / math.sqrt(n))
    return Lst((round(mean_val - margin, 9), round(mean_val + margin, 9)))


@register("ci_t_mean", CAT_INFERENCE, "Calculate t-based confidence interval for population mean given mean, stdev, sample size n, and confidence level", args=(4, 4), example="ci_t_mean(50, 5, 10, 0.95) => {46.42321547, 53.57678453}")
def ci_t_mean(mean_val, stdev, n, confidence=0.95):
    mean_val, stdev, n, confidence = float(mean_val), float(stdev), int(n), float(confidence)
    if stdev <= 0.0 or n <= 1 or not (0.0 < confidence < 1.0):
        raise ValueError("Math ERROR")
    alpha = 1.0 - confidence
    t_val = critical_t(alpha, df=n-1, tails=2)
    margin = t_val * (stdev / math.sqrt(n))
    return Lst((round(mean_val - margin, 9), round(mean_val + margin, 9)))


@register("ci_proportion", CAT_INFERENCE, "Calculate confidence interval for population proportion given successes x, sample size n, and confidence level", args=(3, 3), example="ci_proportion(45, 100, 0.95) => {0.352493023, 0.547506977}")
def ci_proportion(x, n, confidence=0.95):
    x, n, confidence = int(x), int(n), float(confidence)
    if n <= 0 or x < 0 or x > n or not (0.0 < confidence < 1.0):
        raise ValueError("Math ERROR")
    p_hat = x / n
    alpha = 1.0 - confidence
    z_val = critical_z(alpha, tails=2)
    se = math.sqrt((p_hat * (1.0 - p_hat)) / n)
    margin = z_val * se
    return Lst((round(max(0.0, p_hat - margin), 9), round(min(1.0, p_hat + margin), 9)))


@register("t_stat_one_sample", CAT_INFERENCE, "Calculate one-sample t-test statistic given sample mean, hypothesized mean, stdev, and sample size n", args=(4, 4), example="t_stat_one_sample(52, 50, 5, 20) => 1.788854382")
def t_stat_one_sample(sample_mean, hypothesized_mean, stdev, n):
    sample_mean, hypothesized_mean, stdev, n = float(sample_mean), float(hypothesized_mean), float(stdev), int(n)
    if stdev <= 0.0 or n <= 1:
        raise ValueError("Math ERROR")
    return (sample_mean - hypothesized_mean) / (stdev / math.sqrt(n))


@register("t_stat_two_sample", CAT_INFERENCE, "Calculate independent two-sample t-test statistic (equal variance assumed)", args=(6, 6), example="t_stat_two_sample(52, 48, 5, 5, 20, 20) => 2.529822128")
def t_stat_two_sample(mean1, mean2, stdev1, stdev2, n1, n2):
    mean1, mean2, stdev1, stdev2, n1, n2 = float(mean1), float(mean2), float(stdev1), float(stdev2), int(n1), int(n2)
    if stdev1 <= 0.0 or stdev2 <= 0.0 or n1 <= 1 or n2 <= 1:
        raise ValueError("Math ERROR")
    sp_sq = (((n1 - 1) * (stdev1 ** 2)) + ((n2 - 1) * (stdev2 ** 2))) / (n1 + n2 - 2)
    se = math.sqrt(sp_sq * ((1.0 / n1) + (1.0 / n2)))
    if se == 0:
        return 0.0
    return (mean1 - mean2) / se


@register("p_value_z", CAT_INFERENCE, "Calculate p-value for a given z-score and number of tails (1 or 2)", args=(1, 2), example="p_value_z(1.96, 2) => 0.0499957903")
def p_value_z(z_score_val, tails=2):
    z_score_val, tails = float(z_score_val), int(tails)
    if tails not in (1, 2):
        raise ValueError("Math ERROR")
    cdf = 0.5 * (1.0 + math.erf(abs(z_score_val) / math.sqrt(2.0)))
    p_one_tailed = 1.0 - cdf
    return p_one_tailed * tails if tails == 2 else p_one_tailed


@register("p_value_t", CAT_INFERENCE, "Calculate p-value for a given t-statistic and degrees of freedom df", args=(2, 3), example="p_value_t(2.5, 15, 2) => 0.02450580325")
def p_value_t(t_stat_val, df, tails=2):
    t_stat_val, df, tails = float(t_stat_val), float(df), int(tails)
    if df <= 0.0 or tails not in (1, 2):
        raise ValueError("Math ERROR")
    cdf = t_cdf(abs(t_stat_val), df)
    p_one_tailed = 1.0 - cdf
    return p_one_tailed * tails if tails == 2 else p_one_tailed


@register("cohens_d_one_sample", CAT_INFERENCE, "Calculate Cohen's d effect size for one sample (mean - hypothesized) / stdev", args=(3, 3), example="cohens_d_one_sample(52, 50, 5) => 0.4")
def cohens_d_one_sample(sample_mean, hypothesized_mean, stdev):
    sample_mean, hypothesized_mean, stdev = float(sample_mean), float(hypothesized_mean), float(stdev)
    if stdev <= 0.0:
        raise ValueError("Math ERROR")
    return (sample_mean - hypothesized_mean) / stdev


@register("cohens_d_two_sample", CAT_INFERENCE, "Calculate Cohen's d effect size for independent samples using pooled standard deviation", args=(6, 6), example="cohens_d_two_sample(52, 48, 5, 5, 20, 20) => 0.8")
def cohens_d_two_sample(mean1, mean2, stdev1, stdev2, n1, n2):
    mean1, mean2, stdev1, stdev2, n1, n2 = float(mean1), float(mean2), float(stdev1), float(stdev2), int(n1), int(n2)
    if stdev1 <= 0.0 or stdev2 <= 0.0 or n1 <= 1 or n2 <= 1:
        raise ValueError("Math ERROR")
    sp = math.sqrt((((n1 - 1) * (stdev1 ** 2)) + ((n2 - 1) * (stdev2 ** 2))) / (n1 + n2 - 2))
    if sp == 0:
        return 0.0
    return (mean1 - mean2) / sp


@register("sample_size_mean", CAT_INFERENCE, "Calculate required sample size for estimating a population mean given stdev, margin of error E, and confidence level", args=(3, 3), example="sample_size_mean(5, 1, 0.95) => 97")
def sample_size_mean(stdev, margin_error, confidence=0.95):
    stdev, margin_error, confidence = float(stdev), float(margin_error), float(confidence)
    if stdev <= 0.0 or margin_error <= 0.0 or not (0.0 < confidence < 1.0):
        raise ValueError("Math ERROR")
    alpha = 1.0 - confidence
    z_val = critical_z(alpha, tails=2)
    n = (z_val * stdev / margin_error) ** 2
    return math.ceil(n)


@register("sample_size_proportion", CAT_INFERENCE, "Calculate required sample size for estimating a population proportion given margin of error E and confidence level (uses p=0.5 max variance)", args=(2, 3), example="sample_size_proportion(0.05, 0.95) => 385")
def sample_size_proportion(margin_error, confidence=0.95, p=0.5):
    margin_error, confidence, p = float(margin_error), float(confidence), float(p)
    if margin_error <= 0.0 or not (0.0 < confidence < 1.0) or not (0.0 < p < 1.0):
        raise ValueError("Math ERROR")
    alpha = 1.0 - confidence
    z_val = critical_z(alpha, tails=2)
    n = (z_val ** 2 * p * (1.0 - p)) / (margin_error ** 2)
    return math.ceil(n)


@register("z_test_one_proportion", CAT_INFERENCE, "Calculate one-proportion z-test statistic given successes x, sample size n, and hypothesized proportion p0", args=(3, 3), example="z_test_one_proportion(55, 100, 0.5) => 1")
def z_test_one_proportion(x, n, p0):
    x, n, p0 = int(x), int(n), float(p0)
    if n <= 0 or x < 0 or x > n or not (0.0 < p0 < 1.0):
        raise ValueError("Math ERROR")
    p_hat = x / n
    se = math.sqrt((p0 * (1.0 - p0)) / n)
    if se == 0:
        return 0.0
    return (p_hat - p0) / se


@register("chi2_goodness_of_fit", CAT_INFERENCE, "Calculate Chi-square goodness-of-fit statistic given observed counts and expected counts lists", args=(2, 99), example="chi2_goodness_of_fit(10, 20, 30, 15, 15, 30) => 3.333333333")
def chi2_goodness_of_fit(*args):
    if len(args) == 2 and isinstance(args[0], (list, tuple)) and isinstance(args[1], (list, tuple)):
        obs, exp = [float(x) for x in args[0]], [float(x) for x in args[1]]
    else:
        flat = _parse_numeric_args(args)
        half = len(flat) // 2
        obs, exp = flat[:half], flat[half:]
    if len(obs) != len(exp) or not obs or any(e <= 0 for e in exp):
        raise ValueError("Math ERROR")
    return sum(((o - e) ** 2) / e for o, e in zip(obs, exp))


@register("chi2_contingency", CAT_INFERENCE, "Calculate Chi-square statistic for a 2x2 contingency table given 4 cell counts [a, b, c, d]", args=(4, 4), example="chi2_contingency(20, 30, 15, 35) => 1.098901099")
def chi2_contingency(a, b, c, d):
    a, b, c, d = float(a), float(b), float(c), float(d)
    n = a + b + c + d
    if n <= 0 or (a + b) == 0 or (c + d) == 0 or (a + c) == 0 or (b + d) == 0:
        raise ValueError("Math ERROR")
    num = n * ((a * d - b * c) ** 2)
    den = (a + b) * (c + d) * (a + c) * (b + d)
    return num / den


# ==============================================================================
# SPRINT 1 - GAP FILL: roadmap functions that were missing or built under another name
# ==============================================================================
# Argument conventions follow ROADMAP_700.md. Where an older function already does the job
# the roadmap name is added as an alias (aliases are NOT counted as functions).
# Known differences that were kept on purpose (documented in PROJECT_NOTES.md):
#   moment(k, ...)            central moment (roadmap: raw)   -> raw_moment(k, ...) is the raw one
#   hypergeom_pmf/cdf         (k, N, K, n)  (roadmap: N, K, n, k)
#   gamma_pdf/cdf             shape + RATE  (roadmap: shape + scale theta)
#   critical_z/t/chi2         take alpha    (roadmap: confidence in %)
# New *_ci_*, p-value and sample-size functions below take the confidence in PERCENT (95).


def _conf_pct(conf):
    c = float(conf) / 100.0
    if not 0.0 < c < 1.0:
        raise ValueError("Math ERROR")
    return c


@register("mode", CAT_STAT_REG, "Most frequent value (the smallest one if tied): mode(x1, x2, ...)", args=(1, None),
          exact=True, example="mode(1,2,2,3) => 2")
def mode_(*xs):
    counts = {}
    for x in xs:
        counts[x] = counts.get(x, 0) + 1
    best = max(counts.values())
    return min(k for k, v in counts.items() if v == best)


@register("mode_count", CAT_STAT_REG, "How many times the most frequent value occurs: mode_count(x1, ...)", args=(1, None),
          exact=True, example="mode_count(1,2,2,3) => 2")
def mode_count(*xs):
    counts = {}
    for x in xs:
        counts[x] = counts.get(x, 0) + 1
    return max(counts.values())


@register("total", CAT_STAT_REG, "Sum of the values: total(x1, ...)", args=(1, None), exact=True,
          example="total(1,2,3.5) => 6.5")
def total_(*xs):
    return sum(xs)


@register("sum_sq", CAT_STAT_REG, "Sum of squares: sum_sq(x1, ...)", args=(1, None), exact=True,
          example="sum_sq(1,2,3) => 14")
def sum_sq(*xs):
    return sum(x * x for x in xs)


@register("q1", CAT_STAT_REG, "First quartile (linear interpolation): q1(x1, ...)", args=(1, None),
          example="q1(1,2,3,4,5,6,7,8) => 2.75")
def q1(*xs):
    return percentile(25.0, *xs)


@register("q3", CAT_STAT_REG, "Third quartile (linear interpolation): q3(x1, ...)", args=(1, None),
          example="q3(1,2,3,4,5,6,7,8) => 6.25")
def q3(*xs):
    return percentile(75.0, *xs)


@register("quantile", CAT_STAT_REG, "q-th quantile, q from 0 to 1: quantile(q, x1, ...)", args=(2, None),
          example="quantile(0.5,1,2,3,4) => 2.5")
def quantile(q, *xs):
    return percentile(float(q) * 100.0, *xs)


@register("median_abs_dev", CAT_STAT_REG, "Median absolute deviation: median of |x - median|", args=(1, None),
          example="median_abs_dev(1,2,3,4,100) => 1")
def median_abs_dev(*xs):
    med = quartile2(*xs)
    return quartile2(*[abs(float(x) - med) for x in xs])


@register("cv", CAT_STAT_REG, "Coefficient of variation in % (sample stdev / mean * 100)", args=(1, None),
          example="cv(2,4,4,4,5,5,7,9) => 42.76179871")
def cv(*xs):
    return coefficient_of_variation(*xs) * 100.0


@register("midrange", CAT_STAT_REG, "(smallest + largest) / 2", args=(1, None), exact=True,
          example="midrange(1,5,10) => 5.5")
def midrange(*xs):
    return ar_div(ar_add(min(xs), max(xs)), 2)


@register("skew_pop", CAT_STAT_REG, "Population skewness m3 / m2^1.5", args=(1, None),
          example="skew_pop(1,2,3,4,10) => 1.138419958")
def skew_pop(*xs):
    n = len(xs)
    m = sum(xs) / n
    m2 = sum((x - m) ** 2 for x in xs) / n
    if m2 == 0:
        raise MathError("all values are equal")
    m3 = sum((x - m) ** 3 for x in xs) / n
    return m3 / m2 ** 1.5


@register("raw_moment", CAT_STAT_REG, "k-th raw moment, the mean of x^k: raw_moment(k, x1, ...)", args=(2, None),
          example="raw_moment(2,1,2,3) => 4.666666667")
def raw_moment(k, *xs):
    return sum(x ** int(k) for x in xs) / len(xs)


@register("cov_pop", CAT_STAT_REG, "Population covariance of X and Y (x1..xn then y1..yn)", args=(4, 99),
          example="cov_pop(1,2,3,2,4,6) => 1.333333333")
def cov_pop(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / n


@register("expon_inv", CAT_PROB_DIST, "Exponential inverse CDF: value with cumulative probability p and rate lambda",
          args=2, example="expon_inv(0.5,1) => 0.6931471806")
def expon_inv(p, rate):
    p, rate = float(p), float(rate)
    if not 0.0 <= p < 1.0 or rate <= 0.0:
        raise ValueError("Math ERROR")
    return -math.log1p(-p) / rate


@register("binomial_cdf", CAT_PROB_DIST, "Binomial P(X <= k) with the roadmap order: binomial_cdf(n, k, p)", args=3,
          example="binomial_cdf(5,3,0.5) => 0.8125")
def binomial_cdf(n, k, p):
    return binom_cdf(k, n, p)


# ---- intervals and tests (confidence in percent) ----

def _z_margin(sigma, n, conf):
    c = _conf_pct(conf)
    if sigma < 0 or n <= 0:
        raise ValueError("Math ERROR")
    return norm_inv(1.0 - (1.0 - c) / 2.0, 0.0, 1.0) * float(sigma) / math.sqrt(n)


def _t_margin(s, n, conf):
    c = _conf_pct(conf)
    if s < 0 or n <= 1:
        raise ValueError("Math ERROR")
    return t_inv(1.0 - (1.0 - c) / 2.0, n - 1) * float(s) / math.sqrt(n)


def _p_margin(x, n, conf):
    c = _conf_pct(conf)
    x, n = float(x), float(n)
    if n <= 0 or x < 0 or x > n:
        raise ValueError("Math ERROR")
    ph = x / n
    return ph, norm_inv(1.0 - (1.0 - c) / 2.0, 0.0, 1.0) * math.sqrt(ph * (1.0 - ph) / n)


@register("z_ci_low", CAT_INFERENCE, "Lower end of a z interval for a mean: z_ci_low(mean, sigma, n, conf%)", args=4,
          example="z_ci_low(50,5,30,95) => 48.21080586")
def z_ci_low(mean_val, sigma, n, conf):
    return float(mean_val) - _z_margin(sigma, n, conf)


@register("z_ci_high", CAT_INFERENCE, "Upper end of a z interval for a mean: z_ci_high(mean, sigma, n, conf%)", args=4,
          example="z_ci_high(50,5,30,95) => 51.78919414")
def z_ci_high(mean_val, sigma, n, conf):
    return float(mean_val) + _z_margin(sigma, n, conf)


@register("t_ci_low", CAT_INFERENCE, "Lower end of a t interval for a mean: t_ci_low(mean, s, n, conf%)", args=4,
          example="t_ci_low(50,5,10,95) => 46.42321547")
def t_ci_low(mean_val, s, n, conf):
    return float(mean_val) - _t_margin(s, n, conf)


@register("t_ci_high", CAT_INFERENCE, "Upper end of a t interval for a mean: t_ci_high(mean, s, n, conf%)", args=4,
          example="t_ci_high(50,5,10,95) => 53.57678453")
def t_ci_high(mean_val, s, n, conf):
    return float(mean_val) + _t_margin(s, n, conf)


@register("prop_ci_low", CAT_INFERENCE, "Lower end of a proportion interval: prop_ci_low(x, n, conf%)", args=3,
          example="prop_ci_low(45,100,95) => 0.3524930229")
def prop_ci_low(x, n, conf):
    ph, m = _p_margin(x, n, conf)
    return max(0.0, ph - m)


@register("prop_ci_high", CAT_INFERENCE, "Upper end of a proportion interval: prop_ci_high(x, n, conf%)", args=3,
          example="prop_ci_high(45,100,95) => 0.5475069771")
def prop_ci_high(x, n, conf):
    ph, m = _p_margin(x, n, conf)
    return min(1.0, ph + m)


@register("t_stat_two", CAT_INFERENCE, "Two-sample (Welch) t statistic: t_stat_two(m1, s1, n1, m2, s2, n2)", args=6,
          example="t_stat_two(52,5,20,48,5,20) => 2.529822128")
def t_stat_two(m1, s1, n1, m2, s2, n2):
    if n1 <= 1 or n2 <= 1 or s1 < 0 or s2 < 0:
        raise ValueError("Math ERROR")
    se = math.sqrt(float(s1) ** 2 / n1 + float(s2) ** 2 / n2)
    if se == 0:
        raise MathError("both standard deviations are zero")
    return (float(m1) - float(m2)) / se


@register("z_p_two", CAT_INFERENCE, "Two-tailed p-value of a z statistic", args=1,
          example="z_p_two(1.96) => 0.0499957903")
def z_p_two(z):
    return math.erfc(abs(float(z)) / math.sqrt(2.0))


@register("t_p_two", CAT_INFERENCE, "Two-tailed p-value of a t statistic: t_p_two(t, df)", args=2,
          example="t_p_two(2.5,15) => 0.02450580325")
def t_p_two(t, df):
    t, df = float(t), float(df)
    if df <= 0.0:
        raise ValueError("Math ERROR")
    return beta_inc(df / 2.0, 0.5, df / (df + t * t))


@register("chi2_p", CAT_INFERENCE, "Right-tail p-value of a chi-square statistic: chi2_p(x, df)", args=2,
          example="chi2_p(11.07049769,5) => 0.05000000007")
def chi2_p(x, df):
    x, df = float(x), float(df)
    if df <= 0.0 or x < 0.0:
        raise ValueError("Math ERROR")
    return 1.0 - gamma_inc_p(df / 2.0, x / 2.0)


@register("cohen_d", CAT_INFERENCE, "Cohen's d with a pooled stdev: cohen_d(m1, s1, n1, m2, s2, n2)", args=6,
          example="cohen_d(52,5,20,48,5,20) => 0.8")
def cohen_d(m1, s1, n1, m2, s2, n2):
    if n1 <= 1 or n2 <= 1 or s1 < 0 or s2 < 0:
        raise ValueError("Math ERROR")
    sp = math.sqrt(((n1 - 1) * float(s1) ** 2 + (n2 - 1) * float(s2) ** 2) / (n1 + n2 - 2))
    if sp == 0:
        raise MathError("pooled standard deviation is zero")
    return (float(m1) - float(m2)) / sp


@register("sample_size_prop", CAT_INFERENCE, "Sample size for a proportion: sample_size_prop(p, margin, conf%)", args=3,
          example="sample_size_prop(0.5,0.05,95) => 385")
def sample_size_prop(p, margin, conf):
    p, margin = float(p), float(margin)
    if not 0.0 < p < 1.0 or margin <= 0.0:
        raise ValueError("Math ERROR")
    z = norm_inv(1.0 - (1.0 - _conf_pct(conf)) / 2.0, 0.0, 1.0)
    return math.ceil(z * z * p * (1.0 - p) / (margin * margin))


# roadmap names for functions that already exist
for _alias, _target in [
        ("mean_abs_dev", "mad"), ("central_moment", "moment"), ("cov_sample", "covariance"),
        ("corr", "pearson_corr"), ("r_squared", "linreg_r2"), ("spearman_rho", "spearman_corr"),
        ("linreg_predict", "linreg_pred"), ("powreg_a", "powerreg_a"), ("powreg_b", "powerreg_b"),
        ("expon_pdf", "exp_pdf"), ("expon_cdf", "exp_cdf"), ("geometric_pmf", "geom_pmf"),
        ("geometric_cdf", "geom_cdf"), ("chi2_pdf", "chisq_pdf"), ("chi2_cdf", "chisq_cdf"),
        ("chi2_inv", "chisq_inv"), ("t_stat_one", "t_stat_one_sample")]:
    REGISTRY.add_alias(_alias, _target)


# ==============================================================================
# SPRINT 1 - BATCH 1E: NON-PARAMETRIC TESTS & ANOVA
# ==============================================================================

CAT_NONPARAM = "Non-Parametric & ANOVA"


@register("mann_whitney_u", CAT_NONPARAM, "Calculate Mann-Whitney U statistic for two independent samples", args=(2, 99), example="mann_whitney_u(1, 2, 3, 4, 3, 4, 5, 6) => 2")
def mann_whitney_u(*args):
    if len(args) == 2 and isinstance(args[0], (list, tuple)) and isinstance(args[1], (list, tuple)):
        g1, g2 = [float(x) for x in args[0]], [float(x) for x in args[1]]
    else:
        flat = _parse_numeric_args(args)
        half = len(flat) // 2
        g1, g2 = flat[:half], flat[half:]
    n1, n2 = len(g1), len(g2)
    if n1 == 0 or n2 == 0:
        raise ValueError("Math ERROR")
    
    combined = [(val, 1) for val in g1] + [(val, 2) for val in g2]
    combined.sort(key=lambda x: x[0])
    
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
        
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 1)
    u1 = n1 * n2 + (n1 * (n1 + 1)) / 2.0 - r1
    u2 = n1 * n2 - u1
    return min(u1, u2)


@register("wilcoxon_signed_rank", CAT_NONPARAM, "Calculate Wilcoxon signed-rank test statistic for paired samples", args=(2, 99), example="wilcoxon_signed_rank(125, 115, 130, 140, 142, 110, 122, 125, 120, 130) => 2")
def wilcoxon_signed_rank(*args):
    if len(args) == 2 and isinstance(args[0], (list, tuple)) and isinstance(args[1], (list, tuple)):
        x, y = [float(a) for a in args[0]], [float(a) for a in args[1]]
    else:
        flat = _parse_numeric_args(args)
        half = len(flat) // 2
        x, y = flat[:half], flat[half:]
    if len(x) != len(y) or len(x) == 0:
        raise ValueError("Math ERROR")
    
    diffs = [a - b for a, b in zip(x, y)]
    non_zero = [(d, abs(d)) for d in diffs if d != 0]
    if not non_zero:
        return 0.0
    
    non_zero.sort(key=lambda item: item[1])
    
    ranks = [0.0] * len(non_zero)
    i = 0
    while i < len(non_zero):
        j = i
        while j < len(non_zero) and non_zero[j][1] == non_zero[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
        
    w_pos = sum(ranks[k] for k in range(len(non_zero)) if non_zero[k][0] > 0)
    w_neg = sum(ranks[k] for k in range(len(non_zero)) if non_zero[k][0] < 0)
    return min(w_pos, w_neg)


@register("kruskal_wallis", CAT_NONPARAM, "Calculate Kruskal-Wallis H-test statistic for multiple independent samples", args=(1, 99), example="kruskal_wallis(2, 3, 4, 4, 5, 6, 7, 8, 9) => 6.822222222")
def kruskal_wallis(*args):
    groups = []
    if len(args) == 1 and isinstance(args[0], (list, tuple)) and all(isinstance(g, (list, tuple)) for g in args[0]):
        groups = [[float(x) for x in g] for g in args[0]]
    elif all(isinstance(a, (list, tuple)) for a in args):
        groups = [[float(x) for x in g] for g in args]
    else:
        flat = _parse_numeric_args(args)
        chunk = len(flat) // 3
        groups = [flat[:chunk], flat[chunk:2*chunk], flat[2*chunk:]]
    
    k = len(groups)
    if k < 2:
        raise ValueError("Math ERROR")
    
    all_data = []
    for g_idx, g in enumerate(groups):
        for val in g:
            all_data.append((val, g_idx))
            
    N = len(all_data)
    if N <= k:
        raise ValueError("Math ERROR")
        
    all_data.sort(key=lambda x: x[0])
    
    ranks = [0.0] * N
    i = 0
    while i < N:
        j = i
        while j < N and all_data[j][0] == all_data[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k_idx in range(i, j):
            ranks[k_idx] = avg_rank
        i = j
        
    group_ranks_sums = [0.0] * k
    group_counts = [0] * k
    for idx, (_, g_idx) in enumerate(all_data):
        group_ranks_sums[g_idx] += ranks[idx]
        group_counts[g_idx] += 1
        
    term = sum((r ** 2) / n for r, n in zip(group_ranks_sums, group_counts))
    h = (12.0 / (N * (N + 1))) * term - 3.0 * (N + 1)
    return h


@register("anova_one_way", CAT_NONPARAM, "Calculate One-Way ANOVA F-statistic for multiple groups", args=(1, 99), example="anova_one_way(3, 1, 2, 5, 4, 6, 7, 8, 9) => 27")
def anova_one_way(*args):
    groups = []
    if len(args) == 1 and isinstance(args[0], (list, tuple)) and all(isinstance(g, (list, tuple)) for g in args[0]):
        groups = [[float(x) for x in g] for g in args[0]]
    elif all(isinstance(a, (list, tuple)) for a in args):
        groups = [[float(x) for x in g] for g in args]
    else:
        flat = _parse_numeric_args(args)
        chunk = len(flat) // 3
        groups = [flat[:chunk], flat[chunk:2*chunk], flat[2*chunk:]]
        
    k = len(groups)
    if k < 2:
        raise ValueError("Math ERROR")
        
    flat_all = [val for g in groups for val in g]
    N = len(flat_all)
    if N <= k:
        raise ValueError("Math ERROR")
        
    grand_mean = sum(flat_all) / N
    
    ss_between = 0.0
    ss_within = 0.0
    
    for g in groups:
        n_j = len(g)
        if n_j == 0:
            raise ValueError("Math ERROR")
        mean_j = sum(g) / n_j
        ss_between += n_j * ((mean_j - grand_mean) ** 2)
        ss_within += sum((x - mean_j) ** 2 for x in g)
        
    df_between = k - 1
    df_within = N - k
    
    if df_within == 0 or ss_within == 0:
        return float('inf') if ss_between > 0 else 0.0
        
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    
    return ms_between / ms_within


@register("friedman_chisq", CAT_NONPARAM, "Calculate Friedman test chi-square statistic for repeated measures / randomized blocks", args=(1, 99), example="friedman_chisq(1, 2, 3, 2, 3, 4, 3, 4, 5) => 6")
def friedman_chisq(*args):
    groups = []
    if len(args) == 1 and isinstance(args[0], (list, tuple)) and all(isinstance(g, (list, tuple)) for g in args[0]):
        groups = [[float(x) for x in g] for g in args[0]]
    elif all(isinstance(a, (list, tuple)) for a in args):
        groups = [[float(x) for x in g] for g in args]
    else:
        flat = _parse_numeric_args(args)
        chunk = len(flat) // 3
        groups = [flat[:chunk], flat[chunk:2*chunk], flat[2*chunk:]]
        
    k = len(groups)
    if k < 2:
        raise ValueError("Math ERROR")
    n = len(groups[0])
    for g in groups:
        if len(g) != n:
            raise ValueError("Math ERROR")
            
    if n == 0:
        raise ValueError("Math ERROR")
        
    block_ranks = []
    for i in range(n):
        row_vals = [(groups[j][i], j) for j in range(k)]
        row_vals.sort(key=lambda x: x[0])
        ranks = [0.0] * k
        idx = 0
        while idx < k:
            j = idx
            while j < k and row_vals[j][0] == row_vals[idx][0]:
                j += 1
            avg_rank = (idx + j + 1) / 2.0
            for r_idx in range(idx, j):
                ranks[row_vals[r_idx][1]] = avg_rank
            idx = j
        block_ranks.append(ranks)
        
    column_sums = [sum(block_ranks[i][j] for i in range(n)) for j in range(k)]
    
    sum_sq = sum(r ** 2 for r in column_sums)
    chi2 = (12.0 / (n * k * (k + 1))) * sum_sq - 3.0 * n * (k + 1)
    return chi2
