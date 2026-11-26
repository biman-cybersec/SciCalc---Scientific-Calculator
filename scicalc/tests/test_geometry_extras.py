"""Checks: geometry extras.  Run alone with  python run_tests.py geometry_extras"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "geometry_extras"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .helpers import _err, _expr_error  # noqa: F401


def checks_geometry_extras_18(check, ev, near, ex, simpson):
    """Sprint 4 geometry extras"""
    # ---------------------------------------------------------------- Sprint 4 geometry extras
    # Triangles are rebuilt from coordinates and measured directly (distances, perpendiculars).
    def place(a, b, c):                       # A=(0,0), B=(c,0), C found from the sides
        cx = (b * b + c * c - a * a) / (2 * c)
        return (0.0, 0.0), (c, 0.0), (cx, math.sqrt(max(b * b - cx * cx, 0.0)))

    def cross2(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])

    def dpt(p, q):
        return math.hypot(p[0] - q[0], p[1] - q[1])

    def dline(p, q, r):                       # distance from p to line qr
        return abs(cross2(q, r, p)) / dpt(q, r)

    for a, b, c in [(3, 4, 5), (5, 6, 7), (7, 8, 9), (6, 5, 5), (2.5, 3.5, 4.0), (13, 14, 15)]:
        A, B, C = place(a, b, c)
        area = abs(cross2(A, B, C)) / 2
        tag = f"{a},{b},{c}"
        near(f"inradius({tag}) = area/s", f"inradius({tag})", area / ((a + b + c) / 2), 1e-9)
        near(f"circumradius({tag}) = a/(2 sin A)", f"circumradius({tag})", a / (2 * math.sin(math.acos((b * b + c * c - a * a) / (2 * b * c)))), 1e-9)
        near(f"exradius_a({tag}) = area/(s-a)", f"exradius_a({tag})", area / ((a + b + c) / 2 - a), 1e-9)
        midBC = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
        near(f"tri_median({tag}) measured", f"tri_median({tag})", dpt(A, midBC), 1e-9)
        near(f"tri_altitude({tag}) measured", f"tri_altitude({tag})", dline(A, B, C), 1e-9)
        # bisector from A meets BC at the point dividing it in ratio c:b (measured, not via the formula)
        t = c / (b + c)
        foot = (B[0] + t * (C[0] - B[0]), B[1] + t * (C[1] - B[1]))
        near(f"tri_bisector({tag}) measured", f"tri_bisector({tag})", dpt(A, foot), 1e-9)
        ang = lambda P, Q, R: math.degrees(math.acos((dpt(P, Q) ** 2 + dpt(P, R) ** 2 - dpt(Q, R) ** 2) / (2 * dpt(P, Q) * dpt(P, R))))
        near(f"tri_angle({tag}) measured at A", f"tri_angle({a},{b},{c})", ang(A, B, C), 1e-9)
        near(f"angles of ({tag}) add to 180", f"tri_angle({a},{b},{c})+tri_angle({b},{a},{c})+tri_angle({c},{a},{b})", 180, 1e-9)
        near(f"tri_side_sas({tag}) rebuilds a", f"tri_side_sas({b},{ang(A, B, C)!r},{c})", a, 1e-9)
        near(f"tri_area_sas({tag})", f"tri_area_sas({b},{ang(A, B, C)!r},{c})", area, 1e-9)
        co = f"{A[0]!r},{A[1]!r},{B[0]!r},{B[1]!r},{C[0]!r},{C[1]!r}"
        near(f"area_xy3({tag})", f"area_xy3({co})", area, 1e-9)
        near(f"circle_3pt_r({tag})", f"circle_3pt_r({co})", ev(f"circumradius({tag})"), 1e-9)
        gx, gy = (A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3
        near(f"centroid_x({tag})", f"tri_centroid_x({co})", gx, 1e-9)
        near(f"centroid_y({tag})", f"tri_centroid_y({co})", gy, 1e-9)
        ox, oy = ev(f"tri_circumcenter_x({co})"), ev(f"tri_circumcenter_y({co})")
        check(f"circumcentre({tag}) equidistant from the vertices",
              max(abs(dpt((ox, oy), P) - ev(f"circumradius({tag})")) for P in (A, B, C)) < 1e-9, True)
        ix, iy = ev(f"tri_incenter_x({co})"), ev(f"tri_incenter_y({co})")
        r_in = ev(f"inradius({tag})")
        check(f"incentre({tag}) is r from every side",
              max(abs(dline((ix, iy), P, Q) - r_in) for P, Q in ((A, B), (B, C), (A, C))) < 1e-9, True)
        hx, hy = ev(f"tri_orthocenter_x({co})"), ev(f"tri_orthocenter_y({co})")
        H = (hx, hy)
        dot = lambda P, Q, R, S: (Q[0] - P[0]) * (S[0] - R[0]) + (Q[1] - P[1]) * (S[1] - R[1])
        check(f"orthocentre({tag}): AH perpendicular to BC, BH to AC",
              abs(dot(A, H, B, C)) < 1e-8 and abs(dot(B, H, A, C)) < 1e-8, True)
        near(f"Euler line: G divides O-H 1:2 ({tag})", f"tri_centroid_x({co})*3", ox * 2 + hx, 1e-9)
    near("tri_side_sas 60 degrees", "tri_side_sas(5,60,5)", 5, 1e-12)

    # regular polygons, built from vertex coordinates
    for n in (3, 4, 5, 6, 8, 12):
        for s_ in (1.0, 2.5):
            R_ = s_ / (2 * math.sin(math.pi / n))
            pts = [(R_ * math.cos(2 * math.pi * k / n), R_ * math.sin(2 * math.pi * k / n)) for k in range(n)]
            shoelace = abs(sum(pts[k][0] * pts[(k + 1) % n][1] - pts[(k + 1) % n][0] * pts[k][1] for k in range(n))) / 2
            near(f"reg_poly_area({n},{s_}) by shoelace", f"reg_poly_area({n},{s_})", shoelace, 1e-9)
            mid = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
            near(f"reg_poly_apothem({n},{s_}) measured", f"reg_poly_apothem({n},{s_})", math.hypot(*mid), 1e-9)
            near(f"reg_poly_circumradius({n},{s_}) measured", f"reg_poly_circumradius({n},{s_})", math.hypot(*pts[0]), 1e-9)
        ex(f"reg_poly_diagonals({n}) by counting", f"reg_poly_diagonals({n})", sum(1 for i in range(n) for j in range(i + 2, n) if not (i == 0 and j == n - 1)))
        ex(f"reg_poly_interior({n})", f"reg_poly_interior({n})", Fraction((n - 2) * 180, n))
        near(f"interior angles of {n}-gon sum to (n-2)*180", f"reg_poly_interior({n})*{n}", (n - 2) * 180, 1e-9)

    near("area_xy4 square", "area_xy4(0,0,2,0,2,2,0,2)", 4)
    near("area_xy4 clockwise gives the same", "area_xy4(0,0,0,2,2,2,2,0)", 4)
    near("area_xy4 = two triangles", "area_xy4(0,0,5,1,6,4,1,5)", ev("area_xy3(0,0,5,1,6,4)") + ev("area_xy3(0,0,6,4,1,5)"), 1e-12)

    # circles: sector/segment by integration of the arc, chord by coordinates
    for r_, d_ in [(1, 30), (2, 90), (3.5, 200), (5, 360)]:
        th = math.radians(d_)
        near(f"sector_area({r_},{d_}) fraction of the disc", f"sector_area({r_},{d_})", math.pi * r_ ** 2 * d_ / 360, 1e-12)
        near(f"arc_len({r_},{d_}) fraction of the circumference", f"arc_len({r_},{d_})", 2 * math.pi * r_ * d_ / 360, 1e-12)
        chord = math.hypot(r_ - r_ * math.cos(th), r_ * math.sin(th))
        near(f"chord_len({r_},{d_}) from coordinates", f"chord_len({r_},{d_})", chord, 1e-9)
        near(f"segment({r_},{d_}) = sector - triangle", f"segment_area({r_},{d_})", ev(f"sector_area({r_},{d_})") - 0.5 * r_ * r_ * math.sin(th), 1e-9)
    near("segment_area(1,180) is half a disc", "segment_area(1,180)", math.pi / 2, 1e-12)
    near("annulus_area", "annulus_area(5,3)", math.pi * 25 - math.pi * 9, 1e-12)
    near("annulus_area(r,0) is a disc", "annulus_area(4,0)", math.pi * 16, 1e-12)
    for a_, b_ in [(5, 3), (3, 5), (10, 6), (2, 2)]:
        big, small = max(a_, b_), min(a_, b_)
        f_ = math.sqrt(big ** 2 - small ** 2)
        near(f"ellipse_focus({a_},{b_})", f"ellipse_focus({a_},{b_})", f_, 1e-12)
        near(f"ellipse_ecc({a_},{b_}) = c/a", f"ellipse_ecc({a_},{b_})", f_ / big, 1e-12)

    # solids by numerical integration of the cross-section
    for r1, r2, h in [(1, 2, 3), (3, 6, 4), (2, 2, 5), (0.5, 4, 2)]:
        rad = lambda z: r1 + (r2 - r1) * z / h
        near(f"frustum_cone_vol({r1},{r2},{h}) integral", f"frustum_cone_vol({r1},{r2},{h})", simpson(lambda z: math.pi * rad(z) ** 2, 0, h, 200), 1e-9)
        slant = math.hypot(r1 - r2, h)
        near(f"frustum_cone_lsa({r1},{r2},{h}) integral", f"frustum_cone_lsa({r1},{r2},{h})", simpson(lambda z: 2 * math.pi * rad(z) * slant / h, 0, h, 200), 1e-9)
        near(f"frustum_pyr_vol({r1},{r2},{h}) integral", f"frustum_pyr_vol({r1},{r2},{h})", simpson(lambda z: rad(z) ** 2, 0, h, 200), 1e-9)
    near("frustum with equal radii is a cylinder", "frustum_cone_vol(2,2,5)", ev("vol_cylinder(2,5)"), 1e-12)
    near("frustum with r2->0 is a cone", "frustum_cone_vol(3,0.000001,4)", ev("vol_cone(3,4)"), 1e-5)
    for R_, r_ in [(3, 1), (5, 2), (2, 2)]:
        near(f"torus_vol({R_},{r_}) Pappus integral", f"torus_vol({R_},{r_})",
             simpson(lambda x: 2 * math.pi * (R_ + x) * 2 * math.sqrt(max(r_ * r_ - x * x, 0.0)), -r_, r_, 4000), 1e-5)
        near(f"torus_area({R_},{r_}) = circumference * circumference", f"torus_area({R_},{r_})", (2 * math.pi * R_) * (2 * math.pi * r_), 1e-12)
    for a_, b_, c_ in [(1, 2, 3), (2, 2, 2), (0.5, 1, 4)]:
        near(f"ellipsoid_vol({a_},{b_},{c_}) slices", f"ellipsoid_vol({a_},{b_},{c_})",
             simpson(lambda z: math.pi * a_ * b_ * max(1 - (z / c_) ** 2, 0.0), -c_, c_, 4000), 1e-6)
    near("ellipsoid with equal axes is a sphere", "ellipsoid_vol(3,3,3)", ev("vol_sphere(3)"), 1e-12)
    for r_, h_ in [(2, 2), (2, 1), (3, 4.5), (1, 2)]:
        near(f"cap_vol({r_},{h_}) slices", f"cap_vol({r_},{h_})", simpson(lambda x: math.pi * (r_ * r_ - (r_ - h_ + x) ** 2), 0, h_, 400), 1e-9)
        near(f"cap_area({r_},{h_}) = zone_area", f"cap_area({r_},{h_})", ev(f"zone_area({r_},{h_})"), 1e-12)
        near(f"zone_area({r_},{h_}) Archimedes", f"zone_area({r_},{h_})", 2 * math.pi * r_ * h_, 1e-12)
    near("cap of full height is the whole sphere", "cap_vol(2,4)", ev("vol_sphere(2)"), 1e-12)
    near("cap_area(r,2r) is the whole sphere", "cap_area(2,4)", ev("tsa_sphere(2)"), 1e-12)
    near("cap of height r is a hemisphere", "cap_vol(3,3)", ev("vol_hemisphere(3)"), 1e-12)
    for r_, h_ in [(1, 2), (2.5, 0.5), (3, 6)]:
        near(f"capsule_vol({r_},{h_}) = cylinder + sphere", f"capsule_vol({r_},{h_})", ev(f"vol_cylinder({r_},{h_})") + ev(f"vol_sphere({r_})"), 1e-12)

    # Platonic solids: volume = (1/3) * surface area * inradius, and the tetrahedron from a coordinate determinant
    for a_ in (1, 2.5):
        tet = [(a_ / 2 ** 1.5 * x, a_ / 2 ** 1.5 * y, a_ / 2 ** 1.5 * z) for x, y, z in [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]]
        v1 = [tet[i][k] - tet[0][k] for i in (1, 2, 3) for k in range(3)]
        det = (v1[0] * (v1[4] * v1[8] - v1[5] * v1[7]) - v1[1] * (v1[3] * v1[8] - v1[5] * v1[6]) + v1[2] * (v1[3] * v1[7] - v1[4] * v1[6]))
        near(f"tetra_vol_reg({a_}) determinant", f"tetra_vol_reg({a_})", abs(det) / 6, 1e-9)
        near(f"octa_vol({a_}) = two square pyramids", f"octa_vol({a_})", 2 * (a_ * a_) * (a_ / math.sqrt(2)) / 3, 1e-9)
        pent = 5 * a_ * a_ / (4 * math.tan(math.pi / 5))
        r_dod = a_ * math.sqrt((25 + 11 * math.sqrt(5)) / 40)
        near(f"dodeca_vol({a_}) = (1/3) * 12 faces * inradius", f"dodeca_vol({a_})", 12 * pent * r_dod / 3, 1e-9)
        r_ico = a_ * (3 * math.sqrt(3) + math.sqrt(15)) / 12
        near(f"icosa_vol({a_}) = (1/3) * 20 faces * inradius", f"icosa_vol({a_})", 20 * (math.sqrt(3) / 4 * a_ * a_) * r_ico / 3, 1e-9)
    near("tetra_vol_reg scales with a^3", "tetra_vol_reg(2)/tetra_vol_reg(1)", 8, 1e-12)

    # coordinate geometry
    for p_, q_ in [((0, 0), (3, 4)), ((-1, 2), (5, -6)), ((1.5, 2.5), (1.5, 9))]:
        near(f"dist2{p_}{q_}", f"dist2({p_[0]},{p_[1]},{q_[0]},{q_[1]})", math.dist(p_, q_), 1e-12)
        near(f"dist2 symmetric {p_}{q_}", f"dist2({q_[0]},{q_[1]},{p_[0]},{p_[1]})", math.dist(p_, q_), 1e-12)
    for p_, q_ in [((0, 0, 0), (2, 3, 6)), ((1, -2, 3), (-4, 5, 0.5))]:
        near(f"dist3{p_}{q_}", f"dist3({p_[0]},{p_[1]},{p_[2]},{q_[0]},{q_[1]},{q_[2]})", math.dist(p_, q_), 1e-12)
    for x1, x2 in [(2, 6), (-3, 5), (0.5, 0.25)]:
        near(f"midpoint_x({x1},{x2})", f"midpoint_x({x1},{x2})", (x1 + x2) / 2, 1e-12)
        near(f"section_x({x1},{x2},1,1) is the midpoint", f"section_x({x1},{x2},1,1)", (x1 + x2) / 2, 1e-12)
        near(f"section_x({x1},{x2},0,5) is the start", f"section_x({x1},{x2},0,5)", x1, 1e-12)
        near(f"section_x({x1},{x2},3,0) is the end", f"section_x({x1},{x2},3,0)", x2, 1e-12)
    near("section_x 2:3", "section_x(0,10,2,3)", 4)
    near("section_x external division", "section_x(0,10,3,-1)", 15)
    for (px, py, a_, b_, c_) in [(0, 0, 3, 4, -10), (2, 3, 1, -1, 0), (5, -2, 0, 2, 4), (1, 1, 2, 1, -3)]:
        # foot of the perpendicular found by projecting onto the line
        k = (a_ * px + b_ * py + c_) / (a_ * a_ + b_ * b_)
        foot = (px - a_ * k, py - b_ * k)
        check(f"foot of perpendicular lies on the line ({px},{py},{a_},{b_},{c_})", abs(a_ * foot[0] + b_ * foot[1] + c_) < 1e-9, True)
        near(f"point_line_dist({px},{py},{a_},{b_},{c_}) = distance to the foot", f"point_line_dist({px},{py},{a_},{b_},{c_})", math.dist((px, py), foot), 1e-9)
    for m1, m2 in [(1, -1), (0, 1), (2, 3), (-0.5, 4), (1, 1)]:
        t1, t2 = math.atan(m1), math.atan(m2)
        want = abs(math.degrees(t1 - t2))
        want = min(want, 180 - want)
        near(f"lines_angle({m1},{m2})", f"lines_angle({m1},{m2})", want, 1e-9)
    near("lines_angle perpendicular", "lines_angle(2,-0.5)", 90, 1e-9)
    near("lines_angle parallel", "lines_angle(3,3)", 0, 1e-9)
    ex("collinear yes", "collinear(0,0,1,1,2,2)", 1)
    ex("collinear no", "collinear(0,0,1,1,2,3)", 0)
    ex("collinear exact fractions", "collinear(0,0,1/3,1/3,2/3,2/3)", 1)
    ex("collinear vertical", "collinear(2,0,2,5,2,-7)", 1)
    ex("collinear same point", "collinear(1,1,1,1,4,4)", 1)
    ex("collinear decimals", "collinear(0,0,0.1,0.2,0.3,0.6)", 1)
    for r_, h_ in [(3, 4), (5, 12), (1, 1), (2.5, 6)]:
        sl = math.sqrt(r_ * r_ + h_ * h_)
        near(f"cone_slant({r_},{h_})", f"cone_slant({r_},{h_})", sl, 1e-12)
        near(f"slant_to_height({r_},slant) round trip", f"slant_to_height({r_},cone_slant({r_},{h_}))", h_, 1e-9)
        near(f"cone_slant matches lsa_cone ({r_},{h_})", f"lsa_cone({r_},{h_})", math.pi * r_ * sl, 1e-9)

    # pentagonal and hexagonal prisms / pyramids: base area from vertex coordinates
    for n, nm in ((5, "pent"), (6, "hex")):
        for s_, h_ in [(1, 1), (2, 3.5)]:
            Rb = s_ / (2 * math.sin(math.pi / n))
            pts = [(Rb * math.cos(2 * math.pi * k / n), Rb * math.sin(2 * math.pi * k / n)) for k in range(n)]
            base = abs(sum(pts[k][0] * pts[(k + 1) % n][1] - pts[(k + 1) % n][0] * pts[k][1] for k in range(n))) / 2
            near(f"vol_{nm}_prism({s_},{h_})", f"vol_{nm}_prism({s_},{h_})", base * h_, 1e-9)
            near(f"tsa_{nm}_prism({s_},{h_})", f"tsa_{nm}_prism({s_},{h_})", 2 * base + n * s_ * h_, 1e-9)
            near(f"vol_{nm}_pyramid({s_},{h_}) slices", f"vol_{nm}_pyramid({s_},{h_})", simpson(lambda z: base * (1 - z / h_) ** 2, 0, h_, 200), 1e-9)
    near("hexagonal prism equals six triangular prisms", "vol_hex_prism(2,3)", 6 * ev("area_xy3(0,0,2,0,1,1.7320508075688772)") * 3, 1e-9)
    near("pentagonal pyramid is a third of its prism", "vol_pent_pyramid(2,5)*3", ev("vol_pent_prism(2,5)"), 1e-12)
