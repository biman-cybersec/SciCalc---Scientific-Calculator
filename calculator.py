"""SCICALC - an offline, Casio-style scientific calculator (main executor; the code lives in the scicalc/ package).

HOW TO USE
    python3 calculator.py                  Casio-style calculator: type 3+4*2, sin(30), 1/3+1/6 ...
    python3 calculator.py "sin(30)+2"      one answer, then exit
    python3 calculator.py --menu           the old numbered menu (geometry, BMI, converters ...)
    python3 calculator.py --selftest       run the built-in checks

    Inside the calculator type  help  for the commands (mode, norm, fix, sci, vars, list, search, menu ...).

HOW THIS FILE IS ORGANISED  (search for "PART n" to jump around)
    PART 1  Errors                     Math ERROR / Syntax ERROR / Argument ERROR
    PART 2  Function registry          @register  <- every new function is added with this
    PART 3  Arithmetic                 exact fractions + clean floats (ar_* helpers)
    PART 4  Display                    Norm 1/2, Fix, Sci, fractions
    PART 5  Parser                     tokenizer + Casio-style precedence (no eval anywhere)
    PART 6  Calculator                 angle mode, variables, Ans, history, evaluator
    PART 7  Function library           trig, exp/log, rounding, combinatorics, constants  <- ADD NEW FUNCTIONS HERE
    PART 8  Old numbered menu          (menu_* functions) geometry, BMI, converters, tables
    PART 9  Command line               the interactive Casio-style prompt
    PART 10 Self-test + entry point

TO ADD A FUNCTION (in PART 7):
    @register("sinh", "Hyperbolic", "Hyperbolic sine", example="sinh(0) => 0")
    def sinh(x):
        return math.sinh(x)

THE CODE IS SPLIT INTO MODULES  (see scicalc/MODULES.md for the list)
    calculator.py      <- this file: the main executor, it only starts scicalc.app.main()
    scicalc/*.py       <- 47 modules, loaded in order; each imports everything from the one before
    run_tests.py       <- test one module at a time:   python run_tests.py lib_trig
"""

from scicalc.app import main

if __name__ == "__main__":
    raise SystemExit(main())
