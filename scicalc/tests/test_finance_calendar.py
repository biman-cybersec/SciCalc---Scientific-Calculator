"""Checks: finance calendar.  Run alone with  python run_tests.py finance_calendar"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "finance_calendar"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_finance_calendar_24(check, ev, near, ex, fn, nearr):
    """Sprint 7: finance, calendar, trig and navigation"""
    # ================= Sprint 7: finance, calendar, trig and navigation =================
    import datetime as _dt
    # --- loans: month-by-month simulation
    def _sim(P, rate, n, k):
        r = rate / 1200.0
        pmt = P / n if r == 0 else P * r / (1 - (1 + r) ** -n)
        b = P
        for _ in range(k):
            b = b * (1 + r) - pmt
        return pmt, b
    for P, rate, n, k in [(100000, 12, 120, 30), (5000, 7.5, 36, 12), (250000, 3.2, 360, 100), (900, 0, 9, 4)]:
        pmt, b = _sim(P, rate, n, k)
        near(f"loan_balance simulation {P},{rate},{n},{k}", f"loan_balance({P},{rate},{n},{k})", b, 1e-8)
        near(f"loan_total_interest simulation {P},{rate},{n}", f"loan_total_interest({P},{rate},{n})", pmt * n - P, 1e-8)
    near("loan_balance at the start", "loan_balance(5000,7.5,36,0)", 5000, 1e-12)
    near("loan_balance at the end", "loan_balance(5000,7.5,36,36)", 0, 1e-9)
    near("loan_term inverts emi", "loan_term(100000, 12, emi(100000,12,120))", 120, 1e-9)
    near("loan_term hand value", "loan_term(1000,12,100)", math.log(100 / (100 - 10)) / math.log(1.01), 1e-12)
    # --- SIP
    def _sipsim(pmt, rate, n):
        i = rate / 1200.0
        b = 0.0
        for _ in range(n):
            b = (b + pmt) * (1 + i)
        return b
    near("sip_fv simulation", "sip_fv(5000,12,60)", _sipsim(5000, 12, 60), 1e-9)
    near("sip_fv simulation 2", "sip_fv(250,6.5,120)", _sipsim(250, 6.5, 120), 1e-9)
    near("sip_target inverts sip_fv", "sip_fv(sip_target(1000000,10,180),10,180)", 1000000, 1e-9)
    near("rule_of_72 hand", "rule_of_72(6)", 12, 1e-12)
    near("real_rate zero inflation", "real_rate(5,0)", 5, 1e-12)
    near("real_rate hand", "real_rate(8,3)", (1.08 / 1.03 - 1) * 100, 1e-12)
    near("ear annual", "ear(5,1)", 5, 1e-12)
    near("ear continuous limit", "ear(10,1000000)", (math.e ** 0.1 - 1) * 100, 1e-6)
    near("inflation_adjust two years", "inflation_adjust(1000,5,2)", 1000 / 1.05 ** 2, 1e-12)
    # --- business
    near("break_even covers fixed cost", "break_even(5000,25,15)*(25-15)", 5000, 1e-12)
    near("margin and markup relation", "margin_pct(60,100)", 40, 1e-12)
    near("markup 60 to 100", "markup_pct(60,100)", 66.66666666666667, 1e-12)
    near("successive 10 then 20 equals reversed", "successive_discount(500,20,10)", ev("successive_discount(500,10,20)"), 1e-12)
    near("successive equals two discount steps", "successive_discount(800,15,5)", 800 * 0.85 * 0.95, 1e-12)
    near("gst_split twice gives gst", "2*gst_split(1000,18)", 180, 1e-12)
    near("vat_remove inverts vat_add", "vat_remove(vat_add(250,18),18)", 250, 1e-12)
    near("vat_add 5 percent", "vat_add(200,5)", 210, 1e-12)
    # depreciation: schedules sum correctly
    near("dep_straight hand", "dep_straight(50000,5000,5)", 9000, 1e-12)
    bal = 10000.0
    tot = 0.0
    for yr in range(1, 6):
        d = bal * 0.3
        near(f"dep_declining year {yr}", f"dep_declining(10000,30,{yr})", d, 1e-12)
        bal -= d
        tot += d
    near("dep_declining book value", "10000-dep_declining(10000,30,1)-dep_declining(10000,30,2)-dep_declining(10000,30,3)-dep_declining(10000,30,4)-dep_declining(10000,30,5)", bal, 1e-9)
    near("dep_syd schedule sums to depreciable amount", "dep_syd(12000,2000,5,1)+dep_syd(12000,2000,5,2)+dep_syd(12000,2000,5,3)+dep_syd(12000,2000,5,4)+dep_syd(12000,2000,5,5)", 10000, 1e-12)
    near("dep_syd last year", "dep_syd(12000,2000,5,5)", 10000 / 15, 1e-12)
    # bonds
    near("bond_price par", "bond_price(1000,6,6,7)", 1000, 1e-9)
    near("bond_price discount when yield higher", "bond_price(1000,5,6,3)", 50 / 1.06 + 50 / 1.06 ** 2 + 1050 / 1.06 ** 3, 1e-12)
    check("bond_price premium above face when yield lower", ev("bond_price(1000,8,5,5)") > 1000, True)
    near("bond_price zero coupon", "bond_price(1000,0,5,2)", 1000 / 1.05 ** 2, 1e-12)
    near("current_yield hand", "current_yield(80,950)", 80 / 950 * 100, 1e-12)
    near("dividend_yield hand", "dividend_yield(1.5,60)", 2.5, 1e-12)
    near("pe_ratio hand", "pe_ratio(100,4)", 25, 1e-12)
    near("roe negative income", "roe(-5,50)", -10, 1e-12)
    # irr: root of npv, plus known value
    for cfs in [(-1000, 300, 400, 500), (-500, 100, 200, 300, 400), (100, -60, -60), (-100, 0, 0, 133.1)]:
        a = ",".join(str(c) for c in cfs)
        r = ev(f"irr({a})")
        npv_at = sum(c / (1 + r / 100) ** t for t, c in enumerate(cfs))
        check(f"irr is a root of npv {cfs}", abs(npv_at) < 1e-6, True)
    near("irr hand value 10 percent", "irr(-100,0,0,133.1)", 10, 1e-9)
    near("irr agrees with npv function", "npv(irr(-1000,300,400,500),-1000,300,400,500)", 0, 1e-6)
    near("payback exact year", "payback(-100,50,50)", 2, 1e-12)
    near("payback instant", "payback(10,5)", 0, 1e-12)
    near("payback interpolation", "payback(-1000,100,200,900)", 2 + 700 / 900, 1e-12)
    near("annuity_due_fv is one period past ordinary", "annuity_due_fv(100,0.05,10)", ev("annuity_fv(100,0.05,10)") * 1.05, 1e-9)
    near("perpetuity hand", "perpetuity(120,0.06)", 2000, 1e-12)
    near("growing_perpetuity zero growth is perpetuity", "growing_perpetuity(100,0.05,0)", ev("perpetuity(100,0.05)"), 1e-12)
    near("fx_convert hand", "fx_convert(250,0.5)", 125, 1e-12)
    near("split_bill no tip", "split_bill(90,3,0)", 30, 1e-12)
    near("mileage hand", "mileage(450,30)", 15, 1e-12)
    near("trip_cost consistent with mileage", "trip_cost(450,mileage(450,30),90)", 30 * 90, 1e-12)
    near("electricity_bill hand", "electricity_bill(2,3,7.5)", 45, 1e-12)
    # --- calendar versus the datetime module
    import random as _rnd
    rg = _rnd.Random(7)
    base = _dt.date(1970, 1, 1)
    bad = {"w": 0, "wk": 0, "doy": 0, "jd": 0, "diff": 0, "dim": 0, "unix": 0}
    pairs = [_dt.date.fromordinal(rg.randint(_dt.date(1850, 1, 1).toordinal(), _dt.date(2150, 12, 31).toordinal())) for _ in range(1500)]
    pairs += [_dt.date(y, 12, d) for y in range(1998, 2032) for d in (28, 29, 30, 31)] + [_dt.date(y, 1, d) for y in range(1998, 2032) for d in (1, 2, 3, 4)]
    f_weekday, f_week, f_doy, f_jd = fn("weekday"), fn("week_number"), fn("day_of_year"), fn("julian_day")
    f_db, f_dim, f_unix = fn("days_between"), fn("days_in_month"), fn("unix_time")
    for d in pairs:
        if f_weekday(d.year, d.month, d.day) != d.weekday():
            bad["w"] += 1
        if f_week(d.year, d.month, d.day) != d.isocalendar()[1]:
            bad["wk"] += 1
        if f_doy(d.year, d.month, d.day) != d.timetuple().tm_yday:
            bad["doy"] += 1
        if f_jd(d.year, d.month, d.day) != d.toordinal() + 1721425:
            bad["jd"] += 1
        if f_db(1970, 1, 1, d.year, d.month, d.day) != (d - base).days:
            bad["diff"] += 1
        if f_dim(d.year, d.month) != ((_dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)) - _dt.date(d.year, d.month, 1)).days:
            bad["dim"] += 1
        if f_unix(d.year, d.month, d.day, 13, 45, 7) != int(_dt.datetime(d.year, d.month, d.day, 13, 45, 7, tzinfo=_dt.timezone.utc).timestamp()):
            bad["unix"] += 1
    for k, v in bad.items():
        check(f"calendar {k} matches datetime over {len(pairs)} dates", v, 0)
    for y, want in [(1600, 1), (1700, 0), (1900, 0), (2000, 1), (2024, 1), (2023, 0), (2100, 0), (2400, 1), (4, 1), (0, 1), (-4, 1)]:
        ex(f"is_leap({y})", f"is_leap({y})", want)
    ex("days_between 1900 not leap", "days_between(1900,2,28,1900,3,1)", 1)
    ex("days_between 2000 leap", "days_between(2000,2,28,2000,3,1)", 2)
    ex("days_between negative", "days_between(2000,1,2,2000,1,1)", -1)
    ex("days_between over a century", "days_between(1900,1,1,2000,1,1)", 36524)
    ex("days_between 400-year cycle", "days_between(2000,1,1,2400,1,1)", 146097)
    ex("days_in_month Feb 1900", "days_in_month(1900,2)", 28)
    ex("days_in_month Feb 2000", "days_in_month(2000,2)", 29)
    ex("days_in_month Apr", "days_in_month(2023,4)", 30)
    ex("day_of_year 1 March leap", "day_of_year(2024,3,1)", 61)
    ex("day_of_year 1 March common", "day_of_year(2023,3,1)", 60)
    ex("weekday 1970-01-01 Thursday", "weekday(1970,1,1)", 3)
    ex("weekday 1900-01-01 Monday", "weekday(1900,1,1)", 0)
    ex("weekday 2024-02-29 Thursday", "weekday(2024,2,29)", 3)
    ex("week_number 2021-01-03", "week_number(2021,1,3)", 53)
    ex("week_number 2020-12-31", "week_number(2020,12,31)", 53)
    ex("week_number 2018-12-31 is week 1", "week_number(2018,12,31)", 1)
    ex("week_number 2016-01-01 is week 53", "week_number(2016,1,1)", 53)
    ex("julian_day 1970", "julian_day(1970,1,1)", 2440588)
    ex("julian_day modified JD epoch", "julian_day(1858,11,17)", 2400001)
    ex("unix_time 2038", "unix_time(2038,1,19,3,14,7)", 2147483647)
    ex("unix_time before 1970", "unix_time(1969,12,31,23,59,59)", -1)
    ex("age_years birthday not yet", "age_years(1990,6,15,2020,6,14)", 29)
    ex("age_years birthday today", "age_years(1990,6,15,2020,6,15)", 30)
    ex("age_years leap day birth, 1 Mar", "age_years(2000,2,29,2023,3,1)", 23)
    ex("age_years leap day birth, leap year", "age_years(2000,2,29,2024,2,29)", 24)
    ex("age_years same day", "age_years(2000,5,5,2000,5,5)", 0)
    # --- trigonometry in fixed units
    for a in (-720, -135, -90, -30, 0, 30, 45, 60, 90, 120, 180, 270, 360, 390, 1000):
        near(f"sin_deg({a})", f"sin_deg({a})", math.sin(math.radians(a)), 1e-12)
        near(f"cos_deg({a})", f"cos_deg({a})", math.cos(math.radians(a)), 1e-12)
    for a in (-135, -60, -45, 0, 30, 60, 100, 225, 1000):
        near(f"tan_deg({a})", f"tan_deg({a})", math.tan(math.radians(a)), 1e-11)
    for a in (-135, -60, -45, 30, 60, 100, 225, 1000):
        near(f"cot_deg({a})", f"cot_deg({a})", 1 / math.tan(math.radians(a)), 1e-11)
    for a in (-135, -60, 0, 30, 60, 100, 225, 1000):
        near(f"sec_deg({a})", f"sec_deg({a})", 1 / math.cos(math.radians(a)), 1e-11)
    for a in (-135, -60, 30, 60, 100, 225, 1000):
        near(f"csc_deg({a})", f"csc_deg({a})", 1 / math.sin(math.radians(a)), 1e-11)
    for v in (-1, -0.5, 0, 0.3, 1):
        near(f"asin_deg({v})", f"asin_deg({v})", math.degrees(math.asin(v)), 1e-12)
        near(f"acos_deg({v})", f"acos_deg({v})", math.degrees(math.acos(v)), 1e-12)
    for v in (-100, -1, 0, 0.5, 3):
        near(f"atan_deg({v})", f"atan_deg({v})", math.degrees(math.atan(v)), 1e-12)
    ex("sin_deg(180) is exactly 0", "sin_deg(180)", 0)
    ex("cos_deg(90) is exactly 0", "cos_deg(90)", 0)
    ex("sin_deg(30) is exactly 0.5", "sin_deg(30)", 0.5)
    for a in (-2, -0.7, 0, 0.5, 1, 2.5, 7):
        near(f"sin_rad({a})", f"sin_rad({a})", math.sin(a), 1e-12)
        near(f"cos_rad({a})", f"cos_rad({a})", math.cos(a), 1e-12)
    for a in (-2, -0.7, 0, 0.5, 1, 2.5, 7):
        near(f"tan_rad({a})", f"tan_rad({a})", math.tan(a), 1e-11)
    cdeg = Calculator()
    cdeg.angle = "RAD" if hasattr(cdeg, "angle") else cdeg.angle
    nearr("sin_deg ignores the RAD angle mode", "sin_deg(30)", 0.5)
    nearr("sin_rad ignores the RAD angle mode", "sin_rad(pi/6)", 0.5)
    d_ = Calculator()
    d_.angle = "DEG"
    check("sin_rad ignores the DEG angle mode", abs(float(d_.evaluate("sin_rad(pi/6)").value) - 0.5) < 1e-9, True)
    for a, w360, w180 in [(-30, 330, -30), (0, 0, 0), (360, 0, 0), (720.5, 0.5, 0.5), (180, 180, 180), (-180, 180, 180), (181, 181, -179), (540, 180, 180), (-370, 350, -10)]:
        near(f"angle_norm360({a})", f"angle_norm360({a})", w360, 1e-12)
        near(f"angle_norm180({a})", f"angle_norm180({a})", w180, 1e-12)
    for a, b, w in [(10, 350, 20), (350, 10, -20), (0, 180, 180), (90, 0, 90), (0, 90, -90), (-170, 170, 20), (45, 45, 0)]:
        near(f"angle_diff({a},{b})", f"angle_diff({a},{b})", w, 1e-12)
    # --- navigation versus 3-D vector arithmetic
    def _vec(lat, lon):
        p, l = math.radians(lat), math.radians(lon)
        return (math.cos(p) * math.cos(l), math.cos(p) * math.sin(l), math.sin(p))
    def _ang(u, v):
        c = sum(a * b for a, b in zip(u, v))
        cr = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        return math.atan2(math.sqrt(sum(a * a for a in cr)), c)
    cities = [(51.5074, -0.1278), (40.7128, -74.006), (35.6762, 139.6503), (-33.8688, 151.2093), (-22.9068, -43.1729), (28.6139, 77.209), (64.1466, -21.9426), (1.3521, 103.8198)]
    for i in range(len(cities)):
        for j in range(len(cities)):
            if i == j:
                continue
            (la1, lo1), (la2, lo2) = cities[i], cities[j]
            u, v = _vec(la1, lo1), _vec(la2, lo2)
            dist = 6371.0 * _ang(u, v)
            # bearing via local east/north tangent basis
            east = (-math.sin(math.radians(lo1)), math.cos(math.radians(lo1)), 0.0)
            p1 = math.radians(la1)
            north = (-math.sin(p1) * math.cos(math.radians(lo1)), -math.sin(p1) * math.sin(math.radians(lo1)), math.cos(p1))
            be = sum(a * b for a, b in zip(v, east))
            bn = sum(a * b for a, b in zip(v, north))
            want = math.degrees(math.atan2(be, bn)) % 360
            near(f"bearing {i}->{j}", f"bearing({la1},{lo1},{la2},{lo2})", want, 1e-9)
            b_ = ev(f"bearing({la1},{lo1},{la2},{lo2})")
            dlat = ev(f"dest_lat({la1},{lo1},{b_},{dist})")
            dlon = ev(f"dest_lon({la1},{lo1},{b_},{dist})")
            dl = (dlon - lo2 + 180) % 360 - 180
            check(f"destination round trip {i}->{j}", abs(dlat - la2) < 1e-6 and abs(dl) < 1e-6, True)
            mla, mlo = ev(f"midpoint_lat({la1},{lo1},{la2},{lo2})"), ev(f"midpoint_lon({la1},{lo1},{la2},{lo2})")
            m = _vec(mla, mlo)
            check(f"midpoint equidistant {i}->{j}", abs(_ang(u, m) - _ang(m, v)) < 1e-9 and abs(_ang(u, m) * 2 - _ang(u, v)) < 1e-9, True)
            near(f"haversine of midpoint half {i}->{j}", f"haversine_dist({la1},{lo1},midpoint_lat({la1},{lo1},{la2},{lo2}),midpoint_lon({la1},{lo1},{la2},{lo2}))*2", dist, 1e-7)
    ex("bearing due north", "bearing(0,0,10,0)", 0)
    ex("bearing due south", "bearing(0,0,-10,0)", 180)
    ex("bearing due west", "bearing(0,0,0,-90)", 270)
    near("dest due north 10 degrees", "dest_lat(0,0,0,6371*pi/18)", 10, 1e-9)
    near("dest over the date line", "dest_lon(0,179,90,6371*pi/180*2)", -179, 1e-9)
    near("dest over the pole", "dest_lat(80,0,0,6371*pi/180*20)", 80, 1e-9)
    near("dest zero distance lon", "dest_lon(45,30,123,0)", 30, 1e-12)
    near("midpoint across date line", "midpoint_lon(0,170,0,-170)", 180, 1e-9)
    near("midpoint of equal points lat", "midpoint_lat(33,44,33,44)", 33, 1e-9)
    near("midpoint of equal points lon", "midpoint_lon(33,44,33,44)", 44, 1e-9)
