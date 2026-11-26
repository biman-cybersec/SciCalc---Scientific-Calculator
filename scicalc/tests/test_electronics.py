"""Checks: electronics.  Run alone with  python run_tests.py electronics"""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "electronics"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

import math

from .helpers import _err, _expr_error  # noqa: F401


def checks_electronics_32(check, ev, near, ex):
    """Phase 3: electronics and signals"""
    # ================= Phase 3: electronics and signals =================
    near("dB power", "db_ratio_power(100,1)", 20)
    near("dB voltage is 2x power dB for same ratio", "db_ratio_voltage(7,2)", 2 * ev("db_ratio_power(7,2)"))
    near("dB round trip power", "db_to_power_ratio(db_ratio_power(37,5))", 37 / 5)
    near("dB round trip voltage", "db_to_voltage_ratio(db_ratio_voltage(37,5))", 37 / 5)
    near("3 dB is about 2x", "db_to_power_ratio(3)", 2, 5e-3)
    near("dBm 30 is 1 W", "dbm2w(30)", 1)
    near("dBm 0 is 1 mW", "dbm2w(0)", 1e-3)
    near("W to dBm", "w2dbm(0.001)", 0)
    near("dBm round trip", "w2dbm(dbm2w(-47.5))", -47.5)
    near("rc cutoff: reactance equals R", "cap_reactance(rc_cutoff(1000,1e-6),1e-6)", 1000)
    near("rl cutoff: reactance equals R", "ind_reactance(rl_cutoff(100,0.01),0.01)", 100)
    near("rc cutoff value", "rc_cutoff(1000,1e-6)", 1 / (2 * math.pi * 1e-3))
    near("shannon", "shannon_capacity(3000,1000)", 3000 * math.log(1001) / math.log(2))
    near("shannon 1 -> B", "shannon_capacity(5,1)", 5)
    ex("adc levels", "adc_levels(12)", 4096)
    near("adc lsb x levels = vref", "adc_lsb(5,10)*adc_levels(10)", 5)
    near("duty", "duty_cycle(2,8)", 25)
    near("rms of sine by sampling", "rms_sine(325)", math.sqrt(sum((325 * math.sin(2 * math.pi * k / 10000)) ** 2 for k in range(10000)) / 10000), 1e-9)
    near("peak to peak round trip", "peak_to_peak(rms_sine(100)/1)", 2 * 100)
    near("cap reactance", "cap_reactance(50,1e-6)", 1 / (2 * math.pi * 50 * 1e-6))
    near("ind reactance", "ind_reactance(50,0.1)", 2 * math.pi * 5)
    near("skin depth of copper at 1 MHz is ~65 um", "skin_depth(1e6,5.96e7)", 65.2e-6, 2e-3)
    near("skin depth falls with sqrt(f)", "skin_depth(4e6,5.96e7)", ev("skin_depth(1e6,5.96e7)") / 2)
    near("skin depth with mu_r", "skin_depth(1e6,1e7,100)", ev("skin_depth(1e6,1e7)") / 10)
    near("dipole 14.2 MHz", "dipole_length(14.2e6)", 0.95 * 299792458 / 2 / 14.2e6)
    near("dipole vf 1 is half a wavelength", "dipole_length(100e6,1)", ev("wavelength_from_freq(100e6)") / 2)
    near("wavelength", "wavelength_from_freq(100e6)", 2.99792458)
    near("lc resonance: reactances cancel", "ind_reactance(lc_resonance(0.001,1e-6),0.001)-cap_reactance(lc_resonance(0.001,1e-6),1e-6)", 0, 1e-9)
    near("q = X / R at resonance", "rlc_q_series(10,0.001,1e-6)", 2 * math.pi * 5032.921210448704 * 0.001 / 10, 1e-9)
    near("rlc impedance at resonance is R", "rlc_impedance(10,0.001,1e-6,lc_resonance(0.001,1e-6))", 10, 1e-6)
    near("rlc impedance far from resonance", "rlc_impedance(10,0.1,1e-6,50)", math.hypot(10, 2 * math.pi * 50 * 0.1 - 1 / (2 * math.pi * 50 * 1e-6)))
    near("divider", "voltage_divider(12,10000,5000)", 4)
    near("divider with zero top", "voltage_divider(12,0,5000)", 12)
    near("led resistor", "led_resistor(5,2,0.02)", 150)
    near("nyquist", "nyquist_rate(20000)", 40000)
    near("snr", "signal_snr_db(1,0.001)", 30)
    near("quantisation SNR of 12 bits ~ 6.02n+1.76", "quantization_snr(12)", 6.02 * 12 + 1.76, 1e-3)
    near("rise time to bandwidth", "rise_time_bandwidth(1e-9)", 3.5e8)
    near("pwm average", "pwm_average(5,40)", 2)
    near("rms of pulse train by sampling", "rms_square(10,25)", math.sqrt(sum((10 if k < 250 else 0) ** 2 for k in range(1000)) / 1000))
    near("op-amp inverting", "opamp_gain_inv(100000,10000)", -10)
    near("op-amp non-inverting", "opamp_gain_noninv(90000,10000)", 10)
    near("fspl against the km/MHz form", "fspl_db(1000,2.4e9)", 20 * math.log10(1) + 20 * math.log10(2400) + 32.44, 5e-4)
    near("fspl doubles distance adds 6 dB", "fspl_db(2000,1e9)-fspl_db(1000,1e9)", 6.0206, 1e-4)
    near("thermal noise about -174 dBm per Hz", "thermal_noise_dbm(1)", -174, 2e-2)
    near("thermal noise 1 MHz is 60 dB higher", "thermal_noise_dbm(1e6)-thermal_noise_dbm(1)", 60, 1e-9)
    near("3 phase power", "ac_power_3phase(400,10,0.8)", 400 * 10 * 0.8 * math.sqrt(3))
    near("transformer", "transformer_turns(230,12,1000)", 12 * 1000 / 230)
    for e in ["db_ratio_power(0,1)", "db_ratio_power(1,0)", "db_ratio_power(-1,1)", "db_ratio_voltage(1,0)", "db_to_power_ratio(1e308)",
              "w2dbm(0)", "dbm2w(1e308)", "rc_cutoff(0,1)", "rc_cutoff(1,0)", "rl_cutoff(1,0)", "shannon_capacity(0,1)", "shannon_capacity(1,-1)",
              "adc_levels(0)", "adc_levels(65)", "adc_levels(1.5)", "adc_lsb(0,8)", "adc_lsb(5,0)", "adc_lsb(5,1.5)", "duty_cycle(1,0)", "duty_cycle(9,8)",
              "duty_cycle(-1,8)", "peak_to_peak(-1)", "cap_reactance(0,1)", "cap_reactance(1,0)", "ind_reactance(-1,1)", "skin_depth(0,1)",
              "skin_depth(1,0)", "skin_depth(1,1,0)", "dipole_length(0)", "dipole_length(1,1.5)", "dipole_length(1,0)", "wavelength_from_freq(0)",
              "lc_resonance(0,1)", "lc_resonance(1,0)", "rlc_q_series(0,1,1)", "rlc_impedance(1,1,1,0)", "rlc_impedance(1,1,0,1)",
              "voltage_divider(1,0,0)", "voltage_divider(1,-1,1)", "led_resistor(2,3,0.01)", "led_resistor(5,2,0)", "nyquist_rate(0)",
              "signal_snr_db(0,1)", "signal_snr_db(1,0)", "quantization_snr(0)", "rise_time_bandwidth(0)", "pwm_average(5,101)", "pwm_average(5,-1)",
              "rms_square(5,101)", "opamp_gain_inv(1,0)", "opamp_gain_inv(-1,1)", "opamp_gain_noninv(1,0)", "fspl_db(0,1)", "fspl_db(1,0)",
              "thermal_noise_dbm(0)", "ac_power_3phase(1,1,2)", "ac_power_3phase(-1,1,1)", "transformer_turns(0,1,1)", "transformer_turns(1,1,0)"]:
        check(f"bad input {e}", _err(e) in ("Math ERROR", "Argument ERROR"), True)
