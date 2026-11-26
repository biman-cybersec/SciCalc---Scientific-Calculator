"""Unit conversion table and convert()

Module 21 of 47.  Taken from lines 6285-6439 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_units"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from .errors import ArgumentError, MathError
from .registry import Function, REGISTRY, register
from .arithmetic import ar_normalize
from .display import format_number

CONVERSION_REGISTRY = {}

def register_unit(from_unit, to_unit):
    """Decorator to automatically register conversion functions."""
    def decorator(func):
        CONVERSION_REGISTRY[(from_unit.lower(), to_unit.lower())] = func
        return func
    return decorator


# ==========================================
# Unit conversion table (exact factors; the reverse direction is the exact inverse)
# ==========================================
# _lin(a, b, num, den): b = a * num / den, and a = b * den / num.
# Every factor is the legal / SI definition, so a2b followed by b2a returns the start value
# (up to one rounding step) and nothing is ever derived from a rounded reciprocal.

def _unit_name(a, b):
    return f"{a}_to_{b}" if (a, b) in (("f", "k"), ("k", "f")) else f"{a}2{b}"


def _lin(a, b, num, den=1.0, both=True):
    def fwd(x, num=num, den=den):
        return x * num / den

    def rev(x, num=num, den=den):
        return x * den / num

    fwd.__name__ = _unit_name(a, b)
    register_unit(a, b)(fwd)
    if both:
        rev.__name__ = _unit_name(b, a)
        register_unit(b, a)(rev)


_MILE_KM = 1.609344             # international mile
_GAL_L = 3.785411784            # US liquid gallon

# length
_lin("m", "ft", 1, 0.3048)
_lin("km", "mi", 1, _MILE_KM)
_lin("cm", "in", 1, 2.54)
_lin("mm", "in", 1, 25.4)
_lin("m", "yd", 1, 0.9144)
_lin("km", "nmi", 1, 1.852)
# mass
_lin("kg", "lb", 1, 0.45359237)
_lin("g", "oz", 1, 28.349523125)
_lin("kg", "st", 1, 6.35029318)
_lin("t", "kg", 1000)
# area and volume
_lin("sqm", "sqft", 1, 0.09290304)
_lin("ha", "acre", 1, 0.40468564224)
_lin("sqkm", "sqmi", 1, 2.589988110336)
_lin("l", "gal", 1, _GAL_L)
_lin("ml", "floz", 1, 29.5735295625)
_lin("cup", "ml", 236.5882365)
_lin("cuft", "l", 28.316846592)
# speed
_lin("kmh", "mph", 1, _MILE_KM)
_lin("ms", "kmh", 3.6)
_lin("kn", "kmh", 1.852)
_lin("mach", "ms", 343.0)        # speed of sound at 20 C, dry air
# pressure, energy, power, force
_lin("atm", "pa", 101325.0)
_lin("mmhg", "pa", 133.322387415)
_lin("psi", "kpa", 6.894757293168)
_lin("kwh", "j", 3600000.0)
_lin("ev", "j", 1.602176634e-19)
_lin("kcal", "j", 4184.0)
_lin("hp", "kw", 0.7456998715822702)   # mechanical horsepower
_lin("n", "lbf", 1, 4.4482216152605)
_lin("kgf", "n", 9.80665)
# time
_lin("min", "s", 60.0)
_lin("hr", "min", 60.0)
_lin("day", "hr", 24.0)
# data (binary: 1 TB = 1024 GB here; the hand-registered kb2mb / mb2gb are decimal)
_lin("gb", "tb", 1, 1024.0)
_lin("mb", "kb", 1024.0, both=False)
_lin("byte", "bit", 8.0, both=False)
# fuel economy (US mpg)
_lin("kmpl", "mpg", _GAL_L, _MILE_KM)


@register_unit("f", "k")
def f_to_k(x): return (x - 32.0) * 5.0 / 9.0 + 273.15


@register_unit("k", "f")
def k_to_f(x): return (x - 273.15) * 9.0 / 5.0 + 32.0


def _l100_mpg(x):
    if x == 0:
        raise MathError("fuel use cannot be zero")
    return 100.0 * _GAL_L / _MILE_KM / x      # the formula is its own inverse


_l100_mpg.__name__ = "l100km2mpg"
register_unit("l100km", "mpg")(_l100_mpg)


def _mpg_l100(x):
    return _l100_mpg(x)


_mpg_l100.__name__ = "mpg2l100km"
register_unit("mpg", "l100km")(_mpg_l100)


# ==========================================
# Generic Dynamic Converter Function
# ==========================================

def convert(value, from_unit, to_unit):
    """Dynamically route to any registered unit conversion function."""
    key = (from_unit.strip().lower(), to_unit.strip().lower())
    
    if key in CONVERSION_REGISTRY:
        return CONVERSION_REGISTRY[key](value)
        
    raise ValueError(f"Unsupported conversion from '{from_unit}' to '{to_unit}'")


# ---- Hook the unit table into the function registry (m2ft(1), km2mi(5) ... work at the prompt) ----

def _fmt_example(value):
    return format_number(ar_normalize(value), ("norm", 2))


def _register_unit_pair(fn):
    name = fn.__name__
    if REGISTRY.knows(name):                     # bar2psi, kb2mb ... already registered by hand
        return
    pairs = [k for k, v in CONVERSION_REGISTRY.items() if v is fn]
    src, dst = pairs[0] if pairs else ("?", "?")
    desc = f"Convert {src} to {dst}"
    REGISTRY.add_function(Function(name, fn, "Unit Conversions", desc, 1, 1, (), False, False,
                                   False, False, f"{name}(1) => {_fmt_example(fn(1.0))}"))


for _fn in list(CONVERSION_REGISTRY.values()):
    _register_unit_pair(_fn)


@register("convert", "Unit Conversions", 'Convert by unit name: convert(5,"km","mi")', args=3, exact=True,
          example='convert(5,"km","mi") => ' + _fmt_example(CONVERSION_REGISTRY[("km", "mi")](5.0)))
def convert_(value, from_unit, to_unit):
    if not isinstance(from_unit, str) or not isinstance(to_unit, str):
        raise ArgumentError('convert needs unit names in quotes, e.g. convert(5,"km","mi")')
    return convert(float(value), from_unit, to_unit)
