use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RawSviParams {
    pub a: f64,
    pub b: f64,
    pub rho: f64,
    pub m: f64,
    pub sigma: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SsviParams {
    pub rho: f64,
    pub eta: f64,
    pub gamma: f64,
}

/// Compute total implied variance w(k) from Raw SVI parameterization
/// w(k) = a + b * (rho * (k - m) + sqrt((k - m)^2 + sigma^2))
#[inline]
pub fn raw_svi_total_variance(k: f64, a: f64, b: f64, rho: f64, m: f64, sigma: f64) -> f64 {
    let dk = k - m;
    let disc = (dk * dk + sigma * sigma).sqrt();
    a + b * (rho * dk + disc)
}

/// SSVI power-law phi function: phi(theta) = eta / (theta^gamma)
#[inline]
pub fn ssvi_phi_power_law(theta: f64, eta: f64, gamma: f64) -> f64 {
    if theta <= 1e-8 {
        return eta;
    }
    eta / theta.powf(gamma)
}

/// Compute total implied variance w(k, theta) from SSVI parameterization
/// w(k, theta) = (theta / 2) * (1 + rho * phi(theta) * k + sqrt((phi(theta) * k + rho)^2 + (1 - rho^2)))
pub fn ssvi_total_variance(k: f64, theta: f64, rho: f64, eta: f64, gamma: f64) -> f64 {
    if theta <= 1e-8 {
        return 0.0;
    }
    let phi = ssvi_phi_power_law(theta, eta, gamma);
    let phi_k = phi * k;
    let radical = ((phi_k + rho).powi(2) + (1.0 - rho * rho)).max(0.0).sqrt();
    0.5 * theta * (1.0 + rho * phi_k + radical)
}

/// Derivative dw/dk for SSVI
pub fn ssvi_dw_dk(k: f64, theta: f64, rho: f64, eta: f64, gamma: f64) -> f64 {
    if theta <= 1e-8 {
        return 0.0;
    }
    let phi = ssvi_phi_power_law(theta, eta, gamma);
    let phi_k = phi * k;
    let radical = ((phi_k + rho).powi(2) + (1.0 - rho * rho)).max(1e-12).sqrt();
    0.5 * theta * phi * (rho + (phi_k + rho) / radical)
}

/// Second derivative d2w/dk2 for SSVI
pub fn ssvi_d2w_dk2(k: f64, theta: f64, rho: f64, eta: f64, gamma: f64) -> f64 {
    if theta <= 1e-8 {
        return 0.0;
    }
    let phi = ssvi_phi_power_law(theta, eta, gamma);
    let phi_k = phi * k;
    let radical_sq = (phi_k + rho).powi(2) + (1.0 - rho * rho);
    let radical_cubed = radical_sq.max(1e-12).powf(1.5);
    0.5 * theta * phi * phi * (1.0 - rho * rho) / radical_cubed
}
