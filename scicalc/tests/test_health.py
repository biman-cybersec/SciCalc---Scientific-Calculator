"""Checks: health.  Run alone with  python run_tests.py health"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "health"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_health_34(check, near, ex):
    """Phase 3: health and fitness"""
    # ================= Phase 3: health and fitness =================
    ex("mifflin male", "bmr_mifflin('m',80,180,30)", 1780)
    ex("mifflin female", "bmr_mifflin('f',60,165,30)", 600 + 1031.25 - 150 - 161)
    ex("sex spellings agree", "bmr_mifflin('male',80,180,30)", 1780)
    ex("sex as number", "bmr_mifflin(0,60,165,30)", 600 + 1031.25 - 150 - 161)
    near("female differs by 166", "bmr_mifflin('m',70,170,40)-bmr_mifflin('f',70,170,40)", 166)
    near("harris male", "bmr_harris('m',80,180,30)", 88.362 + 13.397 * 80 + 4.799 * 180 - 5.677 * 30)
    near("harris female", "bmr_harris('f',60,165,30)", 447.593 + 9.247 * 60 + 3.098 * 165 - 4.330 * 30)
    near("harris within 5% of mifflin", "bmr_harris('m',80,180,30)/bmr_mifflin('m',80,180,30)", 1, 0.05)
    near("katch", "bmr_katch(60)", 370 + 21.6 * 60)
    near("tdee", "tdee(1780,1.55)", 1780 * 1.55)
    near("ideal weight man 180 cm", "ideal_weight('m',180)", 50 + 2.3 * (180 / 2.54 - 60))
    near("ideal weight woman 165 cm", "ideal_weight('f',165)", 45.5 + 2.3 * (165 / 2.54 - 60))
    near("ideal weight of a short adult stays at the base", "ideal_weight('m',140)", 50)
    # Navy method: the original inch-based formulas are an independent form of the metric ones
    inch = 2.54
    near("navy man", "body_fat_navy('m',180,90,38)", 86.010 * math.log10((90 - 38) / inch) - 70.041 * math.log10(180 / inch) + 36.76, 1e-2)   # the published inch and metric constants are rounded differently
    near("navy woman", "body_fat_navy('f',165,75,32,98)", 163.205 * math.log10((75 + 98 - 32) / inch) - 97.684 * math.log10(165 / inch) - 78.387, 2e-2)
    near("bsa mosteller", "bsa_mosteller(180,80)", math.sqrt(180 * 80 / 3600))
    near("bsa dubois", "bsa_dubois(180,80)", 0.007184 * 80 ** 0.425 * 180 ** 0.725)
    near("bsa formulas agree with Haycock within 3%", "bsa_mosteller(175,70)", 0.024265 * 70 ** 0.5378 * 175 ** 0.3964, 0.03)
    near("bsa dubois vs Haycock within 3%", "bsa_dubois(175,70)", 0.024265 * 70 ** 0.5378 * 175 ** 0.3964, 0.03)
    near("water", "water_intake(70)", 2.45)
    near("tanaka", "hr_max_tanaka(40)", 180)
    near("karvonen", "hr_zone(40,60,70)", 60 + 0.7 * (180 - 60))
    near("karvonen at 0% is resting", "hr_zone(40,60,0)", 60)
    near("karvonen at 100% is max", "hr_zone(40,60,100)", 180)
    near("calories burned", "calories_burned(8,70,0.5)", 280)
    near("pace to speed", "pace_to_speed(5)", 12)
    near("pace round trip", "speed_to_pace(pace_to_speed(6.25))", 6.25)
    near("vo2max uth", "vo2max_uth(190,60)", 15.3 * 190 / 60)
    near("vo2max cooper", "vo2max_cooper(2800)", (2800 - 504.9) / 44.73)
    near("epley", "one_rep_max(100,5)", 100 * (1 + 5 / 30))
    near("epley one rep", "one_rep_max(100,1)", 100)
    near("brzycki", "one_rep_max_brzycki(100,5)", 100 * 36 / 32)
    near("brzycki and epley agree within 5% at 5 reps", "one_rep_max(100,5)/one_rep_max_brzycki(100,5)", 1, 0.05)
    near("macro protein", "macro_protein_g(2000,30)", 150)
    near("macros add back to the calories", "macro_protein_g(2000,30)*4+macro_carb_g(2000,50)*4+macro_fat_g(2000,20)*9", 2000)
    near("whr", "waist_hip_ratio(80,100)", 0.8)
    near("map", "map_pressure(120,80)", 80 + (120 - 80) / 3)
    near("pulse pressure", "pulse_pressure(120,80)", 40)
    near("cockcroft-gault man", "creatinine_clearance('m',60,80,1)", (140 - 60) * 80 / 72)
    near("cockcroft-gault woman is 85%", "creatinine_clearance('f',60,80,1)", 0.85 * (140 - 60) * 80 / 72)
    near("widmark in per mille form", "bac_widmark('m',40,80,2)", (40 / (0.68 * 80) - 0.15 * 2) / 10)
    near("widmark never negative", "bac_widmark('f',10,80,10)", 0)
    near("riegel same distance", "riegel_predict(25,5,5)", 25)
    near("riegel", "riegel_predict(25,5,10)", 25 * 2 ** 1.06)
    near("days to goal", "days_to_goal(5,500)", 77)
    for e in ["bmr_mifflin('x',80,180,30)", "bmr_mifflin(2,80,180,30)", "bmr_mifflin('m',0,180,30)", "bmr_mifflin('m',80,10,30)",
              "bmr_mifflin('m',80,180,0)", "bmr_mifflin('m',80,180,130)", "bmr_mifflin('m',80,180)", "bmr_mifflin(80,'m',180,30)",
              "bmr_harris('q',60,165,30)", "bmr_katch(0)", "tdee(1780,0.5)", "tdee(50,1.5)", "ideal_weight('m',10)", "ideal_weight('z',180)",
              "body_fat_navy('m',180,30,38)", "body_fat_navy('f',165,75,32)", "body_fat_navy('f',165,75,32,0)", "body_fat_navy('m',180,90,5)",
              "bsa_mosteller(0,80)", "bsa_dubois(180,-1)", "water_intake(0)", "hr_max_tanaka(0)", "hr_zone(40,60,101)", "hr_zone(40,200,50)",
              "hr_zone(40,10,50)", "calories_burned(0,70,1)", "calories_burned(8,70,-1)", "pace_to_speed(0)", "speed_to_pace(-1)",
              "vo2max_uth(190,190)", "vo2max_uth(190,0)", "vo2max_cooper(-1)", "one_rep_max(100,0)", "one_rep_max(100,2.5)", "one_rep_max_brzycki(100,40)",
              "one_rep_max_brzycki(-1,5)", "macro_protein_g(2000,101)", "macro_carb_g(-1,50)", "macro_fat_g(2000,-1)", "waist_hip_ratio(80,0)",
              "map_pressure(80,120)", "pulse_pressure(80,120)", "creatinine_clearance('m',10,80,1)", "creatinine_clearance('m',60,80,0)",
              "bac_widmark('m',-1,80,1)", "bac_widmark('m',40,80,-1)", "riegel_predict(25,0,10)", "riegel_predict(25,5,0)", "days_to_goal(5,0)",
              "days_to_goal(-1,100)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
