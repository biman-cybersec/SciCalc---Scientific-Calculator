"""Daily life helpers, 2-D and 3-D geometry

Module 11 of 47.  Taken from lines 2466-2813 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_geometry_daily"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .arithmetic import ar_add, ar_mul, ar_power
from .lib_powers_rounding import sq

# ---------- 7f. Daily Life, Health & Conversions ----------

@register("bmi", "Daily Life", "Body Mass Index: bmi(weight_kg, height_m)", args=2, example="bmi(70,1.75) => 22.86")
def bmi(weight, height):
    if height <= 0:
        raise MathError("height must be greater than zero")
    return round(weight / (height * height), 2)


@register("c_to_f", "Daily Life", "Celsius to Fahrenheit", example="c_to_f(25) => 77")
def c_to_f(c):
    c = float(c)
    if c < -273.15:
        raise MathError("temperature below absolute zero")
    return c * 9 / 5 + 32


@register("f_to_c", "Daily Life", "Fahrenheit to Celsius", example="f_to_c(77) => 25")
def f_to_c(f):
    c = (float(f) - 32) * 5 / 9
    if c < -273.15:
        raise MathError("temperature below absolute zero")
    return c


@register("c_to_k", "Daily Life", "Celsius to Kelvin", example="c_to_k(25) => 298.15")
def c_to_k(c):
    c = float(c)
    if c < -273.15:
        raise MathError("temperature below absolute zero")
    return c + 273.15


@register("k_to_c", "Daily Life", "Kelvin to Celsius", example="k_to_c(298.15) => 25")
def k_to_c(k):
    k = float(k)
    if k < 0:
        raise MathError("temperature below absolute zero")
    return k - 273.15


@register("speed", "Daily Life", "Speed given distance and time: speed(distance, time)", args=2, example="speed(100,2) => 50")
def speed_(distance, time):
    if time == 0:
        raise MathError("time cannot be zero")
    return distance / time


@register("distance", "Daily Life", "Distance given speed and time: distance(speed, time)", args=2, example="distance(50,2) => 100")
def distance_(speed, time):
    return speed * time


@register("time_taken", "Daily Life", "Time given distance and speed: time_taken(distance, speed)", args=2, aliases=("time",), example="time_taken(100,50) => 2")
def time_taken(distance, speed):
    if speed == 0:
        raise MathError("speed cannot be zero")
    return distance / speed


# ---------- 7g. Geometry (2D Shapes) ----------

@register("area_square", "Geometry", "Area of a square given its side", exact=True, example="area_square(5) => 25")
def area_square(side):
    if side < 0:
        raise MathError("side length cannot be negative")
    return sq(side)


@register("area_rect", "Geometry", "Area of a rectangle: area_rect(length, width)", args=2, exact=True, example="area_rect(4,5) => 20")
def area_rect(length, width):
    if length < 0 or width < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(length, width)


@register("area_circle", "Geometry", "Area of a circle given its radius", example="area_circle(3) => 28.27433388")
def area_circle(radius):
    if radius < 0:
        raise MathError("radius cannot be negative")
    return math.pi * sq(radius)  # pyright: ignore[reportOperatorIssue]


@register("area_triangle", "Geometry", "Area of a triangle given base and height: area_triangle(base, height)", args=2, example="area_triangle(10,5) => 25")
def area_triangle(base, height):
    if base < 0 or height < 0:
        raise MathError("dimensions cannot be negative")
    return base * height / 2


# --- Perimeters ---

@register("perim_square", "Geometry", "Perimeter of a square given its side", exact=True, example="perim_square(5) => 20")
def perim_square(side):
    if side < 0:
        raise MathError("side length cannot be negative")
    return ar_mul(4, side)


@register("perim_rect", "Geometry", "Perimeter of a rectangle: perim_rect(length, width)", args=2, exact=True, example="perim_rect(4,5) => 18")
def perim_rect(length, width):
    if length < 0 or width < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(2, ar_add(length, width))


@register("perim_circle", "Geometry", "Perimeter/Circumference of a circle given its radius", aliases=("circumference",), example="perim_circle(5) => 31.41592654")
def perim_circle(radius):
    if radius < 0:
        raise MathError("radius cannot be negative")
    return 2 * math.pi * radius


@register("perim_triangle", "Geometry", "Perimeter of a triangle given three sides: perim_triangle(a, b, c)", args=3, exact=True, example="perim_triangle(3,4,5) => 12")
def perim_triangle(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        raise MathError("side lengths must be positive")
    if a + b <= c or a + c <= b or b + c <= a:
        raise MathError("these sides cannot form a valid triangle")
    return ar_add(ar_add(a, b), c)


# --- Remaining Areas & Perimeters ---

@register("area_para", "Geometry", "Area of a parallelogram: area_para(base, height)", args=2, exact=True, example="area_para(6,4) => 24")
def area_para(base, height):
    if base < 0 or height < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(base, height)


@register("perim_para", "Geometry", "Perimeter of a parallelogram: perim_para(side1, side2)", args=2, exact=True, example="perim_para(5,3) => 16")
def perim_para(a, b):
    if a < 0 or b < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(2, ar_add(a, b))


@register("area_rhombus", "Geometry", "Area of a rhombus given diagonals: area_rhombus(d1, d2)", args=2, example="area_rhombus(6,8) => 24")
def area_rhombus(d1, d2):
    if d1 < 0 or d2 < 0:
        raise MathError("diagonals cannot be negative")
    return d1 * d2 / 2


@register("perim_rhombus", "Geometry", "Perimeter of a rhombus given side length", exact=True, example="perim_rhombus(5) => 20")
def perim_rhombus(side):
    if side < 0:
        raise MathError("side length cannot be negative")
    return ar_mul(4, side)


@register("area_trap", "Geometry", "Area of a trapezium: area_trap(parallel_a, parallel_b, height)", args=3, example="area_trap(4,6,5) => 25")
def area_trap(a, b, height):
    if a < 0 or b < 0 or height < 0:
        raise MathError("dimensions cannot be negative")
    return (a + b) * height / 2


@register("perim_trap", "Geometry", "Perimeter of a trapezium given four sides: perim_trap(a, b, c, d)", args=4, exact=True, example="perim_trap(3,4,5,6) => 18")
def perim_trap(a, b, c, d):
    if a < 0 or b < 0 or c < 0 or d < 0:
        raise MathError("side lengths cannot be negative")
    return ar_add(ar_add(a, b), ar_add(c, d))


@register("area_ellipse", "Geometry", "Area of an ellipse given semi-axes: area_ellipse(a, b)", args=2, example="area_ellipse(3,2) => 18.84955592")
def area_ellipse(a, b):
    if a < 0 or b < 0:
        raise MathError("semi-axes cannot be negative")
    return math.pi * a * b


@register("perim_ellipse", "Geometry", "Perimeter of an ellipse (Ramanujan's 2nd approximation, very accurate): perim_ellipse(a, b)", args=2, example="perim_ellipse(3,2) => 15.86543959")
def perim_ellipse(a, b):
    if a < 0 or b < 0:
        raise MathError("semi-axes cannot be negative")
    if a == 0 and b == 0:
        return 0
    h = ((a - b) / (a + b)) ** 2
    return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))


@register("heron", "Geometry", "Area of a triangle given 3 sides (Heron's formula): heron(a, b, c)", args=3, example="heron(3,4,5) => 6")
def heron_area(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        raise MathError("side lengths must be positive")
    if a + b <= c or a + c <= b or b + c <= a:
        raise MathError("these sides cannot form a valid triangle")
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))


# ---------- 7h. Geometry (3D Shapes) ----------

# --- Cube & Cuboid ---

@register("vol_cube", "Geometry 3D", "Volume of a cube given side length", exact=True, example="vol_cube(3) => 27")
def vol_cube(s):
    if s < 0:
        raise MathError("side length cannot be negative")
    return ar_power(s, 3)


@register("lsa_cube", "Geometry 3D", "Lateral Surface Area of a cube given side length", exact=True, example="lsa_cube(3) => 36")
def lsa_cube(s):
    if s < 0:
        raise MathError("side length cannot be negative")
    return ar_mul(4, sq(s))


@register("tsa_cube", "Geometry 3D", "Total Surface Area of a cube given side length", exact=True, example="tsa_cube(3) => 54")
def tsa_cube(s):
    if s < 0:
        raise MathError("side length cannot be negative")
    return ar_mul(6, sq(s))


@register("vol_cuboid", "Geometry 3D", "Volume of a cuboid: vol_cuboid(l, w, h)", args=3, exact=True, example="vol_cuboid(2,3,4) => 24")
def vol_cuboid(l, w, h):
    if l < 0 or w < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(ar_mul(l, w), h)


@register("lsa_cuboid", "Geometry 3D", "Lateral Surface Area of a cuboid: lsa_cuboid(l, w, h)", args=3, exact=True, example="lsa_cuboid(2,3,4) => 40")
def lsa_cuboid(l, w, h):
    if l < 0 or w < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(ar_mul(2, h), ar_add(l, w))


@register("tsa_cuboid", "Geometry 3D", "Total Surface Area of a cuboid: tsa_cuboid(l, w, h)", args=3, exact=True, example="tsa_cuboid(2,3,4) => 52")
def tsa_cuboid(l, w, h):
    if l < 0 or w < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return ar_mul(2, ar_add(ar_add(ar_mul(l, w), ar_mul(w, h)), ar_mul(l, h)))


# --- Cone, Cylinder, Sphere, Hemisphere ---

@register("vol_cone", "Geometry 3D", "Volume of a cone given radius and height: vol_cone(r, h)", args=2, example="vol_cone(3,4) => 37.69911184")
def vol_cone(r, h):
    if r < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return math.pi * sq(r) * h / 3  # pyright: ignore[reportOperatorIssue]


@register("lsa_cone", "Geometry 3D", "Lateral Surface Area of a cone given radius and height: lsa_cone(r, h)", args=2, example="lsa_cone(3,4) => 47.1238898")
def lsa_cone(r, h):
    if r < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    slant = math.hypot(r, h)
    return math.pi * r * slant


@register("tsa_cone", "Geometry 3D", "Total Surface Area of a cone given radius and height: tsa_cone(r, h)", args=2, example="tsa_cone(3,4) => 75.39822369")
def tsa_cone(r, h):
    if r < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    slant = math.hypot(r, h)
    return math.pi * r * (slant + r)


@register("vol_cylinder", "Geometry 3D", "Volume of a cylinder given radius and height: vol_cylinder(r, h)", args=2, example="vol_cylinder(3,5) => 141.3716694")
def vol_cylinder(r, h):
    if r < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return math.pi * sq(r) * h  # pyright: ignore[reportOperatorIssue]


@register("lsa_cylinder", "Geometry 3D", "Curved/Lateral Surface Area of a cylinder: lsa_cylinder(r, h)", args=2, example="lsa_cylinder(3,5) => 94.24777961")
def lsa_cylinder(r, h):
    if r < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return 2 * math.pi * r * h


@register("tsa_cylinder", "Geometry 3D", "Total Surface Area of a cylinder: tsa_cylinder(r, h)", args=2, example="tsa_cylinder(3,5) => 150.7964474")
def tsa_cylinder(r, h):
    if r < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return 2 * math.pi * r * (r + h)


@register("vol_sphere", "Geometry 3D", "Volume of a sphere given radius", example="vol_sphere(3) => 113.0973355")
def vol_sphere(r):
    if r < 0:
        raise MathError("radius cannot be negative")
    return (4 / 3) * math.pi * ar_power(r, 3)  # pyright: ignore[reportOperatorIssue]


@register("tsa_sphere", "Geometry 3D", "Surface Area of a sphere given radius", aliases=("lsa_sphere",), example="tsa_sphere(3) => 113.0973355")
def tsa_sphere(r):
    if r < 0:
        raise MathError("radius cannot be negative")
    return 4 * math.pi * sq(r)  # pyright: ignore[reportOperatorIssue]


@register("vol_hemisphere", "Geometry 3D", "Volume of a hemisphere given radius", example="vol_hemisphere(3) => 56.54866776")
def vol_hemisphere(r):
    if r < 0:
        raise MathError("radius cannot be negative")
    return (2 / 3) * math.pi * ar_power(r, 3)  # pyright: ignore[reportOperatorIssue]


@register("lsa_hemisphere", "Geometry 3D", "Curved Surface Area of a hemisphere given radius", example="lsa_hemisphere(3) => 56.54866776")
def lsa_hemisphere(r):
    if r < 0:
        raise MathError("radius cannot be negative")
    return 2 * math.pi * sq(r)  # pyright: ignore[reportOperatorIssue]


@register("tsa_hemisphere", "Geometry 3D", "Total Surface Area of a hemisphere given radius", example="tsa_hemisphere(3) => 84.82300165")
def tsa_hemisphere(r):
    if r < 0:
        raise MathError("radius cannot be negative")
    return 3 * math.pi * sq(r)  # pyright: ignore[reportOperatorIssue]


# --- Pyramids & Prisms ---

@register("vol_sq_pyramid", "Geometry 3D", "Volume of a square pyramid: vol_sq_pyramid(base_side, height)", args=2, example="vol_sq_pyramid(6,5) => 60")
def vol_sq_pyramid(s, h):
    if s < 0 or h < 0:
        raise MathError("dimensions cannot be negative")
    return sq(s) * h / 3


@register("tsa_sq_pyramid", "Geometry 3D", "Total Surface Area of a square pyramid: tsa_sq_pyramid(base_side, slant_height)", args=2, example="tsa_sq_pyramid(6,5) => 96")
def tsa_sq_pyramid(s, slant):
    if s < 0 or slant < 0:
        raise MathError("dimensions cannot be negative")
    base_area = sq(s)
    lateral_area = 2 * s * slant
    return base_area + lateral_area


@register("vol_rect_prism", "Geometry 3D", "Volume of a rectangular prism: vol_rect_prism(l, w, h)", args=3, exact=True, example="vol_rect_prism(2,3,4) => 24")
def vol_rect_prism(l, w, h):
    return vol_cuboid(l, w, h)


@register("tsa_rect_prism", "Geometry 3D", "Total Surface Area of a rectangular prism: tsa_rect_prism(l, w, h)", args=3, exact=True, example="tsa_rect_prism(2,3,4) => 52")
def tsa_rect_prism(l, w, h):
    return tsa_cuboid(l, w, h)
