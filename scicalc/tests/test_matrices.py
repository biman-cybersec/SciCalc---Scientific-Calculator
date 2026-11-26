"""Checks: matrices.  Run alone with  python run_tests.py matrices"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "matrices"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
import random

from .helpers import _err, _expr_error  # noqa: F401


def checks_matrices_22(check, ev, near, ex, mtext):
    """Sprint 5 : matrices and vectors"""
    # ---------------------------------------------------------------- Sprint 5 : matrices and vectors
    import itertools
    rnd = random.Random(2026)

    def perm_sign(p):
        s = 1
        p = list(p)
        for i in range(len(p)):
            while p[i] != i:
                j = p[i]
                p[i], p[j] = p[j], p[i]
                s = -s
        return s

    def leibniz(M):
        n = len(M)
        return sum(perm_sign(p) * math.prod(M[i][p[i]] for i in range(n)) for p in itertools.permutations(range(n)))

    def mm3(A, B):
        return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

    def flat(M):
        return ",".join(str(x) for row in M for x in row)

    mats = [[[rnd.randint(-5, 5) for _ in range(3)] for _ in range(3)] for _ in range(14)]
    mats += [[[1, 2, 3], [4, 5, 6], [7, 8, 10]], [[2, 0, 0], [0, 3, 0], [0, 0, 4]], [[0, 1, 0], [0, 0, 1], [1, 0, 0]], [[1, 2, 3], [2, 4, 6], [1, 0, 1]]]
    for M in mats:
        tag = flat(M)
        d = leibniz(M)
        near(f"triple_scalar({tag}) = det", f"triple_scalar({tag})", d)
        if d != 0:
            inv = mtext(f"mat_inv3({tag})")
            prod = mm3(M, inv)
            check(f"mat_inv3({tag}): M times inverse is I", all(abs(prod[i][j] - (i == j)) < 1e-7 for i in range(3) for j in range(3)), True)
            adj = [[(-1) ** (i + j) * leibniz([[M[r][c] for c in range(3) if c != j] for r in range(3) if r != i]) for i in range(3)] for j in range(3)]
            check(f"mat_inv3({tag}) = adjugate / det", all(abs(inv[i][j] - adj[i][j] / d) < 1e-7 for i in range(3) for j in range(3)), True)
            for n_ in (-2, -1):
                want = inv
                for _ in range(abs(n_) - 1):
                    want = mm3(want, inv)
                got = mtext(f"mat_pow3({tag},{n_})")
                check(f"mat_pow3({tag},{n_}) uses the inverse", all(abs(got[i][j] - want[i][j]) < 1e-5 * max(1, abs(want[i][j])) for i in range(3) for j in range(3)), True)
        else:
            check(f"mat_inv3 of singular ({tag})", _err(f"mat_inv3({tag})"), "Math ERROR")
        check(f"mat_transpose3({tag})", mtext(f"mat_transpose3({tag})"), [[M[j][i] for j in range(3)] for i in range(3)])
        near(f"trace3({tag})", f"trace3({tag})", M[0][0] + M[1][1] + M[2][2])
        check(f"mat_scalar3(3,{tag})", mtext(f"mat_scalar3(3,{tag})"), [[3 * x for x in row] for row in M])
        for n_, want in ((0, [[1, 0, 0], [0, 1, 0], [0, 0, 1]]), (1, M), (2, mm3(M, M)), (5, mm3(mm3(mm3(M, M), M), mm3(M, M)))):
            check(f"mat_pow3({tag},{n_})", mtext(f"mat_pow3({tag},{n_})"), want)
        for i in (1, 2, 3):
            for j in (1, 2, 3):
                mnr = leibniz([[M[r][c] for c in range(3) if c != j - 1] for r in range(3) if r != i - 1])
                near(f"mat_minor3({tag},{i},{j})", f"mat_minor3({tag},{i},{j})", mnr)
                near(f"mat_cofactor3({tag},{i},{j})", f"mat_cofactor3({tag},{i},{j})", (-1) ** (i + j) * mnr)
        near(f"det by cofactor expansion along row 1 ({tag})", "+".join(f"mat_cofactor3({tag},1,{j})*{M[0][j - 1]}" for j in (1, 2, 3)), d)
    for A, B in zip(mats[:6], mats[6:12]):
        check("mat_mul3", mtext(f"mat_mul3({flat(A)},{flat(B)})"), mm3(A, B))
        check("mat_add3", mtext(f"mat_add3({flat(A)},{flat(B)})"), [[A[i][j] + B[i][j] for j in range(3)] for i in range(3)])
        near("det of a product is the product of dets", f"triple_scalar({flat(mm3(A, B))})", leibniz(A) * leibniz(B))
    I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    check("mat_mul3 identity", mtext(f"mat_mul3({flat(mats[0])},{flat(I3)})"), mats[0])
    check("mat_inv3 fraction", mtext("mat_inv3(2,0,0,0,4,0,0,0,8)"), [[0.5, 0, 0], [0, 0.25, 0], [0, 0, 0.125]])
    ex("mat_pow3 exact integers stay exact", "mat_pow3(1,1,0,0,1,1,0,0,1,40)", ((1, 40, 780), (0, 1, 40), (0, 0, 1)))
    for k in range(5):
        M4 = [[rnd.randint(-4, 4) for _ in range(4)] for _ in range(4)]
        near(f"det4 random {k}", f"det4({flat(M4)})", leibniz(M4))
        near(f"det4 transpose {k}", f"det4({flat([[M4[j][i] for j in range(4)] for i in range(4)])})", leibniz(M4))
        near(f"det4 swapping two rows flips the sign {k}", f"det4({flat([M4[1], M4[0], M4[2], M4[3]])})", -leibniz(M4))
        near(f"det4 scaling a row {k}", f"det4({flat([[3 * x for x in M4[0]]] + M4[1:])})", 3 * leibniz(M4))
    near("det4 identity", "det4(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1)", 1)
    near("det4 repeated rows", "det4(1,2,3,4,1,2,3,4,5,6,7,8,9,1,2,3)", 0)
    near("det4 with fractions is exact", "det4(1/2,0,0,0,0,1/3,0,0,0,0,1/5,0,0,0,0,1/7)", 1 / 210, 1e-12)
    for rows, want in [([[1, 0, 0], [0, 1, 0], [0, 0, 1]], 3), ([[0, 0, 0]] * 3, 0), ([[1, 2, 3], [2, 4, 6], [3, 6, 9]], 1),
                       ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2), ([[1, 2, 3], [4, 5, 6], [7, 8, 10]], 3), ([[0, 0, 1], [0, 0, 2], [0, 0, 5]], 1)]:
        near(f"mat_rank3({flat(rows)})", f"mat_rank3({flat(rows)})", want)
    for _ in range(8):
        r1, r2 = [rnd.randint(-4, 4) for _ in range(3)], [rnd.randint(-4, 4) for _ in range(3)]
        a_, b_ = rnd.randint(-3, 3), rnd.randint(-3, 3)
        r3 = [a_ * x + b_ * y for x, y in zip(r1, r2)]
        rk = ev(f"mat_rank3({flat([r1, r2, r3])})")
        check(f"mat_rank3 of a dependent third row {r1}{r2}", rk <= 2 and abs(leibniz([r1, r2, r3])) == 0, True)

    vecs = [(1, 2, 3), (-4, 5, 6), (0.5, -2, 7), (3, 0, -1), (2, 2, 2)]
    for u in vecs:
        for v in vecs:
            tu, tv = ",".join(map(str, u)), ",".join(map(str, v))
            cr = [ev(f"cross3_{c}({tu},{tv})") for c in "xyz"]
            want = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            check(f"cross3_xyz({u},{v})", all(abs(a - b) < 1e-9 for a, b in zip(cr, want)), True)
            check(f"cross3({u},{v}) is perpendicular to both", abs(sum(a * b for a, b in zip(cr, u))) < 1e-9 and abs(sum(a * b for a, b in zip(cr, v))) < 1e-9, True)
            dotuv = sum(a * b for a, b in zip(u, v))
            check(f"Lagrange identity |uxv|^2 = |u|^2|v|^2 - (u.v)^2 ({u},{v})",
                  abs(sum(c * c for c in cr) - (sum(a * a for a in u) * sum(b * b for b in v) - dotuv ** 2)) < 1e-7, True)
            if u != v:
                mu, mv = math.sqrt(sum(a * a for a in u)), math.sqrt(sum(a * a for a in v))
                near(f"angle_vectors3({u},{v}) via atan2(|uxv|, u.v)", f"angle_vectors3({tu},{tv})", math.degrees(math.atan2(math.sqrt(sum(c * c for c in cr)), dotuv)), 1e-9)
            near(f"dot_n 3 ({u},{v})", f"dot_n(3,{tu},{tv})", sum(a * b for a, b in zip(u, v)), 1e-9)
    for u, v, w in zip(vecs, vecs[1:], vecs[2:]):
        t3 = ",".join(map(str, u + v + w))
        crx = [v[1] * w[2] - v[2] * w[1], v[2] * w[0] - v[0] * w[2], v[0] * w[1] - v[1] * w[0]]
        near(f"triple_scalar = u.(v x w) {u}{v}{w}", f"triple_scalar({t3})", sum(a * b for a, b in zip(u, crx)), 1e-9)
        near(f"tetra_vol_pts is |triple|/6 {u}{v}{w}", f"tetra_vol_pts(0,0,0,{t3})", abs(sum(a * b for a, b in zip(u, crx))) / 6, 1e-9)
    near("tetra_vol_pts unit corner", "tetra_vol_pts(0,0,0,1,0,0,0,1,0,0,0,1)", 1 / 6, 1e-12)
    near("tetra_vol_pts regular tetrahedron", "tetra_vol_pts(1,1,1,1,-1,-1,-1,1,-1,-1,-1,1)", ev("tetra_vol_reg(2*sqrt(2))"), 1e-9)
    near("tetra_vol_pts coplanar", "tetra_vol_pts(0,0,0,1,0,0,0,1,0,1,1,0)", 0)
    for n_ in (1, 2, 3, 5, 8):
        xs = [rnd.randint(-9, 9) for _ in range(n_)]
        ys = [rnd.randint(-9, 9) for _ in range(n_)]
        sx, sy = ",".join(map(str, xs)), ",".join(map(str, ys))
        near(f"dot_n n={n_}", f"dot_n({n_},{sx},{sy})", sum(a * b for a, b in zip(xs, ys)))
        near(f"norm_n n={n_}", f"norm_n({sx})", math.hypot(*xs), 1e-12)
        near(f"norm_l1 n={n_}", f"norm_l1({sx})", sum(abs(a) for a in xs))
        near(f"norm_inf n={n_}", f"norm_inf({sx})", max(abs(a) for a in xs))
        check(f"norm ordering inf <= n <= l1 ({n_})", ev(f"norm_inf({sx})") <= ev(f"norm_n({sx})") + 1e-12 <= ev(f"norm_l1({sx})") + 2e-12, True)
    near("norm_n 3-4-12", "norm_n(3,4,12)", 13)
    for (x, y) in [(3, 4), (-1, 1), (0, 5), (0.3, -0.9)]:
        ux, uy = ev(f"unit2_x({x},{y})"), ev(f"unit2_y({x},{y})")
        check(f"unit2({x},{y}) has length 1", abs(math.hypot(ux, uy) - 1) < 1e-12, True)
        check(f"unit2({x},{y}) points the same way", abs(ux * y - uy * x) < 1e-12 and ux * x + uy * y > 0, True)
    for u in vecs:
        t = ",".join(map(str, u))
        w = [ev(f"unit3_{c}({t})") for c in "xyz"]
        check(f"unit3({u}) has length 1", abs(math.sqrt(sum(a * a for a in w)) - 1) < 1e-12, True)
        check(f"unit3({u}) is parallel", all(abs(c) < 1e-12 for c in (w[1] * u[2] - w[2] * u[1], w[2] * u[0] - w[0] * u[2], w[0] * u[1] - w[1] * u[0])), True)
    for (nx, ny, nz, px, py, pz) in [(1, 2, 3, 1, 1, 1), (0, 0, 1, 5, 5, 4), (2, -1, 4, 0.5, 2, -3)]:
        d_ = ev(f"plane_d({nx},{ny},{nz},{px},{py},{pz})")
        check(f"plane_d({nx},{ny},{nz}): the point lies on the plane", abs(nx * px + ny * py + nz * pz + d_) < 1e-12, True)
        for (qx, qy, qz) in [(0, 0, 0), (3, -2, 1), (px, py, pz)]:
            nn = math.sqrt(nx * nx + ny * ny + nz * nz)
            k = (nx * qx + ny * qy + nz * qz + d_) / (nn * nn)
            foot = (qx - nx * k, qy - ny * k, qz - nz * k)
            check("foot of the perpendicular lies on the plane", abs(nx * foot[0] + ny * foot[1] + nz * foot[2] + d_) < 1e-9, True)
            near(f"point_plane_dist(({qx},{qy},{qz}), n=({nx},{ny},{nz}))", f"point_plane_dist({qx},{qy},{qz},{nx},{ny},{nz},{d_!r})", math.dist((qx, qy, qz), foot), 1e-9)
    for P in [((0, 0, 0), (4, 0, 0), (0, 3, 0)), ((1, 2, 3), (4, 6, 3), (1, 2, 9)), ((0, 0, 0), (1, 2, 3), (-2, 5, 1))]:
        t = ",".join(str(c) for pt in P for c in pt)
        a_, b_, c_ = math.dist(P[1], P[2]), math.dist(P[0], P[2]), math.dist(P[0], P[1])
        s_ = (a_ + b_ + c_) / 2
        near(f"tri_area3 by Heron {P}", f"tri_area3({t})", math.sqrt(max(s_ * (s_ - a_) * (s_ - b_) * (s_ - c_), 0)), 1e-9)
    near("tri_area3 collinear points", "tri_area3(0,0,0,1,1,1,2,2,2)", 0, 1e-12)
