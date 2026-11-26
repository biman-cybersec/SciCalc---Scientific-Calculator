"""Sprint 5B: base-N and bit operations

Module 28 of 47.  Taken from lines 9319-9533 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_basen"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from .errors import MathError
from .registry import register
from .lib_powers_rounding import _whole
from .lib_vectors_solver_basen import CAT_BASE

# ======================================================================================
#  SPRINT 5 - PART B : BASE-N AND BIT OPERATIONS (24)
#  Words are unsigned unless a function says "two's complement".  Bit positions count from 0.
# ======================================================================================

def _nat(n, what="n"):
    n = _whole(n, what)
    if n < 0:
        raise MathError(f"{what} must not be negative")
    return n


def _bits(bits):
    bits = _whole(bits, "bits")
    if not 1 <= bits <= 1024:
        raise MathError("bits must be between 1 and 1024")
    return bits


def _word(n, bits):
    n = _nat(n)
    bits = _bits(bits)
    if n >> bits:
        raise MathError("the number does not fit in that many bits")
    return n, bits


def _bn(name, desc, args, example):
    return register(name, CAT_BASE, desc, args, exact=True, example=example)


_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@_bn("dec2base", "Integer to text in base 2..36: dec2base(n, b)", 2, 'dec2base(255, 16) => FF')
def dec2base(n, b):
    n, b = _whole(n, "n"), _whole(b, "base")
    if not 2 <= b <= 36:
        raise MathError("base must be between 2 and 36")
    if n == 0:
        return "0"
    sign, n = ("-" if n < 0 else ""), abs(n)
    out = []
    while n:
        n, r = divmod(n, b)
        out.append(_DIGITS[r])
    return sign + "".join(reversed(out))


@_bn("base2dec", 'Text in base 2..36 to an integer: base2dec("text", b)', 2, 'base2dec("ff", 16) => 255')
def base2dec(text, b):
    b = _whole(b, "base")
    if not 2 <= b <= 36:
        raise MathError("base must be between 2 and 36")
    if not isinstance(text, str):
        text = str(_whole(text, "digits"))
    t = text.strip().upper()
    sign = -1 if t.startswith("-") else 1
    t = t.lstrip("+-")
    if not t:
        raise MathError("no digits")
    value = 0
    for ch in t:
        d = _DIGITS.find(ch)
        if d < 0 or d >= b:
            raise MathError(f"'{ch}' is not a base-{b} digit")
        value = value * b + d
    return sign * value


@_bn("bit_count", "Number of 1 bits in n >= 0: bit_count(n)", 1, "bit_count(255) => 8")
def bit_count(n):
    return bin(_nat(n)).count("1")


@_bn("bit_length", "Number of bits needed for n >= 0: bit_length(n)", 1, "bit_length(255) => 8")
def bit_length(n):
    return _nat(n).bit_length()


def _pos(i):
    i = _nat(i, "bit position")
    if i > 4096:
        raise MathError("bit position too large")
    return i


@_bn("bit_get", "Bit i of n (0 = lowest): bit_get(n, i)", 2, "bit_get(5, 2) => 1")
def bit_get(n, i):
    return (_nat(n) >> _pos(i)) & 1


@_bn("bit_set", "n with bit i set to 1: bit_set(n, i)", 2, "bit_set(5, 1) => 7")
def bit_set(n, i):
    return _nat(n) | (1 << _pos(i))


@_bn("bit_clear", "n with bit i cleared to 0: bit_clear(n, i)", 2, "bit_clear(7, 1) => 5")
def bit_clear(n, i):
    return _nat(n) & ~(1 << _pos(i))


@_bn("bit_toggle", "n with bit i flipped: bit_toggle(n, i)", 2, "bit_toggle(5, 0) => 4")
def bit_toggle(n, i):
    return _nat(n) ^ (1 << _pos(i))


@_bn("rotl", "Rotate left by k inside a word of the given bit size: rotl(n, k, bits)", 3, "rotl(1, 3, 8) => 8")
def rotl(n, k, bits):
    n, bits = _word(n, bits)
    k = _whole(k, "k") % bits
    return ((n << k) | (n >> (bits - k))) & ((1 << bits) - 1)


@_bn("rotr", "Rotate right by k inside a word of the given bit size: rotr(n, k, bits)", 3, "rotr(1, 1, 8) => 128")
def rotr(n, k, bits):
    n, bits = _word(n, bits)
    k = _whole(k, "k") % bits
    return ((n >> k) | (n << (bits - k))) & ((1 << bits) - 1)


@_bn("reverse_bits", "Reverse the bit order inside a word: reverse_bits(n, bits)", 2, "reverse_bits(1, 8) => 128")
def reverse_bits(n, bits):
    n, bits = _word(n, bits)
    return int(format(n, f"0{bits}b")[::-1], 2)


@_bn("bin2gray", "Binary to Gray code: bin2gray(n)", 1, "bin2gray(5) => 7")
def bin2gray(n):
    n = _nat(n)
    return n ^ (n >> 1)


@_bn("gray2bin", "Gray code to binary: gray2bin(n)", 1, "gray2bin(7) => 5")
def gray2bin(n):
    n = _nat(n)
    out = 0
    while n:
        out ^= n
        n >>= 1
    return out


@_bn("parity", "1 if the number of 1 bits is odd, else 0: parity(n)", 1, "parity(7) => 1")
def parity(n):
    return bin(_nat(n)).count("1") & 1


def _truth(x):
    return 1 if x != 0 else 0


@_bn("nand", "Logical NAND (non-zero is true): nand(a, b)", 2, "nand(1, 1) => 0")
def nand(a, b):
    return 1 - (_truth(a) & _truth(b))


@_bn("nor", "Logical NOR: nor(a, b)", 2, "nor(0, 0) => 1")
def nor(a, b):
    return 1 - (_truth(a) | _truth(b))


@_bn("xnor", "Logical XNOR (equal truth values): xnor(a, b)", 2, "xnor(1, 1) => 1")
def xnor(a, b):
    return 1 - (_truth(a) ^ _truth(b))


@_bn("imply", "Logical implication a -> b: imply(a, b)", 2, "imply(1, 0) => 0")
def imply(a, b):
    return 1 if (_truth(a) == 0 or _truth(b) == 1) else 0


@_bn("twos_comp", "Two's complement word (unsigned value) of a signed n: twos_comp(n, bits)", 2, "twos_comp(-1, 8) => 255")
def twos_comp(n, bits):
    n, bits = _whole(n, "n"), _bits(bits)
    if not -(1 << (bits - 1)) <= n < (1 << (bits - 1)):
        raise MathError("the number does not fit in that many bits")
    return n & ((1 << bits) - 1)


@_bn("from_twos", "Signed value of a two's complement word: from_twos(n, bits)", 2, "from_twos(255, 8) => -1")
def from_twos(n, bits):
    n, bits = _word(n, bits)
    return n - (1 << bits) if n >> (bits - 1) else n


@_bn("sign_extend", "Sign-extend a word from from_bits to to_bits: sign_extend(n, from_bits, to_bits)", 3, "sign_extend(255, 8, 16) => 65535")
def sign_extend(n, from_bits, to_bits):
    n, fb = _word(n, from_bits)
    tb = _bits(to_bits)
    if tb < fb:
        raise MathError("to_bits must not be smaller than from_bits")
    signed = n - (1 << fb) if n >> (fb - 1) else n
    return signed & ((1 << tb) - 1)


@_bn("hamming_dist", "Number of differing bits: hamming_dist(a, b)", 2, "hamming_dist(5, 3) => 2")
def hamming_dist(a, b):
    return bin(_nat(a, "a") ^ _nat(b, "b")).count("1")


@_bn("mask_bits", "Number with k low bits set: mask_bits(k)", 1, "mask_bits(4) => 15")
def mask_bits(k):
    k = _nat(k, "k")
    if k > 4096:
        raise MathError("k too large")
    return (1 << k) - 1


@_bn("lowest_set_bit", "Value of the lowest 1 bit (0 for 0): lowest_set_bit(n)", 1, "lowest_set_bit(12) => 4")
def lowest_set_bit(n):
    n = _nat(n)
    return n & -n
