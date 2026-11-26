"""Checks: distributions.  Run alone with  python run_tests.py distributions"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "distributions"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_distributions_4(check, ev, near, simpson):
    """distributions"""
    # ---------------------------------------------------------------- distributions
    def pdf_cdf(label, pdf_expr, cdf_expr, a, b, tol=2e-7):
        f_pdf = lambda x: ev(pdf_expr.format(x=repr(x)))
        want = simpson(f_pdf, a, b)
        got = ev(cdf_expr.format(x=repr(b))) - ev(cdf_expr.format(x=repr(a)))
        check(f"{label}: cdf(b)-cdf(a) equals integral of pdf", abs(got - want) <= tol, True)

    pdf_cdf("norm", "norm_pdf({x},1,2)", "norm_cdf({x},1,2)", -2.5, 4.0)
    pdf_cdf("t(5)", "t_pdf({x},5)", "t_cdf({x},5)", -3.0, 1.2)
    pdf_cdf("t(2)", "t_pdf({x},2)", "t_cdf({x},2)", -2.0, 2.5)
    pdf_cdf("chisq(3)", "chisq_pdf({x},3)", "chisq_cdf({x},3)", 0.5, 6.0)
    pdf_cdf("chisq(6)", "chisq_pdf({x},6)", "chisq_cdf({x},6)", 0.5, 9.0)
    pdf_cdf("f(4,6)", "f_pdf({x},4,6)", "f_cdf({x},4,6)", 0.2, 3.0)
    pdf_cdf("gamma(2.5,1.5)", "gamma_pdf({x},2.5,1.5)", "gamma_cdf({x},2.5,1.5)", 0.05, 4.0)
    pdf_cdf("beta(2,3)", "beta_pdf({x},2,3)", "beta_cdf({x},2,3)", 0.1, 0.8)
    pdf_cdf("weibull(1.5,2)", "weibull_pdf({x},1.5,2)", "weibull_cdf({x},1.5,2)", 0.2, 3.0)
    pdf_cdf("lognorm(0.2,0.5)", "lognorm_pdf({x},0.2,0.5)", "lognorm_cdf({x},0.2,0.5)", 0.1, 3.0)
    pdf_cdf("exp(1.3)", "exp_pdf({x},1.3)", "exp_cdf({x},1.3)", 0.0, 3.0)
    pdf_cdf("expon(1.3)", "expon_pdf({x},1.3)", "expon_cdf({x},1.3)", 0.0, 3.0)
    pdf_cdf("uniform", "uniform_pdf({x},0,5)", "uniform_cdf({x},0,5)", 0.5, 4.5)
    pdf_cdf("chi2 (roadmap names)", "chi2_pdf({x},4)", "chi2_cdf({x},4)", 0.4, 7.0)
    for p in (0.01, 0.25, 0.5, 0.9, 0.999):
        near(f"norm_cdf(norm_inv({p}))", f"norm_cdf(norm_inv({p},2,3),2,3)", p, 1e-9)
        near(f"t_cdf(t_inv({p}))", f"t_cdf(t_inv({p},7),7)", p, 1e-9)
        near(f"chisq_cdf(chisq_inv({p}))", f"chisq_cdf(chisq_inv({p},4),4)", p, 1e-9)
        near(f"f_cdf(f_inv({p}))", f"f_cdf(f_inv({p},5,9),5,9)", p, 1e-9)
        near(f"exp_cdf(expon_inv({p}))", f"exp_cdf(expon_inv({p},1.7),1.7)", p, 1e-9)
        near(f"chi2_cdf(chi2_inv({p}))", f"chi2_cdf(chi2_inv({p},3),3)", p, 1e-9)
    near("norm_between", "norm_between(-1.96,1.96,0,1)", 0.9500042097035591)
    near("table z 1.96", "norm_cdf(1.96,0,1)", 0.9750021048517795)
    near("table t(10) 97.5%", "t_inv(0.975,10)", 2.2281388519649385, 1e-8)
    near("table chi2(5) 95%", "chisq_inv(0.95,5)", 11.070497693516351, 1e-8)
    near("table F(5,5) 95%", "f_inv(0.95,5,5)", 5.050329058, 1e-8)
    near("critical_z", "critical_z(0.05)", 1.959963984540054, 1e-8)
    near("critical_t", "critical_t(0.05,10)", 2.2281388519649385, 1e-8)
    near("critical_chi2", "critical_chi2(0.05,5)", 11.070497693516351, 1e-8)
    for k in range(0, 6):
        want = math.comb(5, k) * 0.3 ** k * 0.7 ** (5 - k)
        near(f"binom_pmf k={k}", f"binom_pmf({k},5,0.3)", want)
        near(f"binomial_pmf k={k}", f"binomial_pmf(5,{k},0.3)", want)
        near(f"binom_cdf k={k}", f"binom_cdf({k},5,0.3)", sum(math.comb(5, j) * 0.3 ** j * 0.7 ** (5 - j) for j in range(k + 1)))
        near(f"binomial_cdf k={k}", f"binomial_cdf(5,{k},0.3)", sum(math.comb(5, j) * 0.3 ** j * 0.7 ** (5 - j) for j in range(k + 1)))
    for k in range(0, 8):
        pm = math.exp(-2.5) * 2.5 ** k / math.factorial(k)
        near(f"poisson_pmf k={k}", f"poisson_pmf(2.5,{k})", pm)
        near(f"poisson_cdf k={k}", f"poisson_cdf({k},2.5)", sum(math.exp(-2.5) * 2.5 ** j / math.factorial(j) for j in range(k + 1)))
    for k in range(1, 6):
        near(f"geom_pmf k={k}", f"geom_pmf({k},0.3)", 0.7 ** (k - 1) * 0.3)
        near(f"geometric_pmf k={k}", f"geometric_pmf({k},0.3)", 0.7 ** (k - 1) * 0.3)
        near(f"geom_cdf k={k}", f"geom_cdf({k},0.3)", 1 - 0.7 ** k)
        near(f"geometric_cdf k={k}", f"geometric_cdf({k},0.3)", 1 - 0.7 ** k)
    for k in range(0, 5):
        pm = math.comb(6, k) * math.comb(14, 5 - k) / math.comb(20, 5)
        near(f"hypergeom_pmf k={k}", f"hypergeom_pmf({k},20,6,5)", pm)
        near(f"hypergeom_cdf k={k}", f"hypergeom_cdf({k},20,6,5)",
             sum(math.comb(6, j) * math.comb(14, 5 - j) / math.comb(20, 5) for j in range(k + 1)))
    near("norm_pdf", "norm_pdf(1.5,1,2)", math.exp(-0.5 * 0.25 ** 2) / (2 * math.sqrt(2 * math.pi)))
