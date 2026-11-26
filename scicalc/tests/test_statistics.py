"""Checks: statistics.  Run alone with  python run_tests.py statistics"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "statistics"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_statistics_2(near, csv, st):
    """one-variable statistics"""
    # ---------------------------------------------------------------- one-variable statistics
    D = [2, 4, 4, 4, 5, 5, 7, 9]
    E = [3.5, 1.25, 9, 4, 4, 7.75, 2, 10, 6]
    for tag, data in (("D", D), ("E", E)):
        sd = csv(data)
        n = len(data)
        m = st.mean(data)
        near(f"mean {tag}", f"mean({sd})", m)
        near(f"avg {tag}", f"avg({sd})", m)
        near(f"total {tag}", f"total({sd})", sum(data))
        near(f"sum_sq {tag}", f"sum_sq({sd})", sum(x * x for x in data))
        near(f"median {tag}", f"median({sd})", st.median(data))
        near(f"variance {tag}", f"variance({sd})", st.variance(data))
        near(f"sample_variance {tag}", f"sample_variance({sd})", st.variance(data))
        near(f"stdev {tag}", f"stdev({sd})", st.stdev(data))
        near(f"sample_stdev {tag}", f"sample_stdev({sd})", st.stdev(data))
        near(f"population_variance {tag}", f"population_variance({sd})", st.pvariance(data))
        near(f"population_stdev {tag}", f"population_stdev({sd})", st.pstdev(data))
        near(f"standard_error {tag}", f"standard_error({sd})", st.stdev(data) / math.sqrt(n))
        near(f"geometric_mean {tag}", f"geometric_mean({sd})", st.geometric_mean(data))
        near(f"geometric_mean_stat {tag}", f"geometric_mean_stat({sd})", st.geometric_mean(data))
        near(f"harmonic_mean {tag}", f"harmonic_mean({sd})", st.harmonic_mean(data))
        near(f"harmonic_mean_stat {tag}", f"harmonic_mean_stat({sd})", st.harmonic_mean(data))
        near(f"rms {tag}", f"rms({sd})", math.sqrt(sum(x * x for x in data) / n))
        near(f"rms_stat {tag}", f"rms_stat({sd})", math.sqrt(sum(x * x for x in data) / n))
        near(f"range_stat {tag}", f"range_stat({sd})", max(data) - min(data))
        near(f"midrange {tag}", f"midrange({sd})", (max(data) + min(data)) / 2)
        near(f"mode {tag}", f"mode({sd})", st.mode(data))
        near(f"mode_count {tag}", f"mode_count({sd})", data.count(st.mode(data)))
        qs = st.quantiles(data, n=4, method="inclusive")
        near(f"q1 {tag}", f"q1({sd})", qs[0])
        near(f"quartile1 {tag}", f"quartile1({sd})", qs[0])
        near(f"quartile2 {tag}", f"quartile2({sd})", qs[1])
        near(f"q3 {tag}", f"q3({sd})", qs[2])
        near(f"quartile3 {tag}", f"quartile3({sd})", qs[2])
        near(f"iqr {tag}", f"iqr({sd})", qs[2] - qs[0])
        near(f"quartile_skewness {tag}", f"quartile_skewness({sd})", (qs[2] - 2 * qs[1] + qs[0]) / (qs[2] - qs[0]))
        deciles = st.quantiles(data, n=10, method="inclusive")
        near(f"quantile {tag}", f"quantile(0.9,{sd})", deciles[8])
        near(f"percentile {tag}", f"percentile(30,{sd})", deciles[2])
        near(f"mad {tag}", f"mad({sd})", sum(abs(x - m) for x in data) / n)
        near(f"mean_abs_dev {tag}", f"mean_abs_dev({sd})", sum(abs(x - m) for x in data) / n)
        med = st.median(data)
        near(f"mean_absolute_deviation_median {tag}", f"mean_absolute_deviation_median({sd})",
             sum(abs(x - med) for x in data) / n)
        near(f"median_abs_dev {tag}", f"median_abs_dev({sd})", st.median([abs(x - med) for x in data]))
        near(f"cv {tag}", f"cv({sd})", st.stdev(data) / m * 100)
        near(f"coefficient_of_variation {tag}", f"coefficient_of_variation({sd})", st.stdev(data) / m)
        m2 = sum((x - m) ** 2 for x in data) / n
        m3 = sum((x - m) ** 3 for x in data) / n
        m4 = sum((x - m) ** 4 for x in data) / n
        near(f"skew_pop {tag}", f"skew_pop({sd})", m3 / m2 ** 1.5)
        g1 = m3 / m2 ** 1.5
        near(f"skewness {tag}", f"skewness({sd})", g1 * math.sqrt(n * (n - 1)) / (n - 2))
        g2 = m4 / m2 ** 2 - 3
        near(f"kurtosis {tag}", f"kurtosis({sd})", ((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * g2 + 6))
        near(f"excess_kurtosis {tag}", f"excess_kurtosis({sd})", ((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * g2 + 6))
        near(f"moment(3) {tag}", f"moment(3,{sd})", m3)
        near(f"central_moment(4) {tag}", f"central_moment(4,{sd})", m4)
        near(f"raw_moment(3) {tag}", f"raw_moment(3,{sd})", sum(x ** 3 for x in data) / n)
        s_sorted = sorted(data)
        k = int(n * 0.2)
        near(f"trimmed_mean {tag}", f"trimmed_mean(0.2,{sd})", st.mean(s_sorted[k:n - k]))
        w = [1 + i for i in range(n)]
        near(f"weighted_mean {tag}", f"weighted_mean({csv(w)},{sd})", sum(a * b for a, b in zip(w, data)) / sum(w))
    near("z_score", "z_score(85,75,5)", 2)
    near("z_score negative", "z_score(70,75,5)", -1)


def checks_statistics_3(near, csv, st):
    """two-variable statistics"""
    # ---------------------------------------------------------------- two-variable statistics
    X = [1, 2, 3, 4, 5, 6, 7]
    Y = [2.1, 3.9, 6.2, 7.8, 10.1, 12.2, 13.8]
    xy = csv(X) + "," + csv(Y)
    lr = st.linear_regression(X, Y)
    r = st.correlation(X, Y)
    near("covariance", f"covariance({xy})", st.covariance(X, Y))
    near("cov_sample", f"cov_sample({xy})", st.covariance(X, Y))
    near("cov_pop", f"cov_pop({xy})", st.covariance(X, Y) * (len(X) - 1) / len(X))
    near("pearson_corr", f"pearson_corr({xy})", r)
    near("corr", f"corr({xy})", r)
    near("linreg_slope", f"linreg_slope({xy})", lr.slope)
    near("linreg_intercept", f"linreg_intercept({xy})", lr.intercept)
    near("linreg_r2", f"linreg_r2({xy})", r * r)
    near("r_squared", f"r_squared({xy})", r * r)
    near("linreg_pred", f"linreg_pred(9,{xy})", lr.slope * 9 + lr.intercept)
    near("linreg_predict", f"linreg_predict(9,{xy})", lr.slope * 9 + lr.intercept)
    rank = lambda v: [sorted(v).index(a) + 1 for a in v]
    near("spearman_corr", f"spearman_corr({xy})", st.correlation(rank(X), rank(Y)))
    near("spearman_rho", f"spearman_rho({xy})", st.correlation(rank(X), rank(Y)))

    def solve3(Mx, bv):                       # tiny Gaussian elimination for the quadratic fit
        n3 = len(bv)
        A = [row[:] + [bv[i]] for i, row in enumerate(Mx)]
        for i in range(n3):
            piv = max(range(i, n3), key=lambda r_: abs(A[r_][i]))
            A[i], A[piv] = A[piv], A[i]
            for r_ in range(n3):
                if r_ != i:
                    fct = A[r_][i] / A[i][i]
                    A[r_] = [u - fct * v for u, v in zip(A[r_], A[i])]
        return [A[i][n3] / A[i][i] for i in range(n3)]

    Yq = [1.2, 4.1, 9.3, 15.8, 25.4, 36.1, 49.5]
    S = lambda p, ys=None: sum((x ** p) * (1 if ys is None else ys[i]) for i, x in enumerate(X))
    c_, b_, a_ = solve3([[S(0), S(1), S(2)], [S(1), S(2), S(3)], [S(2), S(3), S(4)]], [S(0, Yq), S(1, Yq), S(2, Yq)])
    xq = csv(X) + "," + csv(Yq)
    near("quadreg_a", f"quadreg_a({xq})", a_, 1e-7)
    near("quadreg_b", f"quadreg_b({xq})", b_, 1e-7)
    near("quadreg_c", f"quadreg_c({xq})", c_, 1e-7)
    near("quadreg_pred", f"quadreg_pred(8,{xq})", a_ * 64 + b_ * 8 + c_, 1e-7)
    Ye = [2.7, 7.4, 20.1, 54.6, 148.4, 403.4, 1096.6]
    le = st.linear_regression(X, [math.log(v) for v in Ye])
    xe = csv(X) + "," + csv(Ye)
    near("expreg_a", f"expreg_a({xe})", math.exp(le.intercept))
    near("expreg_b", f"expreg_b({xe})", math.exp(le.slope))
    near("expreg_pred", f"expreg_pred(8,{xe})", math.exp(le.intercept) * math.exp(le.slope) ** 8)
    lg = st.linear_regression([math.log(v) for v in X], Y)
    near("logreg_a", f"logreg_a({xy})", lg.slope)
    near("logreg_b", f"logreg_b({xy})", lg.intercept)
    near("logreg_pred", f"logreg_pred(9,{xy})", lg.slope * math.log(9) + lg.intercept)
    pw = st.linear_regression([math.log(v) for v in X], [math.log(v) for v in Y])
    near("powerreg_a", f"powerreg_a({xy})", math.exp(pw.intercept))
    near("powerreg_b", f"powerreg_b({xy})", pw.slope)
    near("powreg_a", f"powreg_a({xy})", math.exp(pw.intercept))
    near("powreg_b", f"powreg_b({xy})", pw.slope)
    near("powerreg_pred", f"powerreg_pred(9,{xy})", math.exp(pw.intercept) * 9 ** pw.slope)
