"""Phase 3: cooking and home

Module 42 of 47.  Taken from lines 13951-14093 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_cooking_home"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .lib_vectors_matrices import _fr

#  PHASE 3 : COOKING AND HOME (16)
#  Everyday conversions and quantity estimates.  Cup weights are the usual metric-cup
#  figures (flour 125 g, sugar 200 g, butter 227 g per US cup of 236.588 ml).  Gas marks are
#  approximate: mark = (C - 121) / 14, the rule that matches the printed tables to a degree
#  or so for marks 2 to 9.
# ======================================================================================
_KIT = "Cooking & Home"


def _kit(name, desc, args, example, **kw):
    return register(name, _KIT, desc, args, example=example, **kw)


def _kpos(x, what="value"):
    x = float(x)
    if not math.isfinite(x) or x <= 0:
        raise MathError(f"{what} must be positive")
    return x


def _knn(x, what="value"):
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise MathError(f"{what} cannot be negative")
    return x


@_kit("cup2g_flour", "Grams of plain flour in a number of US cups (125 g per cup): cup2g_flour(cups)", 1, "cup2g_flour(2) => 250")
def cup2g_flour(c):
    return _knn(c, "cups") * 125


@_kit("cup2g_sugar", "Grams of granulated sugar in a number of US cups (200 g per cup): cup2g_sugar(cups)", 1, "cup2g_sugar(1.5) => 300")
def cup2g_sugar(c):
    return _knn(c, "cups") * 200


@_kit("cup2g_butter", "Grams of butter in a number of US cups (227 g per cup): cup2g_butter(cups)", 1, "cup2g_butter(0.5) => 113.5")
def cup2g_butter(c):
    return _knn(c, "cups") * 227


@_kit("oven_c2gas", "Approximate gas mark for an oven temperature in Celsius (140 to 260): oven_c2gas(celsius)", 1, "oven_c2gas(177) => 4")
def oven_c2gas(c):
    c = _kpos(c, "temperature")
    if not 135 <= c <= 275:
        raise MathError("gas marks cover about 135 to 275 degrees Celsius")
    return (c - 121) / 14


@_kit("oven_gas2c", "Approximate Celsius for a gas mark (1 to 10): oven_gas2c(mark)", 1, "oven_gas2c(4) => 177")
def oven_gas2c(g):
    g = _kpos(g, "gas mark")
    if not 1 <= g <= 10:
        raise MathError("gas marks run from 1 to 10")
    return 121 + 14 * g


@_kit("servings_scale", "Scale an ingredient amount to a new number of servings: servings_scale(amount, servings_now, servings_wanted)", 3,
      "servings_scale(250, 4, 6) => 375")
def servings_scale(a, now, want):
    return _knn(a, "amount") * _knn(want, "servings") / _kpos(now, "servings")


@_kit("tile_count", "Tiles needed with an allowance for cuts: tile_count(area_m2, tile_w_m, tile_h_m, waste_percent)", 4,
      "tile_count(12, 0.3, 0.3, 10) => 147", exact=True)
def tile_count(area, w, h, waste):
    area, w, h, waste = _fr(area), _fr(w), _fr(h), _fr(waste)
    if area <= 0 or w <= 0 or h <= 0 or not 0 <= waste <= 100:
        raise MathError("area and tile size must be positive; waste is 0 to 100 percent")
    n = area / (w * h) * (1 + waste / 100)
    return int(n) if n.denominator == 1 else int(n) + 1


@_kit("wall_paint_litres", "Litres of paint for a room: wall_paint_litres(perimeter_m, height_m, openings_m2, coats, m2_per_litre)", 5,
      "wall_paint_litres(14, 2.5, 4, 2, 10) => 6.2")
def wall_paint_litres(p, h, openings, coats, rate):
    area = _kpos(p, "perimeter") * _kpos(h, "height") - _knn(openings, "openings")
    if area < 0:
        raise MathError("the openings are larger than the walls")
    return area * _kpos(coats, "coats") / _kpos(rate, "coverage")


@_kit("bakers_percent", "Baker's percentage of an ingredient relative to the flour weight: bakers_percent(ingredient_g, flour_g)", 2,
      "bakers_percent(350, 500) => 70")
def bakers_percent(i, flour):
    return _knn(i, "ingredient") / _kpos(flour, "flour") * 100


@_kit("dough_hydration", "Dough hydration in percent: dough_hydration(water_g, flour_g)", 2, "dough_hydration(650, 1000) => 65")
def dough_hydration(water, flour):
    return _knn(water, "water") / _kpos(flour, "flour") * 100


@_kit("coffee_grams", "Grams of coffee for a water volume (ml) at 1 : ratio (e.g. 16): coffee_grams(water_ml, ratio)", 2, "coffee_grams(500, 16) => 31.25")
def coffee_grams(water, ratio):
    return _knn(water, "water") / _kpos(ratio, "ratio")


@_kit("roast_time", "Roasting time in minutes: roast_time(weight_kg, minutes_per_kg, extra_minutes)", 3, "roast_time(2.2, 45, 20) => 119")
def roast_time(w, per_kg, extra):
    return _kpos(w, "weight") * _knn(per_kg, "minutes per kg") + _knn(extra, "extra time")


@_kit("wallpaper_rolls", "Rolls of wallpaper (whole rolls): wallpaper_rolls(perimeter_m, height_m, roll_width_m, roll_length_m)", 4,
      "wallpaper_rolls(14, 2.5, 0.53, 10) => 7", exact=True)
def wallpaper_rolls(p, h, w, l):
    p, h, w, l = _fr(p), _fr(h), _fr(w), _fr(l)
    if p <= 0 or h <= 0 or w <= 0 or l <= 0:
        raise MathError("all sizes must be positive")
    if h > l:
        raise MathError("the wall is taller than a roll is long")
    drops_per_roll = int(l // h)
    strips = p / w
    strips = int(strips) if strips.denominator == 1 else int(strips) + 1
    return -(-strips // drops_per_roll)


@_kit("fence_posts", "Posts for a straight fence: fence_posts(length_m, spacing_m) = ceil(length/spacing) + 1", 2, "fence_posts(20, 2.5) => 9", exact=True)
def fence_posts(length, spacing):
    length, spacing = _fr(length), _fr(spacing)
    if length <= 0 or spacing <= 0:
        raise MathError("length and spacing must be positive")
    n = length / spacing
    return (int(n) if n.denominator == 1 else int(n) + 1) + 1


@_kit("mulch_volume", "Cubic metres of mulch or soil for an area at a depth in cm: mulch_volume(area_m2, depth_cm)", 2, "mulch_volume(12, 7.5) => 0.9")
def mulch_volume(area, depth):
    return _kpos(area, "area") * _kpos(depth, "depth") / 100


@_kit("flooring_boxes", "Boxes of flooring with a waste allowance: flooring_boxes(area_m2, box_covers_m2, waste_percent)", 3,
      "flooring_boxes(18, 2.2, 10) => 9", exact=True)
def flooring_boxes(area, cover, waste):
    area, cover, waste = _fr(area), _fr(cover), _fr(waste)
    if area <= 0 or cover <= 0 or not 0 <= waste <= 100:
        raise MathError("area and coverage must be positive; waste is 0 to 100 percent")
    n = area * (1 + waste / 100) / cover
    return int(n) if n.denominator == 1 else int(n) + 1


# ======================================================================================
