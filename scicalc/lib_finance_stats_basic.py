"""First financial helpers and basic statistics

Module 12 of 47.  Taken from lines 2814-2997 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_finance_stats_basic"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .arithmetic import ar_add, ar_div, ar_mul, ar_power, ar_sub

# --- Financial & Everyday Helpers ---

@register("gst", "Daily Life", "Calculate tax amount given price and GST rate percentage: gst(amount, rate_pct)", args=2, example="gst(100,18) => 18")
def gst(amount, rate):
    if amount < 0 or rate < 0:
        raise MathError("amount and rate cannot be negative")
    return ar_mul(amount, ar_div(rate, 100))


@register("gst_total", "Daily Life", "Total price including GST: gst_total(amount, rate_pct)", args=2, example="gst_total(100,18) => 118")
def gst_total(amount, rate):
    if amount < 0 or rate < 0:
        raise MathError("amount and rate cannot be negative")
    return ar_add(amount, gst(amount, rate))


@register("discount", "Daily Life", "Discount amount: discount(price, discount_pct)", args=2, example="discount(500,20) => 100")
def discount(price, pct):
    if price < 0 or pct < 0:
        raise MathError("price and percentage cannot be negative")
    return ar_mul(price, ar_div(pct, 100))


@register("sale_price", "Daily Life", "Price after discount: sale_price(price, discount_pct)", args=2, example="sale_price(500,20) => 400")
def sale_price(price, pct):
    if price < 0 or pct < 0:
        raise MathError("price and percentage cannot be negative")
    return ar_sub(price, discount(price, pct))


@register("avg", "Daily Life", "Average (mean) of one or more values: avg(v1, v2, ...)", args=(1, None), example="avg(10,20,30) => 20")
def avg(*xs):
    return ar_div(sum(xs), len(xs))


@register("pct_of", "Daily Life", "Calculate p% of total: pct_of(p, total)", args=2, example="pct_of(15,200) => 30")
def pct_of(p, total):
    return ar_mul(total, ar_div(p, 100))


@register("pct_change", "Daily Life", "Percentage change from old_val to new_val: pct_change(old, new)", args=2, example="pct_change(50,75) => 50")
def pct_change(old, new):
    if old == 0:
        raise MathError("initial value cannot be zero")
    return ar_mul(ar_div(ar_sub(new, old), abs(old)), 100)


# ---------- 7i. Financial Math ----------

@register("si", "Financial", "Simple Interest: si(principal, rate_pct, time_years)", args=3, example="si(1000,5,2) => 100")
def simple_interest(p, r, t):
    if p < 0 or r < 0 or t < 0:
        raise MathError("financial values cannot be negative")
    return ar_mul(ar_mul(p, ar_div(r, 100)), t)


@register("ci", "Financial", "Compound Interest (total amount): ci(principal, rate_pct, time_years, times_per_year)", args=4, example="ci(1000,5,2,1) => 1102.5")
def compound_interest(p, r, t, n=1):
    if p < 0 or r < 0 or t < 0 or n <= 0:
        raise MathError("invalid financial inputs")
    base = ar_add(1, ar_div(ar_div(r, 100), n))
    exponent = ar_mul(n, t)
    return ar_mul(p, ar_power(base, exponent))


@register("emi", "Financial", "Equated Monthly Installment (loan EMI): emi(principal, annual_rate_pct, months)", args=3, example="emi(100000,12,12) => 8884.878868")
def emi(p, annual_rate, months):
    p, months = float(p), int(months)
    if p < 0 or annual_rate < 0 or months <= 0:
        raise MathError("invalid loan parameters")
    r = (annual_rate / 100.0) / 12.0
    if r == 0:
        return p / months
    factor = (1 + r) ** months
    return p * r * factor / (factor - 1)


@register("fv", "Financial", "Future Value: fv(present_value, rate_pct, periods)", args=3, example="fv(1000,5,3) => 1157.625")
def future_value(pv, r, t):
    if pv < 0 or r < 0 or t < 0:
        raise MathError("inputs cannot be negative")
    return ar_mul(pv, ar_power(ar_add(1, ar_div(r, 100)), t))


@register("pv", "Financial", "Present Value: pv(future_value, rate_pct, periods)", args=3, example="pv(1157.625,5,3) => 1000")
def present_value(fv_val, r, t):
    if fv_val < 0 or r < 0 or t < 0:
        raise MathError("inputs cannot be negative")
    return ar_div(fv_val, ar_power(ar_add(1, ar_div(r, 100)), t))


@register("cagr", "Financial", "Compound Annual Growth Rate: cagr(start_value, end_value, years)", args=3, example="cagr(100,200,3) => 25.99210499")
def cagr(start, end, years):
    if start <= 0 or end <= 0 or years <= 0:
        raise MathError("values must be positive")
    return ar_mul(ar_sub(ar_power(ar_div(end, start), ar_div(1, years)), 1), 100)


@register("roi", "Financial", "Return on Investment percentage: roi(gain, cost)", args=2, example="roi(150,100) => 50")
def roi(gain, cost):
    if cost == 0:
        raise MathError("cost cannot be zero")
    return ar_mul(ar_div(ar_sub(gain, cost), abs(cost)), 100)


# ---------- 7j. Statistics & Data Analysis ----------

CAT_STATS = "Statistics"


@register("mean", CAT_STATS, "Arithmetic mean of values: mean(v1, v2, ...)", args=(1, None), example="mean(10,20,30) => 20")
def mean_(*xs):
    return ar_div(sum(xs), len(xs))


@register("median", CAT_STATS, "Median of values: median(v1, v2, ...)", args=(1, None), example="median(1,3,2) => 2")
def median_(*xs):
    s = sorted(xs)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return ar_div(ar_add(s[n // 2 - 1], s[n // 2]), 2)


@register("variance", CAT_STATS, "Sample variance: variance(v1, v2, ...)", args=(1, None), example="variance(2,4,4,4,5,5,7,9) => 4.571428571")
def variance_(*xs):
    n = len(xs)
    if n < 2:
        raise MathError("variance requires at least 2 values")
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / (n - 1)


@register("stdev", CAT_STATS, "Sample standard deviation: stdev(v1, v2, ...)", args=(1, None), example="stdev(2,4,4,4,5,5,7,9) => 2.138089935")
def stdev_(*xs):
    return math.sqrt(variance_(*xs))


# --- Advanced Statistics & Probability Expansion ---

@register("harmonic_mean", CAT_STATS, "Harmonic mean of values: harmonic_mean(v1, v2, ...)", args=(1, None), example="harmonic_mean(1, 2, 4) => 1.714285714")
def harmonic_mean(*xs):
    if any(x <= 0 for x in xs):
        raise MathError("harmonic mean requires positive values")
    n = len(xs)
    total_inv = sum(1.0 / x for x in xs)
    return ar_div(n, total_inv)


@register("geometric_mean", CAT_STATS, "Geometric mean of values: geometric_mean(v1, v2, ...)", args=(1, None), example="geometric_mean(2, 8) => 4")
def geometric_mean(*xs):
    if any(x < 0 for x in xs):
        raise MathError("geometric mean cannot use negative values")
    n = len(xs)
    log_sum = sum(math.log(x) if x > 0 else float('-inf') for x in xs)
    return math.exp(log_sum / n)


@register("rms", CAT_STATS, "Root Mean Square (RMS): rms(v1, v2, ...)", args=(1, None), example="rms(1, 2, 3) => 2.160246899")
def root_mean_square(*xs):
    n = len(xs)
    sum_sq = sum(x ** 2 for x in xs)
    return math.sqrt(sum_sq / n)


@register("population_variance", CAT_STATS, "Population variance (sigma^2): population_variance(v1, v2, ...)", args=(1, None), example="population_variance(2,4,4,4,5,5,7,9) => 4")
def population_variance(*xs):
    n = len(xs)
    if n < 1:
        raise MathError("variance requires at least 1 value")
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / n


@register("population_stdev", CAT_STATS, "Population standard deviation (sigma): population_stdev(v1, v2, ...)", args=(1, None), example="population_stdev(2,4,4,4,5,5,7,9) => 2")
def population_stdev(*xs):
    return math.sqrt(population_variance(*xs))


@register("range_stat", CAT_STATS, "Range of values (max - min): range_stat(v1, v2, ...)", args=(1, None), exact=True, example="range_stat(2, 5, 10, 3) => 8")
def range_stat(*xs):
    return max(xs) - min(xs)
