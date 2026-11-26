"""HELP text and the interactive prompt (calc_main)

Module 25 of 47.  Taken from lines 7938-8442 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "cli"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
import sys
import textwrap

from .errors import CalcError
from .registry import REGISTRY
from .arithmetic import Lst, Mat
from .engine import Calculator, _ACTIVE_CALC, load_session, save_session
from .menu import menu_main

# ======================================================================================
#  PART 9 : COMMAND LINE (the Casio-style prompt)
# ======================================================================================

# Command-line front end. All maths lives in scicalc.engine; this file only reads
# lines, runs commands and prints results.


GOAL = 700

HELP = """\
Type an expression and press Enter, like a Casio:

  3+4*2          2pi           sin(30)        sqrt(16)      5!         50%
  1/3+1/6        6/2(1+2)      2^10           (-8)^(1/3)    7 mod 3    5 nCr 2
  5->A           A*2           *3  (starts with Ans)        M+  M-

Names:   Ans  PreAns   variables A B C D E F X Y M   constants pi e tau phi
Angles:  sin(30) uses the current mode; 30° always means "30 degrees"

Commands:
  help [name]           this help, or details for one function
  list [category]       list categories, or the functions in one category
  listall               list all registered functions alphabetically by category
  listconstants         show all registered constants, their values, and descriptions
  search <word>         find functions by name or description
  graph <expr> [min] [max]  plot an ASCII graph of a function in terms of x
  mode deg|rad|grad     angle mode
  norm 1|2   fix 0-9   sci 1-10   eng 1-10   custom 0-10   display modes
  frac improper|mixed|off   show exact fractions as 7/2 or 3 1/2
  sym on|off                show results as 2√3, π/6, √3/2, 3/10 when they are that simple (sym_form(x) does it for one value)
  base hex|bin|oct|dec      show whole numbers as 0xFF, 0b1010, 0o17      dms on|off  show angles as D°M'S"
  complex on|off|rect|polar complex-number mode and display
  f(x)=x^2+1            define your own function (then f(3));  funcs  list them;  delfunc f  remove one
  table f(x), a, b, step    value table;   solve_all('expr', lo, hi) finds every root
  constants [word]      browse the constants (by category, or search);   const <name>  details
  save <file>  load <file>  keep or restore variables, lists, matrices, functions, settings and history
  vars                  show variables        history    show past calculations
  full                  show the exact value of the last answer
  stats                 how many functions & constants are registered
  reset                 reset mode, display, variables and Ans
  menu                  open the old numbered menu (geometry, BMI, converters, tables...)
  quit                  leave
