"""Sprint 4: geometry extras

Module 26 of 47.  Taken from lines 8443-8923 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_geometry_extras"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import MathError
from .registry import register
from .arithmetic import ar_is_exact
from .lib_powers_rounding import _whole

# ======================================================================================
#  SPRINT 4 : GEOMETRY EXTRAS (61)
#  Conventions: every angle argument and every angle result is in DEGREES (like
#  projectile_range and sector_area(r, deg)), whatever the DEG/RAD/GRAD mode says.
#  Lengths, radii and heights must be positive; impossible shapes give Math ERROR.
# ======================================================================================

def _gpos(*vals):
    for v in vals:
        if not (v > 0) or math.isinf(v):
            raise MathError("lengths must be positive")


def _gtri(a, b, c):
    _gpos(a, b, c)
    if a + b <= c or a + c <= b or b + c <= a:
        raise MathError("these sides do not form a triangle")
    s = (a + b + c) / 2
    return s, math.sqrt(s * (s - a) * (s - b) * (s - c))


def _gangle(deg, lo=0.0, hi=360.0):
    if not (lo <= deg <= hi):
        raise MathError("angle out of range")
    return math.radians(deg)


def _gpoly_n(n):
    n = _whole(n, "number of sides")
    if n < 3:
        raise MathError("a polygon needs at least 3 sides")
    return n


def _xy_area(*pts):
    """Absolute shoelace area; pts = x1, y1, x2, y2, ..."""
    n = len(pts) // 2
    total = 0.0
    for i in range(n):
        x1, y1 = pts[2 * i], pts[2 * i + 1]
        x2, y2 = pts[2 * ((i + 1) % n)], pts[2 * ((i + 1) % n) + 1]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2


def _tri_sides_xy(x1, y1, x2, y2, x3, y3):
    a = math.hypot(x2 - x3, y2 - y3)
    b = math.hypot(x1 - x3, y1 - y3)
    c = math.hypot(x1 - x2, y1 - y2)
    if _xy_area(x1, y1, x2, y2, x3, y3) <= 1e-12 * max(1.0, a * b, b * c, a * c):
        raise MathError("the three points are on one line")
    return a, b, c


def _circumcenter(x1, y1, x2, y2, x3, y3):
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) <= 1e-12 * max(1.0, abs(x1 * y2), abs(x2 * y3), abs(x3 * y1)):
        raise MathError("the three points are on one line")
    s1, s2, s3 = x1 * x1 + y1 * y1, x2 * x2 + y2 * y2, x3 * x3 + y3 * y3
    ux = (s1 * (y2 - y3) + s2 * (y3 - y1) + s3 * (y1 - y2)) / d
    uy = (s1 * (x3 - x2) + s2 * (x1 - x3) + s3 * (x2 - x1)) / d
    return ux, uy


_G2 = "Geometry"
_G3 = "Geometry 3D"


# ---------- triangle solving ----------
@register("tri_side_sas", _G2, "Third side from two sides and the angle between them in degrees (law of cosines): tri_side_sas(a, C, b)", 3, example="tri_side_sas(3, 90, 4) => 5")
def tri_side_sas(a, C, b):
    _gpos(a, b)
    rad = _gangle(C, 0.0, 180.0)
    if C in (0.0, 180.0):
        raise MathError("angle must be between 0 and 180")
    return math.sqrt(max(a * a + b * b - 2 * a * b * math.cos(rad), 0.0))


@register("tri_angle", _G2, "Angle in degrees opposite side a, from three sides: tri_angle(a, b, c)", 3, example="tri_angle(3, 4, 5) => 36.86989765")
def tri_angle(a, b, c):
    _gtri(a, b, c)
    x = (b * b + c * c - a * a) / (2 * b * c)
    return math.degrees(math.acos(max(-1.0, min(1.0, x))))


@register("tri_area_sas", _G2, "Triangle area from two sides and the included angle in degrees: tri_area_sas(a, C, b)", 3, example="tri_area_sas(3, 90, 4) => 6")
def tri_area_sas(a, C, b):
    _gpos(a, b)
    if not (0.0 < C < 180.0):
        raise MathError("angle must be between 0 and 180")
    return 0.5 * a * b * math.sin(math.radians(C))


@register("circumradius", _G2, "Radius of the circumscribed circle of a triangle: circumradius(a, b, c)", 3, example="circumradius(3, 4, 5) => 2.5")
def circumradius(a, b, c):
    s, k = _gtri(a, b, c)
    return a * b * c / (4 * k)


@register("inradius", _G2, "Radius of the inscribed circle of a triangle: inradius(a, b, c)", 3, example="inradius(3, 4, 5) => 1")
def inradius(a, b, c):
    s, k = _gtri(a, b, c)
    return k / s


@register("exradius_a", _G2, "Radius of the excircle opposite side a: exradius_a(a, b, c)", 3, example="exradius_a(3, 4, 5) => 2")
def exradius_a(a, b, c):
    s, k = _gtri(a, b, c)
    return k / (s - a)


@register("tri_median", _G2, "Median to side a: tri_median(a, b, c)", 3, example="tri_median(5, 3, 4) => 2.5")
def tri_median(a, b, c):
    _gtri(a, b, c)
    return 0.5 * math.sqrt(2 * b * b + 2 * c * c - a * a)


@register("tri_altitude", _G2, "Altitude to side a: tri_altitude(a, b, c)", 3, example="tri_altitude(5, 3, 4) => 2.4")
def tri_altitude(a, b, c):
    s, k = _gtri(a, b, c)
    return 2 * k / a


@register("tri_bisector", _G2, "Length of the angle bisector from the vertex opposite side a: tri_bisector(a, b, c)", 3, example="tri_bisector(6, 5, 5) => 4")
def tri_bisector(a, b, c):
    _gtri(a, b, c)
    return math.sqrt(b * c * ((b + c) ** 2 - a * a)) / (b + c)


# ---------- triangle centres from coordinates ----------
@register("tri_centroid_x", _G2, "x of the centroid of a triangle: tri_centroid_x(x1, y1, x2, y2, x3, y3)", 6, example="tri_centroid_x(0, 0, 6, 0, 0, 3) => 2")
def tri_centroid_x(x1, y1, x2, y2, x3, y3):
    return (x1 + x2 + x3) / 3


@register("tri_centroid_y", _G2, "y of the centroid of a triangle: tri_centroid_y(x1, y1, x2, y2, x3, y3)", 6, example="tri_centroid_y(0, 0, 6, 0, 0, 3) => 1")
def tri_centroid_y(x1, y1, x2, y2, x3, y3):
    return (y1 + y2 + y3) / 3


@register("tri_circumcenter_x", _G2, "x of the circumcentre: tri_circumcenter_x(x1, y1, x2, y2, x3, y3)", 6, example="tri_circumcenter_x(0, 0, 4, 0, 0, 3) => 2")
def tri_circumcenter_x(x1, y1, x2, y2, x3, y3):
    return _circumcenter(x1, y1, x2, y2, x3, y3)[0]


@register("tri_circumcenter_y", _G2, "y of the circumcentre: tri_circumcenter_y(x1, y1, x2, y2, x3, y3)", 6, example="tri_circumcenter_y(0, 0, 4, 0, 0, 3) => 1.5")
def tri_circumcenter_y(x1, y1, x2, y2, x3, y3):
    return _circumcenter(x1, y1, x2, y2, x3, y3)[1]


def _incenter(x1, y1, x2, y2, x3, y3):
    a, b, c = _tri_sides_xy(x1, y1, x2, y2, x3, y3)
    p = a + b + c
    return (a * x1 + b * x2 + c * x3) / p, (a * y1 + b * y2 + c * y3) / p


@register("tri_incenter_x", _G2, "x of the incentre: tri_incenter_x(x1, y1, x2, y2, x3, y3)", 6, example="tri_incenter_x(0, 0, 4, 0, 0, 3) => 1")
def tri_incenter_x(x1, y1, x2, y2, x3, y3):
    return _incenter(x1, y1, x2, y2, x3, y3)[0]


@register("tri_incenter_y", _G2, "y of the incentre: tri_incenter_y(x1, y1, x2, y2, x3, y3)", 6, example="tri_incenter_y(0, 0, 4, 0, 0, 3) => 1")
def tri_incenter_y(x1, y1, x2, y2, x3, y3):
    return _incenter(x1, y1, x2, y2, x3, y3)[1]


def _orthocenter(x1, y1, x2, y2, x3, y3):
    ux, uy = _circumcenter(x1, y1, x2, y2, x3, y3)
    return x1 + x2 + x3 - 2 * ux, y1 + y2 + y3 - 2 * uy      # H = A + B + C - 2 O


@register("tri_orthocenter_x", _G2, "x of the orthocentre: tri_orthocenter_x(x1, y1, x2, y2, x3, y3)", 6, example="tri_orthocenter_x(0, 0, 4, 0, 0, 3) => 0")
def tri_orthocenter_x(x1, y1, x2, y2, x3, y3):
    return _orthocenter(x1, y1, x2, y2, x3, y3)[0]


@register("tri_orthocenter_y", _G2, "y of the orthocentre: tri_orthocenter_y(x1, y1, x2, y2, x3, y3)", 6, example="tri_orthocenter_y(0, 0, 4, 0, 0, 3) => 0")
def tri_orthocenter_y(x1, y1, x2, y2, x3, y3):
    return _orthocenter(x1, y1, x2, y2, x3, y3)[1]


# ---------- regular polygons ----------
@register("reg_poly_area", _G2, "Area of a regular n-gon with side s: reg_poly_area(n, s)", 2, exact=True, example="reg_poly_area(4, 2) => 4")
def reg_poly_area(n, s):
    n = _gpoly_n(n)
    s = float(s)
    _gpos(s)
    return n * s * s / (4 * math.tan(math.pi / n))


@register("reg_poly_apothem", _G2, "Apothem of a regular n-gon with side s: reg_poly_apothem(n, s)", 2, exact=True, example="reg_poly_apothem(4, 2) => 1")
def reg_poly_apothem(n, s):
    n = _gpoly_n(n)
    s = float(s)
    _gpos(s)
    return s / (2 * math.tan(math.pi / n))


@register("reg_poly_interior", _G2, "Interior angle in degrees of a regular n-gon: reg_poly_interior(n)", 1, exact=True, example="reg_poly_interior(6) => 120")
def reg_poly_interior(n):
    n = _gpoly_n(n)
    return Fraction((n - 2) * 180, n)


@register("reg_poly_diagonals", _G2, "Number of diagonals of an n-gon: reg_poly_diagonals(n)", 1, exact=True, example="reg_poly_diagonals(6) => 9")
def reg_poly_diagonals(n):
    n = _gpoly_n(n)
    return n * (n - 3) // 2


@register("reg_poly_circumradius", _G2, "Circumradius of a regular n-gon with side s: reg_poly_circumradius(n, s)", 2, exact=True, example="reg_poly_circumradius(6, 2) => 2")
def reg_poly_circumradius(n, s):
    n = _gpoly_n(n)
    s = float(s)
    _gpos(s)
    return s / (2 * math.sin(math.pi / n))


# ---------- areas from coordinates ----------
@register("area_xy3", _G2, "Triangle area from coordinates: area_xy3(x1, y1, x2, y2, x3, y3)", 6, example="area_xy3(0, 0, 4, 0, 0, 3) => 6")
def area_xy3(x1, y1, x2, y2, x3, y3):
    return _xy_area(x1, y1, x2, y2, x3, y3)


@register("area_xy4", _G2, "Quadrilateral area by the shoelace formula, vertices in order: area_xy4(x1, y1, ..., x4, y4)", 8, example="area_xy4(0, 0, 4, 0, 4, 3, 0, 3) => 12")
def area_xy4(x1, y1, x2, y2, x3, y3, x4, y4):
    return _xy_area(x1, y1, x2, y2, x3, y3, x4, y4)


# ---------- circles and ellipses ----------
@register("sector_area", _G2, "Area of a circular sector, angle in degrees: sector_area(r, deg)", 2, example="sector_area(2, 90) => 3.141592654")
def sector_area(r, deg):
    _gpos(r)
    return 0.5 * r * r * _gangle(deg)


@register("arc_len", _G2, "Arc length, angle in degrees: arc_len(r, deg)", 2, example="arc_len(2, 90) => 3.141592654")
def arc_len(r, deg):
    _gpos(r)
    return r * _gangle(deg)


@register("segment_area", _G2, "Area of a circular segment, angle in degrees: segment_area(r, deg)", 2, example="segment_area(2, 90) => 1.141592654")
def segment_area(r, deg):
    _gpos(r)
    t = _gangle(deg)
    return 0.5 * r * r * (t - math.sin(t))


@register("chord_len", _G2, "Chord length for a central angle in degrees: chord_len(r, deg)", 2, example="chord_len(2, 90) => 2.828427125")
def chord_len(r, deg):
    _gpos(r)
    return 2 * r * math.sin(_gangle(deg) / 2)


@register("annulus_area", _G2, "Area of a ring between radii R and r: annulus_area(R, r)", 2, example="annulus_area(3, 2) => 15.70796327")
def annulus_area(R, r):
    _gpos(R)
    if r < 0 or r > R:
        raise MathError("need 0 <= r <= R")
    return math.pi * (R * R - r * r)


@register("circle_3pt_r", _G2, "Radius of the circle through three points: circle_3pt_r(x1, y1, x2, y2, x3, y3)", 6, example="circle_3pt_r(0, 0, 4, 0, 0, 3) => 2.5")
def circle_3pt_r(x1, y1, x2, y2, x3, y3):
    a, b, c = _tri_sides_xy(x1, y1, x2, y2, x3, y3)
    return a * b * c / (4 * _xy_area(x1, y1, x2, y2, x3, y3))


@register("ellipse_ecc", _G2, "Eccentricity of an ellipse with semi-axes a and b: ellipse_ecc(a, b)", 2, example="ellipse_ecc(5, 3) => 0.8")
def ellipse_ecc(a, b):
    _gpos(a, b)
    big, small = max(a, b), min(a, b)
    return math.sqrt(1 - (small / big) ** 2)


@register("ellipse_focus", _G2, "Distance from the centre to a focus: ellipse_focus(a, b)", 2, example="ellipse_focus(5, 3) => 4")
def ellipse_focus(a, b):
    _gpos(a, b)
    return math.sqrt(abs(a * a - b * b))


# ---------- solids ----------
@register("frustum_cone_vol", _G3, "Volume of a cone frustum: frustum_cone_vol(r1, r2, h)", 3, example="frustum_cone_vol(1, 2, 3) => 21.99114858")
def frustum_cone_vol(r1, r2, h):
    _gpos(r1, r2, h)
    return math.pi * h / 3 * (r1 * r1 + r1 * r2 + r2 * r2)


@register("frustum_cone_lsa", _G3, "Curved area of a cone frustum: frustum_cone_lsa(r1, r2, h)", 3, example="frustum_cone_lsa(3, 6, 4) => 141.3716694")
def frustum_cone_lsa(r1, r2, h):
    _gpos(r1, r2, h)
    return math.pi * (r1 + r2) * math.hypot(r1 - r2, h)


@register("frustum_pyr_vol", _G3, "Volume of a square pyramid frustum with base sides a1 and a2: frustum_pyr_vol(a1, a2, h)", 3, example="frustum_pyr_vol(1, 2, 3) => 7")
def frustum_pyr_vol(a1, a2, h):
    _gpos(a1, a2, h)
    return h / 3 * (a1 * a1 + a1 * a2 + a2 * a2)


@register("torus_vol", _G3, "Volume of a torus, centre radius R and tube radius r (R >= r): torus_vol(R, r)", 2, example="torus_vol(3, 1) => 59.21762641")
def torus_vol(R, r):
    _gpos(R, r)
    if r > R:
        raise MathError("tube radius cannot exceed R")
    return 2 * math.pi ** 2 * R * r * r


@register("torus_area", _G3, "Surface area of a torus (R >= r): torus_area(R, r)", 2, example="torus_area(3, 1) => 118.4352528")
def torus_area(R, r):
    _gpos(R, r)
    if r > R:
        raise MathError("tube radius cannot exceed R")
    return 4 * math.pi ** 2 * R * r


@register("ellipsoid_vol", _G3, "Volume of an ellipsoid with semi-axes a, b, c: ellipsoid_vol(a, b, c)", 3, example="ellipsoid_vol(1, 2, 3) => 25.13274123")
def ellipsoid_vol(a, b, c):
    _gpos(a, b, c)
    return 4 / 3 * math.pi * a * b * c


@register("cap_vol", _G3, "Volume of a spherical cap of height h on a sphere of radius r: cap_vol(r, h)", 2, example="cap_vol(2, 2) => 16.75516082")
def cap_vol(r, h):
    _gpos(r, h)
    if h > 2 * r:
        raise MathError("cap height cannot exceed the diameter")
    return math.pi * h * h * (3 * r - h) / 3


@register("cap_area", _G3, "Curved area of a spherical cap: cap_area(r, h)", 2, example="cap_area(2, 2) => 25.13274123")
def cap_area(r, h):
    _gpos(r, h)
    if h > 2 * r:
        raise MathError("cap height cannot exceed the diameter")
    return 2 * math.pi * r * h


@register("zone_area", _G3, "Area of a spherical zone of height h: zone_area(r, h)", 2, example="zone_area(2, 1) => 12.56637061")
def zone_area(r, h):
    _gpos(r, h)
    if h > 2 * r:
        raise MathError("zone height cannot exceed the diameter")
    return 2 * math.pi * r * h


@register("capsule_vol", _G3, "Volume of a capsule: cylinder of length h with a hemisphere of radius r on each end: capsule_vol(r, h)", 2, example="capsule_vol(1, 2) => 10.47197551")
def capsule_vol(r, h):
    _gpos(r, h)
    return math.pi * r * r * h + 4 / 3 * math.pi * r ** 3


@register("tetra_vol_reg", _G3, "Volume of a regular tetrahedron with edge a: tetra_vol_reg(a)", 1, example="tetra_vol_reg(1) => 0.1178511302")
def tetra_vol_reg(a):
    _gpos(a)
    return a ** 3 * math.sqrt(2) / 12


@register("octa_vol", _G3, "Volume of a regular octahedron with edge a: octa_vol(a)", 1, example="octa_vol(1) => 0.4714045208")
def octa_vol(a):
    _gpos(a)
    return a ** 3 * math.sqrt(2) / 3


@register("dodeca_vol", _G3, "Volume of a regular dodecahedron with edge a: dodeca_vol(a)", 1, example="dodeca_vol(1) => 7.663118961")
def dodeca_vol(a):
    _gpos(a)
    return a ** 3 * (15 + 7 * math.sqrt(5)) / 4


@register("icosa_vol", _G3, "Volume of a regular icosahedron with edge a: icosa_vol(a)", 1, example="icosa_vol(1) => 2.181694991")
def icosa_vol(a):
    _gpos(a)
    return a ** 3 * 5 * (3 + math.sqrt(5)) / 12


# ---------- coordinate geometry ----------
@register("dist2", _G2, "Distance between two points: dist2(x1, y1, x2, y2)", 4, example="dist2(0, 0, 3, 4) => 5")
def dist2(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


@register("dist3", _G2, "Distance between two points in 3-D: dist3(x1, y1, z1, x2, y2, z2)", 6, example="dist3(0, 0, 0, 2, 3, 6) => 7")
def dist3(x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


@register("midpoint_x", _G2, "Midpoint coordinate of two values: midpoint_x(x1, x2)", 2, example="midpoint_x(2, 6) => 4")
def midpoint_x(x1, x2):
    return (x1 + x2) / 2


@register("section_x", _G2, "Coordinate of the point dividing x1 to x2 in the ratio m:n: section_x(x1, x2, m, n)", 4, example="section_x(0, 10, 2, 3) => 4")
def section_x(x1, x2, m, n):
    if m + n == 0:
        raise MathError("m + n cannot be zero")
    return (m * x2 + n * x1) / (m + n)


@register("point_line_dist", _G2, "Distance from point (px, py) to the line ax + by + c = 0: point_line_dist(px, py, a, b, c)", 5, example="point_line_dist(0, 0, 3, 4, -10) => 2")
def point_line_dist(px, py, a, b, c):
    if a == 0 and b == 0:
        raise MathError("a and b cannot both be zero")
    return abs(a * px + b * py + c) / math.hypot(a, b)


@register("lines_angle", _G2, "Acute angle in degrees between two lines with slopes m1 and m2: lines_angle(m1, m2)", 2, example="lines_angle(1, -1) => 90")
def lines_angle(m1, m2):
    d = 1 + m1 * m2
    if d == 0:
        return 90.0
    return math.degrees(math.atan(abs((m1 - m2) / d)))


@register("collinear", _G2, "1 if three points lie on one line, else 0: collinear(x1, y1, x2, y2, x3, y3)", 6, exact=True, example="collinear(0, 0, 1, 1, 2, 2) => 1")
def collinear(x1, y1, x2, y2, x3, y3):
    cross = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if all(ar_is_exact(v) for v in (x1, y1, x2, y2, x3, y3)):
        return int(cross == 0)
    scale = max(1.0, abs((x2 - x1) * (y3 - y1)), abs((x3 - x1) * (y2 - y1)))
    return int(abs(cross) <= 1e-12 * scale)


@register("slant_to_height", _G3, "Vertical height from radius and slant height: slant_to_height(r, slant)", 2, example="slant_to_height(3, 5) => 4")
def slant_to_height(r, slant):
    _gpos(r, slant)
    if slant < r:
        raise MathError("slant height cannot be shorter than the radius")
    return math.sqrt(slant * slant - r * r)


@register("cone_slant", _G3, "Slant height of a cone: cone_slant(r, h)", 2, example="cone_slant(3, 4) => 5")
def cone_slant(r, h):
    _gpos(r, h)
    return math.hypot(r, h)


# ---------- pentagon and hexagon prisms and pyramids ----------
def _base(n, s):
    _gpos(s)
    return n * s * s / (4 * math.tan(math.pi / n))


@register("vol_pent_prism", _G3, "Volume of a regular pentagonal prism: vol_pent_prism(s, h)", 2, example="vol_pent_prism(1, 1) => 1.720477401")
def vol_pent_prism(s, h):
    _gpos(h)
    return _base(5, s) * h


@register("tsa_pent_prism", _G3, "Total surface area of a regular pentagonal prism: tsa_pent_prism(s, h)", 2, example="tsa_pent_prism(1, 1) => 8.440954801")
def tsa_pent_prism(s, h):
    _gpos(h)
    return 2 * _base(5, s) + 5 * s * h


@register("vol_hex_prism", _G3, "Volume of a regular hexagonal prism: vol_hex_prism(s, h)", 2, example="vol_hex_prism(1, 1) => 2.598076211")
def vol_hex_prism(s, h):
    _gpos(h)
    return _base(6, s) * h


@register("tsa_hex_prism", _G3, "Total surface area of a regular hexagonal prism: tsa_hex_prism(s, h)", 2, example="tsa_hex_prism(1, 1) => 11.19615242")
def tsa_hex_prism(s, h):
    _gpos(h)
    return 2 * _base(6, s) + 6 * s * h


@register("vol_pent_pyramid", _G3, "Volume of a regular pentagonal pyramid: vol_pent_pyramid(s, h)", 2, example="vol_pent_pyramid(1, 3) => 1.720477401")
def vol_pent_pyramid(s, h):
    _gpos(h)
    return _base(5, s) * h / 3


@register("vol_hex_pyramid", _G3, "Volume of a regular hexagonal pyramid: vol_hex_pyramid(s, h)", 2, example="vol_hex_pyramid(1, 3) => 2.598076211")
def vol_hex_pyramid(s, h):
    _gpos(h)
    return _base(6, s) * h / 3
