"""Checks: basen.  Run alone with  python run_tests.py basen"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "basen"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from .helpers import _err, _expr_error  # noqa: F401


def checks_basen_15(ex, text):
    """bases and bit operations"""
    # ---------------------------------------------------------------- bases and bit operations
    for n in (0, 5, 42, 255, 1000):
        text(f"dec2bin({n})", f"dec2bin({n})", bin(n))
        text(f"dec2oct({n})", f"dec2oct({n})", oct(n))
        text(f"dec2hex({n})", f"dec2hex({n})", hex(n))
        ex(f"bin2dec({bin(n)[2:]})", f"bin2dec({bin(n)[2:]})", n)
        ex(f"oct2dec({oct(n)[2:]})", f"oct2dec({oct(n)[2:]})", n)
        ex(f"hex2dec('{hex(n)[2:]}')", f"hex2dec('{hex(n)[2:]}')", n)
    for a, b in [(12, 10), (255, 15), (7, 0), (1023, 512)]:
        ex(f"bitand({a},{b})", f"bitand({a},{b})", a & b)
        ex(f"bitor({a},{b})", f"bitor({a},{b})", a | b)
        ex(f"bitxor({a},{b})", f"bitxor({a},{b})", a ^ b)
    for a in (0, 5, 255):
        ex(f"bitnot({a})", f"bitnot({a})", ~a)
    for a, sft in [(3, 2), (12, 2), (1, 10)]:
        ex(f"shl({a},{sft})", f"shl({a},{sft})", a << sft)
        ex(f"shr({a * 64},{sft})", f"shr({a * 64},{sft})", (a * 64) >> sft)


def checks_basen_20(check, run, ex, text):
    """Sprint 5 : base-N and bits (brute force)"""
    # ---------------------------------------------------------------- Sprint 5 : base-N and bits (brute force)
    for n in (0, 1, 7, 10, 35, 36, 255, 1000, 65535, 123456789):
        for b in (2, 3, 7, 8, 10, 16, 25, 36):
            txt = run(f"dec2base({n},{b})").text
            check(f"dec2base({n},{b}) parses back with int()", int(txt, b), n)
            ex(f"base2dec round trip {n} base {b}", f'base2dec("{txt}",{b})', n)
    text("dec2base 255 base 16", "dec2base(255,16)", "FF")
    text("dec2base 255 base 2", "dec2base(255,2)", "11111111")
    text("dec2base negative", "dec2base(-10,2)", "-1010")
    text("dec2base 35 base 36", "dec2base(35,36)", "Z")
    ex("base2dec lower case", 'base2dec("ff",16)', 255)
    ex("base2dec negative", 'base2dec("-101",2)', -5)
    ex("base2dec agrees with hex2dec", 'base2dec("1f4",16)', 500)
    for n in range(0, 300):
        ex(f"bit_count({n})", f"bit_count({n})", bin(n).count("1"))
        ex(f"bit_length({n})", f"bit_length({n})", len(bin(n)) - 2 if n else 0)
        ex(f"parity({n})", f"parity({n})", bin(n).count("1") % 2)
        ex(f"bin2gray({n})", f"bin2gray({n})", n ^ (n >> 1))
        ex(f"gray2bin(bin2gray({n}))", f"gray2bin(bin2gray({n}))", n)
        ex(f"lowest_set_bit({n})", f"lowest_set_bit({n})", next((1 << k for k in range(10) if n >> k & 1), 0))
        if n < 299:
            ex(f"gray codes {n},{n + 1} differ in one bit", f"hamming_dist(bin2gray({n}),bin2gray({n + 1}))", 1)
        for i in (0, 3, 8):
            ex(f"bit_get({n},{i})", f"bit_get({n},{i})", int(format(n, "b").zfill(12)[::-1][i]))
            ex(f"bit_set({n},{i})", f"bit_set({n},{i})", n | (1 << i))
            ex(f"bit_clear({n},{i})", f"bit_clear({n},{i})", n & ~(1 << i))
            ex(f"bit_toggle({n},{i})", f"bit_toggle({n},{i})", n ^ (1 << i))
    for n in (0, 1, 5, 129, 200, 255):
        s8 = format(n, "08b")
        for k in range(0, 10):
            kk = k % 8
            ex(f"rotl({n},{k},8) as a string rotation", f"rotl({n},{k},8)", int(s8[kk:] + s8[:kk], 2))
            ex(f"rotr({n},{k},8) as a string rotation", f"rotr({n},{k},8)", int(s8[8 - kk:] + s8[:8 - kk], 2) if kk else n)
            ex(f"rotr undoes rotl ({n},{k})", f"rotr(rotl({n},{k},8),{k},8)", n)
        ex(f"reverse_bits({n},8)", f"reverse_bits({n},8)", int(s8[::-1], 2))
        ex(f"reverse_bits twice({n})", f"reverse_bits(reverse_bits({n},8),8)", n)
        ex(f"mask and word: bitand({n},mask_bits(4))", f"bitand({n},mask_bits(4))", n & 15)
    ex("rotl 16 bit", "rotl(32769,1,16)", 3)
    ex("reverse_bits 16", "reverse_bits(1,16)", 32768)
    for a in (0, 1, 2, -3, 0.5):
        for b in (0, 1, 2, -7):
            ta, tb = a != 0, b != 0
            ex(f"nand({a},{b})", f"nand({a},{b})", int(not (ta and tb)))
            ex(f"nor({a},{b})", f"nor({a},{b})", int(not (ta or tb)))
            ex(f"xnor({a},{b})", f"xnor({a},{b})", int(ta == tb))
            ex(f"imply({a},{b})", f"imply({a},{b})", int((not ta) or tb))
    for v in range(-128, 128):
        w = v & 255
        ex(f"twos_comp({v},8)", f"twos_comp({v},8)", w)
        ex(f"from_twos({w},8)", f"from_twos({w},8)", v)
        ex(f"sign_extend({w},8,16) keeps the value", f"from_twos(sign_extend({w},8,16),16)", v)
    ex("sign_extend positive", "sign_extend(127,8,16)", 127)
    ex("sign_extend negative", "sign_extend(128,8,16)", 65408)
    ex("twos_comp 16 bit", "twos_comp(-2,16)", 65534)
    for a, b in [(0, 0), (5, 3), (255, 0), (1023, 512), (12345, 54321)]:
        ex(f"hamming_dist({a},{b})", f"hamming_dist({a},{b})", bin(a ^ b).count("1"))
    for k in (0, 1, 4, 8, 31, 64):
        ex(f"mask_bits({k})", f"mask_bits({k})", 2 ** k - 1)
        ex(f"bit_count(mask_bits({k}))", f"bit_count(mask_bits({k}))", k)