"""


def _wrap(text, indent="  "):
    return textwrap.fill(text, width=88, initial_indent=indent, subsequent_indent=indent)


def _describe(item):
    lines = [f"{item.name}  [{item.category}]", f"  {item.desc}"]
    if hasattr(item, "arity_text"):
        lines.append(f"  takes {item.arity_text}")
    if getattr(item, "aliases", ()):
        lines.append("  also: " + ", ".join(item.aliases))
    if getattr(item, "example", ""):
        lines.append("  example: " + item.example.replace(" => ", "  ->  "))
    if not hasattr(item, "arity_text"):
        lines.append(f"  value: {item.value!r}")
    return "\n".join(lines)


def _command(calc, line):
    """Returns True if `line` was a command (already handled), 'quit' to leave, else False."""
    parts = line.split()
    word = parts[0].lower()
    args = parts[1:]

    if word in ("quit", "exit", "q"):
        return "quit"
    if word in ("norm", "fix", "sci", "eng", "custom") and len(args) <= 1 and (args or word != "fix"):
        try:
            calc.set_display(word, int(args[0]) if args else 2)
            print(f"  display: {word} {calc.display[1]}")
        except ValueError as err:
            print(f"  {err}")
        return True
    if word == "complex" and len(args) <= 1:
        choice = args[0].lower() if args else ""
        if choice in ("on", "off"):
            calc.complex_mode = choice == "on"
        elif choice in ("rect", "polar"):
            calc.complex_polar = choice == "polar"
        elif choice:
            print("  use: complex on | off | rect | polar")
            return True
        print(f"  complex mode: {'on' if calc.complex_mode else 'off'}, display: {'polar r∠θ' if calc.complex_polar else 'rectangular a+bi'}")
        return True
    if word == "base" and len(args) <= 1:
        choice = args[0].lower() if args else ""
        names = {"hex": "hex", "bin": "bin", "oct": "oct", "dec": None, "off": None}
        if choice and choice not in names:
            print("  use: base hex | bin | oct | dec")
            return True
        if choice:
            calc.base_display = names[choice]
        print(f"  whole-number results shown in: {calc.base_display or 'decimal'}")
        return True
    if word == "constants":
        text = " ".join(args).lower()
        cats = {}
        for k in REGISTRY.constants():
            cats.setdefault(k.category, []).append(k)
        if not text:
            for name, items in sorted(cats.items()):
                print(f"  {name:<30} {len(items):>3} constants")
            print("  use: constants <word>   (search names and descriptions)   const <name>   (details)")
            return True
        hits = [k for k in sorted(REGISTRY.constants(), key=lambda k: (k.category, k.name))
                if text in k.name.lower() or text in k.desc.lower() or text in k.category.lower()
                or any(text in a.lower() for a in k.aliases)]
        if not hits:
            print(f"  no constant matches '{text}'")
        for k in hits:
            print(f"  {k.name:<24} = {k.value:<22.10g}  {k.desc}" if isinstance(k.value, (int, float)) else f"  {k.name:<24} = {k.value}  {k.desc}")
        return True
    if word == "const" and len(args) == 1:
        k = REGISTRY.constant(args[0])
        if k is None:
            near_ = [c.name for c in REGISTRY.constants() if args[0].lower() in c.name.lower() or any(args[0].lower() in a.lower() for a in c.aliases)]
            print(f"  no constant named '{args[0]}'" + (f"; did you mean: {', '.join(near_[:8])}" if near_ else ""))
            return True
        print(f"  {k.name}  [{k.category}]\n    {k.desc}\n    value: {k.value!r}")
        if k.aliases:
            print("    also: " + ", ".join(k.aliases))
        return True
    if word in ("save", "load") and len(args) == 1:
        path = args[0] if args[0].lower().endswith(".json") else args[0] + ".json"
        try:
            if word == "save":
                save_session(calc, path)
                print(f"  saved to {path}")
            else:
                load_session(calc, path)
                print(f"  loaded {path}: {len(calc.user_functions)} function(s), {len(calc.history)} history line(s)")
        except CalcError as err:
            print(f"  {err}")
        except OSError as err:
            print(f"  cannot use {path}: {err.strerror or err}")
        return True
    if word == "sym" and len(args) <= 1:
        if args and args[0].lower() not in ("on", "off"):
            print("  use: sym on | off")
            return True
        if args:
            calc.sym_display = args[0].lower() == "on"
        print(f"  exact forms (2√3, π/6, √3/2, 3/10): {'on' if calc.sym_display else 'off'}")
        return True
    if word == "frac" and len(args) <= 1:
        names = {"improper": "improper", "on": "improper", "mixed": "mixed", "off": None, "decimal": None}
        choice = args[0].lower() if args else ""
        if choice and choice not in names:
            print("  use: frac improper | mixed | off")
            return True
        if choice:
            calc.frac_display = names[choice]
        print(f"  exact fractions shown as: {calc.frac_display or 'decimals'}")
        return True
    if word == "dms" and len(args) <= 1:
        if args and args[0].lower() not in ("on", "off"):
            print("  use: dms on | off")
            return True
        if args:
            calc.dms_display = args[0].lower() == "on"
        print(f"  degrees-minutes-seconds display: {'on' if calc.dms_display else 'off'}")
        return True
    if word == "funcs" and not args:
        lines = calc.list_functions()
        print("\n".join("  " + l for l in lines) if lines else "  no user functions yet - define one with f(x)=x^2+1")
        return True
    if word == "delfunc" and len(args) == 1:
        try:
            calc.delete_function(args[0])
            print(f"  deleted {args[0]}")
        except CalcError as err:
            print(f"  {err}")
        return True
    if word == "table":
        return _handle_table(calc, line[len(parts[0]):])
    if word == "graph":
        return _handle_graph(calc, args)
    if word == "listall":
            funcs = REGISTRY.functions()
            print(f"\n--- All Registered Functions ({len(funcs)}) ---")
            for f in sorted(funcs, key=lambda x: x.category):
                print(f"  {f.name:<20} [{f.category}] — {f.desc}")
            return True
    if word == "listconstants":
        consts = REGISTRY.constants()
        print(f"\n--- All Registered Constants ({len(consts)}) ---")
        for c in sorted(consts, key=lambda x: (x.category, x.name)):
            aliases_str = f" (also: {', '.join(c.aliases)})" if c.aliases else ""
            print(f"  {c.name:<25} [{c.category}] = {c.value}{aliases_str}\n      -> {c.desc}")
        return True
    if word == "catfilter" and args:
        wanted_cat = " ".join(args).lower()
        cats = REGISTRY.categories()
        matched = False
        
        for cat_name, items in cats.items():
            if wanted_cat in cat_name.lower():
                matched = True
                print(f"\n--- Category: {cat_name} ({len(items)} functions) ---")
                for f in items:
                    print(f"  {f.name:<20} — {f.desc}")
                    
        if not matched:
            print(f"  No category found matching '{wanted_cat}'. Try: list")
        return True
    if word == "help":
        if args:
            item = REGISTRY.function(args[0]) or REGISTRY.constant(args[0])
            print(_describe(item) if item else f"No function called '{args[0]}'. Try: search {args[0]}")
        else:
            print(HELP)
        return True
    if word == "list":
        cats = REGISTRY.categories()
        if not args:
            for name, items in cats.items():
                print(f"  {name} ({len(items)})")
            print("  (type 'list <category>' to see the names)")
        else:
            wanted = " ".join(args).lower()
            for name, items in cats.items():
                if wanted in name.lower():
                    print(name)
                    print(_wrap(", ".join(i.name for i in items)))
        return True
    if word == "search" and args:
        hits = REGISTRY.search(" ".join(args))
        for h in hits[:30]:
            print(f"  {h.name:<10} {h.desc}")
        print(f"  ({len(hits)} found)" if hits else "  nothing found")
        return True
    if word == "mode" and len(args) == 1 and args[0][:1].isalpha():
        try:
            calc.set_angle(args[0])
            print(f"  angle mode: {calc.angle.upper()}")
        except ValueError as err:
            print(f"  {err}")
        return True
    if word in ("norm", "fix", "sci") and len(args) <= 1 and (args or word != "fix"):
        try:
            calc.set_display(word, int(args[0]) if args else 2)
            print(f"  display: {word} {calc.display[1]}")
        except ValueError as err:
            print(f"  {err}")
        return True
    if word == "vars":
        for name, value in calc.variables.items():
            print(f"  {name} = {calc.format(value)[0]}")
        print(f"  Ans = {calc.format(calc.ans)[0]}")
        return True
    if word == "history":
        for r in calc.history[-20:]:
            print(f"  {r.expr}  =  {r.text}")
        if not calc.history:
            print("  (empty)")
        return True
    if word == "full":
        v = calc.ans
        print(f"  {calc.format(v)[0] if isinstance(v, (Lst, Mat)) else v}")
        return True
    if word == "stats":
        n_funcs, n_consts = REGISTRY.count()
        print(f"  {n_funcs} functions + {n_consts} constants registered  (goal: {GOAL}+)")
        for name, items in REGISTRY.categories().items():
            print(f"    {name:<32}{len(items)}")
        return True
    if word == "menu":
        menu_main()
        return True
    if word == "reset":
        calc.reset()
        print("  reset")
        return True
    return False
    

def run_line(calc, line):
    """Evaluate one line and print the outcome. Returns 'quit' to stop."""
    line = line.strip()
    if not line:
        return None
    outcome = _command(calc, line)
    if outcome:
        return "quit" if outcome == "quit" else None
    try:
        result = calc.evaluate(line)
    except CalcError as err:
        if err.pos is not None:
            print("  " + line)
            print("  " + " " * err.pos + "^")
        print(f"  {err}")
        return None
    print(f"  = {result.text}" + (f"    ≈ {result.decimal}" if result.decimal else ""))
    return None


def calc_main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    calc = Calculator()
    if argv:                                            # one-shot:  python -m scicalc "sin(30)+2"
        run_line(calc, " ".join(argv))
        return 0

    interactive = sys.stdin.isatty()
    if interactive:
        try:
            import readline  # noqa: F401  (arrow keys + history)
        except ImportError:
            pass
        n_funcs, n_consts = REGISTRY.count()
        print(f"Offline scientific calculator ({n_funcs} functions). Type 'help'.")
    while True:
        try:
            line = input(f"[{calc.angle.upper()}] > " if interactive else "")
        except (EOFError, KeyboardInterrupt):
            if interactive:
                print()
            break
        if run_line(calc, line) == "quit":
            break
    return 0


def _split_top(text):
    """Split at commas that are not inside brackets or quotes."""
    out, depth, quote, cur = [], 0, "", []
    for ch in text:
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "'\"":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    out.append("".join(cur).strip())
    return out


def _handle_table(calc, rest):
    """table f(x), start, end, step   or   table f(x), g(x), start, end, step   (variable x)."""
    from .lib_equations_tables import table1, table2  # imported here because lib_equations_tables is loaded after this module
    parts = _split_top(rest)
    if len(parts) not in (4, 5) or not all(parts):
        print("  use: table f(x), start, end, step    or    table f(x), g(x), start, end, step")
        return True
    try:
        exprs = [e.strip("'\"") for e in parts[:-3]]
        nums = [calc.evaluate(t).value for t in parts[-3:]]
        _ACTIVE_CALC[0] = calc
        rows = table1(exprs[0], *nums) if len(exprs) == 1 else table2(exprs[0], exprs[1], *nums)
    except CalcError as err:
        print(f"  {err.message if hasattr(err, 'message') else err}")
        return True
    head = ["x"] + ["f(x)" if len(exprs) == 1 else n for n in ("f(x)", "g(x)")][:len(exprs)]
    cells = [[calc.format(v)[0] for v in row] for row in rows]
    width = [max(len(h), *(len(r[i]) for r in cells)) for i, h in enumerate(head)]
    print("  " + "  ".join(h.rjust(w) for h, w in zip(head, width)))
    for r in cells:
        print("  " + "  ".join(c.rjust(w) for c, w in zip(r, width)))
    return True


def _handle_graph(calc, args):
    if not args:
        print("  Usage: graph \"expression\" [xmin] [xmax]")
        print("  Example: graph \"x^2 - 4\" -5 5")
        return True
    
    # Join all args back and extract expression (handling quotes if present)
    full_args_str = " ".join(args).strip()
    
    # Check if expression is quoted
    expr_str = ""
    
    remainder = ""
    if full_args_str.startswith('"') or full_args_str.startswith("'"):
        quote_char = full_args_str[0]
        end_idx = full_args_str.find(quote_char, 1)
        if end_idx != -1:
            expr_str = full_args_str[1:end_idx]
            remainder = full_args_str[end_idx+1:].strip()
        else:
            expr_str = full_args_str[1:]
    else:
        # If not quoted, assume last two tokens are xmin and xmax if they are numbers
        tokens = full_args_str.split()
        if len(tokens) >= 3:
            try:
                float(tokens[-1])
                float(tokens[-2])
                expr_str = " ".join(tokens[:-2])
                remainder = f"{tokens[-2]} {tokens[-1]}"
            except ValueError:
                expr_str = full_args_str
        else:
            expr_str = full_args_str

    xmin, xmax = -10.0, 10.0
    if remainder:
        rem_tokens = remainder.split()
        if len(rem_tokens) >= 2:
            try:
                xmin, xmax = float(rem_tokens[0]), float(rem_tokens[1])
            except ValueError:
                pass
    # Strip any stray single or double quotes left over from PowerShell/CLI arguments
    expr_str = expr_str.strip().strip('"').strip("'").strip()
            
    if xmin >= xmax:
        print("  Math ERROR: xmin must be less than xmax.")
        return True

    width, height = 60, 21
    xs = [xmin + i * (xmax - xmin) / (width - 1) for i in range(width)]
    
    ys = []
    for x_val in xs:
        try:
            subbed = expr_str.replace("x", f"({x_val})")
            val = float(calc.evaluate(subbed).value)
            ys.append(val if math.isfinite(val) else None)
        except Exception:
            ys.append(None)
            
    valid_ys = [y for y in ys if y is not None]
    if not valid_ys:
        print("  Math ERROR: No valid points to plot for this expression.")
        return True
        
    ymin, ymax = min(valid_ys), max(valid_ys)
    if ymin == ymax:
        ymin = ymin - 1.0
        ymax = ymax + 1.0

    span = ymax - ymin
    ymin = ymin - span * 0.05
    ymax = ymax + span * 0.05

    grid = [[" " for _ in range(width)] for _ in range(height)]
    
    zero_row = None
    if ymin <= 0 <= ymax:
        zero_row = int(height - 1 - (0 - ymin) / (ymax - ymin) * (height - 1))
        for c in range(width):
            grid[zero_row][c] = "─"
            
    zero_col = None
    if xmin <= 0 <= xmax:
        zero_col = int((0 - xmin) / (xmax - xmin) * (width - 1))
        for r in range(height):
            if grid[r][zero_col] == "─":
                grid[r][zero_col] = "┼"
            else:
                grid[r][zero_col] = "│"

    for c, y_val in enumerate(ys):
        if y_val is not None:
            r = int(height - 1 - (y_val - ymin) / (ymax - ymin) * (height - 1))
            if 0 <= r < height:
                if grid[r][c] in ("│", "─"):
                    grid[r][c] = "┼"
                else:
                    grid[r][c] = "*"

    top_label = f"{ymax:+.2f}"
    mid_label = f"{((ymax + ymin) / 2):+.2f}"
    bot_label = f"{ymin:+.2f}"
    
    print(f"\n  Plotting: y = {expr_str}")
    print(f"  Domain (x): [{xmin}, {xmax}]  |  Range (y): [{ymin:.2f}, {ymax:.2f}]")
    print("  " + " " * 9 + "┌" + "─" * width + "┐")
    
    mid_idx = height // 2
    for r in range(height):
        row_str = "".join(grid[r])
        if r == 0:
            label = f"{top_label:>8}"
        elif r == mid_idx:
            label = f"{mid_label:>8}"
        elif r == height - 1:
            label = f"{bot_label:>8}"
        else:
            label = "        "
        print(f"  {label} │{row_str}│")
        
    print("  " + " " * 9 + "└" + "─" * width + "┘")
    
    x_left = f"{xmin:.1f}"
    x_mid = f"{((xmin + xmax) / 2):.1f}"
    x_right = f"{xmax:.1f}"
    print("  " + " " * 10 + x_left + " " * max(1, width - len(x_left) - len(x_right) - len(x_mid)) + x_mid + " " * (width // 2 - len(x_mid)) + x_right)
    print()
    return True
