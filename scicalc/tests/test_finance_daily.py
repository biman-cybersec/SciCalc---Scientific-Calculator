"""Checks: finance daily.  Run alone with  python run_tests.py finance_daily"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "finance_daily"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_finance_daily_13(check, ev, near):
    """finance and daily life"""
    # ---------------------------------------------------------------- finance and daily life
    near("si", "si(1000,5,2)", 100)
    near("ci vs loop", "ci(1000,5,3,4)", 1000 * (1 + 0.05 / 4) ** 12, 1e-12)
    near("fv", "fv(1000,5,3)", 1000 * 1.05 ** 3, 1e-12)
    near("pv inverts fv", "pv(fv(1000,5,3),5,3)", 1000, 1e-12)
    pm = ev("emi(100000,12,12)")
    r_m = 0.12 / 12
    check("emi pays the loan off", abs(sum(pm / (1 + r_m) ** k for k in range(1, 13)) - 100000) < 1e-6, True)
    near("emi zero rate", "emi(1200,0,12)", 100)
    near("cagr", "cagr(100,200,3)", ((200 / 100) ** (1 / 3) - 1) * 100, 1e-12)
    check("cagr compounds back", abs(100 * (1 + ev("cagr(100,200,3)") / 100) ** 3 - 200) < 1e-9, True)
    near("roi", "roi(150,100)", 50)
    near("npv", "npv(10,-1000,300,400,500)", sum(cf / 1.1 ** t for t, cf in enumerate([-1000, 300, 400, 500])), 1e-12)
    near("continuous_compounding", "continuous_compounding(1000,0.05,2)", 1000 * math.exp(0.1), 1e-12)
    near("annuity_fv vs loop", "annuity_fv(100,0.05,10)", sum(100 * 1.05 ** k for k in range(10)), 1e-12)
    near("annuity_pv vs loop", "annuity_pv(100,0.05,10)", sum(100 / 1.05 ** k for k in range(1, 11)), 1e-12)
    near("gst", "gst(250,18)", 45)
    near("gst_total", "gst_total(250,18)", 295)
    near("discount", "discount(500,20)", 100)
    near("sale_price", "sale_price(500,20)", 400)
    near("pct_of", "pct_of(15,200)", 30)
    near("pct_change", "pct_change(50,75)", 50)
    near("pct_change negative", "pct_change(80,60)", -25)
    near("tip", "tip(50,15)", 7.5)
    near("bmi", "bmi(70,1.75)", round(70 / 1.75 ** 2, 2))
    near("speed*time=distance", "distance(speed(150,3),3)", 150)
    near("time_taken", "time_taken(150,50)", 3)
    near("c_to_f", "c_to_f(100)", 212)
    near("f_to_c round trip", "f_to_c(c_to_f(37))", 37, 1e-12)
    near("c_to_k", "c_to_k(0)", 273.15)
    near("k_to_c round trip", "k_to_c(c_to_k(-40))", -40, 1e-12)
    near("c_to_f(-40) equals f_to_c(-40)", "c_to_f(-40)", -40)
