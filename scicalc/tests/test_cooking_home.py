"""Checks: cooking home.  Run alone with  python run_tests.py cooking_home"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "cooking_home"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .helpers import _err, _expr_error  # noqa: F401


def checks_cooking_home_36(check, ev, near, ex):
    """Phase 3: cooking and home"""
    # ================= Phase 3: cooking and home =================
    ex("cup of flour", "cup2g_flour(2)", 250)
    near("cup of sugar", "cup2g_sugar(1.5)", 300)
    near("cup of butter", "cup2g_butter(0.5)", 113.5)
    near("a cup of sugar is 8/5 the flour", "cup2g_sugar(3)/cup2g_flour(3)", 1.6)
    near("gas mark 4 is 177 C", "oven_c2gas(177)", 4)
    near("gas round trip", "oven_c2gas(oven_gas2c(6.5))", 6.5)
    for c, gm in [(150, 2), (160, 3), (180, 4), (190, 5), (200, 6), (220, 7), (230, 8), (240, 9)]:
        check(f"gas mark {gm} within a mark of the printed table ({c} C)", abs(ev(f"oven_c2gas({c})") - gm) <= 0.6, True)
    near("servings", "servings_scale(250,4,6)", 375)
    near("servings halve", "servings_scale(250,4,2)", 125)
    # tile counts against counting tiles one at a time (a different method)
    for area, w, h, waste in [(12, 0.3, 0.3, 10), (7.5, 0.6, 0.3, 5), (3, 0.25, 0.25, 0), (10, 0.45, 0.45, 15)]:
        need = Fraction(str(area)) * (1 + Fraction(waste, 100))
        n, tiled = 0, Fraction(0)
        while tiled < need:
            n += 1
            tiled += Fraction(str(w)) * Fraction(str(h))
        ex(f"tile_count({area},{w},{h},{waste})", f"tile_count({area},{w},{h},{waste})", n)
    near("paint for a room", "wall_paint_litres(14,2.5,4,2,10)", (14 * 2.5 - 4) * 2 / 10)
    near("baker's percent", "bakers_percent(350,500)", 70)
    near("hydration", "dough_hydration(650,1000)", 65)
    near("hydration equals baker's percent of water", "dough_hydration(300,400)", ev("bakers_percent(300,400)"))
    near("coffee", "coffee_grams(500,16)", 31.25)
    near("roast", "roast_time(2.2,45,20)", 2.2 * 45 + 20)
    # wallpaper: cut strips from rolls one at a time
    for p, h, w, l in [(14, 2.5, 0.53, 10), (10, 2.4, 0.5, 5), (20, 3, 1, 10), (6, 2.5, 0.52, 10.05)]:
        strips = math.ceil(Fraction(str(p)) / Fraction(str(w)))
        rolls, left = 0, Fraction(0)
        for _ in range(strips):
            if left < Fraction(str(h)):
                rolls += 1
                left = Fraction(str(l))
            left -= Fraction(str(h))
        ex(f"wallpaper_rolls({p},{h},{w},{l})", f"wallpaper_rolls({p},{h},{w},{l})", rolls)
    ex("fence posts", "fence_posts(20,2.5)", 9)
    ex("fence posts rounding up", "fence_posts(21,2.5)", 10)
    ex("fence posts short run", "fence_posts(1,2.5)", 2)
    near("mulch", "mulch_volume(12,7.5)", 0.9)
    for area, cover, waste in [(18, 2.2, 10), (20, 2, 0), (5.5, 1.2, 7)]:
        need = Fraction(str(area)) * (1 + Fraction(waste, 100))
        n = 0
        while n * Fraction(str(cover)) < need:
            n += 1
        ex(f"flooring_boxes({area},{cover},{waste})", f"flooring_boxes({area},{cover},{waste})", n)
    for e in ["cup2g_flour(-1)", "cup2g_sugar(1e999)", "cup2g_butter(-0.1)", "oven_c2gas(100)", "oven_c2gas(300)", "oven_c2gas(0)", "oven_gas2c(0)",
              "oven_gas2c(11)", "servings_scale(1,0,2)", "servings_scale(-1,2,2)", "servings_scale(1,2,-2)", "tile_count(0,1,1,0)", "tile_count(1,0,1,0)",
              "tile_count(1,1,1,-1)", "tile_count(1,1,1,101)", "wall_paint_litres(0,2,0,1,10)", "wall_paint_litres(10,2,30,1,10)", "wall_paint_litres(10,2,0,0,10)",
              "wall_paint_litres(10,2,0,1,0)", "bakers_percent(1,0)", "bakers_percent(-1,5)", "dough_hydration(1,0)", "coffee_grams(100,0)", "coffee_grams(-1,16)",
              "roast_time(0,45,20)", "roast_time(2,-1,20)", "wallpaper_rolls(10,2.5,0,10)", "wallpaper_rolls(10,11,0.5,10)", "wallpaper_rolls(0,2.5,0.5,10)",
              "fence_posts(0,2)", "fence_posts(10,0)", "mulch_volume(0,5)", "mulch_volume(5,0)", "flooring_boxes(0,2,10)", "flooring_boxes(10,0,10)",
              "flooring_boxes(10,2,200)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
