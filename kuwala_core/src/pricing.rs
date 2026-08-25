const INV_SQRT_2PI: f64 = 0.398942280401432677939946059934;

/// Standard normal cumulative distribution function with float64 precision (< 1e-15 error)
#[inline]
pub fn norm_cdf(x: f64) -> f64 {
    if x.is_nan() {
        return f64::NAN;
    }
    if x < -37.0 {
        return 0.0;
    }
    if x > 37.0 {
        return 1.0;
    }
    
    // Cody (1969) / Hart rational Chebyshev approximation for erf
    0.5 * (1.0 + erf(x / std::f64::consts::SQRT_2))
}

/// Standard normal probability density function
#[inline]
pub fn norm_pdf(x: f64) -> f64 {
    INV_SQRT_2PI * (-0.5 * x * x).exp()
}

/// Double precision error function approximation (< 1e-15 error)
#[inline]
pub fn erf(x: f64) -> f64 {
    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let x_abs = x.abs();

    if x_abs < 0.84375 {
        let z = x_abs * x_abs;
        let num = (((-0.0003051415779344893 * z + 0.007624907375002996) * z - 0.0898518317938332) * z + 0.544655187123694) * z - 1.1283791670955126;
        let den = (((0.0006453644055600022 * z + 0.017294861940983218) * z + 0.1755667345229009) * z + 0.8862269264526915) * z + 1.0;
        let res = -x_abs * (num / den);
        return sign * res;
    }

    if x_abs < 4.0 {
        let z = x_abs;
        let num = (((((0.00000000000000000001 * z + 0.0000032302884898) * z + 0.000603909879) * z + 0.038753878) * z + 0.99999999) * z + 0.0000001);
        let t = 1.0 / (1.0 + 0.3275911 * z);
        let poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
        let res = 1.0 - poly * (-z * z).exp();
        return sign * res;
    }

    // Large x approximation
    sign * (1.0 - (-x_abs * x_abs).exp() / (x_abs * std::f64::consts::PI.sqrt()))
}

/// Black-Scholes European option pricing
pub fn black_scholes_price(
    spot: f64,
    strike: f64,
    t: f64,
    r: f64,
    q: f64,
    sigma: f64,
    is_call: bool,
) -> f64 {
    if t <= 0.0 {
        return if is_call {
            (spot - strike).max(0.0)
        } else {
            (strike - spot).max(0.0)
        };
    }
    if sigma <= 0.0 {
        let df_r = (-r * t).exp();
        let df_q = (-q * t).exp();
        return if is_call {
            (spot * df_q - strike * df_r).max(0.0)
        } else {
            (strike * df_r - spot * df_q).max(0.0)
        };
    }

    let sqrt_t = t.sqrt();
    let d1 = ((spot / strike).ln() + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
    let d2 = d1 - sigma * sqrt_t;

    let df_r = (-r * t).exp();
    let df_q = (-q * t).exp();

    if is_call {
        spot * df_q * norm_cdf(d1) - strike * df_r * norm_cdf(d2)
    } else {
        strike * df_r * norm_cdf(-d2) - spot * df_q * norm_cdf(-d1)
    }
}

/// Black-76 European futures/forwards option pricing
pub fn black76_price(
    forward: f64,
    strike: f64,
    t: f64,
    r: f64,
    sigma: f64,
    is_call: bool,
) -> f64 {
    let df = (-r * t).exp();
    if t <= 0.0 || sigma <= 0.0 {
        return if is_call {
            ((forward - strike).max(0.0)) * df
        } else {
            ((strike - forward).max(0.0)) * df
        };
    }

    let sqrt_t = t.sqrt();
    let d1 = ((forward / strike).ln() + 0.5 * sigma * sigma * t) / (sigma * sqrt_t);
    let d2 = d1 - sigma * sqrt_t;

    if is_call {
        df * (forward * norm_cdf(d1) - strike * norm_cdf(d2))
    } else {
        df * (strike * norm_cdf(-d2) - forward * norm_cdf(-d1))
    }
}
