"""Checks: geometry.  Run alone with  python run_tests.py geometry"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "geometry"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_geometry_12(near, simpson):
    """geometry"""
    # ---------------------------------------------------------------- geometry
    for r_ in (0.5, 3, 7.25):
        near(f"area_circle({r_})", f"area_circle({r_})", math.pi * r_ ** 2)
        near(f"perim_circle({r_})", f"perim_circle({r_})", 2 * math.pi * r_)
        near(f"area_ellipse(r,r)={r_}", f"area_ellipse({r_},{r_})", math.pi * r_ ** 2)
        near(f"perim_ellipse(r,r)={r_}", f"perim_ellipse({r_},{r_})", 2 * math.pi * r_, 1e-9)
        near(f"vol_sphere({r_}) by calculus", f"vol_sphere({r_})", simpson(lambda x: math.pi * (r_ * r_ - x * x), -r_, r_, 200), 1e-9)
        near(f"tsa_sphere({r_})", f"tsa_sphere({r_})", 4 * math.pi * r_ ** 2)
        near(f"vol_hemisphere({r_})", f"vol_hemisphere({r_})", 2 * math.pi * r_ ** 3 / 3)
        near(f"lsa_hemisphere({r_})", f"lsa_hemisphere({r_})", 2 * math.pi * r_ ** 2)
        near(f"tsa_hemisphere({r_})", f"tsa_hemisphere({r_})", 3 * math.pi * r_ ** 2)
        for h in (1.5, 4):
            near(f"vol_cylinder({r_},{h})", f"vol_cylinder({r_},{h})", math.pi * r_ ** 2 * h)
            near(f"lsa_cylinder({r_},{h})", f"lsa_cylinder({r_},{h})", 2 * math.pi * r_ * h)
            near(f"tsa_cylinder({r_},{h})", f"tsa_cylinder({r_},{h})", 2 * math.pi * r_ * (r_ + h))
            near(f"vol_cone({r_},{h}) is a third of the cylinder", f"vol_cone({r_},{h})*3", math.pi * r_ ** 2 * h)
            sl = math.sqrt(r_ * r_ + h * h)
            near(f"lsa_cone({r_},{h})", f"lsa_cone({r_},{h})", math.pi * r_ * sl)
            near(f"tsa_cone({r_},{h})", f"tsa_cone({r_},{h})", math.pi * r_ * sl + math.pi * r_ ** 2)
    for s_ in (0.5, 3, 7):
        near(f"area_square({s_})", f"area_square({s_})", s_ * s_)
        near(f"perim_square({s_})", f"perim_square({s_})", 4 * s_)
        near(f"perim_rhombus({s_})", f"perim_rhombus({s_})", 4 * s_)
        near(f"vol_cube({s_})", f"vol_cube({s_})", s_ ** 3)
        near(f"lsa_cube({s_})", f"lsa_cube({s_})", 4 * s_ * s_)
        near(f"tsa_cube({s_})", f"tsa_cube({s_})", 6 * s_ * s_)
        near(f"vol_sq_pyramid({s_},5)", f"vol_sq_pyramid({s_},5)", s_ * s_ * 5 / 3)
        near(f"tsa_sq_pyramid({s_},5)", f"tsa_sq_pyramid({s_},5)", s_ * s_ + 2 * s_ * 5)
    for l_, w_, h_ in [(2, 3, 4), (1.5, 7, 0.5)]:
        near(f"area_rect({l_},{w_})", f"area_rect({l_},{w_})", l_ * w_)
        near(f"perim_rect({l_},{w_})", f"perim_rect({l_},{w_})", 2 * (l_ + w_))
        near(f"area_para({l_},{w_})", f"area_para({l_},{w_})", l_ * w_)
        near(f"perim_para({l_},{w_})", f"perim_para({l_},{w_})", 2 * (l_ + w_))
        near(f"area_rhombus({l_},{w_})", f"area_rhombus({l_},{w_})", l_ * w_ / 2)
        near(f"area_triangle({l_},{w_})", f"area_triangle({l_},{w_})", l_ * w_ / 2)
        near(f"vol_cuboid({l_},{w_},{h_})", f"vol_cuboid({l_},{w_},{h_})", l_ * w_ * h_)
        near(f"vol_rect_prism({l_},{w_},{h_})", f"vol_rect_prism({l_},{w_},{h_})", l_ * w_ * h_)
        near(f"lsa_cuboid({l_},{w_},{h_})", f"lsa_cuboid({l_},{w_},{h_})", 2 * h_ * (l_ + w_))
        near(f"tsa_cuboid({l_},{w_},{h_})", f"tsa_cuboid({l_},{w_},{h_})", 2 * (l_ * w_ + w_ * h_ + l_ * h_))
        near(f"tsa_rect_prism({l_},{w_},{h_})", f"tsa_rect_prism({l_},{w_},{h_})", 2 * (l_ * w_ + w_ * h_ + l_ * h_))
        near(f"area_trap({l_},{w_},{h_})", f"area_trap({l_},{w_},{h_})", (l_ + w_) * h_ / 2)
        near(f"perim_trap({l_},{w_},{h_},2)", f"perim_trap({l_},{w_},{h_},2)", l_ + w_ + h_ + 2)
    for a, b, c in [(3, 4, 5), (5, 6, 7), (7, 8, 9)]:
        s_ = (a + b + c) / 2
        near(f"heron({a},{b},{c})", f"heron({a},{b},{c})", 0.5 * a * b * math.sin(math.acos((a * a + b * b - c * c) / (2 * a * b))), 1e-9)
        near(f"perim_triangle({a},{b},{c})", f"perim_triangle({a},{b},{c})", a + b + c)
    near("heron 3-4-5", "heron(3,4,5)", 6)
    near("perim_ellipse vs integral", "perim_ellipse(5,3)", simpson(lambda t: math.sqrt(25 * math.sin(t) ** 2 + 9 * math.cos(t) ** 2), 0, 2 * math.pi, 2000), 1e-7)
    near("haversine_dist London-Paris", "haversine_dist(51.5074,-0.1278,48.8566,2.3522)", 343.5560603, 1e-6)
