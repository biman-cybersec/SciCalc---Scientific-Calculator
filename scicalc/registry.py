"""Function registry: @register and register_constant

Module 2 of 47.  Taken from lines 78-237 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "registry"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from dataclasses import dataclass

# ======================================================================================
#  PART 2 : FUNCTION REGISTRY
# ======================================================================================

# The function registry - the heart of the calculator.
#
# To add a new function anywhere in the project you only write this:
#
#     @register("sinh", "Hyperbolic", "Hyperbolic sine", example="sinh(0) => 0")
#     def sinh(x):
#         return math.sinh(x)
#
# The parser, the help system, the search, the function counter and the automatic
# tests all discover it from here. Nothing else needs to change.
#
# register() options
#     args        1 (exactly one), 2, (1, 2) = one or two, (1, None) = one or more, 0 = none
#     aliases     other names that call the same function
#     exact       False (default): arguments arrive as floats and the result is tidied.
#                 True: arguments arrive as int / Fraction / float untouched, so the
#                 function can keep exact answers (gcd, factorial, sqrt(16) = 4 ...).
#     angle_in    first argument is an angle: converted from DEG/RAD/GRAD to radians
#     angle_out   result is an angle: converted from radians to DEG/RAD/GRAD
#     snap_zero   results smaller than 1e-14 become exactly 0 (sin(180) = 0, not 1e-16)
#     example     "expression => displayed result"  (checked by the test-suite)


@dataclass(frozen=True)
class Function:
    name: str
    fn: object
    category: str
    desc: str
    min_args: int
    max_args: object            # int, or None for "any number"
    aliases: tuple = ()
    exact: bool = False
    angle_in: bool = False
    angle_out: bool = False
    snap_zero: bool = False
    example: str = ""
    lists: bool = False         # receives lists/matrices as they are (otherwise lists are spliced or broadcast)

    @property
    def arity_text(self):
        if self.max_args is None:
            return f"{self.min_args} or more arguments"
        if self.min_args == self.max_args:
            return "no arguments" if self.max_args == 0 else \
                   f"{self.max_args} argument" + ("" if self.max_args == 1 else "s")
        return f"{self.min_args} to {self.max_args} arguments"


@dataclass(frozen=True)
class Constant:
    name: str
    value: object
    category: str
    desc: str
    aliases: tuple = ()


class Registry:
    def __init__(self):
        self._funcs = {}        # unique functions by name
        self._names = {}        # every name and alias -> Function
        self._consts = {}       # unique constants by name
        self._const_names = {}  # every constant name and alias -> Constant

    # ---------- adding ----------
    def _claim(self, name, table):
        key = name if len(name) == 1 else name.lower()
        if key in self._names or key in self._const_names:
            raise ValueError(f"name '{name}' is already registered")
        return key

    def add_function(self, f):
        for n in (f.name,) + tuple(f.aliases):
            if len(n) < 2:
                raise ValueError(f"function names need 2+ letters: '{n}'")
        for n in (f.name,) + tuple(f.aliases):
            self._names[self._claim(n, self._names)] = f
        self._funcs[f.name] = f

    def add_constant(self, c):
        for n in (c.name,) + tuple(c.aliases):
            self._const_names[self._claim(n, self._const_names)] = c
        self._consts[c.name] = c

    def add_alias(self, alias, target):
        """Give an already registered function one more name (aliases are not counted as functions)."""
        import dataclasses
        f = self._funcs[target]
        key = self._claim(alias, self._names)
        g = dataclasses.replace(f, aliases=tuple(f.aliases) + (alias,))
        self._funcs[f.name] = g
        for k, v in list(self._names.items()):
            if v is f:
                self._names[k] = g
        self._names[key] = g

    # ---------- looking up ----------
    def function(self, name):
        return self._names.get(name if len(name) == 1 else name.lower())

    def constant(self, name):
        return self._const_names.get(name if len(name) == 1 else name.lower())

    def knows(self, name):
        return self.function(name) is not None or self.constant(name) is not None

    # ---------- browsing ----------
    def functions(self):
        return list(self._funcs.values())

    def constants(self):
        return list(self._consts.values())

    def categories(self):
        cats = {}
        for f in self._funcs.values():
            cats.setdefault(f.category, []).append(f)
        for c in self._consts.values():
            cats.setdefault(c.category, []).append(c)
        return {k: sorted(v, key=lambda x: x.name) for k, v in sorted(cats.items())}

    def search(self, text):
        t = text.lower().strip()
        items = list(self._funcs.values()) + list(self._consts.values())
        hits = [i for i in items
                if t in i.name.lower() or t in i.desc.lower() or t in i.category.lower()
                or any(t in a.lower() for a in i.aliases)]
        return sorted(hits, key=lambda i: (i.name.lower() != t, i.name))

    def count(self):
        return len(self._funcs), len(self._consts)


REGISTRY = Registry()


def register(name, category, desc, args: "int | tuple[int, int | None]" = 1, *, aliases=(), exact=False, angle_in=False,
             angle_out=False, snap_zero=False, example="", lists=False):
    if isinstance(args, int):
        lo, hi = args, args
    else:
        lo, hi = args

    def decorator(fn):
        REGISTRY.add_function(Function(name, fn, category, desc, lo, hi, tuple(aliases),
                                       exact, angle_in, angle_out, snap_zero, example, lists))
        return fn
    return decorator


def register_constant(name, value, desc, category="Constants", aliases=()):
    REGISTRY.add_constant(Constant(name, value, category, desc, tuple(aliases)))
