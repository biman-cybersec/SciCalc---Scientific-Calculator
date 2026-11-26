"""Bad-input tests: every error case must give the right Casio-style error and no Python exception may escape."""

if __name__ == "__main__":      # run directly (e.g. VS Code "Run Python File"): test this file instead of failing on its relative imports
    import os
    import runpy
    import sys

    _root = os.path.dirname(os.path.abspath(__file__))
    while not os.path.exists(os.path.join(_root, "run_tests.py")):
        _root = os.path.dirname(_root)
    sys.path.insert(0, _root)
    sys.argv = ["run_tests.py", "--topic", "bad_input"]
    runpy.run_path(os.path.join(_root, "run_tests.py"), run_name="__main__")

from ..errors import CalcError
from ..registry import REGISTRY
from ..engine import Calculator

from .helpers import _err, _expr_error  # noqa: F401


def _bad_input_checks(check):
    # 1. a table of inputs that must be refused with the right Casio-style error
    math_errors = [
        "log(0)", "ln(-1)", "log2(0)", "logb(1,5)", "asin(2)", "acos(-2)", "acosh(0)", "atanh(1)", "acoth(0.5)",
        "sqrt(-4)", "root(2,-9)", "factorial(-1)", "factorial(2000)", "0^0", "1/0", "5 mod 0",
        "npr(3,5)", "ncr(-1,2)", "gamma(0)", "gamma(-3)", "lgamma(0)", "beta(0,1)", "digamma(-2)", "zeta(1)",
        "totient(0)", "divisors_count(-5)", "modinv(2,4)", "modpow(2,-1,5)", "jacobi(2,4)", "legendre(2,4)",
        "isprime(1.5)", "gcd(1.5,3)", "fib(-1)", "lucas(-3)", "catalan(-2)", "partitions(-1)", "bell(-1)",
        "prev_prime(2)", "nth_prime(0)", "collatz_steps(0)", "primitive_root(1)", "crt2(1,4,2,6)", "order_mod(2,4)",
        "norm_cdf(0,0,0)", "norm_inv(0,0,1)", "norm_inv(1,0,1)", "t_pdf(1,0)", "t_inv(0.5,0)", "chisq_cdf(1,0)",
        "chisq_inv(1,3)", "f_cdf(1,0,5)", "f_inv(0,3,4)", "gamma_cdf(1,0,1)", "beta_cdf(2,1,1)", "weibull_cdf(1,0,1)",
        "binom_pmf(1,5,2)", "binom_cdf(1,-5,0.5)", "poisson_pmf(-1,2)", "geom_pmf(0,0.5)", "hypergeom_pmf(1,5,9,2)",
        "uniform_pdf(1,3,3)", "expon_inv(1,1)", "expon_inv(0.5,0)", "binomial_cdf(5,2,1.5)",
        "z_ci_low(50,5,30,100)", "z_ci_high(50,-5,30,95)", "t_ci_low(50,5,1,95)", "prop_ci_low(120,100,95)",
        "t_stat_two(1,0,1,2,0,1)", "t_p_two(1,0)", "chi2_p(-1,3)", "cohen_d(1,1,1,2,1,5)", "sample_size_prop(1.5,0.05,95)",
        "critical_z(0)", "critical_t(1,5)", "sample_size_mean(5,0,0.95)", "ci_z_mean(1,0,30,0.95)",
        "variance(5)", "skewness(1,2)", "kurtosis(1,2,3)", "skew_pop(4,4,4)", "cv(-1,1)", "harmonic_mean(1,0)",
        "geometric_mean(-1,4)", "z_score(1,2,0)", "percentile(101,1,2,3)", "quantile(1.5,1,2,3)",
        "pearson_corr(1,2,3)", "linreg_slope(1,1,1,2,3,4)", "expreg_a(1,2,3,-1,2,3)", "logreg_a(0,1,2,1,2,3)",
        "quad_root1(0,1,1)", "quad_root1(1,0,1)", "lin2_x(1,1,1,2,2,2)", "lin3_x(1,1,1,1,2,2,2,2,3,3,3,3)",
        "line_slope(1,2,1,5)", "ap_count(2,3,30)", "gp_sum_inf(1,2)", "hp_nth(0,1,3)", "binom_term(3,5,1,1)",
        "pf_a(1,1,2,2)", "solve_exp(2,1,3)", "solve('x^2+1',1)", "bisect('x^2+1',0,2)", "root_bisection('x^2+1',0,2)",
        "fixed_point('x+1',0)", "secant('1',0,1)", "convert(1,\"km\",\"kg\")", "convert(1,\"parsec\",\"mi\")",
        "mpg2l100km(0)", "l100km2mpg(0)", "c_to_f(-300)", "k_to_c(-1)", "bmi(70,0)", "speed(5,0)", "time_taken(5,0)",
        "emi(1000,12,0)", "cagr(0,5,2)", "roi(5,0)", "pct_change(0,5)", "area_circle(-1)", "heron(1,2,10)",
        "perim_triangle(1,1,5)", "vol_cone(-1,2)", "area_square(-3)", "mat_inv2(1,2,2,4)", "angle_vectors2(0,0,1,1)",
        "vector_projection(1,1,0,0)", "c_div(1,1,0,0)", "c_arg(0,0)", "atan2(0,0)", "snells_law(1,1.5,90)*0+snells_law(2,1,60)",
        "critical_angle(1,1.5)", "orbital_period(0,5)", "grav_force(1,1,0)", "ph_calc(0)", "molarity(1,0)",
        "snr_db(0,1)", "ideal_pressure(1,300,0)", "reynolds_number(1,1,1,0)", "sound_speed_air(-300)",
        "tri_side_sas(3,0,4)", "tri_side_sas(3,180,4)", "tri_side_sas(-3,60,4)", "tri_angle(1,2,10)", "tri_angle(0,1,1)",
        "tri_area_sas(3,180,4)", "tri_area_sas(3,-5,4)", "circumradius(1,1,3)", "inradius(1,2,3)", "exradius_a(5,1,1)",
        "tri_median(1,1,5)", "tri_altitude(0,3,4)", "tri_bisector(9,3,4)", "tri_circumcenter_x(0,0,1,1,2,2)",
        "tri_circumcenter_y(0,0,1,1,2,2)", "tri_incenter_x(0,0,1,1,2,2)", "tri_incenter_y(0,0,1,1,2,2)",
        "tri_orthocenter_x(0,0,1,1,2,2)", "tri_orthocenter_y(0,0,1,1,2,2)", "reg_poly_area(2,1)", "reg_poly_area(5.5,1)",
        "reg_poly_area(5,-1)", "reg_poly_apothem(2,1)", "reg_poly_interior(2)", "reg_poly_interior(3.5)", "reg_poly_diagonals(1)",
        "reg_poly_circumradius(5,0)", "sector_area(-1,90)", "sector_area(1,400)", "arc_len(1,-10)", "segment_area(0,90)",
        "chord_len(1,361)", "annulus_area(2,3)", "annulus_area(2,-1)", "circle_3pt_r(0,0,1,1,2,2)", "ellipse_ecc(0,3)",
        "ellipse_focus(-1,2)", "frustum_cone_vol(0,1,2)", "frustum_cone_lsa(1,2,-3)", "frustum_pyr_vol(1,1,0)", "torus_vol(1,2)",
        "torus_area(0,1)", "ellipsoid_vol(1,0,3)", "cap_vol(1,3)", "cap_area(1,-1)", "zone_area(1,2.5)", "capsule_vol(0,1)",
        "tetra_vol_reg(0)", "octa_vol(-1)", "dodeca_vol(0)", "icosa_vol(-2)", "section_x(1,2,1,-1)", "point_line_dist(1,1,0,0,5)",
        "slant_to_height(5,3)", "slant_to_height(0,3)", "cone_slant(-1,2)", "vol_pent_prism(0,1)", "tsa_pent_prism(1,-1)",
        "vol_hex_prism(1,0)", "tsa_hex_prism(-1,1)", "vol_pent_pyramid(1,0)", "vol_hex_pyramid(0,1)",
        "deriv_n('x',0,1)", "deriv_n('x',7,1)", "deriv_n('x',1.5,1)", "deriv('1/x',0)", "deriv(5,1)", "partial_x('x/y',1,0)",
        "partial_y('ln(y)',1,-1)", "integrate_simpson('x',0,1,3)", "integrate_simpson('x',0,1,0)", "integrate_simpson('x',0,1,100000)",
        "integrate_trap('x',0,1,0)", "integrate_trap('x',0,1,99999)", "integrate_romberg('1/x',-1,1)", "integrate_to_inf('x',0)",
        "integrate_to_inf('1/x',1)", "double_integral('1/(x*y)',0,1,0,1)", "limit('1/x',0)", "limit('abs(x)/x',0)",
        "limit_left('1/x',0)", "limit_right('1/x',0)", "limit_inf('x')", "sum_series('x',1,30000)", "sum_series('1/x',0,3)",
        "sum_series('x',1.5,3)", "prod_series('1/x',-1,1)", "taylor_value('x',0,1,7)", "taylor_value('x',0,1,-1)",
        "taylor_value('ln(x)',-5,1,2)", "curve_length('1/x',-1,1)", "area_between('1/x','x',-1,1)", "vol_revolution_x('ln(x)',-1,1)",
        "mean_value('x',1,1)", "mean_value('x',2,2)", "curvature('1/x',0)", "critical_point('x',0,1)", "critical_point('x',2,1)",
        "dec2base(5,1)", "dec2base(5,37)", "dec2base(1.5,2)", 'base2dec("12",2)', 'base2dec("",10)', 'base2dec("zz",16)',
        "bit_count(-1)", "bit_length(-5)", "bit_get(5,-1)", "bit_set(1,5000)", "rotl(300,1,8)", "rotl(1,1,0)", "rotr(1,1,2000)",
        "reverse_bits(256,8)", "bin2gray(-1)", "gray2bin(-3)", "parity(-2)", "twos_comp(200,8)", "twos_comp(-129,8)",
        "from_twos(256,8)", "sign_extend(255,8,4)", "sign_extend(256,8,16)", "mask_bits(-1)", "mask_bits(5000)", "hamming_dist(-1,2)",
        "lowest_set_bit(-4)", "nand(1.5)", "c_recip(0,0)", "c_ln(0,0)", "c_pow(0,0,0,0)", "c_pow(0,0,-1,0)", "c_pow_n(0,0,-1)",
        "c_pow_n(1,1,0.5)", "c_pow_n(1,1,100000)", "c_nth_root(1,1,0,0)", "c_nth_root(1,1,3,3)", "c_nth_root(1,1,3,-1)",
        "c_roots_unity(0,0)", "c_roots_unity(4,4)", "c_quad_root1(0,1,1)", "c_quad_root2(0,0,0)", "c_atan(0,1)", "c_atan(0,-1)",
        "c_exp(1000,0)", "c_sqrt(1)", "c_from_polar(1)", "det4(1,2)", "mat_inv3(1,2,3,2,4,6,3,6,9)", "mat_inv3(0,0,0,0,0,0,0,0,0)",
        "mat_pow3(0,0,0,0,0,0,0,0,0,-1)", "mat_pow3(1,0,0,0,1,0,0,0,1,0.5)", "mat_pow3(1,0,0,0,1,0,0,0,1,100000)",
        "mat_minor3(1,2,3,4,5,6,7,8,9,4,1)", "mat_cofactor3(1,2,3,4,5,6,7,8,9,0,1)", "mat_minor3(1,2,3,4,5,6,7,8,9,1.5,1)",
        "dot_n(2,1,2,3)", "dot_n(0,1,2)", "dot_n(1.5,1,2,3)", "unit2_x(0,0)", "unit2_y(0,0)", "unit3_x(0,0,0)", "unit3_z(0,0,0)",
        "angle_vectors3(0,0,0,1,0,0)", "point_plane_dist(1,1,1,0,0,0,5)", "plane_d(0,0,0,1,1,1)",
        "accel_from(1,2,0)", "velocity_sq(1,-2,5)", "free_fall_time(-1)", "free_fall_speed(-4)", "proj_max_height(10,91)",
        "proj_max_height(10,-1)", "proj_max_height(-5,45)", "proj_time(10,120)", "centripetal_acc(5,0)", "centripetal_acc(5,-2)",
        "newton_force(-1,2)", "weight_n(-3)", "friction_force(-0.1,5)", "incline_accel(95,0.1)", "incline_accel(30,-1)",
        "torque(1,-2,30)", "mi_disk(-1,2)", "mi_rod(1,-2)", "mi_sphere(-1,1)", "mi_hollow_sphere(1,-1)", "rot_ke(-2,3)",
        "power_work(10,0)", "power_work(10,-1)", "pendulum_period(-1)", "spring_period(0,5)", "spring_period(1,0)", "hooke_force(-5,1)",
        "doppler_freq(440,343,0)", "doppler_freq(440,400,0)", "doppler_freq(440,0,-400)", "doppler_freq(-1,0,0)", "string_freq(0,1,1)",
        "string_freq(1,-1,1)", "string_freq(1,1,0)", "boyle_p2(1,1,0)", "boyle_p2(-1,1,1)", "charles_v2(1,0,300)", "charles_v2(1,-5,300)",
        "gay_lussac_p2(1,0,300)", "combined_gas_p2(1,1,0,1,1)", "combined_gas_p2(1,1,1,0,1)", "carnot_eff(0,0)", "carnot_eff(300,400)",
        "carnot_eff(300,-1)", "entropy_change(5,0)", "entropy_change(5,-10)", "latent_heat(-1,5)", "conduction_rate(1,1,1,0)",
        "conduction_rate(-1,1,1,1)", "wien_peak(0)", "wien_peak(-5)", "res_series2(-1,5)", "res_parallel2(-1,5)", "res_series3(1,-1,1)",
        "res_parallel3(1,-1,1)", "cap_series2(0,5)", "cap_parallel2(-1,5)", "rc_tau(-1,1)", "rl_tau(1,0)", "rl_tau(-1,1)", "lc_freq(0,1)",
        "lc_freq(1,-1)", "impedance_rlc(1,1,0,50)", "impedance_rlc(1,1,1,0)", "impedance_rlc(-1,1,1,50)", "power_factor(5,3)",
        "power_factor(1,0)", "transformer_vs(1,0,1)", "transformer_vs(1,1,-1)", "coulomb_force(1,1,0)", "electric_field(1,-1)",
        "electric_potential(1,0)", "plate_capacitance(0,1,1)", "plate_capacitance(1,0,1)", "plate_capacitance(1,1,-2)",
        "magnetic_force(1,-1,1,30)", "magnetic_force(1,1,1,200)", "wire_field(5,0)", "solenoid_field(-1,2)", "faraday_emf(1,1,0)",
        "faraday_emf(-3,1,1)", "lens_image_dist(10,10)", "lens_image_dist(0,5)", "lens_image_dist(10,0)", "lens_magnification(1,0)",
        "brewster_angle(0,1)", "brewster_angle(1,-1)", "grating_angle(5,500,1000)", "grating_angle(1,0,1000)", "grating_angle(1,500,0)",
        "de_broglie(0,5)", "de_broglie(1,0)", "de_broglie(-1,5)", "compton_shift(181)", "compton_shift(-1)", "bohr_energy(0,1)",
        "bohr_energy(1.5,1)", "bohr_energy(2,0)", "rydberg_wavelength(2,2)", "rydberg_wavelength(3,2)", "rydberg_wavelength(0,2)",
        "rydberg_wavelength(1.5,3)", "mass_energy(-1)", "lorentz_gamma(const_c)", "lorentz_gamma(-const_c)", "lorentz_gamma(1e9)",
        "time_dilation(1,const_c)", "length_contraction(1,2*const_c)", "rel_momentum(-1,5)", "rel_momentum(1,const_c)", "rel_energy(-1,5)",
        "rel_energy(1,1e9)", "half_life_remaining(1,1,0)", "half_life_remaining(-1,1,1)", "half_life_remaining(1,-1,1)", "decay_constant(0)",
        "decay_constant(-4)", "activity(1,0)", "activity(-1,5)", "hill_sphere(0,1,1)", "hill_sphere(1,-1,1)", "hill_sphere(1,1,0)",
        "roche_limit(0,1,1)", "roche_limit(1,1,0)", "roche_limit(1,-1,1)", "surface_gravity(0,1)", "surface_gravity(1,0)",
        "parallax_distance(0)", "parallax_distance(-1)", "hubble_velocity(-1)", "luminosity_bb(0,5000)", "luminosity_bb(1,0)",
        "loan_balance(1000,5,12,13)", "loan_balance(1000,5,0,0)", "loan_balance(-1,5,12,1)", "loan_balance(1000,-5,12,1)", "loan_balance(1000,5,12.5,1)",
        "loan_total_interest(1000,5,0)", "loan_total_interest(-1,5,12)", "loan_total_interest(1000,-1,12)", "loan_term(1000,12,5)", "loan_term(0,5,100)",
        "loan_term(1000,5,0)", "sip_fv(100,5,0)", "sip_fv(-1,5,12)", "sip_fv(100,-5,12)", "sip_target(100,5,0)", "sip_target(-1,5,12)",
        "rule_of_72(0)", "rule_of_72(-3)", "real_rate(-100,5)", "real_rate(5,-100)", "ear(5,0)", "ear(5,1.5)", "ear(-1200,12)",
        "inflation_adjust(100,-100,1)", "inflation_adjust(-1,5,1)", "inflation_adjust(100,5,-1)", "break_even(100,10,10)", "break_even(100,5,10)",
        "break_even(-1,10,5)", "margin_pct(5,0)", "margin_pct(-1,5)", "markup_pct(0,5)", "markup_pct(5,-1)", "successive_discount(100,101,5)",
        "successive_discount(100,5,-1)", "successive_discount(-1,5,5)", "gst_split(-1,18)", "vat_add(-1,20)", "vat_remove(100,-1)",
        "dep_straight(100,10,0)", "dep_straight(100,200,5)", "dep_straight(100,-1,5)", "dep_declining(100,0,1)", "dep_declining(100,101,1)",
        "dep_declining(100,20,0)", "dep_declining(100,20,1.5)", "dep_syd(100,10,5,0)", "dep_syd(100,10,5,6)", "dep_syd(100,200,5,1)",
        "bond_price(1000,5,5,0)", "bond_price(1000,5,-100,5)", "bond_price(-1,5,5,5)", "bond_price(1000,5,5,2.5)", "current_yield(5,0)",
        "current_yield(-1,100)", "dividend_yield(1,0)", "dividend_yield(-1,5)", "pe_ratio(10,0)", "pe_ratio(-1,5)", "roe(5,0)",
        "irr(100,50)", "irr(-100,-50)", "payback(-100,10,10)", "payback(-100,50,0)", "annuity_due_fv(100,-1,5)", "annuity_due_fv(100,0.05,-1)",
        "perpetuity(10,0)", "perpetuity(10,-0.05)", "growing_perpetuity(10,0.03,0.03)", "growing_perpetuity(10,0.02,0.05)", "fx_convert(5,0)",
        "fx_convert(-1,5)", "split_bill(100,0,10)", "split_bill(100,2.5,10)", "split_bill(-1,2,10)", "mileage(10,0)", "mileage(-1,5)",
        "trip_cost(10,0,5)", "trip_cost(-1,5,5)", "electricity_bill(-1,2,3)", "electricity_bill(1,-2,3)",
        "days_between(2023,2,29,2024,1,1)", "days_between(2024,13,1,2024,1,1)", "days_between(2024,1,0,2024,1,1)", "days_between(2024.5,1,1,2024,1,1)",
        "weekday(1900,2,29)", "weekday(2000,0,5)", "is_leap(1.5)", "days_in_month(2024,13)", "days_in_month(2024,0)", "day_of_year(2023,4,31)",
        "week_number(2023,2,30)", "age_years(2000,1,1,1999,12,31)", "age_years(2001,2,29,2002,1,1)", "julian_day(2023,2,29)", "unix_time(2000,1,1,24,0,0)",
        "unix_time(2000,1,1,0,60,0)", "unix_time(2000,1,1,0,0,60)", "unix_time(2000,1,1,-1,0,0)", "unix_time(2000,1,1,0.5,0,0)",
        "tan_deg(90)", "tan_deg(-270)", "cot_deg(0)", "cot_deg(180)", "sec_deg(90)", "sec_deg(450)", "csc_deg(0)", "csc_deg(360)",
        "asin_deg(1.5)", "acos_deg(-1.5)", "tan_rad(pi/2)",
        "bearing(91,0,0,0)", "bearing(0,0,-91,0)", "bearing(10,20,10,20)", "bearing(90,0,90,50)", "dest_lat(95,0,0,10)", "dest_lat(0,0,0,-1)",
        "dest_lon(0,0,0,-5)", "dest_lon(-91,0,0,5)", "midpoint_lat(0,0,0,180)", "midpoint_lon(10,20,-10,-160)", "midpoint_lat(100,0,0,0)",
        "mat_pow2(1,2,3,4,-1)", "ode_rk4('x',0,1,1,0)", "num_integrate_simpson('x',0,1,3)",
        "fib_mod(1e308,7)", "harmonic_number(1e308)", "bessel_j(0.5,1)", "bessel_y(0,0)", "elliptic_k(1)", "lambertw(-1)",
        "erf_inv(1)", "hyp2f1(1,1,2,1.5)", "cosine_integral(0)", "digital_root(1.5)", "sigma_k(1,0)",
    ]
    for expr in math_errors:
        got = _err(expr)
        check(f"bad input {expr}", got in ("Math ERROR", "Argument ERROR"), True)
    for expr in ["2+", "foo(1)", "(1+", "3 4 5 +", "sin(", "@", "1..2", "5->Z", "sin 30 cos"]:
        check(f"syntax {expr}", _err(expr) in ("Syntax ERROR", ""), True)
    for expr in ["sin()", "sin(1,2)", "atan2(1)", "mean()", "convert(1,2)", "round(1,2,3)", "rand(1)"]:
        check(f"argument {expr}", _err(expr), "Argument ERROR")

    # 2. every function must refuse the wrong number of arguments, and never leak a Python error
    leaks = []
    for f in REGISTRY.functions():
        if f.min_args > 0:
            expr = f"{f.name}(" + ",".join(["1"] * (f.min_args - 1)) + ")"
            got = _err(expr)
            check(f"too few arguments: {expr}", got, "Argument ERROR")
        if f.max_args is not None:
            expr = f"{f.name}(" + ",".join(["1"] * (f.max_args + 1)) + ")"
            got = _err(expr)
            check(f"too many arguments: {expr}", got, "Argument ERROR")
        if f.name == "rand":
            continue
        lo = f.min_args
        hi = f.max_args if f.max_args is not None else lo + 2
        for n in sorted({lo, hi}):
            for v in ("0", "-1", "0.5", "1e308"):
                expr = f"{f.name}(" + ",".join([v] * n) + ")"
                try:
                    Calculator().evaluate(expr)
                except CalcError:
                    pass
                except Exception as exc:                        # a Python traceback would reach the user
                    leaks.append(f"{expr}: {type(exc).__name__}: {exc}")
    check("no Python exception escapes any function", leaks[:5], [])
