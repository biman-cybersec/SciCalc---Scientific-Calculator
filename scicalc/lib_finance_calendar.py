"""Sprint 7: finance, calendar, navigation

Module 32 of 47.  Taken from lines 10577-11219 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_finance_calendar"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .arithmetic import ar_snap
from .lib_powers_rounding import _whole

# ======================================================================================
#  SPRINT 7 : FINANCE, BUSINESS, CALENDAR (43) AND TRIG / NAVIGATION UTILITIES (20)
#  Rates are percent per year (5 = 5%), like emi, fv, pv and npv - EXCEPT annuity_due_fv,
#  perpetuity and growing_perpetuity, which take a decimal rate (0.05 = 5%) like their
#  siblings annuity_fv and annuity_pv.
#  Calendar: the proleptic Gregorian calendar (the leap-year rule is applied to every year,
#  including years before 1582); year 0 and negative years follow astronomical numbering.
#  Weekdays count 0 = Monday ... 6 = Sunday.  Weeks are ISO 8601 weeks.
#  Navigation: spherical Earth of radius 6371 km (the same as haversine_dist); latitudes and
#  longitudes in degrees (north and east positive); bearings clockwise from north.
# ======================================================================================
_FIN = "Financial"
_CAL = "Calendar & Dates"
_TRG = "Trigonometry"
_CAT_DAILY = "Daily Life"


def _f(name, desc, args, example, cat=_FIN, exact=False):
    return register(name, cat, desc, args, exact=exact, example=example)


def _fpos(*vals):
    for v in vals:
        if not (v > 0) or math.isinf(v):
            raise MathError("this value must be positive")


def _fnn(*vals):
    for v in vals:
        if v < 0 or math.isinf(v) or math.isnan(v):
            raise MathError("this value must not be negative")


def _monthly(rate):
    if rate < 0 or math.isinf(rate):
        raise MathError("rate must not be negative")
    return rate / 1200.0


def _pmt(P, rate, n):
    r = _monthly(rate)
    return P / n if r == 0 else P * r / (1 - (1 + r) ** -n)


# ---------- loans and savings ----------
@_f("loan_balance", "Balance left after k monthly payments of a loan (rate % per year, n months): loan_balance(P, rate, n, k)", 4, "loan_balance(1200, 0, 12, 6) => 600", exact=True)
def loan_balance(P, rate, n, k):
    n, k = _whole(n, "n"), _whole(k, "k")
    P, rate = float(P), float(rate)
    _fnn(P)
    if n < 1 or not 0 <= k <= n:
        raise MathError("need n >= 1 and 0 <= k <= n")
    r = _monthly(rate)
    if r == 0:
        return P * (1 - k / n)
    pmt = _pmt(P, rate, n)
    g = (1 + r) ** k
    bal = P * g - pmt * (g - 1) / r
    return 0.0 if k == n else max(bal, 0.0)


@_f("loan_total_interest", "Total interest paid over the loan (rate % per year, n months): loan_total_interest(P, rate, n)", 3, "loan_total_interest(1200, 0, 12) => 0", exact=True)
def loan_total_interest(P, rate, n):
    n = _whole(n, "n")
    P, rate = float(P), float(rate)
    _fnn(P)
    if n < 1:
        raise MathError("n must be at least 1")
    return _pmt(P, rate, n) * n - P


@_f("loan_term", "Number of monthly payments needed to repay a loan with payment pmt (rate % per year): loan_term(P, rate, pmt)", 3, "loan_term(1200, 0, 100) => 12")
def loan_term(P, rate, pmt):
    _fpos(P, pmt)
    r = _monthly(rate)
    if r == 0:
        return P / pmt
    if pmt <= P * r:
        raise MathError("the payment does not even cover the interest")
    return -math.log(1 - P * r / pmt) / math.log(1 + r)


@_f("sip_fv", "Future value of a monthly SIP, deposits at the start of each month (rate % per year, n months): sip_fv(pmt, rate, n)", 3, "sip_fv(1000, 0, 12) => 12000", exact=True)
def sip_fv(pmt, rate, n):
    n = _whole(n, "n")
    pmt, rate = float(pmt), float(rate)
    _fnn(pmt)
    if n < 1:
        raise MathError("n must be at least 1")
    i = _monthly(rate)
    return pmt * n if i == 0 else pmt * ((1 + i) ** n - 1) / i * (1 + i)


@_f("sip_target", "Monthly SIP needed to reach a target (rate % per year, n months, deposits at the start of each month): sip_target(target, rate, n)", 3, "sip_target(12000, 0, 12) => 1000", exact=True)
def sip_target(target, rate, n):
    n = _whole(n, "n")
    target, rate = float(target), float(rate)
    _fnn(target)
    if n < 1:
        raise MathError("n must be at least 1")
    i = _monthly(rate)
    per_unit = n if i == 0 else ((1 + i) ** n - 1) / i * (1 + i)
    return target / per_unit


@_f("rule_of_72", "Approximate years to double at rate % per year, 72/rate: rule_of_72(rate)", 1, "rule_of_72(8) => 9")
def rule_of_72(rate):
    _fpos(rate)
    return 72 / rate


@_f("real_rate", "Inflation-adjusted (Fisher) rate in %, ((1+nominal)/(1+inflation) - 1) with both in %: real_rate(nominal, inflation)", 2, "real_rate(21, 10) => 10")
def real_rate(nominal, inflation):
    if nominal <= -100 or inflation <= -100:
        raise MathError("rates must be above -100%")
    return ((1 + nominal / 100) / (1 + inflation / 100) - 1) * 100


@_f("ear", "Effective annual rate in % for a nominal rate % compounded m times a year: ear(rate, m)", 2, "ear(12, 12) => 12.68250301", exact=True)
def ear(rate, m):
    m = _whole(m, "m")
    rate = float(rate)
    if m < 1 or rate <= -100 * m:
        raise MathError("need m >= 1 and a sensible rate")
    return ((1 + rate / (100 * m)) ** m - 1) * 100


@_f("inflation_adjust", "Purchasing power today of an amount after a number of years of inflation at rate %: inflation_adjust(amount, rate, years)", 3, "inflation_adjust(1100, 10, 1) => 1000")
def inflation_adjust(amount, rate, years):
    _fnn(amount, years)
    if rate <= -100:
        raise MathError("rate must be above -100%")
    return amount / (1 + rate / 100) ** years


# ---------- business ----------
@_f("break_even", "Break-even quantity fixed/(price - variable cost): break_even(fixed, price, var)", 3, "break_even(1000, 15, 10) => 200")
def break_even(fixed, price, var):
    _fnn(fixed, var)
    if price <= var:
        raise MathError("price must exceed the variable cost")
    return fixed / (price - var)


@_f("margin_pct", "Gross margin % = (price - cost)/price*100: margin_pct(cost, price)", 2, "margin_pct(80, 100) => 20")
def margin_pct(cost, price):
    _fnn(cost)
    _fpos(price)
    return (price - cost) / price * 100


@_f("markup_pct", "Markup % = (price - cost)/cost*100: markup_pct(cost, price)", 2, "markup_pct(80, 100) => 25")
def markup_pct(cost, price):
    _fpos(cost)
    _fnn(price)
    return (price - cost) / cost * 100


@_f("successive_discount", "Price after two successive discounts d1 % and d2 %: successive_discount(price, d1, d2)", 3, "successive_discount(1000, 10, 20) => 720")
def successive_discount(price, d1, d2):
    _fnn(price)
    for d in (d1, d2):
        if not 0 <= d <= 100:
            raise MathError("discounts must be between 0 and 100")
    return price * (1 - d1 / 100) * (1 - d2 / 100)


@_f("gst_split", "Half of the GST on a pre-tax amount (CGST or SGST): gst_split(amount, rate)", 2, "gst_split(1000, 18) => 90")
def gst_split(amount, rate):
    _fnn(amount, rate)
    return amount * rate / 200


@_f("vat_add", "Price including VAT, amount*(1 + rate/100): vat_add(amount, rate)", 2, "vat_add(100, 20) => 120")
def vat_add(amount, rate):
    _fnn(amount, rate)
    return amount * (1 + rate / 100)


@_f("vat_remove", "Pre-tax price from a price that includes VAT: vat_remove(amount, rate)", 2, "vat_remove(120, 20) => 100")
def vat_remove(amount, rate):
    _fnn(amount, rate)
    return amount / (1 + rate / 100)


@_f("dep_straight", "Straight-line depreciation per year (cost - salvage)/life: dep_straight(cost, salvage, life)", 3, "dep_straight(10000, 1000, 9) => 1000")
def dep_straight(cost, salvage, life):
    _fnn(salvage)
    _fpos(life)
    if salvage > cost:
        raise MathError("salvage cannot exceed the cost")
    return (cost - salvage) / life


@_f("dep_declining", "Declining-balance depreciation in a given year (rate % of the book value, year 1, 2, ...): dep_declining(cost, rate, year)", 3, "dep_declining(10000, 20, 2) => 1600", exact=True)
def dep_declining(cost, rate, year):
    year = _whole(year, "year")
    cost, rate = float(cost), float(rate)
    _fnn(cost)
    if year < 1 or not 0 < rate <= 100:
        raise MathError("need year >= 1 and 0 < rate <= 100")
    return cost * (1 - rate / 100) ** (year - 1) * rate / 100


@_f("dep_syd", "Sum-of-years'-digits depreciation in a given year (1..life): dep_syd(cost, salvage, life, year)", 4, "dep_syd(10000, 1000, 4, 1) => 3600", exact=True)
def dep_syd(cost, salvage, life, year):
    life, year = _whole(life, "life"), _whole(year, "year")
    cost, salvage = float(cost), float(salvage)
    _fnn(salvage)
    if life < 1 or not 1 <= year <= life or salvage > cost:
        raise MathError("need 1 <= year <= life and salvage <= cost")
    return (cost - salvage) * (life - year + 1) * 2 / (life * (life + 1))


@_f("bond_price", "Price of a bond with annual coupons: face value, coupon rate %, yield to maturity %, years: bond_price(face, coupon, ytm, n)", 4, "bond_price(1000, 5, 5, 10) => 1000", exact=True)
def bond_price(face, coupon, ytm, n):
    n = _whole(n, "n")
    face, coupon, ytm = float(face), float(coupon), float(ytm)
    _fnn(face, coupon)
    if n < 1 or ytm <= -100:
        raise MathError("need n >= 1 and a yield above -100%")
    y = ytm / 100
    c = face * coupon / 100
    return sum(c / (1 + y) ** t for t in range(1, n + 1)) + face / (1 + y) ** n


@_f("current_yield", "Current yield % = annual coupon / price * 100: current_yield(coupon, price)", 2, "current_yield(50, 1000) => 5")
def current_yield(coupon, price):
    _fnn(coupon)
    _fpos(price)
    return coupon / price * 100


@_f("dividend_yield", "Dividend yield % = dividend / price * 100: dividend_yield(div, price)", 2, "dividend_yield(2, 50) => 4")
def dividend_yield(div, price):
    _fnn(div)
    _fpos(price)
    return div / price * 100


@_f("pe_ratio", "Price/earnings ratio: pe_ratio(price, eps)", 2, "pe_ratio(150, 5) => 30")
def pe_ratio(price, eps):
    _fnn(price)
    _fpos(eps)
    return price / eps


@_f("roe", "Return on equity % = income / equity * 100: roe(income, equity)", 2, "roe(20, 100) => 20")
def roe(income, equity):
    _fpos(equity)
    return income / equity * 100


def _npv_dec(r, cfs):
    return sum(cf / (1 + r) ** t for t, cf in enumerate(cfs))


@register("irr", _FIN, "Internal rate of return in %, the lowest rate above -100% where the NPV is zero: irr(cf0, cf1, ...) or irr({cf0, cf1, ...})", (2, None), example="irr(-100, 110) => 10")
def irr(*cfs):
    if not (any(c > 0 for c in cfs) and any(c < 0 for c in cfs)):
        raise MathError("cash flows need both a deposit and a return")
    grid = [-0.99 + 0.005 * i for i in range(0, 2200)] + [10 * 1.02 ** i for i in range(0, 700)]
    prev_r, prev_v = grid[0], _npv_dec(grid[0], cfs)
    if prev_v == 0:
        return prev_r * 100
    for r in grid[1:]:
        v = _npv_dec(r, cfs)
        if v == 0:
            return r * 100
        if prev_v * v < 0:
            lo, hi, vlo = prev_r, r, prev_v
            for _ in range(200):
                mid = (lo + hi) / 2
                vm = _npv_dec(mid, cfs)
                if vlo * vm <= 0:
                    hi = mid
                else:
                    lo, vlo = mid, vm
            return (lo + hi) / 2 * 100
        prev_r, prev_v = r, v
    raise MathError("no internal rate of return found")


@register("payback", _FIN, "Payback period in periods, interpolated inside the period: payback(cf0, cf1, ...) or payback({cf0, cf1, ...})", (2, None), example="payback(-1000, 300, 400, 500) => 2.6")
def payback(*cfs):
    cum = cfs[0]
    if cum >= 0:
        return 0.0
    for t in range(1, len(cfs)):
        nxt = cum + cfs[t]
        if nxt >= 0:
            return t - 1 + (-cum) / cfs[t]
        cum = nxt
    raise MathError("the investment is never paid back")


@_f("annuity_due_fv", "Future value of an annuity due (payments at the start of each period), decimal rate per period (0.05 = 5%): annuity_due_fv(pmt, rate, n)", 3, "annuity_due_fv(100, 0, 5) => 500")
def annuity_due_fv(pmt, rate, n):
    _fnn(n)
    if rate <= -1:
        raise MathError("rate must be above -1")
    if rate == 0:
        return pmt * n
    return pmt * ((1 + rate) ** n - 1) / rate * (1 + rate)


@_f("perpetuity", "Present value of a perpetuity, pmt / rate (decimal rate, 0.05 = 5%): perpetuity(pmt, rate)", 2, "perpetuity(50, 0.05) => 1000")
def perpetuity(pmt, rate):
    _fpos(rate)
    return pmt / rate


@_f("growing_perpetuity", "Present value of a growing perpetuity, pmt / (rate - g) with decimal rates and rate > g: growing_perpetuity(pmt, rate, g)", 3, "growing_perpetuity(50, 0.08, 0.03) => 1000")
def growing_perpetuity(pmt, rate, g):
    if rate <= g:
        raise MathError("rate must exceed the growth rate")
    return pmt / (rate - g)


# ---------- everyday money ----------
@_f("fx_convert", "Currency conversion amount * rate (you supply the rate): fx_convert(amount, rate)", 2, "fx_convert(100, 83.5) => 8350")
def fx_convert(amount, rate):
    _fnn(amount)
    _fpos(rate)
    return amount * rate


@_f("split_bill", "Amount per person including a tip of tip_pct %: split_bill(total, people, tip_pct)", 3, "split_bill(1000, 4, 10) => 275")
def split_bill(total, people, tip_pct):
    _fnn(total, tip_pct)
    if people < 1 or people != int(people):
        raise MathError("people must be a whole number of at least 1")
    return total * (1 + tip_pct / 100) / people


@_f("mileage", "Fuel economy in km per litre: mileage(km, litres)", 2, "mileage(300, 20) => 15")
def mileage(km, litres):
    _fnn(km)
    _fpos(litres)
    return km / litres


@_f("trip_cost", "Fuel cost of a trip: distance km, mileage km/litre, price per litre: trip_cost(km, mileage, price)", 3, "trip_cost(300, 15, 100) => 2000")
def trip_cost(km, mileage, price):
    _fnn(km, price)
    _fpos(mileage)
    return km / mileage * price


@_f("electricity_bill", "Cost of running a device: kilowatts * hours * price per kWh: electricity_bill(kw, hours, rate)", 3, "electricity_bill(1.5, 4, 8) => 48")
def electricity_bill(kw, hours, rate):
    _fnn(kw, hours, rate)
    return kw * hours * rate


# ---------- calendar (proleptic Gregorian) ----------
def _leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


_DIM = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _dim(y, m):
    return 29 if m == 2 and _leap(y) else _DIM[m - 1]


def _date(y, m, d):
    y, m, d = _whole(y, "year"), _whole(m, "month"), _whole(d, "day")
    if abs(y) > 1000000 or not 1 <= m <= 12 or not 1 <= d <= _dim(y, m):
        raise MathError("not a valid date")
    return y, m, d


def _days(y, m, d):
    """Days since 1970-01-01 (negative before it)."""
    y, m, d = _date(y, m, d)
    if m <= 2:
        y -= 1
    era = y // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _cal(name, desc, args, example):
    return _f(name, desc, args, example, cat=_CAL, exact=True)


@_cal("days_between", "Days from the first date to the second (negative if earlier): days_between(y1, m1, d1, y2, m2, d2)", 6, "days_between(2000, 1, 1, 2000, 12, 31) => 365")
def days_between(y1, m1, d1, y2, m2, d2):
    return _days(y2, m2, d2) - _days(y1, m1, d1)


@_cal("weekday", "Day of the week, 0 = Monday ... 6 = Sunday: weekday(y, m, d)", 3, "weekday(2000, 1, 1) => 5")
def weekday(y, m, d):
    return (_days(y, m, d) + 3) % 7


@_cal("is_leap", "1 if the year is a leap year (proleptic Gregorian rule), else 0: is_leap(y)", 1, "is_leap(1900) => 0")
def is_leap(y):
    return int(_leap(_whole(y, "year")))


@_cal("days_in_month", "Number of days in a month: days_in_month(y, m)", 2, "days_in_month(2024, 2) => 29")
def days_in_month(y, m):
    y, m = _whole(y, "year"), _whole(m, "month")
    if not 1 <= m <= 12:
        raise MathError("month must be between 1 and 12")
    return _dim(y, m)


@_cal("day_of_year", "Day number in the year, 1 January = 1: day_of_year(y, m, d)", 3, "day_of_year(2024, 12, 31) => 366")
def day_of_year(y, m, d):
    return _days(y, m, d) - _days(y, 1, 1) + 1


def _p_year(y):
    return (y + y // 4 - y // 100 + y // 400) % 7


def _iso_weeks(y):
    return 53 if _p_year(y) == 4 or _p_year(y - 1) == 3 else 52


@_cal("week_number", "ISO 8601 week number (1..53); the week belongs to the year that holds its Thursday: week_number(y, m, d)", 3, "week_number(2021, 1, 3) => 53")
def week_number(y, m, d):
    y, m, d = _date(y, m, d)
    doy = day_of_year(y, m, d)
    wd = weekday(y, m, d) + 1                     # Monday = 1 ... Sunday = 7
    w = (doy - wd + 10) // 7
    if w < 1:
        return _iso_weeks(y - 1)
    if w > _iso_weeks(y):
        return 1
    return w


@_cal("age_years", "Age in whole years on a date; a 29 February birthday counts from 1 March in other years: age_years(y, m, d, ty, tm, td)", 6, "age_years(2000, 2, 29, 2023, 2, 28) => 22")
def age_years(y, m, d, ty, tm, td):
    y, m, d = _date(y, m, d)
    ty, tm, td = _date(ty, tm, td)
    if _days(ty, tm, td) < _days(y, m, d):
        raise MathError("the target date is before the birth date")
    years = ty - y
    if (tm, td) < (m, d):
        years -= 1
    return years


@_cal("julian_day", "Julian Day Number of the civil date (the integer JD at noon; 2000-01-01 = 2451545): julian_day(y, m, d)", 3, "julian_day(2000, 1, 1) => 2451545")
def julian_day(y, m, d):
    return _days(y, m, d) + 2440588


@_cal("unix_time", "Seconds since 1970-01-01 00:00:00 UTC (leap seconds ignored): unix_time(y, m, d, h, mi, s)", 6, "unix_time(2000, 1, 1, 0, 0, 0) => 946684800")
def unix_time(y, m, d, h, mi, s):
    days = _days(y, m, d)
    h, mi = _whole(h, "hour"), _whole(mi, "minute")
    if not (0 <= h <= 23 and 0 <= mi <= 59 and 0 <= s < 60):
        raise MathError("not a valid time of day")
    return days * 86400 + h * 3600 + mi * 60 + s


# ---------- trigonometry in a fixed unit ----------
def _clean(v):
    return 0.0 if abs(v) < 1e-15 else ar_snap(v)


def _t(name, desc, example):
    return register(name, _TRG, desc, 1, example=example)


@_t("sin_deg", "Sine of an angle in degrees, whatever the angle mode: sin_deg(x)", "sin_deg(30) => 0.5")
def sin_deg(x):
    return _clean(math.sin(math.radians(x % 360)))


@_t("cos_deg", "Cosine of an angle in degrees: cos_deg(x)", "cos_deg(60) => 0.5")
def cos_deg(x):
    return _clean(math.cos(math.radians(x % 360)))


@_t("tan_deg", "Tangent of an angle in degrees: tan_deg(x)", "tan_deg(45) => 1")
def tan_deg(x):
    if x % 180 == 90:
        raise MathError("tangent is undefined here")
    return _clean(math.tan(math.radians(x % 360)))


@_t("cot_deg", "Cotangent of an angle in degrees: cot_deg(x)", "cot_deg(45) => 1")
def cot_deg(x):
    if x % 180 == 0:
        raise MathError("cotangent is undefined here")
    return _clean(1 / math.tan(math.radians(x % 360)))


@_t("sec_deg", "Secant of an angle in degrees: sec_deg(x)", "sec_deg(60) => 2")
def sec_deg(x):
    if x % 180 == 90:
        raise MathError("secant is undefined here")
    return _clean(1 / math.cos(math.radians(x % 360)))


@_t("csc_deg", "Cosecant of an angle in degrees: csc_deg(x)", "csc_deg(30) => 2")
def csc_deg(x):
    if x % 180 == 0:
        raise MathError("cosecant is undefined here")
    return _clean(1 / math.sin(math.radians(x % 360)))


@_t("asin_deg", "Inverse sine in degrees (-90..90): asin_deg(x)", "asin_deg(0.5) => 30")
def asin_deg(x):
    return _clean(math.degrees(math.asin(x)))


@_t("acos_deg", "Inverse cosine in degrees (0..180): acos_deg(x)", "acos_deg(0.5) => 60")
def acos_deg(x):
    return _clean(math.degrees(math.acos(x)))


@_t("atan_deg", "Inverse tangent in degrees (-90..90): atan_deg(x)", "atan_deg(1) => 45")
def atan_deg(x):
    return _clean(math.degrees(math.atan(x)))


@_t("sin_rad", "Sine of an angle in radians, whatever the angle mode: sin_rad(x)", "sin_rad(pi/6) => 0.5")
def sin_rad(x):
    return _clean(math.sin(x))


@_t("cos_rad", "Cosine of an angle in radians: cos_rad(x)", "cos_rad(pi/3) => 0.5")
def cos_rad(x):
    return _clean(math.cos(x))


@_t("tan_rad", "Tangent of an angle in radians: tan_rad(x)", "tan_rad(pi/4) => 1")
def tan_rad(x):
    if abs(math.cos(x)) < 1e-12:
        raise MathError("tangent is undefined here")
    return _clean(math.tan(x))


@register("angle_norm360", _TRG, "Angle in degrees wrapped to 0 <= a < 360: angle_norm360(x)", 1, example="angle_norm360(-30) => 330")
def angle_norm360(x):
    r = x % 360
    return 0.0 if r >= 360 else r


@register("angle_norm180", _TRG, "Angle in degrees wrapped to -180 < a <= 180: angle_norm180(x)", 1, example="angle_norm180(270) => -90")
def angle_norm180(x):
    r = x % 360
    r = 0.0 if r >= 360 else r
    return r - 360 if r > 180 else r


@register("angle_diff", _TRG, "Smallest signed difference a - b in degrees, in (-180, 180]: angle_diff(a, b)", 2, example="angle_diff(10, 350) => 20")
def angle_diff(a, b):
    r = (a - b) % 360
    r = 0.0 if r >= 360 else r
    return r - 360 if r > 180 else r


# ---------- navigation on a sphere (R = 6371 km) ----------
_R_EARTH_KM = 6371.0


def _ll(lat, lon):
    if not -90 <= lat <= 90:
        raise MathError("latitude must be between -90 and 90")
    if math.isinf(lon) or math.isnan(lon):
        raise MathError("longitude must be finite")
    return math.radians(lat), math.radians(lon)


def _wrap_lon(deg):
    r = deg % 360
    r = 0.0 if r >= 360 else r
    return r - 360 if r > 180 else r


def _n(name, desc, args, example):
    return register(name, _CAT_DAILY, desc, args, example=example)


@_n("bearing", "Initial compass bearing (0..360, clockwise from north) from point 1 to point 2: bearing(lat1, lon1, lat2, lon2)", 4, "bearing(0, 0, 0, 90) => 90")
def bearing(lat1, lon1, lat2, lon2):
    p1, l1 = _ll(lat1, lon1)
    p2, l2 = _ll(lat2, lon2)
    y = math.sin(l2 - l1) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(l2 - l1)
    if abs(x) < 1e-15 and abs(y) < 1e-15:
        raise MathError("the bearing is undefined for these points")
    return _clean(math.degrees(math.atan2(y, x)) % 360) % 360


def _dest(lat, lon, brg, dist):
    if dist < 0 or math.isinf(dist):
        raise MathError("distance must not be negative")
    p1, l1 = _ll(lat, lon)
    th = math.radians(brg)
    dl = dist / _R_EARTH_KM
    p2 = math.asin(max(-1.0, min(1.0, math.sin(p1) * math.cos(dl) + math.cos(p1) * math.sin(dl) * math.cos(th))))
    l2 = l1 + math.atan2(math.sin(th) * math.sin(dl) * math.cos(p1), math.cos(dl) - math.sin(p1) * math.sin(p2))
    return math.degrees(p2), _wrap_lon(math.degrees(l2))


@_n("dest_lat", "Latitude reached from a start point, a bearing in degrees and a distance in km: dest_lat(lat, lon, bearing, dist)", 4, "dest_lat(0, 0, 0, 6371*pi/180) => 1")
def dest_lat(lat, lon, brg, dist):
    return _clean(_dest(lat, lon, brg, dist)[0])


@_n("dest_lon", "Longitude reached from a start point, a bearing in degrees and a distance in km: dest_lon(lat, lon, bearing, dist)", 4, "dest_lon(0, 0, 90, 6371*pi/180) => 1")
def dest_lon(lat, lon, brg, dist):
    return _clean(_dest(lat, lon, brg, dist)[1])


def _mid(lat1, lon1, lat2, lon2):
    p1, l1 = _ll(lat1, lon1)
    p2, l2 = _ll(lat2, lon2)
    bx = math.cos(p2) * math.cos(l2 - l1)
    by = math.cos(p2) * math.sin(l2 - l1)
    den = math.hypot(math.cos(p1) + bx, by)
    num = math.sin(p1) + math.sin(p2)
    if den < 1e-12 and abs(num) < 1e-12:
        raise MathError("the midpoint of antipodal points is undefined")
    pm = math.atan2(num, den)
    lm = l1 + math.atan2(by, math.cos(p1) + bx)
    return math.degrees(pm), _wrap_lon(math.degrees(lm))


@_n("midpoint_lat", "Latitude of the great-circle midpoint of two points: midpoint_lat(lat1, lon1, lat2, lon2)", 4, "midpoint_lat(0, 0, 90, 0) => 45")
def midpoint_lat(lat1, lon1, lat2, lon2):
    return _clean(_mid(lat1, lon1, lat2, lon2)[0])


@_n("midpoint_lon", "Longitude of the great-circle midpoint of two points: midpoint_lon(lat1, lon1, lat2, lon2)", 4, "midpoint_lon(0, 0, 0, 90) => 45")
def midpoint_lon(lat1, lon1, lat2, lon2):
    return _clean(_mid(lat1, lon1, lat2, lon2)[1])
