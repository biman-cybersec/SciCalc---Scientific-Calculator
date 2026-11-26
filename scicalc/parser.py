"""Tokenizer and parser

Module 5 of 47.  Taken from lines 634-991 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "parser"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import re
from fractions import Fraction

from .errors import CalcSyntaxError

# ======================================================================================
#  PART 5 : PARSER
# ======================================================================================

# Tokenizer + recursive-descent parser with Casio-style precedence (highest first):
#
#     ( )  functions        sin(30)   sqrt 16   log(100)
#     postfix               5!  50%  30°  x²  x³  x⁻¹
#     power                 2^3   (right to left: 2^3^2 = 2^9)
#     prefix + -            -2^2 = -4
#     implicit multiply     2pi  3(4+5)  2sin(30)   (binds tighter than * and /)
#     nPr  nCr
#     *  /  mod
#     +  -
#     ->                    5 -> A   (store in a variable)
#
# It builds a small tree of tuples; session.py evaluates it. No eval() is used anywhere.


VARIABLES = "ABCDEFXYM"
INFIX_WORDS = {"mod", "npr", "ncr"}
POSTFIX = {"!", "%", "°", "²", "³", "⁻¹"}
MAX_DEPTH = 50
MAX_LENGTH = 500

_NUM = re.compile(r"\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?", re.ASCII)
_LETTERS = re.compile(r"[A-Za-z_]+")
_BASEN = re.compile(r"0(?:[xX][0-9a-fA-F]+|[bB][01]+|[oO][0-7]+)(?![0-9A-Za-z_])", re.ASCII)
_DMS = re.compile(r"°\s*(\d+\.?\d*)\s*'\s*(?:(\d+\.?\d*)\s*\")?", re.ASCII)
_DIGITS_RE = re.compile(r"\d+", re.ASCII)
_WORD = re.compile(r"[A-Za-z_][A-Za-z_0-9]*")
_SYMBOLS = {"+": "+", "-": "-", "−": "-", "–": "-", "*": "*", "×": "*", "·": "*",
            "/": "/", "÷": "/", "^": "^", "!": "!", "%": "%", "°": "°", "²": "²", "³": "³"}


class Token:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind, value, pos):
        self.kind, self.value, self.pos = kind, value, pos

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.pos})"


def _split_letters(run, known):
    """'sinx' -> ['sin', 'x'];  'AB' -> ['A', 'B'];  'pix' -> ['pi', 'x']."""
    parts, k = [], 0
    while k < len(run):
        for length in range(len(run) - k, 1, -1):
            if known(run[k:k + length].lower()):
                parts.append(run[k:k + length])
                k += length
                break
        else:
            parts.append(run[k])
            k += 1
    return parts


def tokenize(text, known):
    """`known(lowercase_name)` says whether a multi-letter name is a function/constant."""
    if len(text) > MAX_LENGTH:
        raise CalcSyntaxError(f"input too long (max {MAX_LENGTH} characters)", MAX_LENGTH)
    tokens, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch.isspace():
            i += 1
            continue
        if ch in ('"', "'"):
            quote_char = ch
            start_pos = i
            i += 1
            val_chars = []
            while i < n and text[i] != quote_char:
                val_chars.append(text[i])
                i += 1
            if i < n:
                i += 1  # consume closing quote
            tokens.append(Token("STR", "".join(val_chars), start_pos))
            continue
        if ch == "0" and _BASEN.match(text, i):                       # 0xFF, 0b1010, 0o17
            m = _BASEN.match(text, i)
            tokens.append(Token("NUM", int(m.group(), 0), i))  # pyright: ignore[reportOptionalMemberAccess]
            i = m.end()  # pyright: ignore[reportOptionalMemberAccess]
        elif ch in "0123456789" or ch == ".":
            m = _NUM.match(text, i)
            if not m:
                raise CalcSyntaxError("stray '.'", i)
            s = m.group()
            try:
                value = int(s) if s.isdigit() else float(s)
            except ValueError:
                raise CalcSyntaxError("number too long", i)
            i = m.end()
            d = _DMS.match(text, i) if "e" not in s.lower() else None
            if d and s.isdigit():                                       # 1°30'15"  ->  1.504166...°
                value = value + Fraction(d.group(1)) / 60
                if d.group(2):
                    value += Fraction(d.group(2)) / 3600
                tokens.append(Token("NUM", value, i - len(s)))
                tokens.append(Token("OP", "°", i))
                i = d.end()
            else:
                tokens.append(Token("NUM", value, i - len(s)))
        elif text.startswith("**", i):
            tokens.append(Token("OP", "^", i)); i += 2
        elif text.startswith("->", i):
            tokens.append(Token("ARROW", "->", i)); i += 2
        elif text.startswith("⁻¹", i):
            tokens.append(Token("OP", "⁻¹", i)); i += 2
        elif ch == "→":
            tokens.append(Token("ARROW", "->", i)); i += 1
        elif ch in _SYMBOLS:
            tokens.append(Token("OP", _SYMBOLS[ch], i)); i += 1
        elif ch in "([":
            tokens.append(Token("LP", "(", i)); i += 1
        elif ch in ")]":
            tokens.append(Token("RP", ")", i)); i += 1
        elif ch == "{":
            tokens.append(Token("LB", "{", i)); i += 1
        elif ch == "}":
            tokens.append(Token("RB", "}", i)); i += 1
        elif ch == ",":
            tokens.append(Token("COMMA", ",", i)); i += 1
        elif ch == "π":
            tokens.append(Token("NAME", "pi", i)); i += 1
        elif ch == "√":
            tokens.append(Token("NAME", "sqrt", i)); i += 1
        elif ch == "∛":
            tokens.append(Token("NAME", "cbrt", i)); i += 1
        elif ch.isascii() and (ch.isalpha() or ch == "_"):
            word = _WORD.match(text, i).group()  # pyright: ignore[reportOptionalMemberAccess]
            run = _LETTERS.match(text, i).group()  # pyright: ignore[reportOptionalMemberAccess]
            end = i + len(run)
            if known(word.lower()):                                   # log10, atan2, deg2rad ...
                tokens.append(Token("NAME", word, i))
                i += len(word)
            else:
                parts = _split_letters(run, known)
                for part in parts:                      # e.g. 'foo' -> f, o, o: 'o' is nothing
                    if len(part) == 1 and part not in ("e", "i") and part.upper() not in VARIABLES:
                        raise CalcSyntaxError(f"unknown name '{run}'", i)
                offset = i
                for part in parts:
                    tokens.append(Token("NAME", part, offset))
                    offset += len(part)
                i = end
        else:
            raise CalcSyntaxError(f"unexpected character '{ch}'", i)
    tokens.append(Token("END", None, n))
    return tokens


class Parser:
    def __init__(self, tokens, registry, user=None):
        self.t = tokens
        self.i = 0
        self.reg = registry
        self.user = user or {}                   # user-defined functions: name -> (params, body, tree)
        self.depth = 0

    # ---- helpers ----
    def peek(self):
        return self.t[self.i]

    def take(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def is_op(self, *values):
        tok = self.peek()
        return tok.kind == "OP" and tok.value in values

    def is_word(self, *words):
        tok = self.peek()
        return tok.kind == "NAME" and tok.value.lower() in words

    def enter(self):
        self.depth += 1
        if self.depth > MAX_DEPTH:
            raise CalcSyntaxError("expression is nested too deeply", self.peek().pos)

    def leave(self):
        self.depth -= 1

    def starts_operand(self):
        tok = self.peek()
        return tok.kind in ("NUM", "LP", "LB") or (tok.kind == "NAME" and tok.value.lower() not in INFIX_WORDS) \
            or (tok.kind == "OP" and tok.value in "+-")

    def close_paren(self):
        tok = self.peek()
        if tok.kind == "RP":
            self.take()
        elif tok.kind != "END":                     # a missing ')' at the very end is allowed
            raise CalcSyntaxError("expected ')'", tok.pos)

    # ---- grammar ----
    def parse(self):
        tree = self.expr()
        target = None
        if self.peek().kind == "ARROW":
            self.take()
            tok = self.take()
            name = tok.value.upper() if tok.kind == "NAME" and len(tok.value) == 1 else None
            if name is None or name not in VARIABLES or tok.value == "e":
                raise CalcSyntaxError(f"can only store into {', '.join(VARIABLES)}", tok.pos)
            target = name
        if self.peek().kind != "END":
            raise CalcSyntaxError("unexpected input", self.peek().pos)
        return tree, target

    def expr(self):
        self.enter()
        node = self.muldiv()
        while self.is_op("+", "-"):
            op = self.take().value
            node = ("bin", op, node, self.muldiv())
        self.leave()
        return node

    def muldiv(self):
        node = self.permcomb()
        while self.is_op("*", "/") or self.is_word("mod"):
            tok = self.take()
            op = tok.value.lower() if tok.kind == "NAME" else tok.value
            node = ("bin", op, node, self.permcomb())
        return node

    def permcomb(self):
        node = self.implicit()
        while self.is_word("npr", "ncr"):
            tok = self.take()
            node = ("call", tok.value.lower(), [node, self.implicit()], tok.pos)
        return node

    def implicit(self):
        node = self.unary()
        while self.starts_factor():
            node = ("bin", "*", node, self.power())
        return node

    def starts_factor(self):
        tok = self.peek()
        if tok.kind == "NUM":
            return self.t[self.i - 1].kind != "NUM"
        if tok.kind == "NAME":
            return tok.value.lower() not in INFIX_WORDS
        return tok.kind in ("LP", "LB")

    def unary(self):
        if self.is_op("+", "-"):
            self.enter()
            op = self.take().value
            operand = self.unary()
            self.leave()
            return ("neg", operand) if op == "-" else operand
        return self.power()

    def power(self):
        base = self.postfix()
        if self.is_op("^"):
            self.take()
            self.enter()
            exponent = self.unary()
            self.leave()
            return ("bin", "^", base, exponent)
        return base

    def postfix(self):
        node = self.primary()
        while self.peek().kind == "OP" and self.peek().value in POSTFIX:
            node = ("post", self.take().value, node)
        return node

    def primary(self):
        tok = self.take()
        if tok.kind == "NUM":
            return ("num", tok.value)
        if tok.kind == "STR":
            return ("str", tok.value)
        if tok.kind == "LP":
            node = self.expr()
            self.close_paren()
            return node
        if tok.kind == "LB":                                        # list {1, 2, 3} or matrix {{1, 2}, {3, 4}}
            if self.peek().kind == "RB":
                raise CalcSyntaxError("a list cannot be empty", tok.pos)
            self.enter()
            items = [self.expr()]
            while self.peek().kind == "COMMA":
                self.take()
                items.append(self.expr())
            self.leave()
            end = self.peek()
            if end.kind == "RB":
                self.take()
            elif end.kind != "END":
                raise CalcSyntaxError("expected '}'", end.pos)
            return ("list", items)
        if tok.kind != "NAME":
            self.i -= 1
            what = "end of input" if tok.kind == "END" else f"'{tok.value}'"
            raise CalcSyntaxError(f"unexpected {what}", tok.pos)

        name = tok.value
        lname = name.lower()
        if lname == "ans":
            return ("ans", 0)
        if lname == "preans":
            return ("ans", 1)
        if lname in self.user and self.peek().kind == "LP":            # f(3) with a user function f
            self.take()
            args = []
            if self.peek().kind != "RP":
                args.append(self.expr())
                while self.peek().kind == "COMMA":
                    self.take()
                    args.append(self.expr())
            self.close_paren()
            return ("ucall", lname, args, tok.pos)
        func = self.reg.function(name)
        if func is not None:
            return ("call", func.name, self.call_args(func), tok.pos)
        if name == "i":
            return ("imag",)
        const = self.reg.constant(name)
        if const is not None:
            return ("const", const.name)
        if len(name) == 1 and name.upper() in VARIABLES:
            return ("var", name.upper())
        raise CalcSyntaxError(f"unknown name '{name}'", tok.pos)

    def call_args(self, func):
        if self.peek().kind == "LP":
            self.take()
            args = []
            if self.peek().kind == "RP":
                self.take()
                return args
            args.append(self.expr())
            while self.peek().kind == "COMMA":
                self.take()
                args.append(self.expr())
            self.close_paren()
            return args
        if func.min_args == 0 and not self.starts_operand():
            return []
        self.enter()
        arg = self.unary()                          # sin 30, sqrt 16, ln -2
        self.leave()
        return [arg]
