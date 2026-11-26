"""Phase 3: health and fitness

Module 40 of 47.  Taken from lines 13451-13694 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_health"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import MathError
from .registry import register
from .lib_chemistry import _cn

#  PHASE 3 : HEALTH AND FITNESS (28)
#  Metric units: kg, cm, years, kcal, minutes.  `sex` is 'm' or 'f' (also 'male', 'female',
#  or 1 / 0).  These are textbook estimating formulas, not medical advice; inputs outside
#  a plausible human range give Math ERROR.
# ======================================================================================
_HLT = "Health & Fitness"


def _hlt(name, desc, args, example, **kw):
    if any(a in desc for a in ("sex",)) or kw.pop("sexual", False):
        kw["exact"] = True
    return register(name, _HLT, desc, args, example=example, **kw)


def _hsex(s):
    """True for male, False for female."""
    if isinstance(s, str):
        t = s.strip().lower()
        if t in ("m", "male", "man"):
            return True
        if t in ("f", "female", "woman"):
            return False
        raise MathError("sex must be 'm' or 'f'")
    if isinstance(s, (int, Fraction)) and not isinstance(s, bool) and s in (0, 1):
        return s == 1
    raise MathError("sex must be 'm' or 'f' (or 1 / 0)")


def _hrange(x, lo, hi, what):
    x = _cn(x)
    if not math.isfinite(x) or not lo <= x <= hi:
        raise MathError(f"{what} should be between {lo:g} and {hi:g}")
    return x


def _hw(x):
    return _hrange(x, 1, 700, "weight (kg)")


def _hh(x):
    return _hrange(x, 30, 272, "height (cm)")


def _ha(x):
    return _hrange(x, 1, 120, "age (years)")


def _hpct(x):
    return _hrange(x, 0, 100, "percentage")


@_hlt("bmr_mifflin", "Basal metabolic rate (kcal/day), Mifflin-St Jeor: bmr_mifflin(sex, weight_kg, height_cm, age)", 4,
      "bmr_mifflin('m', 80, 180, 30) => 1780")
def bmr_mifflin(sex, w, h, a):
    return 10 * _hw(w) + 6.25 * _hh(h) - 5 * _ha(a) + (5 if _hsex(sex) else -161)


@_hlt("bmr_harris", "Basal metabolic rate (kcal/day), revised Harris-Benedict: bmr_harris(sex, weight_kg, height_cm, age)", 4,
      "bmr_harris('f', 60, 165, 30) => 1383.683")
def bmr_harris(sex, w, h, a):
    w, h, a = _hw(w), _hh(h), _ha(a)
    if _hsex(sex):
        return 88.362 + 13.397 * w + 4.799 * h - 5.677 * a
    return 447.593 + 9.247 * w + 3.098 * h - 4.330 * a


@_hlt("bmr_katch", "Basal metabolic rate (kcal/day) from lean body mass, Katch-McArdle: bmr_katch(lean_mass_kg)", 1, "bmr_katch(60) => 1666")
def bmr_katch(lbm):
    return 370 + 21.6 * _hw(lbm)


@_hlt("tdee", "Daily energy use: tdee(bmr, activity_factor)  (1.2 sedentary ... 1.9 very active)", 2, "tdee(1780, 1.55) => 2759")
def tdee(bmr, factor):
    return _hrange(bmr, 100, 10000, "BMR") * _hrange(factor, 1, 3, "activity factor")


@_hlt("ideal_weight", "Ideal body weight (kg), Devine formula: ideal_weight(sex, height_cm)", 2, "ideal_weight('m', 180) => 74.99212598")
def ideal_weight(sex, h):
    inches = _hh(h) / 2.54
    return (50 if _hsex(sex) else 45.5) + 2.3 * max(0.0, inches - 60)


@_hlt("body_fat_navy", "Body fat % by the US Navy tape method (cm): body_fat_navy(sex, height, waist, neck [, hip for women])", (4, 5),
      "body_fat_navy('m', 180, 90, 38) => 19.81198841")
def body_fat_navy(sex, h, waist, neck, hip=0):
    h, waist, neck = _hh(h), _hrange(waist, 20, 300, "waist"), _hrange(neck, 10, 100, "neck")
    if _hsex(sex):
        if waist <= neck:
            raise MathError("the waist must be larger than the neck")
        return 495 / (1.0324 - 0.19077 * math.log10(waist - neck) + 0.15456 * math.log10(h)) - 450
    hip = _hrange(hip, 20, 300, "hip")
    if waist + hip <= neck:
        raise MathError("waist + hip must exceed the neck")
    return 495 / (1.29579 - 0.35004 * math.log10(waist + hip - neck) + 0.22100 * math.log10(h)) - 450


@_hlt("bsa_mosteller", "Body surface area (m^2), Mosteller: bsa_mosteller(height_cm, weight_kg)", 2, "bsa_mosteller(180, 80) => 2")
def bsa_mosteller(h, w):
    return math.sqrt(_hh(h) * _hw(w) / 3600)


@_hlt("bsa_dubois", "Body surface area (m^2), Du Bois: bsa_dubois(height_cm, weight_kg)", 2, "bsa_dubois(180, 80) => 1.996421022")
def bsa_dubois(h, w):
    return 0.007184 * _hw(w) ** 0.425 * _hh(h) ** 0.725


@_hlt("water_intake", "Rule-of-thumb daily water (litres), 35 ml per kg: water_intake(weight_kg)", 1, "water_intake(70) => 2.45")
def water_intake(w):
    return 0.035 * _hw(w)


@_hlt("hr_max_tanaka", "Maximum heart rate (bpm), Tanaka: 208 - 0.7 age", 1, "hr_max_tanaka(40) => 180")
def hr_max_tanaka(a):
    return 208 - 0.7 * _ha(a)


@_hlt("hr_zone", "Target heart rate (bpm), Karvonen with Tanaka's maximum: hr_zone(age, resting_hr, percent_intensity)", 3,
      "hr_zone(40, 60, 70) => 144")
def hr_zone(a, rest, pct):
    rest = _hrange(rest, 20, 200, "resting heart rate")
    top = 208 - 0.7 * _ha(a)
    if rest >= top:
        raise MathError("the resting rate is above the maximum")
    return (top - rest) * _hpct(pct) / 100 + rest


@_hlt("calories_burned", "Energy (kcal) from the MET value of an activity: calories_burned(MET, weight_kg, hours)", 3,
      "calories_burned(8, 70, 0.5) => 280")
def calories_burned(met, w, hours):
    return _hrange(met, 0.5, 25, "MET") * _hw(w) * _hrange(hours, 0, 48, "hours")


@_hlt("pace_to_speed", "Speed (km/h) from a pace in minutes per km: pace_to_speed(min_per_km)", 1, "pace_to_speed(5) => 12")
def pace_to_speed(p):
    p = _cn(p)
    if not math.isfinite(p) or p <= 0:
        raise MathError("the pace must be positive")
    return 60 / p


@_hlt("speed_to_pace", "Pace (minutes per km) from a speed in km/h: speed_to_pace(kmh)", 1, "speed_to_pace(12) => 5")
def speed_to_pace(v):
    v = _cn(v)
    if not math.isfinite(v) or v <= 0:
        raise MathError("the speed must be positive")
    return 60 / v


@_hlt("vo2max_uth", "VO2 max estimate (ml/kg/min), Uth: 15.3 x max heart rate / resting heart rate", 2, "vo2max_uth(190, 60) => 48.45")
def vo2max_uth(hrmax, hrrest):
    mx, rest = _hrange(hrmax, 60, 250, "maximum heart rate"), _hrange(hrrest, 20, 200, "resting heart rate")
    if rest >= mx:
        raise MathError("the resting rate is above the maximum")
    return 15.3 * mx / rest


@_hlt("vo2max_cooper", "VO2 max estimate (ml/kg/min) from the 12-minute run distance in metres: (d - 504.9) / 44.73", 1, "vo2max_cooper(2800) => 51.31008272")
def vo2max_cooper(d):
    return (_hrange(d, 0, 6000, "distance") - 504.9) / 44.73


@_hlt("one_rep_max", "Estimated one-rep maximum, Epley: one_rep_max(weight, reps)", 2, "one_rep_max(100, 5) => 116.6666667")
def one_rep_max(w, reps):
    w, reps = _hrange(w, 0, 2000, "weight"), _hrange(reps, 1, 30, "repetitions")
    if reps != int(reps):
        raise MathError("repetitions must be a whole number")
    return w if reps == 1 else w * (1 + reps / 30)


@_hlt("one_rep_max_brzycki", "Estimated one-rep maximum, Brzycki: one_rep_max_brzycki(weight, reps)", 2, "one_rep_max_brzycki(100, 5) => 112.5")
def one_rep_max_brzycki(w, reps):
    w, reps = _hrange(w, 0, 2000, "weight"), _hrange(reps, 1, 30, "repetitions")
    if reps != int(reps):
        raise MathError("repetitions must be a whole number")
    return w * 36 / (37 - reps)


@_hlt("macro_protein_g", "Grams of protein for a share of calories (4 kcal/g): macro_protein_g(kcal, percent)", 2, "macro_protein_g(2000, 30) => 150")
def macro_protein_g(kcal, pct):
    return _hrange(kcal, 0, 20000, "calories") * _hpct(pct) / 100 / 4


@_hlt("macro_carb_g", "Grams of carbohydrate for a share of calories (4 kcal/g): macro_carb_g(kcal, percent)", 2, "macro_carb_g(2000, 50) => 250")
def macro_carb_g(kcal, pct):
    return _hrange(kcal, 0, 20000, "calories") * _hpct(pct) / 100 / 4


@_hlt("macro_fat_g", "Grams of fat for a share of calories (9 kcal/g): macro_fat_g(kcal, percent)", 2, "macro_fat_g(2000, 20) => 44.44444444")
def macro_fat_g(kcal, pct):
    return _hrange(kcal, 0, 20000, "calories") * _hpct(pct) / 100 / 9


@_hlt("waist_hip_ratio", "Waist-to-hip ratio: waist_hip_ratio(waist, hip)", 2, "waist_hip_ratio(80, 100) => 0.8")
def waist_hip_ratio(w, h):
    return _hrange(w, 20, 300, "waist") / _hrange(h, 20, 300, "hip")


@_hlt("map_pressure", "Mean arterial pressure (mmHg): map_pressure(systolic, diastolic)", 2, "map_pressure(120, 80) => 93.33333333")
def map_pressure(s, d):
    s, d = _hrange(s, 30, 300, "systolic pressure"), _hrange(d, 20, 200, "diastolic pressure")
    if d > s:
        raise MathError("diastolic cannot exceed systolic")
    return (s + 2 * d) / 3


@_hlt("pulse_pressure", "Pulse pressure (mmHg): pulse_pressure(systolic, diastolic)", 2, "pulse_pressure(120, 80) => 40")
def pulse_pressure(s, d):
    s, d = _hrange(s, 30, 300, "systolic pressure"), _hrange(d, 20, 200, "diastolic pressure")
    if d > s:
        raise MathError("diastolic cannot exceed systolic")
    return s - d


@_hlt("creatinine_clearance", "Creatinine clearance (ml/min), Cockcroft-Gault: creatinine_clearance(sex, age, weight_kg, serum_creatinine_mg_dl)", 4,
      "creatinine_clearance('m', 60, 80, 1) => 88.88888889")
def creatinine_clearance(sex, a, w, cr):
    v = (140 - _hrange(a, 18, 120, "age")) * _hw(w) / (72 * _hrange(cr, 0.1, 30, "creatinine"))
    return v if _hsex(sex) else 0.85 * v


@_hlt("bac_widmark", "Blood alcohol (g per 100 ml, i.e. %), Widmark: bac_widmark(sex, alcohol_grams, weight_kg, hours)", 4,
      "bac_widmark('m', 40, 80, 2) => 0.04352941176")
def bac_widmark(sex, grams, w, hours):
    r = 0.68 if _hsex(sex) else 0.55
    peak = _hrange(grams, 0, 2000, "alcohol") / (r * _hw(w) * 1000) * 100
    return max(0.0, peak - 0.015 * _hrange(hours, 0, 100, "hours"))


@_hlt("riegel_predict", "Predicted race time (same unit as t1), Riegel: riegel_predict(t1, d1, d2) = t1 (d2/d1)^1.06", 3,
      "riegel_predict(25, 5, 10) => 52.12328804")
def riegel_predict(t1, d1, d2):
    return _hrange(t1, 0, 1e6, "time") * (_hrange(d2, 1e-9, 1e6, "distance") / _hrange(d1, 1e-9, 1e6, "distance")) ** 1.06


@_hlt("days_to_goal", "Days to lose or gain a mass at a steady daily energy deficit (7700 kcal per kg): days_to_goal(kg, kcal_per_day)", 2,
      "days_to_goal(5, 500) => 77")
def days_to_goal(kg, daily):
    daily = _cn(daily)
    if not math.isfinite(daily) or daily <= 0:
        raise MathError("the daily deficit must be positive")
    return _hrange(kg, 0, 700, "mass") * 7700 / daily


# ======================================================================================
