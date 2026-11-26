"""Phase 3: astronomy and geodesy

Module 41 of 47.  Taken from lines 13695-13950 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_astronomy_geodesy"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .errors import MathError
from .registry import register
from .engine import _ACTIVE_CALC

#  PHASE 3 : MORE ASTRONOMY AND GEODESY (26)
#  Julian dates, sidereal time, day length, magnitudes, rhumb lines, UTM zones and the
#  WGS-84 ellipsoid (a = 6378137 m, 1/f = 298.257223563).  Latitudes and longitudes are in
#  degrees in the navigation functions (like the Sprint 7 ones); solar_declination,
#  sunrise_hour_angle, day_length_hours and geocentric_latitude use the current angle mode.
# ======================================================================================
_AGE = "Astronomy & Geodesy 2"
_WGS_A = 6378137.0
_WGS_F = 1 / 298.257223563
_WGS_E2 = _WGS_F * (2 - _WGS_F)


def _age(name, desc, args, example, **kw):
    return register(name, _AGE, desc, args, example=example, **kw)


def _afin(x, what="value"):
    x = float(x)
    if not math.isfinite(x):
        raise MathError(f"{what} is not a finite number")
    return x


def _apos(x, what="value"):
    x = _afin(x, what)
    if x <= 0:
        raise MathError(f"{what} must be positive")
    return x


def _alat(x):
    x = _afin(x, "latitude")
    if not -90 <= x <= 90:
        raise MathError("latitude is between -90 and 90")
    return x


def _alon(x):
    x = _afin(x, "longitude")
    if not -180 <= x <= 360:
        raise MathError("longitude is between -180 and 360")
    return x


def _aang(x):
    """An angle in the current angle mode -> radians."""
    calc = _ACTIVE_CALC[0]
    return calc.to_radians(_afin(x, "angle")) if calc is not None else math.radians(_afin(x, "angle"))


@_age("julian_date_from_unix", "Julian date from Unix time (seconds): julian_date_from_unix(t)", 1, "julian_date_from_unix(946728000) => 2451545")
def julian_date_from_unix(t):
    return _afin(t, "time") / 86400 + 2440587.5


@_age("unix_from_julian_date", "Unix time (seconds) from a Julian date: unix_from_julian_date(jd)", 1, "unix_from_julian_date(2451545) => 946728000")
def unix_from_julian_date(jd):
    return (_afin(jd, "Julian date") - 2440587.5) * 86400


@_age("sidereal_time", "Greenwich mean sidereal time in hours (0-24) at a Julian date: sidereal_time(jd)", 1, "sidereal_time(2451545) => 18.69737456")
def sidereal_time(jd):
    return (18.697374558 + 24.06570982441908 * (_afin(jd, "Julian date") - 2451545.0)) % 24


@_age("local_sidereal_time", "Local mean sidereal time in hours at east longitude (degrees): local_sidereal_time(jd, longitude)", 2,
      "local_sidereal_time(2451545, 15) => 19.69737456")
def local_sidereal_time(jd, lon):
    return (sidereal_time(jd) + _alon(lon) / 15) % 24


def _spencer_dec(day):
    """Spencer's Fourier series for the Sun's declination (radians); good to about 0.1 degree."""
    g = 2 * math.pi * (day - 1) / 365
    return (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))


@_age("solar_declination", "Sun's declination on a day of the year (1-366), Spencer series (about 0.1 degree), in the current angle mode: solar_declination(day)", 1,
      "solar_declination(172) => 23.45204607", angle_out=True)
def solar_declination(day):
    day = _afin(day, "day")
    if not 1 <= day <= 366:
        raise MathError("the day of the year is 1 to 366")
    return _spencer_dec(day)


@_age("sunrise_hour_angle", "Hour angle of sunrise in hours: sunrise_hour_angle(latitude, declination), both in the current angle mode", 2,
      "sunrise_hour_angle(51.5, 23.44) => 8.201960311")
def sunrise_hour_angle(lat, dec):
    lat, dec = _aang(lat), _aang(dec)
    if abs(lat) > math.pi / 2 or abs(dec) > math.pi / 2:
        raise MathError("latitude and declination are within +-90 degrees")
    v = -math.tan(lat) * math.tan(dec)
    if abs(v) > 1:
        raise MathError("the Sun does not rise or set at this latitude")
    return math.degrees(math.acos(v)) / 15


@_age("day_length_hours", "Hours of daylight at a latitude (current angle mode) on a day of the year: day_length_hours(latitude, day)", 2,
      "day_length_hours(51.5, 172) => 16.40678239")
def day_length_hours(lat, day):
    day = _afin(day, "day")
    if not 1 <= day <= 366:
        raise MathError("the day of the year is 1 to 366")
    dec = _spencer_dec(day)
    lat = _aang(lat)
    if abs(lat) > math.pi / 2:
        raise MathError("latitude is within +-90 degrees")
    v = -math.tan(lat) * math.tan(dec)
    if abs(v) > 1:
        raise MathError("the Sun does not rise or set on this day")
    return 2 * math.degrees(math.acos(v)) / 15


def _rhumb(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(_alat(lat1)), math.radians(_alat(lat2))
    dl = math.radians(_alon(lon2) - _alon(lon1))
    dl = (dl + math.pi) % (2 * math.pi) - math.pi
    if abs(p1) == math.pi / 2 or abs(p2) == math.pi / 2:
        dpsi = math.copysign(1e6, p2 - p1) if p1 != p2 else 0.0
    else:
        dpsi = math.log(math.tan(math.pi / 4 + p2 / 2) / math.tan(math.pi / 4 + p1 / 2))
    dp = p2 - p1
    q = dp / dpsi if abs(dpsi) > 1e-12 else math.cos(p1)
    return dp, dl, dpsi, q


@_age("rhumb_distance", "Rhumb-line (constant bearing) distance in km on a sphere of 6371 km: rhumb_distance(lat1, lon1, lat2, lon2), degrees", 4,
      "rhumb_distance(0, 0, 0, 90) => 10007.5434")
def rhumb_distance(lat1, lon1, lat2, lon2):
    dp, dl, _dpsi, q = _rhumb(lat1, lon1, lat2, lon2)
    return 6371.0 * math.hypot(dp, q * dl)


@_age("rhumb_bearing", "Constant compass bearing in degrees (0-360) of the rhumb line: rhumb_bearing(lat1, lon1, lat2, lon2)", 4,
      "rhumb_bearing(0, 0, 10, 10) => 44.85381264")
def rhumb_bearing(lat1, lon1, lat2, lon2):
    _dp, dl, dpsi, _q = _rhumb(lat1, lon1, lat2, lon2)
    if dl == 0 and dpsi == 0:
        raise MathError("the two points are the same")
    return math.degrees(math.atan2(dl, dpsi)) % 360


@_age("utm_zone", "UTM longitude zone 1-60 (the Norway and Svalbard exceptions are ignored): utm_zone(longitude)", 1, "utm_zone(-0.1) => 30")
def utm_zone(lon):
    lon = _afin(lon, "longitude")
    if not -180 <= lon <= 180:
        raise MathError("longitude is between -180 and 180")
    return int((lon + 180) // 6) % 60 + 1


@_age("utm_band", "UTM latitude band letter C-X (-80 to 84 degrees): utm_band(latitude)", 1, "utm_band(51.5) => U", exact=True)
def utm_band(lat):
    lat = float(lat)
    if not math.isfinite(lat) or not -80 <= lat <= 84:
        raise MathError("UTM covers -80 to 84 degrees of latitude")
    return "CDEFGHJKLMNPQRSTUVWX"[min(19, int((lat + 80) // 8))]


@_age("magnitude_to_flux", "Brightness relative to magnitude 0: 10^(-0.4 m)", 1, "magnitude_to_flux(5) => 0.01")
def magnitude_to_flux(m):
    return 10 ** (-0.4 * _afin(m, "magnitude"))


@_age("flux_to_magnitude", "Magnitude from brightness relative to magnitude 0: -2.5 log10(f)", 1, "flux_to_magnitude(0.01) => 5")
def flux_to_magnitude(f):
    return -2.5 * math.log10(_apos(f, "flux"))


@_age("mag_diff_ratio", "How many times brighter m1 is than m2: mag_diff_ratio(m1, m2) = 10^(0.4 (m2 - m1))", 2, "mag_diff_ratio(1, 6) => 100")
def mag_diff_ratio(m1, m2):
    return 10 ** (0.4 * (_afin(m2, "magnitude") - _afin(m1, "magnitude")))


@_age("absolute_magnitude", "Absolute magnitude from apparent magnitude and distance in parsecs: absolute_magnitude(m, d)", 2,
      "absolute_magnitude(4.83, 10) => 4.83")
def absolute_magnitude(m, d):
    return _afin(m, "magnitude") - 5 * math.log10(_apos(d, "distance") / 10)


@_age("distance_from_modulus", "Distance in parsecs from apparent and absolute magnitude: distance_from_modulus(m, M)", 2,
      "distance_from_modulus(15, 0) => 10000")
def distance_from_modulus(m, big_m):
    return 10 ** ((_afin(m, "magnitude") - _afin(big_m, "magnitude") + 5) / 5)


@_age("airmass", "Relative air mass at an altitude (degrees above the horizon, 0-90), Kasten-Young: airmass(altitude)", 1, "airmass(30) => 1.994292853")
def airmass(h):
    h = _afin(h, "altitude")
    if not 0 <= h <= 90:
        raise MathError("altitude is between 0 and 90 degrees")
    return 1 / (math.sin(math.radians(h)) + 0.50572 * (h + 6.07995) ** -1.6364)


@_age("angular_size_arcsec", "Angular size in arc-seconds of an object of a size at a distance (same unit): angular_size_arcsec(size, distance)", 2,
      "angular_size_arcsec(3474, 384400) => 1864.09745")
def angular_size_arcsec(size, dist):
    return 2 * math.atan(_apos(size, "size") / (2 * _apos(dist, "distance"))) * 180 / math.pi * 3600


@_age("horizon_distance_km", "Distance to the sea horizon in km from a height in metres (sphere of 6371 km): horizon_distance_km(h)", 1,
      "horizon_distance_km(100) => 35.69607822")
def horizon_distance_km(h):
    h = _afin(h, "height")
    if h < 0:
        raise MathError("height cannot be negative")
    r = 6371000.0
    return math.sqrt(h * (2 * r + h)) / 1000


@_age("meridian_radius", "WGS-84 radius of curvature (m) along a meridian at a latitude (degrees): meridian_radius(lat)", 1, "meridian_radius(0) => 6335439.327")
def meridian_radius(lat):
    s = math.sin(math.radians(_alat(lat)))
    return _WGS_A * (1 - _WGS_E2) / (1 - _WGS_E2 * s * s) ** 1.5


@_age("prime_vertical_radius", "WGS-84 radius of curvature (m) in the prime vertical at a latitude (degrees): prime_vertical_radius(lat)", 1,
      "prime_vertical_radius(0) => 6378137")
def prime_vertical_radius(lat):
    s = math.sin(math.radians(_alat(lat)))
    return _WGS_A / math.sqrt(1 - _WGS_E2 * s * s)


@_age("degree_length_lat_km", "Length in km of one degree of latitude at a latitude (degrees): degree_length_lat_km(lat)", 1, "degree_length_lat_km(45) => 111.1317774")
def degree_length_lat_km(lat):
    return math.radians(1) * meridian_radius(lat) / 1000


@_age("degree_length_lon_km", "Length in km of one degree of longitude at a latitude (degrees): degree_length_lon_km(lat)", 1, "degree_length_lon_km(45) => 78.84683509")
def degree_length_lon_km(lat):
    return math.radians(1) * prime_vertical_radius(lat) * math.cos(math.radians(_alat(lat))) / 1000


@_age("geocentric_latitude", "Geocentric latitude from geodetic latitude (WGS-84), in the current angle mode", 1, "geocentric_latitude(45) => 44.80757678", angle_in=True, angle_out=True)
def geocentric_latitude(lat):
    if abs(_afin(lat, "latitude")) > math.pi / 2:
        raise MathError("latitude is within +-90 degrees")
    return math.atan((1 - _WGS_E2) * math.tan(lat))


_SYNODIC = 29.530588853
_NEW_MOON_JD = 2451550.09766


@_age("moon_age_days", "Approximate age of the Moon in days since new moon at a Julian date (mean synodic month)", 1, "moon_age_days(2451564.5) => 14.40234")
def moon_age_days(jd):
    return (_afin(jd, "Julian date") - _NEW_MOON_JD) % _SYNODIC


@_age("moon_illumination", "Approximate illuminated fraction of the Moon's disc (0-1) at a Julian date", 1, "moon_illumination(2451564.5) => 0.9985098023")
def moon_illumination(jd):
    return (1 - math.cos(2 * math.pi * moon_age_days(jd) / _SYNODIC)) / 2


# ======================================================================================
