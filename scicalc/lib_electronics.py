"""Phase 3: electronics and signals

Module 38 of 47.  Taken from lines 12819-13068 of the original single-file calculator.py.
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
    sys.argv = ["run_tests.py", "lib_electronics"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math
from fractions import Fraction

from .errors import MathError
from .registry import register

#  PHASE 3 : ELECTRONICS AND SIGNALS (36)
#  Volts, amps, ohms, farads, henries, hertz, watts, metres.  Decibels are 10 log10 for
#  power and 20 log10 for voltage.  Speed of light 299792458 m/s.
# ======================================================================================
_ELX = "Electronics & Signals"
_C_LIGHT = 299792458.0


def _elx(name, desc, args, example, **kw):
    return register(name, _ELX, desc, args, example=example, **kw)


def _vpos(x, what="value"):
    x = float(x)
    if not math.isfinite(x) or x <= 0:
        raise MathError(f"{what} must be positive")
    return x


def _vnn(x, what="value"):
    x = float(x)
    if not math.isfinite(x) or x < 0:
        raise MathError(f"{what} cannot be negative")
    return x


def _vfin(x, what="value"):
    x = float(x)
    if not math.isfinite(x):
        raise MathError(f"{what} is not a finite number")
    return x


@_elx("db_ratio_power", "Power ratio in decibels: db_ratio_power(p_out, p_in)", 2, "db_ratio_power(100, 1) => 20")
def db_ratio_power(p, q):
    return 10 * math.log10(_vpos(p, "power") / _vpos(q, "power"))


@_elx("db_ratio_voltage", "Voltage ratio in decibels: db_ratio_voltage(v_out, v_in)", 2, "db_ratio_voltage(10, 1) => 20")
def db_ratio_voltage(v, w):
    return 20 * math.log10(_vpos(v, "voltage") / _vpos(w, "voltage"))


@_elx("db_to_power_ratio", "Power ratio from decibels: db_to_power_ratio(dB)", 1, "db_to_power_ratio(3) => 1.995262315")
def db_to_power_ratio(db):
    return 10 ** (_vfin(db) / 10)


@_elx("db_to_voltage_ratio", "Voltage ratio from decibels: db_to_voltage_ratio(dB)", 1, "db_to_voltage_ratio(6) => 1.995262315")
def db_to_voltage_ratio(db):
    return 10 ** (_vfin(db) / 20)


@_elx("dbm2w", "Watts from dBm: dbm2w(dBm)", 1, "dbm2w(30) => 1")
def dbm2w(dbm):
    return 10 ** (_vfin(dbm) / 10) / 1000


@_elx("w2dbm", "dBm from watts: w2dbm(W)", 1, "w2dbm(1) => 30")
def w2dbm(w):
    return 10 * math.log10(_vpos(w, "power") * 1000)


@_elx("rc_cutoff", "Cut-off frequency (Hz) of an RC filter: rc_cutoff(R, C)", 2, "rc_cutoff(1000, 1e-6) => 159.1549431")
def rc_cutoff(r, c):
    return 1 / (2 * math.pi * _vpos(r, "resistance") * _vpos(c, "capacitance"))


@_elx("rl_cutoff", "Cut-off frequency (Hz) of an RL filter: rl_cutoff(R, L)", 2, "rl_cutoff(100, 0.01) => 1591.549431")
def rl_cutoff(r, l):
    return _vpos(r, "resistance") / (2 * math.pi * _vpos(l, "inductance"))


@_elx("shannon_capacity", "Channel capacity (bit/s): shannon_capacity(bandwidth_Hz, snr_ratio)  [C = B log2(1+SNR)]", 2,
      "shannon_capacity(3000, 1000) => 29901.67878")
def shannon_capacity(b, snr):
    return _vpos(b, "bandwidth") * math.log2(1 + _vnn(snr, "signal-to-noise ratio"))


@_elx("adc_levels", "Number of levels of an n-bit converter: adc_levels(bits)", 1, "adc_levels(12) => 4096", exact=True)
def adc_levels(bits):
    if not isinstance(bits, (int, Fraction)) or isinstance(bits, bool) or bits != int(bits) or not 1 <= bits <= 64:
        raise MathError("bits must be a whole number from 1 to 64")
    return 2 ** int(bits)


@_elx("adc_lsb", "Size of one step (V): adc_lsb(v_ref, bits)", 2, "adc_lsb(5, 10) => 0.0048828125")
def adc_lsb(vref, bits):
    bits = _vpos(bits, "bits")
    if bits != int(bits) or bits > 64:
        raise MathError("bits must be a whole number up to 64")
    return _vpos(vref, "reference") / 2 ** int(bits)


@_elx("duty_cycle", "Duty cycle in percent: duty_cycle(t_on, period)", 2, "duty_cycle(2, 8) => 25")
def duty_cycle(t_on, period):
    t_on = _vnn(t_on, "on time")
    period = _vpos(period, "period")
    if t_on > period:
        raise MathError("the on time exceeds the period")
    return t_on / period * 100


@_elx("rms_sine", "RMS of a sine from its peak: rms_sine(peak)", 1, "rms_sine(325) => 229.8097039")
def rms_sine(peak):
    return _vfin(peak) / math.sqrt(2)


@_elx("peak_to_peak", "Peak-to-peak of a sine from its RMS: peak_to_peak(rms)", 1, "peak_to_peak(230) => 650.5382387")
def peak_to_peak(rms):
    return 2 * math.sqrt(2) * _vnn(rms, "RMS")


@_elx("cap_reactance", "Capacitive reactance (ohm): cap_reactance(f, C)", 2, "cap_reactance(50, 1e-6) => 3183.098862")
def cap_reactance(f, c):
    return 1 / (2 * math.pi * _vpos(f, "frequency") * _vpos(c, "capacitance"))


@_elx("ind_reactance", "Inductive reactance (ohm): ind_reactance(f, L)", 2, "ind_reactance(50, 0.1) => 31.41592654")
def ind_reactance(f, l):
    return 2 * math.pi * _vnn(f, "frequency") * _vnn(l, "inductance")


@_elx("skin_depth", "Skin depth (m): skin_depth(f_Hz, conductivity_S_per_m [, relative_permeability = 1])", (2, 3),
      "skin_depth(1e6, 5.96e7) => 0.00006519240484")
def skin_depth(f, sigma, mu_r=1.0):
    mu0 = 4e-7 * math.pi
    return 1 / math.sqrt(math.pi * _vpos(f, "frequency") * mu0 * _vpos(mu_r, "permeability") * _vpos(sigma, "conductivity"))


@_elx("dipole_length", "Half-wave dipole length (m): dipole_length(f_Hz [, velocity_factor = 0.95])", (1, 2),
      "dipole_length(14.2e6) => 10.02826884")
def dipole_length(f, vf=0.95):
    vf = _vpos(vf, "velocity factor")
    if vf > 1:
        raise MathError("velocity factor is at most 1")
    return vf * _C_LIGHT / (2 * _vpos(f, "frequency"))


@_elx("wavelength_from_freq", "Wavelength (m) in free space: wavelength_from_freq(f_Hz)", 1, "wavelength_from_freq(100e6) => 2.99792458")
def wavelength_from_freq(f):
    return _C_LIGHT / _vpos(f, "frequency")


@_elx("lc_resonance", "Resonant frequency (Hz) of an LC circuit: lc_resonance(L, C)", 2, "lc_resonance(0.001, 1e-6) => 5032.92121")
def lc_resonance(l, c):
    return 1 / (2 * math.pi * math.sqrt(_vpos(l, "inductance") * _vpos(c, "capacitance")))


@_elx("rlc_q_series", "Quality factor of a series RLC circuit: rlc_q_series(R, L, C)", 3, "rlc_q_series(10, 0.001, 1e-6) => 3.16227766")
def rlc_q_series(r, l, c):
    return math.sqrt(_vpos(l, "inductance") / _vpos(c, "capacitance")) / _vpos(r, "resistance")


@_elx("rlc_impedance", "Magnitude of the impedance of a series RLC circuit: rlc_impedance(R, L, C, f)", 4,
      "rlc_impedance(10, 0.1, 1e-6, 50) => 3151.6988")
def rlc_impedance(r, l, c, f):
    f = _vpos(f, "frequency")
    x = 2 * math.pi * f * _vnn(l, "inductance") - 1 / (2 * math.pi * f * _vpos(c, "capacitance"))
    return math.hypot(_vnn(r, "resistance"), x)


@_elx("voltage_divider", "Output of a resistor divider: voltage_divider(v_in, r1_top, r2_bottom)", 3, "voltage_divider(12, 10000, 5000) => 4")
def voltage_divider(v, r1, r2):
    r1, r2 = _vnn(r1, "resistance"), _vnn(r2, "resistance")
    if r1 + r2 == 0:
        raise MathError("both resistors cannot be zero")
    return _vfin(v) * r2 / (r1 + r2)


@_elx("led_resistor", "Series resistor (ohm) for an LED: led_resistor(v_supply, v_forward, current_A)", 3, "led_resistor(5, 2, 0.02) => 150")
def led_resistor(vs, vf, i):
    vs, vf = _vfin(vs), _vnn(vf, "forward voltage")
    if vs <= vf:
        raise MathError("the supply must be above the forward voltage")
    return (vs - vf) / _vpos(i, "current")


@_elx("nyquist_rate", "Minimum sampling rate (Hz) for a signal of highest frequency f: nyquist_rate(f)", 1, "nyquist_rate(20000) => 40000")
def nyquist_rate(f):
    return 2 * _vpos(f, "frequency")


@_elx("signal_snr_db", "Signal-to-noise ratio in dB from two powers: signal_snr_db(p_signal, p_noise)", 2, "signal_snr_db(1, 0.001) => 30")
def signal_snr_db(ps, pn):
    return 10 * math.log10(_vpos(ps, "signal power") / _vpos(pn, "noise power"))


@_elx("quantization_snr", "Ideal SNR (dB) of an n-bit converter for a full-scale sine, about 6.02 n + 1.76", 1, "quantization_snr(12) => 74.00811155")
def quantization_snr(bits):
    return 20 * math.log10(2) * _vpos(bits, "bits") + 10 * math.log10(1.5)


@_elx("rise_time_bandwidth", "Bandwidth (Hz) from the 10-90% rise time: 0.35 / t_rise", 1, "rise_time_bandwidth(1e-9) => 350000000")
def rise_time_bandwidth(tr):
    return 0.35 / _vpos(tr, "rise time")


@_elx("pwm_average", "Average voltage of a PWM signal: pwm_average(v_high, duty_percent)", 2, "pwm_average(5, 40) => 2")
def pwm_average(v, duty):
    duty = _vfin(duty)
    if not 0 <= duty <= 100:
        raise MathError("duty cycle is 0 to 100 percent")
    return _vfin(v) * duty / 100


@_elx("rms_square", "RMS of a rectangular pulse train: rms_square(v_high, duty_percent)", 2, "rms_square(10, 25) => 5")
def rms_square(v, duty):
    duty = _vfin(duty)
    if not 0 <= duty <= 100:
        raise MathError("duty cycle is 0 to 100 percent")
    return abs(_vfin(v)) * math.sqrt(duty / 100)


@_elx("opamp_gain_inv", "Gain of an inverting op-amp stage: opamp_gain_inv(r_feedback, r_in)", 2, "opamp_gain_inv(100000, 10000) => -10")
def opamp_gain_inv(rf, rin):
    return -_vnn(rf, "resistance") / _vpos(rin, "input resistance")


@_elx("opamp_gain_noninv", "Gain of a non-inverting op-amp stage: opamp_gain_noninv(r_feedback, r_ground)", 2, "opamp_gain_noninv(90000, 10000) => 10")
def opamp_gain_noninv(rf, rg):
    return 1 + _vnn(rf, "resistance") / _vpos(rg, "resistance")


@_elx("fspl_db", "Free-space path loss in dB: fspl_db(distance_m, frequency_Hz)", 2, "fspl_db(1000, 2.4e9) => 100.0520081")
def fspl_db(d, f):
    return 20 * math.log10(4 * math.pi * _vpos(d, "distance") * _vpos(f, "frequency") / _C_LIGHT)


@_elx("thermal_noise_dbm", "Thermal noise power (dBm) at 290 K in a bandwidth B: thermal_noise_dbm(B_Hz)", 1, "thermal_noise_dbm(1) => -173.9751872")
def thermal_noise_dbm(b):
    return 10 * math.log10(1.380649e-23 * 290 * _vpos(b, "bandwidth") / 1e-3)


@_elx("ac_power_3phase", "Real power (W) of a balanced three-phase load: ac_power_3phase(V_line, I_line, power_factor)", 3,
      "ac_power_3phase(400, 10, 0.8) => 5542.562584")
def ac_power_3phase(v, i, pf):
    pf = _vfin(pf)
    if not -1 <= pf <= 1:
        raise MathError("power factor is between -1 and 1")
    return math.sqrt(3) * _vnn(v, "voltage") * _vnn(i, "current") * pf


@_elx("transformer_turns", "Secondary turns: transformer_turns(v_primary, v_secondary, turns_primary)", 3,
      "transformer_turns(230, 12, 1000) => 52.17391304")
def transformer_turns(vp, vs, n):
    return _vnn(vs, "voltage") * _vpos(n, "turns") / _vpos(vp, "voltage")


# ======================================================================================
