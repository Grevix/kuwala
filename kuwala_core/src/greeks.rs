use crate::pricing::{norm_cdf, norm_pdf};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Greeks {
    pub delta: f64,
    pub gamma: f64,
    pub vega: f64,
    pub theta: f64,
    pub rho: f64,
    pub vanna: f64,
    pub volga: f64,
    pub charm: f64,
}

/// Compute all major 1st and 2nd order analytical Greeks for European options under Black-Scholes
pub fn calculate_greeks(
    spot: f64,
    strike: f64,
    t: f64,
    r: f64,
    q: f64,
    sigma: f64,
    is_call: bool,
) -> Greeks {
    if t <= 1e-12 || sigma <= 1e-12 || spot <= 1e-12 || strike <= 1e-12 {
        let delta = if is_call {
            if spot > strike { 1.0 } else { 0.0 }
        } else {
            if spot < strike { -1.0 } else { 0.0 }
        };
        return Greeks {
            delta,
            gamma: 0.0,
            vega: 0.0,
            theta: 0.0,
            rho: 0.0,
            vanna: 0.0,
            volga: 0.0,
            charm: 0.0,
        };
    }

    let sqrt_t = t.sqrt();
    let vol_sqrt_t = sigma * sqrt_t;
    let d1 = ((spot / strike).ln() + (r - q + 0.5 * sigma * sigma) * t) / vol_sqrt_t;
    let d2 = d1 - vol_sqrt_t;

    let pdf_d1 = norm_pdf(d1);
    let cdf_d1 = norm_cdf(d1);
    let cdf_d2 = norm_cdf(d2);
    let df_r = (-r * t).exp();
    let df_q = (-q * t).exp();

    // 1st order
    let delta = if is_call {
        df_q * cdf_d1
    } else {
        df_q * (cdf_d1 - 1.0)
    };

    let gamma = (df_q * pdf_d1) / (spot * vol_sqrt_t);
    let vega = spot * df_q * sqrt_t * pdf_d1; // per 1.0 vol (divide by 100 for 1% vol point in UI if needed)

    let theta_common = -(spot * df_q * pdf_d1 * sigma) / (2.0 * sqrt_t);
    let theta = if is_call {
        theta_common - r * strike * df_r * cdf_d2 + q * spot * df_q * cdf_d1
    } else {
        theta_common + r * strike * df_r * norm_cdf(-d2) - q * spot * df_q * norm_cdf(-d1)
    };

    let rho = if is_call {
        strike * t * df_r * cdf_d2
    } else {
        -strike * t * df_r * norm_cdf(-d2)
    };

    // 2nd order cross / higher order
    let vanna = -df_q * pdf_d1 * d2 / sigma;
    let volga = vega * d1 * d2 / sigma;
    let charm = if is_call {
        q * df_q * cdf_d1 - df_q * pdf_d1 * (2.0 * (r - q) * t - d2 * vol_sqrt_t) / (2.0 * t * vol_sqrt_t)
    } else {
        -q * df_q * norm_cdf(-d1) - df_q * pdf_d1 * (2.0 * (r - q) * t - d2 * vol_sqrt_t) / (2.0 * t * vol_sqrt_t)
    };

    Greeks {
        delta,
        gamma,
        vega,
        theta,
        rho,
        vanna,
        volga,
        charm,
    }
}
