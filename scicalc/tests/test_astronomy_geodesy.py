"""Checks: astronomy geodesy.  Run alone with  python run_tests.py astronomy_geodesy"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "astronomy_geodesy"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def checks_astronomy_geodesy_35(check, ev, near, ex):
    """Phase 3: more astronomy and geodesy"""
    # ================= Phase 3: more astronomy and geodesy =================
    near("JD of the J2000 epoch from Unix time", "julian_date_from_unix(946728000)", 2451545.0)
    near("JD of the Unix epoch", "julian_date_from_unix(0)", 2440587.5)
    near("JD agrees with the calendar function", "julian_date_from_unix(1700000000)", 2440587.5 + 1700000000 / 86400)
    near("unix round trip", "unix_from_julian_date(julian_date_from_unix(1234567890))", 1234567890, 1e-12)
    near("sidereal time at J2000 noon", "sidereal_time(2451545)", 18 + 41 / 60 + 50.55 / 3600, 1e-6)
    for jd in (2451545.0, 2459000.25, 2460000.8, 2444239.5):
        near(f"GMST {jd} against Meeus' degree form", f"sidereal_time({jd})", ((280.46061837 + 360.98564736629 * (jd - 2451545.0)) % 360) / 15, 1e-8)
    near("local sidereal time is GMST plus longitude/15", "local_sidereal_time(2451545,15)", (18.697374558 + 1) % 24, 1e-9)
    near("local sidereal time wraps", "local_sidereal_time(2451545,-100)", (18.697374558 - 100 / 15) % 24, 1e-9)
    near("declination at the June solstice", "solar_declination(172)", 23.44, 1e-2)
    near("declination at the December solstice", "solar_declination(355)", -23.44, 1e-2)
    near("declination at the equinox is near 0", "solar_declination(80)", 0, 0.5)
    for n in range(1, 366, 7):                    # Cooper's simple sine, a different (rougher) formula
        check(f"declination day {n} within 1.5 degrees of Cooper's sine", abs(ev(f"solar_declination({n})") - 23.45 * math.sin(2 * math.pi * (284 + n) / 365)) < 1.5, True)
    # compare with Spencer's Fourier series for the declination (a different formula)
    def spencer(n):
        g = 2 * math.pi * (n - 1) / 365
        return math.degrees(0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
                            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
    for n in (1, 45, 80, 172, 266, 355):
        check(f"declination day {n} equals Spencer's series", abs(ev(f"solar_declination({n})") - spencer(n)) < 1e-9, True)
    near("day length at the equator", "day_length_hours(0,172)", 12)
    near("equinox day length", "day_length_hours(51.5,80)", 12, 0.02)
    near("sunrise hour angle at the equator", "sunrise_hour_angle(0,20)", 6)
    near("hour angle by direct cosine", "sunrise_hour_angle(51.5,23.44)", math.degrees(math.acos(-math.tan(math.radians(51.5)) * math.tan(math.radians(23.44)))) / 15)
    near("day length is twice the hour angle", "day_length_hours(51.5,172)", 2 * ev("sunrise_hour_angle(51.5,solar_declination(172))"))
    check("summer plus winter day lengths add to 24", abs(ev("day_length_hours(51.5,172)+day_length_hours(51.5,355)") - 24) < 0.02, True)
    ra = Calculator(); ra.set_angle("rad")
    check("sunrise in rad mode", abs(float(ra.evaluate("sunrise_hour_angle(0.9,0.4)").value) - math.degrees(math.acos(-math.tan(0.9) * math.tan(0.4))) / 15) < 1e-9, True)
    # rhumb lines against the closed forms
    near("rhumb along the equator", "rhumb_distance(0,0,0,90)", 6371 * math.pi / 2)
    near("rhumb along a meridian", "rhumb_distance(10,20,50,20)", 6371 * math.radians(40))
    near("rhumb along a parallel", "rhumb_distance(60,0,60,10)", 6371 * math.cos(math.radians(60)) * math.radians(10), 1e-9)
    check("rhumb at least the great circle", ev("rhumb_distance(40,-74,51.5,0)") >= ev("haversine_dist(40,-74,51.5,0)") - 1e-9, True)
    # distance = R |dphi| / cos(bearing) for a non-east-west line
    for args in [(10, 0, 50, 30), (-20, 100, 30, 120), (45, -10, 20, -40)]:
        brg = math.radians(ev("rhumb_bearing(%s,%s,%s,%s)" % args))
        near(f"rhumb distance from bearing {args}", "rhumb_distance(%s,%s,%s,%s)" % args, 6371 * abs(math.radians(args[2] - args[0])) / abs(math.cos(brg)), 1e-9)
    near("rhumb due east", "rhumb_bearing(30,0,30,50)", 90)
    near("rhumb due north", "rhumb_bearing(0,10,40,10)", 0)
    near("rhumb due south", "rhumb_bearing(40,10,0,10)", 180)
    near("rhumb due west", "rhumb_bearing(30,50,30,0)", 270)
    near("rhumb takes the short way over the date line", "rhumb_bearing(0,170,0,-170)", 90)
    ex("utm zone London", "utm_zone(-0.1)", 30)
    ex("utm zone Greenwich east", "utm_zone(0.1)", 31)
    ex("utm zone at the date line", "utm_zone(-180)", 1)
    ex("utm zone 180", "utm_zone(180)", 1)
    ex("utm zone New York", "utm_zone(-74)", 18)
    ex("utm zone Tokyo", "utm_zone(139.7)", 54)
    ex("utm band London", "utm_band(51.5)", "U")
    ex("utm band equator north", "utm_band(0)", "N")
    ex("utm band equator south", "utm_band(-0.1)", "M")
    ex("utm band -80", "utm_band(-80)", "C")
    ex("utm band 84", "utm_band(84)", "X")
    ex("utm band 75", "utm_band(75)", "X")
    near("magnitude to flux", "magnitude_to_flux(5)", 0.01)
    near("flux round trip", "flux_to_magnitude(magnitude_to_flux(3.7))", 3.7)
    near("5 magnitudes is a factor of 100", "mag_diff_ratio(1,6)", 100)
    near("ratio from flux", "mag_diff_ratio(2,7.5)", ev("magnitude_to_flux(2)/magnitude_to_flux(7.5)"))
    near("absolute magnitude at 10 pc", "absolute_magnitude(4.83,10)", 4.83)
    near("the Sun's absolute magnitude from 1 AU", "absolute_magnitude(-26.74,1/206264.806)", 4.83, 2e-3)
    near("distance modulus round trip", "distance_from_modulus(absolute_magnitude(8,250)+0,absolute_magnitude(8,250))*0+distance_from_modulus(8,absolute_magnitude(8,250))", 250, 1e-9)
    near("distance from modulus", "distance_from_modulus(15,0)", 10000)
    near("airmass at the zenith", "airmass(90)", 1, 1e-3)
    near("airmass at 30 degrees is about 2", "airmass(30)", 2, 1e-2)
    near("airmass at the horizon is about 38", "airmass(0)", 38, 5e-2)
    near("airmass is about 1/sin(h) well above the horizon", "airmass(60)", 1 / math.sin(math.radians(60)), 1e-3)
    near("Moon's angular size", "angular_size_arcsec(3474,384400)", math.degrees(2 * math.atan(1737 / 384400)) * 3600)
    near("small-angle form", "angular_size_arcsec(1,1e6)", 206264.806 / 1e6, 1e-6)
    near("horizon distance", "horizon_distance_km(100)", math.sqrt(2 * 6371 * 0.1 + 0.1 ** 2))
    near("horizon rule of thumb 3.57 sqrt(h)", "horizon_distance_km(100)", 3.57 * 10, 5e-3)
    near("meridian radius at the equator", "meridian_radius(0)", 6335439.327, 1e-9)
    near("meridian radius at the pole", "meridian_radius(90)", 6399593.626, 1e-9)
    near("prime vertical radius at the equator", "prime_vertical_radius(0)", 6378137)
    near("prime vertical radius at the pole", "prime_vertical_radius(90)", 6399593.626, 1e-9)
    near("degree of latitude by integrating", "degree_length_lat_km(45)", math.radians(1) * 6367.4491, 1e-3)
    near("degree of latitude at the equator", "degree_length_lat_km(0)", 110.574, 1e-4)
    near("degree of longitude at the equator", "degree_length_lon_km(0)", 111.3195, 1e-4)
    near("degree of longitude at 60 degrees", "degree_length_lon_km(60)", 55.800, 1e-3)
    near("degree of longitude at the pole", "degree_length_lon_km(90)", 0, 1e-9)
    near("geocentric latitude", "geocentric_latitude(45)", math.degrees(math.atan((1 - (1/298.257223563*(2-1/298.257223563))) * 1)), 1e-12)
    near("geocentric equals geodetic at the equator", "geocentric_latitude(0)", 0)
    near("geocentric equals geodetic at the pole", "geocentric_latitude(90)", 90, 1e-12)
    near("moon age at the reference new moon", "moon_age_days(2451550.09766)", 0, 1e-6)
    near("moon age wraps by the synodic month", "moon_age_days(2451550.09766+29.530588853*7+3)", 3, 1e-6)
    near("full moon of January 2000 (JD 2451564.5)", "moon_illumination(2451564.5)", 1, 2e-2)
    near("new moon illumination", "moon_illumination(2451550.09766)", 0, 1e-9)
    near("quarter illumination", "moon_illumination(2451550.09766+29.530588853/4)", 0.5, 1e-9)
    for e in ["julian_date_from_unix(1e999)", "sidereal_time(1e999)", "local_sidereal_time(2451545,500)", "solar_declination(0)", "solar_declination(367)",
              "sunrise_hour_angle(80,23)", "sunrise_hour_angle(91,0)", "sunrise_hour_angle(0,91)", "sunrise_hour_angle(-80,23)", "day_length_hours(51,0)",
              "day_length_hours(89,172)", "day_length_hours(91,100)", "rhumb_distance(91,0,0,0)", "rhumb_distance(0,0,0,400)", "rhumb_bearing(10,10,10,10)",
              "utm_zone(181)", "utm_band(85)", "utm_band(-81)", "utm_band('a')", "flux_to_magnitude(0)", "flux_to_magnitude(-1)", "absolute_magnitude(1,0)",
              "absolute_magnitude(1,-5)", "airmass(-1)", "airmass(91)", "angular_size_arcsec(0,1)", "angular_size_arcsec(1,0)", "horizon_distance_km(-1)",
              "meridian_radius(91)", "prime_vertical_radius(-91)", "degree_length_lat_km(100)", "degree_length_lon_km(-100)", "geocentric_latitude(91)",
              "moon_age_days(1e999)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
