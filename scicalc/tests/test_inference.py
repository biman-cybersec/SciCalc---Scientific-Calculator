"""Checks: inference.  Run alone with  python run_tests.py inference"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "inference"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_inference_5(near, text):
    """inference"""
    # ---------------------------------------------------------------- inference
    z95 = 1.959963984540054
    t95_9 = 2.2621571627409915
    near("z_ci_low", "z_ci_low(50,5,30,95)", 50 - z95 * 5 / math.sqrt(30), 1e-8)
    near("z_ci_high", "z_ci_high(50,5,30,95)", 50 + z95 * 5 / math.sqrt(30), 1e-8)
    near("t_ci_low", "t_ci_low(50,5,10,95)", 50 - t95_9 * 5 / math.sqrt(10), 1e-8)
    near("t_ci_high", "t_ci_high(50,5,10,95)", 50 + t95_9 * 5 / math.sqrt(10), 1e-8)
    ph = 0.45
    mg = z95 * math.sqrt(ph * (1 - ph) / 100)
    near("prop_ci_low", "prop_ci_low(45,100,95)", ph - mg, 1e-8)
    near("prop_ci_high", "prop_ci_high(45,100,95)", ph + mg, 1e-8)
    text("ci_z_mean", "ci_z_mean(50,5,30,0.95)", "{48.21080586, 51.78919414}")
    text("ci_t_mean", "ci_t_mean(50,5,10,0.95)", "{46.42321547, 53.57678453}")
    text("ci_proportion", "ci_proportion(45,100,0.95)", "{0.352493023, 0.547506977}")
    near("t_stat_one_sample", "t_stat_one_sample(52,50,5,20)", 2 / (5 / math.sqrt(20)))
    near("t_stat_one", "t_stat_one(52,50,5,20)", 2 / (5 / math.sqrt(20)))
    near("t_stat_two (Welch)", "t_stat_two(52,5,20,48,6,25)", 4 / math.sqrt(25 / 20 + 36 / 25))
    sp = math.sqrt((19 * 25 + 24 * 36) / 43)
    near("t_stat_two_sample (pooled)", "t_stat_two_sample(52,48,5,6,20,25)", 4 / (sp * math.sqrt(1 / 20 + 1 / 25)))
    near("cohens_d_one_sample", "cohens_d_one_sample(52,50,5)", 0.4)
    near("cohens_d_two_sample", "cohens_d_two_sample(52,48,5,6,20,25)", 4 / sp)
    near("cohen_d", "cohen_d(52,5,20,48,6,25)", 4 / sp)
    near("z_test_stat", "z_test_stat(102,100,15,30)", 2 / (15 / math.sqrt(30)))
    near("z_test_one_proportion", "z_test_one_proportion(55,100,0.5)", 0.05 / math.sqrt(0.25 / 100))
    near("p_value_z", "p_value_z(1.96,2)", math.erfc(1.96 / math.sqrt(2)))
    near("z_p_two", "z_p_two(2.5)", math.erfc(2.5 / math.sqrt(2)))
    near("p_value_t", "p_value_t(2.5,15,2)", 0.024505803246513826, 1e-8)
    near("t_p_two", "t_p_two(2.5,15)", 0.024505803246513826, 1e-8)
    near("chi2_p", "chi2_p(11.070497693516351,5)", 0.05, 1e-7)
    near("sample_size_mean", "sample_size_mean(5,1,0.95)", math.ceil((z95 * 5) ** 2))
    near("sample_size_proportion", "sample_size_proportion(0.05,0.95)", math.ceil(z95 ** 2 * 0.25 / 0.0025))
    near("sample_size_prop", "sample_size_prop(0.5,0.05,95)", math.ceil(z95 ** 2 * 0.25 / 0.0025))
    near("chi2_goodness_of_fit", "chi2_goodness_of_fit(10,20,30,15,15,30)", sum((o - e) ** 2 / e for o, e in zip((10, 20, 30), (15, 15, 30))))
    near("chi2_contingency", "chi2_contingency(20,30,15,35)", 100 * (20 * 35 - 30 * 15) ** 2 / (50 * 50 * 35 * 65))


def checks_inference_6(near, csv):
    """non-parametric / ANOVA (by definition)"""
    # ---------------------------------------------------------------- non-parametric / ANOVA (by definition)
    g1_, g2_ = [1, 2, 3, 4, 7], [3, 4, 5, 6, 9, 10]
    u1 = sum((a > b) + 0.5 * (a == b) for a in g1_ for b in g2_)
    near("mann_whitney_u", f"mann_whitney_u({csv(g1_)},{csv(g2_)})", min(u1, len(g1_) * len(g2_) - u1))
    G = [[2, 3, 4], [4, 5, 6], [7, 8, 9]]
    allv = [v for g in G for v in g]
    gm = sum(allv) / len(allv)
    ssb = sum(len(g) * (sum(g) / len(g) - gm) ** 2 for g in G)
    ssw = sum((v - sum(g) / len(g)) ** 2 for g in G for v in g)
    near("anova_one_way", f"anova_one_way({csv(allv)})", (ssb / 2) / (ssw / 6))
    near("friedman_chisq", "friedman_chisq(1,2,3,2,3,4,3,4,5)", 6)
    pairs_a, pairs_b = [125, 115, 130, 140, 140, 115, 140, 125, 140, 135], [110, 122, 125, 120, 140, 124, 123, 137, 135, 145]
    dif = [a - b for a, b in zip(pairs_a, pairs_b) if a != b]
    order = sorted(range(len(dif)), key=lambda i: abs(dif[i]))
    rk = [0.0] * len(dif)
    i = 0
    while i < len(order):
        j = i
        while j < len(order) and abs(dif[order[j]]) == abs(dif[order[i]]):
            j += 1
        for q in range(i, j):
            rk[order[q]] = (i + j + 1) / 2
        i = j
    wp = sum(r_ for r_, d in zip(rk, dif) if d > 0)
    wn = sum(r_ for r_, d in zip(rk, dif) if d < 0)
    near("wilcoxon_signed_rank", f"wilcoxon_signed_rank({csv(pairs_a)},{csv(pairs_b)})", min(wp, wn))
    allk = [2, 3, 4, 4, 5, 6, 7, 8, 9]
    srt = sorted(allk)
    rank_of = lambda v: (srt.index(v) + 1 + len(srt) - srt[::-1].index(v)) / 2
    gk = [allk[:3], allk[3:6], allk[6:]]
    Nk = len(allk)
    hk = 12 / (Nk * (Nk + 1)) * sum(sum(rank_of(v) for v in g) ** 2 / len(g) for g in gk) - 3 * (Nk + 1)
    near("kruskal_wallis", f"kruskal_wallis({csv(allk)})", hk)
