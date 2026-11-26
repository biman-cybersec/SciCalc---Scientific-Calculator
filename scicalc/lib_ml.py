"""Phase 3: machine learning and data science

Module 39 of 47.  Taken from lines 13069-13450 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_ml"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .lib_lists_matrices import _L
from .lib_chemistry import _cn

#  PHASE 3 : MACHINE LEARNING AND DATA SCIENCE (44)
#  Losses, distances and information measures take real lists: mse({1,2,3}, {1,2,4}).
#  Activation functions take numbers (and, like every scalar function, work element by
#  element on a list).  Classification scores take confusion-matrix counts.
#  Logarithms in entropy_bits and kl_div2 are base 2.  hard_sigmoid is relu6(x+3)/6.
# ======================================================================================
_MLD = "ML & Data Science"


def _mld(name, desc, args, example, **kw):
    if kw.get("lists"):
        kw["exact"] = True                      # lists arrive untouched
    return register(name, _MLD, desc, args, example=example, **kw)


def _mfin(x, what="value"):
    x = float(x)
    if not math.isfinite(x):
        raise MathError(f"{what} is not a finite number")
    return x


def _mpos(x, what="value"):
    x = _mfin(x, what)
    if x <= 0:
        raise MathError(f"{what} must be positive")
    return x


def _mnn(x, what="value"):
    x = _mfin(x, what)
    if x < 0:
        raise MathError(f"{what} cannot be negative")
    return x


def _mvec(L):
    """A non-empty list of plain real numbers as floats."""
    out = [_cn(v) for v in _L(L)]
    if not out:
        raise MathError("the list is empty")
    if any(not math.isfinite(v) for v in out):
        raise MathError("the list holds a value that is not finite")
    return out


def _mpair(A, B):
    a, b = _mvec(A), _mvec(B)
    if len(a) != len(b):
        raise MathError("lists must have the same size")
    return a, b


def _mprobs(P):
    p = _mvec(P)
    if any(v < 0 for v in p) or abs(sum(p) - 1) > 1e-9:
        raise MathError("probabilities must be non-negative and add up to 1")
    return p


def _mcount(x, what="count"):
    x = _mnn(x, what)
    if x != int(x):
        raise MathError(f"{what} must be a whole number")
    return int(x)


# ---- activation functions
@_mld("gelu", "Gaussian error linear unit: x * Phi(x)", 1, "gelu(1) => 0.8413447461")
def gelu(x):
    return x * 0.5 * (1 + math.erf(_mfin(x) / math.sqrt(2)))


@_mld("swish", "Swish / SiLU: swish(x [, beta = 1]) = x / (1 + e^(-beta x))", (1, 2), "swish(1) => 0.7310585786")
def swish(x, beta=1.0):
    z = -_mfin(beta) * _mfin(x)
    if z > 700:
        return 0.0
    return x / (1 + math.exp(z))


@_mld("elu", "Exponential linear unit: elu(x [, alpha = 1])", (1, 2), "elu(-1) => -0.6321205588")
def elu(x, alpha=1.0):
    x = _mfin(x)
    return x if x > 0 else _mfin(alpha) * math.expm1(x)


@_mld("selu", "Scaled exponential linear unit (lambda 1.0507009873554805, alpha 1.6732632423543772)", 1, "selu(-1) => -1.111330738")
def selu(x):
    x = _mfin(x)
    return 1.0507009873554805 * (x if x > 0 else 1.6732632423543772 * math.expm1(x))


@_mld("softplus", "Softplus ln(1 + e^x)", 1, "softplus(0) => 0.6931471806")
def softplus(x):
    x = _mfin(x)
    return x + math.log1p(math.exp(-x)) if x > 0 else math.log1p(math.exp(x))


@_mld("softsign", "Softsign x / (1 + |x|)", 1, "softsign(-3) => -0.75")
def softsign(x):
    x = _mfin(x)
    return x / (1 + abs(x))


@_mld("mish", "Mish x tanh(softplus(x))", 1, "mish(1) => 0.8650983883")
def mish(x):
    return x * math.tanh(softplus(x))


@_mld("relu6", "ReLU capped at 6: min(max(x, 0), 6)", 1, "relu6(8) => 6")
def relu6(x):
    return min(max(_mfin(x), 0.0), 6.0)


@_mld("hard_sigmoid", "Hard sigmoid relu6(x + 3) / 6", 1, "hard_sigmoid(1) => 0.6666666667")
def hard_sigmoid(x):
    return relu6(_mfin(x) + 3) / 6


@_mld("hard_swish", "Hard swish x * hard_sigmoid(x)", 1, "hard_swish(1) => 0.6666666667")
def hard_swish(x):
    return x * hard_sigmoid(x)


# ---- losses on one prediction
@_mld("cross_entropy_bin", "Binary cross-entropy (natural log) for label y (0 or 1) and probability p: cross_entropy_bin(y, p)", 2,
      "cross_entropy_bin(1, 0.9) => 0.1053605157")
def cross_entropy_bin(y, p):
    y, p = _mfin(y), _mfin(p)
    if y not in (0.0, 1.0):
        raise MathError("the label must be 0 or 1")
    if not 0 < p < 1:
        raise MathError("the probability must be strictly between 0 and 1")
    return -math.log(p if y == 1 else 1 - p)


@_mld("huber_loss", "Huber loss of an error: huber_loss(error, delta)", 2, "huber_loss(3, 1) => 2.5")
def huber_loss(e, delta):
    e, delta = abs(_mfin(e)), _mpos(delta, "delta")
    return 0.5 * e * e if e <= delta else delta * (e - 0.5 * delta)


@_mld("hinge_loss", "Hinge loss max(0, 1 - y s) for label y = +1 or -1 and score s: hinge_loss(y, s)", 2, "hinge_loss(1, 0.3) => 0.7")
def hinge_loss(y, s):
    y = _mfin(y)
    if y not in (-1.0, 1.0):
        raise MathError("the label must be +1 or -1")
    return max(0.0, 1 - y * _mfin(s))


# ---- lists
@_mld("mse", "Mean squared error of two lists: mse(predicted, actual)", 2, "mse({1, 2, 3}, {1, 2, 5}) => 1.333333333", lists=True)
def mse(A, B):
    a, b = _mpair(A, B)
    return math.fsum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


@_mld("mae", "Mean absolute error of two lists: mae(predicted, actual)", 2, "mae({1, 2, 3}, {1, 2, 5}) => 0.6666666667", lists=True)
def mae(A, B):
    a, b = _mpair(A, B)
    return math.fsum(abs(x - y) for x, y in zip(a, b)) / len(a)


@_mld("rmse", "Root mean squared error of two lists: rmse(predicted, actual)", 2, "rmse({1, 2, 3}, {1, 2, 5}) => 1.154700538", lists=True)
def rmse(A, B):
    return math.sqrt(mse(A, B))


@_mld("cosine_sim", "Cosine similarity of two lists: cosine_sim(A, B)", 2, "cosine_sim({1, 0}, {1, 1}) => 0.7071067812", lists=True)
def cosine_sim(A, B):
    a, b = _mpair(A, B)
    na, nb = math.sqrt(math.fsum(x * x for x in a)), math.sqrt(math.fsum(y * y for y in b))
    if na == 0 or nb == 0:
        raise MathError("a zero vector has no direction")
    return max(-1.0, min(1.0, math.fsum(x * y for x, y in zip(a, b)) / (na * nb)))


@_mld("cosine_dist", "Cosine distance 1 - cosine similarity: cosine_dist(A, B)", 2, "cosine_dist({1, 0}, {0, 1}) => 1", lists=True)
def cosine_dist(A, B):
    return 1 - cosine_sim(A, B)


@_mld("euclid_n", "Euclidean distance between two lists: euclid_n(A, B)", 2, "euclid_n({1, 2, 3}, {4, 6, 3}) => 5", lists=True)
def euclid_n(A, B):
    a, b = _mpair(A, B)
    return math.sqrt(math.fsum((x - y) ** 2 for x, y in zip(a, b)))


@_mld("manhattan_n", "Manhattan (taxicab) distance between two lists: manhattan_n(A, B)", 2, "manhattan_n({1, 2, 3}, {4, 6, 3}) => 7", lists=True)
def manhattan_n(A, B):
    a, b = _mpair(A, B)
    return math.fsum(abs(x - y) for x, y in zip(a, b))


@_mld("chebyshev_n", "Chebyshev distance (largest coordinate gap): chebyshev_n(A, B)", 2, "chebyshev_n({1, 2, 3}, {4, 6, 3}) => 4", lists=True)
def chebyshev_n(A, B):
    a, b = _mpair(A, B)
    return max(abs(x - y) for x, y in zip(a, b))


@_mld("hamming_n", "Number of positions where two lists differ: hamming_n(A, B)", 2, "hamming_n({1, 0, 1, 1}, {1, 1, 0, 1}) => 2", lists=True)
def hamming_n(A, B):
    a, b = _mpair(A, B)
    return sum(1 for x, y in zip(a, b) if x != y)


@_mld("jaccard", "Jaccard index of two lists read as sets: |A and B| / |A or B|", 2, "jaccard({1, 2, 3}, {2, 3, 4}) => 0.5", lists=True)
def jaccard(A, B):
    a, b = set(_mvec(A)), set(_mvec(B))
    return len(a & b) / len(a | b)


@_mld("dice_coef", "Dice coefficient of two lists read as sets: 2|A and B| / (|A| + |B|)", 2, "dice_coef({1, 2, 3}, {2, 3, 4}) => 0.6666666667", lists=True)
def dice_coef(A, B):
    a, b = set(_mvec(A)), set(_mvec(B))
    return 2 * len(a & b) / (len(a) + len(b))


@_mld("entropy_bits", "Shannon entropy in bits of a list of probabilities", 1, "entropy_bits({0.5, 0.25, 0.25}) => 1.5", lists=True)
def entropy_bits(P):
    return abs(-math.fsum(v * math.log2(v) for v in _mprobs(P) if v > 0))


@_mld("kl_div2", "Kullback-Leibler divergence in bits: kl_div2(P, Q)", 2, "kl_div2({0.5, 0.5}, {0.25, 0.75}) => 0.2075187496", lists=True)
def kl_div2(P, Q):
    p, q = _mprobs(P), _mprobs(Q)
    if len(p) != len(q):
        raise MathError("lists must have the same size")
    total = 0.0
    for x, y in zip(p, q):
        if x > 0:
            if y == 0:
                raise MathError("Q is zero where P is not")
            total += x * math.log2(x / y)
    return max(0.0, total)


@_mld("gini2", "Gini impurity of a two-class node with class probability p: 2p(1-p)", 1, "gini2(0.3) => 0.42")
def gini2(p):
    p = _mfin(p)
    if not 0 <= p <= 1:
        raise MathError("a probability is between 0 and 1")
    return 2 * p * (1 - p)


@_mld("gini_n", "Gini impurity of a list of class probabilities: 1 - sum p^2", 1, "gini_n({0.5, 0.25, 0.25}) => 0.625", lists=True)
def gini_n(P):
    return 1 - math.fsum(v * v for v in _mprobs(P))


@_mld("softmax_i", "i-th (1-based) softmax probability of a list of scores: softmax_i(L, i)", 2, "softmax_i({1, 2, 3}, 3) => 0.6652409558", lists=True)
def softmax_i(L, i):
    v = _mvec(L)
    k = _mfin(i, "index")
    if k != int(k) or not 1 <= k <= len(v):
        raise MathError("index out of range")
    top = max(v)
    e = [math.exp(x - top) for x in v]
    return e[int(k) - 1] / math.fsum(e)


# ---- scaling
@_mld("minmax_scale", "Scale x into 0..1: minmax_scale(x, lo, hi)", 3, "minmax_scale(7, 2, 12) => 0.5")
def minmax_scale(x, lo, hi):
    lo, hi = _mfin(lo), _mfin(hi)
    if hi == lo:
        raise MathError("lo and hi must differ")
    return (_mfin(x) - lo) / (hi - lo)


@_mld("zscore_scale", "Standardise x: zscore_scale(x, mean, standard_deviation)", 3, "zscore_scale(110, 100, 15) => 0.6666666667")
def zscore_scale(x, mean, sd):
    return (_mfin(x) - _mfin(mean)) / _mpos(sd, "standard deviation")


# ---- classification scores from confusion-matrix counts
@_mld("precision", "Precision tp / (tp + fp): precision(tp, fp)", 2, "precision(8, 2) => 0.8")
def precision(tp, fp):
    tp, fp = _mcount(tp), _mcount(fp)
    if tp + fp == 0:
        raise MathError("no positive predictions")
    return tp / (tp + fp)


@_mld("recall", "Recall tp / (tp + fn): recall(tp, fn)", 2, "recall(8, 4) => 0.6666666667")
def recall(tp, fn):
    tp, fn = _mcount(tp), _mcount(fn)
    if tp + fn == 0:
        raise MathError("no positive cases")
    return tp / (tp + fn)


@_mld("specificity", "Specificity tn / (tn + fp): specificity(tn, fp)", 2, "specificity(90, 10) => 0.9")
def specificity(tn, fp):
    tn, fp = _mcount(tn), _mcount(fp)
    if tn + fp == 0:
        raise MathError("no negative cases")
    return tn / (tn + fp)


@_mld("f1_score", "F1 score 2tp / (2tp + fp + fn): f1_score(tp, fp, fn)", 3, "f1_score(8, 2, 4) => 0.7272727273")
def f1_score(tp, fp, fn):
    tp, fp, fn = _mcount(tp), _mcount(fp), _mcount(fn)
    if tp + fp + fn == 0:
        raise MathError("no positives at all")
    return 2 * tp / (2 * tp + fp + fn)


@_mld("f_beta", "F-beta score: f_beta(beta, tp, fp, fn)", 4, "f_beta(2, 8, 2, 4) => 0.6896551724")
def f_beta(beta, tp, fp, fn):
    b2 = _mpos(beta, "beta") ** 2
    tp, fp, fn = _mcount(tp), _mcount(fp), _mcount(fn)
    d = (1 + b2) * tp + b2 * fn + fp
    if d == 0:
        raise MathError("no positives at all")
    return (1 + b2) * tp / d


@_mld("accuracy", "Accuracy (tp + tn) / all: accuracy(tp, tn, fp, fn)", 4, "accuracy(8, 90, 2, 4) => 0.9423076923")
def accuracy(tp, tn, fp, fn):
    tp, tn, fp, fn = _mcount(tp), _mcount(tn), _mcount(fp), _mcount(fn)
    if tp + tn + fp + fn == 0:
        raise MathError("no cases")
    return (tp + tn) / (tp + tn + fp + fn)


@_mld("balanced_accuracy", "Mean of recall and specificity: balanced_accuracy(tp, tn, fp, fn)", 4, "balanced_accuracy(8, 90, 2, 4) => 0.8224637681")
def balanced_accuracy(tp, tn, fp, fn):
    return (recall(tp, fn) + specificity(tn, fp)) / 2


@_mld("mcc", "Matthews correlation coefficient: mcc(tp, tn, fp, fn)", 4, "mcc(8, 90, 2, 4) => 0.6989265369")
def mcc(tp, tn, fp, fn):
    tp, tn, fp, fn = _mcount(tp), _mcount(tn), _mcount(fp), _mcount(fn)
    d = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    if d == 0:
        raise MathError("a row or column of the table is empty")
    return (tp * tn - fp * fn) / math.sqrt(d)


# ---- learning-rate schedules and geometry
@_mld("exp_decay", "Exponential decay lr0 e^(-k t): exp_decay(lr0, k, t)", 3, "exp_decay(0.1, 0.05, 10) => 0.06065306597")
def exp_decay(lr0, k, t):
    return _mpos(lr0, "rate") * math.exp(-_mnn(k, "k") * _mnn(t, "step"))


@_mld("step_decay", "Step decay: lr0 * drop^floor(epoch / every): step_decay(lr0, drop, every, epoch)", 4, "step_decay(0.1, 0.5, 10, 25) => 0.025")
def step_decay(lr0, drop, every, epoch):
    drop = _mpos(drop, "drop")
    if drop > 1:
        raise MathError("the drop factor is at most 1")
    return _mpos(lr0, "rate") * drop ** math.floor(_mnn(epoch, "epoch") / _mpos(every, "interval"))


@_mld("cosine_decay", "Cosine annealing from lr0 to 0: cosine_decay(lr0, t, total_steps)", 3, "cosine_decay(0.1, 50, 100) => 0.05")
def cosine_decay(lr0, t, total):
    t, total = _mnn(t, "step"), _mpos(total, "total steps")
    if t > total:
        raise MathError("the step is past the end of the schedule")
    return _mpos(lr0, "rate") * 0.5 * (1 + math.cos(math.pi * t / total))


@_mld("lr_warmup", "Linear warm-up to lr0 over the first steps: lr_warmup(lr0, step, warmup_steps)", 3, "lr_warmup(0.1, 25, 100) => 0.025")
def lr_warmup(lr0, step, warm):
    return _mpos(lr0, "rate") * min(1.0, _mnn(step, "step") / _mpos(warm, "warm-up steps"))


@_mld("iou_box", "Intersection over union of two boxes (x1,y1,x2,y2) and (u1,v1,u2,v2)", 8, "iou_box(0, 0, 2, 2, 1, 1, 3, 3) => 0.1428571429")
def iou_box(x1, y1, x2, y2, u1, v1, u2, v2):
    a = [_mfin(v) for v in (x1, y1, x2, y2)]
    b = [_mfin(v) for v in (u1, v1, u2, v2)]
    if a[2] <= a[0] or a[3] <= a[1] or b[2] <= b[0] or b[3] <= b[1]:
        raise MathError("a box needs x2 > x1 and y2 > y1")
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    inter = max(0.0, w) * max(0.0, h)
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union


# ======================================================================================
