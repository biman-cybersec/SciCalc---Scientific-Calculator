"""Sprint 5D: vectors and 3x3/4x4 matrices

Module 30 of 47.  Taken from lines 9685-9992 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_vectors_matrices"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import ArgumentError, MathError
from .registry import register
from .arithmetic import Mat
from .lib_powers_rounding import _whole

# ======================================================================================
#  SPRINT 5 - PART D : VECTORS AND 3x3 / 4x4 MATRICES (29)
#  Matrices are given row by row as plain numbers: mat_inv3(a,b,c, d,e,f, g,h,i).
#  Integer and fraction inputs are computed exactly; results come back as text
#  "[[..], [..]]" (9 decimals) or as numbers.  Angles are in degrees.
# ======================================================================================
_MAT = "Advanced Matrix & Linear Algebra"


def _fr(v):
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, (int, Fraction)):
        return Fraction(v)
    v = float(v)
    if not math.isfinite(v):
        raise MathError("numbers must be finite")
    return Fraction(repr(v))


def _mnum(q):
    if q.denominator == 1:
        return int(q)
    v = round(float(q), 9)
    return 0.0 if v == 0 else v


def _mval(M):
    return Mat(tuple(_mnum(q) for q in row) for row in M)


def _mat(nums, r, c=None):
    c = r if c is None else c
    if len(nums) != r * c:
        raise ArgumentError(f"need {r * c} numbers")
    q = [_fr(v) for v in nums]
    return [q[i * c:(i + 1) * c] for i in range(r)]


def _num(q):
    return int(q) if q.denominator == 1 else q


def _det(M):
    M = [row[:] for row in M]
    n = len(M)
    det = Fraction(1)
    for i in range(n):
        p = next((r for r in range(i, n) if M[r][i] != 0), None)
        if p is None:
            return Fraction(0)
        if p != i:
            M[i], M[p] = M[p], M[i]
            det = -det
        det *= M[i][i]
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            if f:
                M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return det


def _minv(M):
    n = len(M)
    A = [row[:] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(M)]
    for i in range(n):
        p = next((r for r in range(i, n) if A[r][i] != 0), None)
        if p is None:
            raise MathError("matrix is singular")
        A[i], A[p] = A[p], A[i]
        pv = A[i][i]
        A[i] = [x / pv for x in A[i]]
        for r in range(n):
            if r != i and A[r][i] != 0:
                f = A[r][i]
                A[r] = [x - f * y for x, y in zip(A[r], A[i])]
    return [row[n:] for row in A]


def _mmul(P, Q):
    return [[sum(P[i][k] * Q[k][j] for k in range(len(Q))) for j in range(len(Q[0]))] for i in range(len(P))]


def _rank(M):
    M = [row[:] for row in M]
    rank, rows, cols = 0, len(M), len(M[0])
    for c in range(cols):
        p = next((r for r in range(rank, rows) if M[r][c] != 0), None)
        if p is None:
            continue
        M[rank], M[p] = M[p], M[rank]
        for r in range(rows):
            if r != rank and M[r][c] != 0:
                f = M[r][c] / M[rank][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[rank])]
        rank += 1
    return rank


def _mr(name, desc, args, example, exact=True):
    return register(name, _MAT, desc, args, exact=exact, example=example)


@_mr("det4", "Determinant of a 4x4 matrix (16 numbers, row by row): det4(a11, ..., a44)", 16, "det4(1,0,0,0, 0,2,0,0, 0,0,3,0, 0,0,0,4) => 24")
def det4(*v):
    return _num(_det(_mat(v, 4)))


@_mr("mat_mul3", "Product of two 3x3 matrices (18 numbers): mat_mul3(A..., B...)", 18, "mat_mul3(1,2,3,4,5,6,7,8,9, 1,0,0,0,1,0,0,0,1) => {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}}")
def mat_mul3(*v):
    return _mval(_mmul(_mat(v[:9], 3), _mat(v[9:], 3)))


@_mr("mat_inv3", "Inverse of a 3x3 matrix (9 numbers): mat_inv3(a11, ..., a33)", 9, "mat_inv3(2,0,0, 0,4,0, 0,0,5) => {{0.5, 0, 0}, {0, 0.25, 0}, {0, 0, 0.2}}")
def mat_inv3(*v):
    return _mval(_minv(_mat(v, 3)))


@_mr("mat_transpose3", "Transpose of a 3x3 matrix (9 numbers): mat_transpose3(a11, ..., a33)", 9, "mat_transpose3(1,2,3,4,5,6,7,8,9) => {{1, 4, 7}, {2, 5, 8}, {3, 6, 9}}")
def mat_transpose3(*v):
    M = _mat(v, 3)
    return _mval([[M[j][i] for j in range(3)] for i in range(3)])


@_mr("mat_add3", "Sum of two 3x3 matrices (18 numbers): mat_add3(A..., B...)", 18, "mat_add3(1,2,3,4,5,6,7,8,9, 9,8,7,6,5,4,3,2,1) => {{10, 10, 10}, {10, 10, 10}, {10, 10, 10}}")
def mat_add3(*v):
    A, B = _mat(v[:9], 3), _mat(v[9:], 3)
    return _mval([[A[i][j] + B[i][j] for j in range(3)] for i in range(3)])


@_mr("mat_scalar3", "Scalar multiple of a 3x3 matrix: mat_scalar3(k, a11, ..., a33)", 10, "mat_scalar3(2, 1,2,3,4,5,6,7,8,9) => {{2, 4, 6}, {8, 10, 12}, {14, 16, 18}}")
def mat_scalar3(k, *v):
    k = _fr(k)
    return _mval([[k * q for q in row] for row in _mat(v, 3)])


@_mr("trace3", "Trace of a 3x3 matrix (9 numbers): trace3(a11, ..., a33)", 9, "trace3(1,2,3,4,5,6,7,8,9) => 15")
def trace3(*v):
    M = _mat(v, 3)
    return _num(M[0][0] + M[1][1] + M[2][2])


@_mr("mat_pow3", "Integer power of a 3x3 matrix (negative n uses the inverse): mat_pow3(a11, ..., a33, n)", 10, "mat_pow3(1,1,0, 0,1,1, 0,0,1, 3) => {{1, 3, 3}, {0, 1, 3}, {0, 0, 1}}")
def mat_pow3(*v):
    n = _whole(v[9], "n")
    if abs(n) > 2000:
        raise MathError("power too large")
    M = _mat(v[:9], 3)
    if n < 0:
        M, n = _minv(M), -n
    R = [[Fraction(int(i == j)) for j in range(3)] for i in range(3)]
    while n:
        if n & 1:
            R = _mmul(R, M)
        M = _mmul(M, M)
        n >>= 1
    return _mval(R)


@_mr("mat_rank3", "Rank of a 3x3 matrix (9 numbers): mat_rank3(a11, ..., a33)", 9, "mat_rank3(1,2,3, 2,4,6, 1,0,1) => 2")
def mat_rank3(*v):
    return _rank(_mat(v, 3))


def _minor3(v, i, j):
    i, j = _whole(i, "i"), _whole(j, "j")
    if not (1 <= i <= 3 and 1 <= j <= 3):
        raise MathError("i and j must be between 1 and 3")
    M = _mat(v, 3)
    sub = [[M[r][c] for c in range(3) if c != j - 1] for r in range(3) if r != i - 1]
    return _det(sub), i, j


@_mr("mat_minor3", "Minor M(i,j) of a 3x3 matrix, i and j from 1: mat_minor3(a11, ..., a33, i, j)", 11, "mat_minor3(1,2,3, 4,5,6, 7,8,10, 1, 1) => 2")
def mat_minor3(*v):
    return _num(_minor3(v[:9], v[9], v[10])[0])


@_mr("mat_cofactor3", "Cofactor C(i,j) of a 3x3 matrix, i and j from 1: mat_cofactor3(a11, ..., a33, i, j)", 11, "mat_cofactor3(1,2,3, 4,5,6, 7,8,10, 1, 2) => 2")
def mat_cofactor3(*v):
    m, i, j = _minor3(v[:9], v[9], v[10])
    return _num(m if (i + j) % 2 == 0 else -m)


# ---------- vectors ----------
def _vec(vals):
    return [_fr(x) for x in vals]


@register("dot_n", _MAT, "Dot product of two n-vectors: dot_n(n, x1..xn, y1..yn)", (3, None), exact=True, example="dot_n(3, 1,2,3, 4,5,6) => 32")
def dot_n(n, *v):
    n = _whole(n, "n")
    if n < 1 or len(v) != 2 * n:
        raise ArgumentError("dot_n needs n followed by 2n numbers")
    return _num(sum(a * b for a, b in zip(_vec(v[:n]), _vec(v[n:]))))


@register("norm_n", _MAT, "Euclidean length of an n-vector: norm_n(x1, ..., xn)", (1, None), example="norm_n(1, 2, 2) => 3")
def norm_n(*v):
    return math.sqrt(sum(x * x for x in v))


@register("norm_l1", _MAT, "Sum of absolute values: norm_l1(x1, ..., xn)", (1, None), exact=True, example="norm_l1(1, -2, 3) => 6")
def norm_l1(*v):
    return _num(sum(abs(x) for x in _vec(v)))


@register("norm_inf", _MAT, "Largest absolute value: norm_inf(x1, ..., xn)", (1, None), exact=True, example="norm_inf(1, -7, 3) => 7")
def norm_inf(*v):
    return _num(max(abs(x) for x in _vec(v)))


def _unit(v):
    m = math.sqrt(sum(float(x) ** 2 for x in v))
    if m == 0:
        raise MathError("the zero vector has no direction")
    return [x / m for x in v]


@register("unit2_x", _MAT, "x component of the unit vector of (x, y): unit2_x(x, y)", 2, example="unit2_x(3, 4) => 0.6")
def unit2_x(x, y):
    return _unit([x, y])[0]


@register("unit2_y", _MAT, "y component of the unit vector of (x, y): unit2_y(x, y)", 2, example="unit2_y(3, 4) => 0.8")
def unit2_y(x, y):
    return _unit([x, y])[1]


@register("unit3_x", _MAT, "x component of the unit vector of (x, y, z): unit3_x(x, y, z)", 3, example="unit3_x(2, 3, 6) => 0.2857142857")
def unit3_x(x, y, z):
    return _unit([x, y, z])[0]


@register("unit3_y", _MAT, "y component of the unit vector of (x, y, z): unit3_y(x, y, z)", 3, example="unit3_y(2, 3, 6) => 0.4285714286")
def unit3_y(x, y, z):
    return _unit([x, y, z])[1]


@register("unit3_z", _MAT, "z component of the unit vector of (x, y, z): unit3_z(x, y, z)", 3, example="unit3_z(2, 3, 6) => 0.8571428571")
def unit3_z(x, y, z):
    return _unit([x, y, z])[2]


@register("angle_vectors3", _MAT, "Angle in degrees between two 3-D vectors: angle_vectors3(ux, uy, uz, vx, vy, vz)", 6, example="angle_vectors3(1, 0, 0, 0, 1, 0) => 90")
def angle_vectors3(ux, uy, uz, vx, vy, vz):
    mu = math.sqrt(ux * ux + uy * uy + uz * uz)
    mv = math.sqrt(vx * vx + vy * vy + vz * vz)
    if mu == 0 or mv == 0:
        raise MathError("the zero vector has no direction")
    c = (ux * vx + uy * vy + uz * vz) / (mu * mv)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


@register("triple_scalar", _MAT, "Scalar triple product u . (v x w), 9 numbers: triple_scalar(u..., v..., w...)", 9, exact=True, example="triple_scalar(1,0,0, 0,1,0, 0,0,1) => 1")
def triple_scalar(*v):
    return _num(_det(_mat(v, 3)))


def _cross(ux, uy, uz, vx, vy, vz):
    u, v = _vec([ux, uy, uz]), _vec([vx, vy, vz])
    return [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]


@register("cross3_x", _MAT, "x of the cross product u x v: cross3_x(ux, uy, uz, vx, vy, vz)", 6, exact=True, example="cross3_x(1, 2, 3, 4, 5, 6) => -3")
def cross3_x(*a):
    return _num(_cross(*a)[0])


@register("cross3_y", _MAT, "y of the cross product u x v: cross3_y(ux, uy, uz, vx, vy, vz)", 6, exact=True, example="cross3_y(1, 2, 3, 4, 5, 6) => 6")
def cross3_y(*a):
    return _num(_cross(*a)[1])


@register("cross3_z", _MAT, "z of the cross product u x v: cross3_z(ux, uy, uz, vx, vy, vz)", 6, exact=True, example="cross3_z(1, 2, 3, 4, 5, 6) => -3")
def cross3_z(*a):
    return _num(_cross(*a)[2])


@register("point_plane_dist", _MAT, "Distance from a point to the plane ax+by+cz+d=0: point_plane_dist(px, py, pz, a, b, c, d)", 7, example="point_plane_dist(1, 2, 3, 0, 0, 1, -1) => 2")
def point_plane_dist(px, py, pz, a, b, c, d):
    n = math.sqrt(a * a + b * b + c * c)
    if n == 0:
        raise MathError("the normal vector must not be zero")
    return abs(a * px + b * py + c * pz + d) / n


@register("plane_d", _MAT, "d in ax+by+cz+d=0 for the plane through p with normal n: plane_d(nx, ny, nz, px, py, pz)", 6, exact=True, example="plane_d(1, 2, 3, 1, 1, 1) => -6")
def plane_d(nx, ny, nz, px, py, pz):
    if nx == 0 and ny == 0 and nz == 0:
        raise MathError("the normal vector must not be zero")
    return _num(-(_fr(nx) * _fr(px) + _fr(ny) * _fr(py) + _fr(nz) * _fr(pz)))


@register("tri_area3", _MAT, "Area of a triangle from three 3-D points (9 numbers): tri_area3(x1,y1,z1, x2,y2,z2, x3,y3,z3)", 9, example="tri_area3(0,0,0, 4,0,0, 0,3,0) => 6")
def tri_area3(x1, y1, z1, x2, y2, z2, x3, y3, z3):
    c = _cross(x2 - x1, y2 - y1, z2 - z1, x3 - x1, y3 - y1, z3 - z1)
    return 0.5 * math.sqrt(sum(float(q) ** 2 for q in c))


@register("tetra_vol_pts", _MAT, "Volume of a tetrahedron from four 3-D points (12 numbers): tetra_vol_pts(x1,y1,z1, ..., x4,y4,z4)", 12, exact=True, example="tetra_vol_pts(0,0,0, 1,0,0, 0,1,0, 0,0,1) => 0.1666666667")
def tetra_vol_pts(*v):
    P = _mat(v, 4, 3)
    rows = [[P[i][k] - P[0][k] for k in range(3)] for i in (1, 2, 3)]
    return _num(abs(_det(rows)) / 6)
