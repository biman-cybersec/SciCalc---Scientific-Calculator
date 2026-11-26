"""Sprint 1C: statistics and regression

Module 18 of 47.  Taken from lines 4908-5316 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_regression"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .registry import register

# ==============================================================================
# SPRINT 1 - BATCH 1C: ONE- & TWO-VARIABLE STATISTICS & REGRESSION (37 Functions)
# ==============================================================================

CAT_STAT_REG = "Statistics & Regression"


def _parse_numeric_args(args):
    flat = []
    for a in args:
        if isinstance(a, (list, tuple)):
            flat.extend([float(x) for x in a])
        else:
            flat.append(float(a))
    return flat


def _split_bivariate_args(args):
    flat = _parse_numeric_args(args)
    n = len(flat)
    if n % 2 != 0 or n == 0:
        raise ValueError("Math ERROR: bivariate functions require an even number of arguments (X values followed by Y values)")
    half = n // 2
    return flat[:half], flat[half:]


@register("percentile", CAT_STAT_REG, "Calculate the p-th percentile (0 <= p <= 100) of a dataset", args=(2, 99), example="percentile(50, 1, 2, 3, 4, 5) => 3")
def percentile(p, *args):
    flat = _parse_numeric_args(args)
    p = float(p)
    if not (0.0 <= p <= 100.0) or not flat:
        raise ValueError("Math ERROR")
    flat.sort()
    k = (len(flat) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return flat[int(k)]
    return flat[int(f)] * (c - k) + flat[int(c)] * (k - f)


@register("quartile1", CAT_STAT_REG, "Calculate the first quartile (Q1 / 25th percentile) of a dataset", args=(1, 99), example="quartile1(1, 2, 3, 4, 5, 6, 7, 8) => 2.75")
def quartile1(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    return percentile(25.0, *flat)


@register("quartile2", CAT_STAT_REG, "Calculate the second quartile (Q2 / median / 50th percentile) of a dataset", args=(1, 99), example="quartile2(1, 2, 3, 4, 5) => 3")
def quartile2(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    return percentile(50.0, *flat)


@register("quartile3", CAT_STAT_REG, "Calculate the third quartile (Q3 / 75th percentile) of a dataset", args=(1, 99), example="quartile3(1, 2, 3, 4, 5, 6, 7, 8) => 6.25")
def quartile3(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    return percentile(75.0, *flat)


@register("iqr", CAT_STAT_REG, "Calculate the Interquartile Range (IQR = Q3 - Q1) of a dataset", args=(1, 99), example="iqr(1, 2, 3, 4, 5, 6, 7, 8) => 3.5")
def iqr(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    return quartile3(*flat) - quartile1(*flat)


@register("mad", CAT_STAT_REG, "Calculate the Mean Absolute Deviation (MAD) of a dataset", args=(1, 99), example="mad(2, 4, 4, 4, 5, 5, 7, 9) => 1.5")
def mad(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    m = sum(flat) / len(flat)
    return sum(abs(x - m) for x in flat) / len(flat)


@register("trimmed_mean", CAT_STAT_REG, "Calculate the trimmed mean by removing a fraction (0 <= trim < 0.5) from both tails", args=(2, 99), example="trimmed_mean(0.1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10) => 5.5")
def trimmed_mean(trim, *args):
    flat = _parse_numeric_args(args)
    trim = float(trim)
    if not (0.0 <= trim < 0.5) or not flat:
        raise ValueError("Math ERROR")
    flat.sort()
    k = int(len(flat) * trim)
    trimmed = flat[k:len(flat) - k]
    if not trimmed:
        return sum(flat) / len(flat)
    return sum(trimmed) / len(trimmed)


@register("weighted_mean", CAT_STAT_REG, "Calculate the weighted mean given weights in first half and values in second half", args=(2, 99), example="weighted_mean(1, 2, 1, 10, 20, 30) => 20")
def weighted_mean(*args):
    flat = _parse_numeric_args(args)
    n = len(flat)
    if n % 2 != 0 or n == 0:
        raise ValueError("Math ERROR: weighted_mean requires an even number of arguments")
    half = n // 2
    weights = flat[:half]
    values = flat[half:]
    sum_w = sum(weights)
    if sum_w == 0:
        raise ValueError("Math ERROR: sum of weights cannot be zero")
    return sum(w * v for w, v in zip(weights, values)) / sum_w


@register("moment", CAT_STAT_REG, "Calculate the r-th central moment of a dataset", args=(2, 99), example="moment(2, 2, 4, 4, 4, 5, 5, 7, 9) => 4")
def moment(r, *args):
    flat = _parse_numeric_args(args)
    r = int(r)
    if not flat:
        raise ValueError("Math ERROR")
    m = sum(flat) / len(flat)
    return sum((x - m) ** r for x in flat) / len(flat)


@register("kurtosis", CAT_STAT_REG, "Calculate the sample excess kurtosis of a dataset", args=(4, 99), example="kurtosis(1, 2, 3, 4, 5) => -1.2")
def kurtosis(*args):
    flat = _parse_numeric_args(args)
    n = len(flat)
    if n < 4:
        raise ValueError("Math ERROR: kurtosis requires at least 4 data points")
    m = sum(flat) / n
    s2 = sum((x - m) ** 2 for x in flat) / (n - 1)
    if s2 == 0:
        return 0.0
    m4 = sum((x - m) ** 4 for x in flat)
    term1 = (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3)) * (m4 / (s2 ** 2))
    term2 = (3 * ((n - 1) ** 2)) / ((n - 2) * (n - 3))
    return term1 - term2


@register("excess_kurtosis", CAT_STAT_REG, "Calculate sample excess kurtosis (alias for kurtosis)", args=(4, 99), example="excess_kurtosis(1, 2, 3, 4, 5) => -1.2")
def excess_kurtosis(*args):
    return kurtosis(*args)


@register("mean_absolute_deviation_median", CAT_STAT_REG, "Calculate Mean Absolute Deviation around the median", args=(1, 99), example="mean_absolute_deviation_median(2, 4, 4, 4, 5, 5, 7, 9) => 1.5")
def mean_absolute_deviation_median(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    med = quartile2(*flat)
    return sum(abs(x - med) for x in flat) / len(flat)


@register("quartile_skewness", CAT_STAT_REG, "Calculate Bowley's coefficient of skewness based on quartiles", args=(1, 99), example="quartile_skewness(1, 2, 3, 4, 5, 6, 7, 8) => 0")
def quartile_skewness(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    q1_v = quartile1(*flat)
    q2_v = quartile2(*flat)
    q3_v = quartile3(*flat)
    denom = q3_v - q1_v
    if denom == 0:
        return 0.0
    return (q3_v - 2.0 * q2_v + q1_v) / denom


@register("coefficient_of_variation", CAT_STAT_REG, "Calculate the coefficient of variation (stdev / mean)", args=(2, 99), example="coefficient_of_variation(2, 4, 4, 4, 5, 5, 7, 9) => 0.4276179871")
def coefficient_of_variation(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    m = sum(flat) / len(flat)
    if m == 0:
        raise ValueError("Math ERROR: mean cannot be zero")
    var = sum((x - m) ** 2 for x in flat) / (len(flat) - 1) if len(flat) > 1 else 0.0
    return math.sqrt(var) / m


@register("rms_stat", CAT_STAT_REG, "Calculate the Root Mean Square (RMS) of a dataset", args=(1, 99), example="rms_stat(1, 2, 3) => 2.160246899")
def rms_stat(*args):
    flat = _parse_numeric_args(args)
    if not flat:
        raise ValueError("Math ERROR")
    return math.sqrt(sum(x ** 2 for x in flat) / len(flat))


@register("harmonic_mean_stat", CAT_STAT_REG, "Calculate the harmonic mean of a dataset", args=(1, 99), example="harmonic_mean_stat(1, 2, 4) => 1.714285714")
def harmonic_mean_stat(*args):
    flat = _parse_numeric_args(args)
    if not flat or any(x <= 0 for x in flat):
        raise ValueError("Math ERROR: all values must be positive")
    return len(flat) / sum(1.0 / x for x in flat)


@register("geometric_mean_stat", CAT_STAT_REG, "Calculate the geometric mean of a dataset", args=(1, 99), example="geometric_mean_stat(2, 8) => 4")
def geometric_mean_stat(*args):
    flat = _parse_numeric_args(args)
    if not flat or any(x <= 0 for x in flat):
        raise ValueError("Math ERROR: all values must be positive")
    return math.exp(sum(math.log(x) for x in flat) / len(flat))


@register("covariance", CAT_STAT_REG, "Calculate sample covariance between X and Y", args=(4, 99), example="covariance(1, 2, 3, 2, 4, 6) => 2")
def covariance(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    if n < 2:
        raise ValueError("Math ERROR")
    mx, my = sum(x) / n, sum(y) / n
    return sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / (n - 1)


@register("pearson_corr", CAT_STAT_REG, "Calculate Pearson correlation coefficient between X and Y", args=(4, 99), example="pearson_corr(1, 2, 3, 2, 4, 6) => 1")
def pearson_corr(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    if n < 2:
        raise ValueError("Math ERROR")
    mx, my = sum(x) / n, sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den_x = sum((xi - mx) ** 2 for xi in x)
    den_y = sum((yi - my) ** 2 for yi in y)
    if den_x == 0 or den_y == 0:
        return 0.0
    return num / math.sqrt(den_x * den_y)


@register("spearman_corr", CAT_STAT_REG, "Calculate Spearman rank correlation coefficient between X and Y", args=(4, 99), example="spearman_corr(1, 2, 3, 2, 4, 5) => 1")
def spearman_corr(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    if n < 2:
        raise ValueError("Math ERROR")

    def rankdata(seq):
        s = sorted(enumerate(seq), key=lambda t: t[1])
        ranks = [0.0] * len(seq)
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j][1] == s[i][1]:
                j += 1
            avg_rank = (i + j - 1) / 2.0 + 1.0
            for k in range(i, j):
                ranks[s[k][0]] = avg_rank
            i = j
        return ranks

    return pearson_corr(*(rankdata(x) + rankdata(y)))


@register("linreg_slope", CAT_STAT_REG, "Calculate slope for linear regression y = mx + c", args=(4, 99), example="linreg_slope(1, 2, 3, 2, 4, 6) => 2")
def linreg_slope(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = sum((xi - mx) ** 2 for xi in x)
    if den == 0:
        raise ValueError("Math ERROR")
    return num / den


@register("linreg_intercept", CAT_STAT_REG, "Calculate intercept for linear regression y = mx + c", args=(4, 99), example="linreg_intercept(1, 2, 3, 2, 4, 6) => 0")
def linreg_intercept(*args):
    x, y = _split_bivariate_args(args)
    m = linreg_slope(*args)
    mx, my = sum(x) / len(x), sum(y) / len(y)
    return my - m * mx


@register("linreg_r2", CAT_STAT_REG, "Calculate R-squared for linear regression", args=(4, 99), example="linreg_r2(1, 2, 3, 2, 4, 6) => 1")
def linreg_r2(*args):
    r = pearson_corr(*args)
    return r * r


@register("linreg_pred", CAT_STAT_REG, "Predict y for given x using linear regression", args=(5, 99), example="linreg_pred(4, 1, 2, 3, 2, 4, 6) => 8")
def linreg_pred(x_val, *args):
    return linreg_slope(*args) * float(x_val) + linreg_intercept(*args)


@register("quadreg_a", CAT_STAT_REG, "Calculate coefficient a for quadratic regression y = ax^2 + bx + c", args=(6, 99), example="quadreg_a(1, 2, 3, 1, 4, 9) => 1")
def quadreg_a(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    if n < 3:
        raise ValueError("Math ERROR")
    sx, sy = sum(x), sum(y)
    sx2 = sum(xi ** 2 for xi in x)
    sx3 = sum(xi ** 3 for xi in x)
    sx4 = sum(xi ** 4 for xi in x)
    sxy = sum(xi * yi for xi, yi in zip(x, y))
    sx2y = sum((xi ** 2) * yi for xi, yi in zip(x, y))
    det = sx4 * (sx2 * n - sx * sx) - sx3 * (sx3 * n - sx * sx2) + sx2 * (sx3 * sx - sx2 * sx2)
    if abs(det) < 1e-12:
        raise ValueError("Math ERROR")
    det_a = sx2y * (sx2 * n - sx * sx) - sx3 * (sxy * n - sx * sy) + sx2 * (sxy * sx - sx2 * sy)
    return det_a / det


@register("quadreg_b", CAT_STAT_REG, "Calculate coefficient b for quadratic regression y = ax^2 + bx + c", args=(6, 99), example="quadreg_b(1, 2, 3, 1, 4, 9) => 0")
def quadreg_b(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    sx, sy = sum(x), sum(y)
    sx2 = sum(xi ** 2 for xi in x)
    sx3 = sum(xi ** 3 for xi in x)
    sx4 = sum(xi ** 4 for xi in x)
    sxy = sum(xi * yi for xi, yi in zip(x, y))
    sx2y = sum((xi ** 2) * yi for xi, yi in zip(x, y))
    det = sx4 * (sx2 * n - sx * sx) - sx3 * (sx3 * n - sx * sx2) + sx2 * (sx3 * sx - sx2 * sx2)
    if abs(det) < 1e-12:
        raise ValueError("Math ERROR")
    det_b = sx4 * (sxy * n - sx * sy) - sx2y * (sx3 * n - sx * sx2) + sx2 * (sx3 * sy - sx2 * sxy)
    return det_b / det


@register("quadreg_c", CAT_STAT_REG, "Calculate coefficient c for quadratic regression y = ax^2 + bx + c", args=(6, 99), example="quadreg_c(1, 2, 3, 1, 4, 9) => 0")
def quadreg_c(*args):
    x, y = _split_bivariate_args(args)
    n = len(x)
    sx, sy = sum(x), sum(y)
    sx2 = sum(xi ** 2 for xi in x)
    sx3 = sum(xi ** 3 for xi in x)
    sx4 = sum(xi ** 4 for xi in x)
    sxy = sum(xi * yi for xi, yi in zip(x, y))
    sx2y = sum((xi ** 2) * yi for xi, yi in zip(x, y))
    det = sx4 * (sx2 * n - sx * sx) - sx3 * (sx3 * n - sx * sx2) + sx2 * (sx3 * sx - sx2 * sx2)
    if abs(det) < 1e-12:
        raise ValueError("Math ERROR")
    det_c = sx4 * (sx2 * sy - sx * sxy) - sx3 * (sx3 * sy - sx2 * sxy) + sx2y * (sx3 * sx - sx2 * sx2)
    return det_c / det


@register("quadreg_pred", CAT_STAT_REG, "Predict y for given x using quadratic regression", args=(7, 99), example="quadreg_pred(4, 1, 2, 3, 1, 4, 9) => 16")
def quadreg_pred(x_val, *args):
    x_val = float(x_val)
    return quadreg_a(*args) * (x_val ** 2) + quadreg_b(*args) * x_val + quadreg_c(*args)


@register("expreg_a", CAT_STAT_REG, "Calculate coefficient a for exponential regression y = a * b^x", args=(4, 99), example="expreg_a(0, 1, 2, 1, 2, 4) => 1")
def expreg_a(*args):
    x, y = _split_bivariate_args(args)
    if any(yi <= 0 for yi in y):
        raise ValueError("Math ERROR")
    return math.exp(linreg_intercept(*(x + [math.log(yi) for yi in y])))


@register("expreg_b", CAT_STAT_REG, "Calculate base b for exponential regression y = a * b^x", args=(4, 99), example="expreg_b(0, 1, 2, 1, 2, 4) => 2")
def expreg_b(*args):
    x, y = _split_bivariate_args(args)
    if any(yi <= 0 for yi in y):
        raise ValueError("Math ERROR")
    return math.exp(linreg_slope(*(x + [math.log(yi) for yi in y])))


@register("expreg_pred", CAT_STAT_REG, "Predict y for given x using exponential regression", args=(5, 99), example="expreg_pred(3, 0, 1, 2, 1, 2, 4) => 8")
def expreg_pred(x_val, *args):
    return expreg_a(*args) * (expreg_b(*args) ** float(x_val))


@register("logreg_a", CAT_STAT_REG, "Calculate coefficient a for logarithmic regression y = a * ln(x) + b", args=(4, 99), example="logreg_a(1, 2, 3, 0, 0.6931471805599453, 1.0986122886681098) => 1")
def logreg_a(*args):
    x, y = _split_bivariate_args(args)
    if any(xi <= 0 for xi in x):
        raise ValueError("Math ERROR")
    return linreg_slope(*([math.log(xi) for xi in x] + y))


@register("logreg_b", CAT_STAT_REG, "Calculate coefficient b for logarithmic regression y = a * ln(x) + b", args=(4, 99), example="logreg_b(1, 2, 3, 0, 0.6931471805599453, 1.0986122886681098) => -1.110223025×10^-16")
def logreg_b(*args):
    x, y = _split_bivariate_args(args)
    if any(xi <= 0 for xi in x):
        raise ValueError("Math ERROR")
    return linreg_intercept(*([math.log(xi) for xi in x] + y))


@register("logreg_pred", CAT_STAT_REG, "Predict y for given x using logarithmic regression", args=(5, 99), example="logreg_pred(4, 1, 2, 3, 0, 0.6931471805599453, 1.0986122886681098) => 1.386294361")
def logreg_pred(x_val, *args):
    x_val = float(x_val)
    if x_val <= 0:
        raise ValueError("Math ERROR")
    return logreg_a(*args) * math.log(x_val) + logreg_b(*args)


@register("powerreg_a", CAT_STAT_REG, "Calculate coefficient a for power regression y = a * x^b", args=(4, 99), example="powerreg_a(1, 2, 3, 1, 4, 9) => 1")
def powerreg_a(*args):
    x, y = _split_bivariate_args(args)
    if any(xi <= 0 or yi <= 0 for xi, yi in zip(x, y)):
        raise ValueError("Math ERROR")
    return math.exp(linreg_intercept(*([math.log(xi) for xi in x] + [math.log(yi) for yi in y])))


@register("powerreg_b", CAT_STAT_REG, "Calculate exponent b for power regression y = a * x^b", args=(4, 99), example="powerreg_b(1, 2, 3, 1, 4, 9) => 2")
def powerreg_b(*args):
    x, y = _split_bivariate_args(args)
    if any(xi <= 0 or yi <= 0 for xi, yi in zip(x, y)):
        raise ValueError("Math ERROR")
    return linreg_slope(*([math.log(xi) for xi in x] + [math.log(yi) for yi in y]))


@register("powerreg_pred", CAT_STAT_REG, "Predict y for given x using power regression", args=(5, 99), example="powerreg_pred(4, 1, 2, 3, 1, 4, 9) => 16")
def powerreg_pred(x_val, *args):
    x_val = float(x_val)
    if x_val <= 0:
        raise ValueError("Math ERROR")
    return powerreg_a(*args) * (x_val ** powerreg_b(*args))
