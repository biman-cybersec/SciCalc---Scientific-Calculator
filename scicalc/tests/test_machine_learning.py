"""Checks: machine learning.  Run alone with  python run_tests.py machine_learning"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "machine_learning"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_machine_learning_33(check, ev, near, ex, fn, lit, rg8):
    """Phase 3: machine learning and data science"""
    # ================= Phase 3: machine learning and data science =================
    sig = lambda z: 1 / (1 + math.exp(-z))
    for x in (-3.5, -1, -0.2, 0, 0.7, 2, 6.5):
        near(f"swish({x}) = x sigmoid(x)", f"swish({x})", x * sig(x), 1e-12)
        near(f"swish beta 2 ({x})", f"swish({x},2)", x * sig(2 * x), 1e-12)
        near(f"gelu({x}) via the normal cdf", f"gelu({x})", x * 0.5 * math.erfc(-x / math.sqrt(2)), 1e-12)
        near(f"elu({x})", f"elu({x})", x if x > 0 else math.exp(x) - 1, 1e-12)
        near(f"elu alpha ({x})", f"elu({x},2)", x if x > 0 else 2 * (math.exp(x) - 1), 1e-12)
        near(f"selu({x})", f"selu({x})", 1.0507009873554805 * (x if x > 0 else 1.6732632423543772 * (math.exp(x) - 1)), 1e-12)
        near(f"softplus({x}) is the integral of the sigmoid", f"softplus({x})", math.log(1 + math.exp(x)), 1e-12)
        near(f"mish({x})", f"mish({x})", x * math.tanh(math.log(1 + math.exp(x))), 1e-12)
        near(f"softsign({x})", f"softsign({x})", x / (1 + abs(x)), 1e-12)
        near(f"relu6({x})", f"relu6({x})", min(6, max(0, x)), 1e-12)
        near(f"hard_sigmoid({x})", f"hard_sigmoid({x})", min(1, max(0, (x + 3) / 6)), 1e-12)
        near(f"hard_swish({x})", f"hard_swish({x})", x * min(1, max(0, (x + 3) / 6)), 1e-12)
    near("softplus large x stays finite", "softplus(800)", 800)
    near("softplus very negative", "softplus(-800)", 0, 1e-12)
    near("swish very negative", "swish(-800)", 0, 1e-12)
    near("gelu list broadcasts", "list_sum(gelu({1,2}))", ev("gelu(1)") + ev("gelu(2)"))
    near("cross entropy y=1", "cross_entropy_bin(1,0.9)", -math.log(0.9))
    near("cross entropy y=0", "cross_entropy_bin(0,0.9)", -math.log(0.1))
    near("huber small", "huber_loss(0.5,1)", 0.125)
    near("huber large", "huber_loss(3,1)", 2.5)
    near("huber is continuous at delta", "huber_loss(2,2)", 2.0)
    near("hinge", "hinge_loss(1,0.3)", 0.7)
    near("hinge satisfied", "hinge_loss(-1,-2)", 0)
    # lists, cross-checked against hand loops written differently
    for _ in range(25):
        n = rg8.randint(1, 7)
        a = [round(rg8.uniform(-5, 5), 2) for _ in range(n)]
        b = [round(rg8.uniform(-5, 5), 2) for _ in range(n)]
        d = [x - y for x, y in zip(a, b)]
        near("mse", f"mse({lit(a)},{lit(b)})", sum(v * v for v in d) / n, 1e-9)
        near("mae", f"mae({lit(a)},{lit(b)})", sum(abs(v) for v in d) / n, 1e-9)
        near("rmse = sqrt(mse)", f"rmse({lit(a)},{lit(b)})", math.sqrt(sum(v * v for v in d) / n), 1e-9)
        near("euclid", f"euclid_n({lit(a)},{lit(b)})", math.dist(a, b), 1e-9)
        near("euclid agrees with the list norm of the difference", f"euclid_n({lit(a)},{lit(b)})", math.sqrt(sum(v * v for v in d)), 1e-9)
        near("manhattan", f"manhattan_n({lit(a)},{lit(b)})", sum(abs(v) for v in d), 1e-9)
        near("chebyshev", f"chebyshev_n({lit(a)},{lit(b)})", max(abs(v) for v in d), 1e-9)
        if any(a) and any(b):
            c = sum(x * y for x, y in zip(a, b)) / (math.hypot(*a) * math.hypot(*b))
            near("cosine similarity", f"cosine_sim({lit(a)},{lit(b)})", c, 1e-9)
            near("cosine distance", f"cosine_dist({lit(a)},{lit(b)})", 1 - c, 1e-9)
            near("cosine agrees with the angle between lists", f"cosine_sim({lit(a)},{lit(b)})", c, 1e-9)
        ia = [rg8.randint(0, 4) for _ in range(n)]
        ib = [rg8.randint(0, 4) for _ in range(n)]
        ex("hamming", f"hamming_n({lit(ia)},{lit(ib)})", sum(x != y for x, y in zip(ia, ib)))
        near("jaccard", f"jaccard({lit(ia)},{lit(ib)})", len(set(ia) & set(ib)) / len(set(ia) | set(ib)), 1e-12)
        near("dice vs jaccard: D = 2J/(1+J)", f"dice_coef({lit(ia)},{lit(ib)})", 2 * ev(f"jaccard({lit(ia)},{lit(ib)})") / (1 + ev(f"jaccard({lit(ia)},{lit(ib)})")), 1e-12)
        s = [rg8.uniform(-3, 3) for _ in range(n)]
        z = sum(math.exp(v) for v in s)
        got = sum(ev(f"softmax_i({lit(s)},{k})") for k in range(1, n + 1))
        check("softmax sums to 1", abs(got - 1) < 1e-9, True)
        near("softmax_i", f"softmax_i({lit(s)},{n})", math.exp(s[-1]) / z, 1e-9)
    near("cosine of orthogonal lists", "cosine_sim({1,0},{0,1})", 0)
    near("cosine of identical lists", "cosine_sim({3,4},{3,4})", 1)
    near("softmax of large scores does not overflow", "softmax_i({1000,1000},1)", 0.5)
    near("entropy of a fair coin", "entropy_bits({0.5,0.5})", 1)
    near("entropy of 8 equal outcomes", "entropy_bits({0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125})", 3)
    near("entropy of a certain outcome", "entropy_bits({1,0})", 0)
    near("entropy", "entropy_bits({0.5,0.25,0.25})", 1.5)
    near("kl divergence", "kl_div2({0.5,0.5},{0.25,0.75})", 0.5 * math.log2(2) + 0.5 * math.log2(0.5 / 0.75))
    near("kl of equal distributions", "kl_div2({0.2,0.8},{0.2,0.8})", 0)
    near("kl = cross entropy - entropy", "kl_div2({0.5,0.5},{0.25,0.75})", -0.5 * math.log2(0.25) - 0.5 * math.log2(0.75) - 1)
    near("gini2", "gini2(0.3)", 1 - 0.3 ** 2 - 0.7 ** 2)
    near("gini_n agrees with gini2", "gini_n({0.3,0.7})", ev("gini2(0.3)"))
    near("gini_n", "gini_n({0.5,0.25,0.25})", 0.625)
    near("minmax", "minmax_scale(7,2,12)", 0.5)
    near("minmax below range", "minmax_scale(0,2,12)", -0.2)
    near("zscore", "zscore_scale(110,100,15)", 2 / 3)
    # classification scores from a table, against a direct count over labelled data
    labels = [1] * 8 + [0] * 4 + [1] * 2 + [0] * 90
    preds = [1] * 8 + [0] * 4 + [0] * 2 + [0] * 90
    tp = sum(1 for y, p in zip(labels, preds) if y == 1 and p == 1)
    tn = sum(1 for y, p in zip(labels, preds) if y == 0 and p == 0)
    fp = sum(1 for y, p in zip(labels, preds) if y == 0 and p == 1)
    fn = sum(1 for y, p in zip(labels, preds) if y == 1 and p == 0)
    prec, rec = tp / (tp + fp), tp / (tp + fn)
    near("precision", f"precision({tp},{fp})", prec)
    near("recall", f"recall({tp},{fn})", rec)
    near("specificity", f"specificity({tn},{fp})", tn / (tn + fp))
    near("f1 is the harmonic mean of precision and recall", f"f1_score({tp},{fp},{fn})", 2 * prec * rec / (prec + rec))
    near("f_beta 1 = f1", f"f_beta(1,{tp},{fp},{fn})", ev(f"f1_score({tp},{fp},{fn})"))
    b = 2.0
    near("f_beta 2 from precision and recall", f"f_beta(2,{tp},{fp},{fn})", (1 + b * b) * prec * rec / (b * b * prec + rec))
    near("accuracy", f"accuracy({tp},{tn},{fp},{fn})", (tp + tn) / len(labels))
    near("balanced accuracy", f"balanced_accuracy({tp},{tn},{fp},{fn})", (rec + tn / (tn + fp)) / 2)
    mc = (tp * tn - fp * fn) / math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    near("mcc", f"mcc({tp},{tn},{fp},{fn})", mc)
    near("mcc of perfect predictions", "mcc(5,5,0,0)", 1)
    near("mcc of reversed predictions", "mcc(0,0,5,5)", -1)
    near("exp decay", "exp_decay(0.1,0.05,10)", 0.1 * math.exp(-0.5))
    near("step decay", "step_decay(0.1,0.5,10,25)", 0.1 * 0.5 ** 2)
    near("cosine decay midpoint", "cosine_decay(0.1,50,100)", 0.05)
    near("cosine decay ends at 0", "cosine_decay(0.1,100,100)", 0, 1e-12)
    near("cosine decay starts at lr0", "cosine_decay(0.1,0,100)", 0.1)
    near("warm-up", "lr_warmup(0.1,25,100)", 0.025)
    near("warm-up caps", "lr_warmup(0.1,500,100)", 0.1)
    near("iou", "iou_box(0,0,2,2,1,1,3,3)", 1 / 7)
    near("iou identical boxes", "iou_box(0,0,2,2,0,0,2,2)", 1)
    near("iou disjoint boxes", "iou_box(0,0,1,1,5,5,6,6)", 0)
    near("iou contained box", "iou_box(0,0,4,4,1,1,3,3)", 4 / 16)
    for e in ["gelu(1e999)", "swish(1,1e999)", "elu(1,1e999)", "cross_entropy_bin(2,0.5)", "cross_entropy_bin(1,0)", "cross_entropy_bin(1,1)",
              "huber_loss(1,0)", "hinge_loss(0,1)", "mse({1,2},{1})", "mse({1},{1,2})", "mae(1,{1})", "rmse({1,2},{1,2,3})", "cosine_sim({0,0},{1,1})",
              "cosine_sim({1},{1,2})", "euclid_n({1,2},{1})", "manhattan_n({1,2},{1})", "chebyshev_n({1,2},{1})", "hamming_n({1,2},{1})",
              "jaccard(1,{1})", "dice_coef({1},2)", "entropy_bits({0.5,0.6})", "entropy_bits({-0.5,1.5})", "entropy_bits(0.5)",
              "kl_div2({0.5,0.5},{1,0})", "kl_div2({0.5,0.5},{1})", "kl_div2({0.4,0.5},{0.5,0.5})", "gini2(1.5)", "gini_n({0.5})", "softmax_i({1,2},0)",
              "softmax_i({1,2},3)", "softmax_i({1,2},1.5)", "minmax_scale(1,2,2)", "zscore_scale(1,0,0)", "precision(0,0)", "recall(0,0)",
              "specificity(0,0)", "f1_score(0,0,0)", "f_beta(0,1,1,1)", "f_beta(1,0,0,0)", "accuracy(0,0,0,0)", "accuracy(-1,1,1,1)", "accuracy(1.5,1,1,1)",
              "mcc(1,0,0,0)", "exp_decay(0,1,1)", "exp_decay(1,-1,1)", "step_decay(1,2,1,1)", "step_decay(1,0.5,0,1)",
              "cosine_decay(1,2,1)", "cosine_decay(1,1,0)", "lr_warmup(1,1,0)", "iou_box(1,1,0,0,0,0,1,1)", "iou_box(0,0,1,1,2,2,1,1)", "mse({i},{1})"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
