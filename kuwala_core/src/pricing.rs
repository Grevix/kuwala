const INV_SQRT_2PI: f64 = 0.398942280401432677939946059934;

/// Standard normal cumulative distribution function (Abramowitz and Stegun approximation with high accuracy)
#[inline]
pub fn norm_cdf(x: f64) -> f64 {
    if x.is_nan() {
        return f64::NAN;
    }
    // Erf based standard normal CDF
    0.5 * (1.0 + erf(x / std::f64::consts::SQRT_2))
}

/// Standard normal probability density function
#[inline]
pub fn norm_pdf(x: f64) -> f64 {
    INV_SQRT_2PI * (-0.5 * x * x).exp()
}

/// Error function approximation (Chebyshev fitting with precision ~ 1.5e-7 or exact erf)
#[inline]
pub fn erf(x: f64) -> f64 {
    // Standard numerical approximation for erf(x) with maximum error 1.2e-7
    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let x_abs = x.abs();

    // Coefficients
    let a1 = 0.254829592;
    let a2 = -0.284496736;
    let a3 = 1.421413741;
    let a4 = -1.453152027;
    let a5 = 1.061405429;
    let p = 0.3275911;

    let t = 1.0 / (1.0 + p * x_abs);
    let poly = ((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t;
    let y = 1.0 - poly * (-x_abs * x_abs).exp();

    sign * y
}

/// Black-Scholes European option pricing
/// spot: Current spot price S
/// strike: Strike price K
/// t: Time to expiration in years T
/// r: Risk-free interest rate
/// q: Continuous dividend yield / borrow cost
/// sigma: Volatility
/// is_call: true for Call, false for Put
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
        let forward = spot * ((r - q) * t).exp();
        let discount = (-r * t).exp();
        return if is_call {
            discount * (forward - strike).max(0.0)
        } else {
            discount * (strike - forward).max(0.0)
        };
    }

    let sqrt_t = t.sqrt();
    let vol_sqrt_t = sigma * sqrt_t;
    let d1 = ((spot / strike).ln() + (r - q + 0.5 * sigma * sigma) * t) / vol_sqrt_t;
    let d2 = d1 - vol_sqrt_t;

    let df_r = (-r * t).exp();
    let df_q = (-q * t).exp();

    if is_call {
        spot * df_q * norm_cdf(d1) - strike * df_r * norm_cdf(d2)
    } else {
        strike * df_r * norm_cdf(-d2) - spot * df_q * norm_cdf(-d1)
    }
}

/// Black-76 European futures/forward option pricing
pub fn black76_price(
    forward: f64,
    strike: f64,
    t: f64,
    r: f64,
    sigma: f64,
    is_call: bool,
) -> f64 {
    if t <= 0.0 {
        return if is_call {
            (forward - strike).max(0.0)
        } else {
            (strike - forward).max(0.0)
        };
    }
    if sigma <= 0.0 {
        let discount = (-r * t).exp();
        return if is_call {
            discount * (forward - strike).max(0.0)
        } else {
            discount * (strike - forward).max(0.0)
        };
    }

    let sqrt_t = t.sqrt();
    let vol_sqrt_t = sigma * sqrt_t;
    let d1 = ((forward / strike).ln() + 0.5 * sigma * sigma * t) / vol_sqrt_t;
    let d2 = d1 - vol_sqrt_t;
    let discount = (-r * t).exp();

    if is_call {
        discount * (forward * norm_cdf(d1) - strike * norm_cdf(d2))
    } else {
        discount * (strike * norm_cdf(-d2) - forward * norm_cdf(-d1))
    }
}
