use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ButterflyViolation {
    pub log_moneyness: f64,
    pub g_value: f64,
    pub total_variance: f64,
    pub strike: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CalendarViolation {
    pub log_moneyness: f64,
    pub expiry_1: f64,
    pub expiry_2: f64,
    pub total_var_1: f64,
    pub total_var_2: f64,
    pub strike: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SliceDiagnosticReport {
    pub expiry: f64,
    pub butterfly_arbitrage_passed: bool,
    pub min_g_value: f64,
    pub violations: Vec<ButterflyViolation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SurfaceDiagnosticReport {
    pub is_arbitrage_free: bool,
    pub butterfly_passed: bool,
    pub calendar_passed: bool,
    pub slice_reports: Vec<SliceDiagnosticReport>,
    pub calendar_violations: Vec<CalendarViolation>,
}

/// Compute Durrleman's g(k) condition for a single point on a variance slice
/// g(k) = (1 - k*w'/(2w))^2 - (w'^2 / 4)*(1/w + 1/4) + w''/2
#[inline]
pub fn durrleman_g(k: f64, w: f64, dw: f64, d2w: f64) -> f64 {
    if w <= 1e-12 {
        return -1.0;
    }
    let term1 = 1.0 - (k * dw) / (2.0 * w);
    let term1_sq = term1 * term1;
    let term2 = (dw * dw / 4.0) * (1.0 / w + 0.25);
    let term3 = 0.5 * d2w;

    term1_sq - term2 + term3
}

/// Check butterfly arbitrage on a grid of log-moneyness for given w, w', w''
pub fn check_slice_butterfly(
    expiry: f64,
    k_grid: &[f64],
    w_grid: &[f64],
    dw_grid: &[f64],
    d2w_grid: &[f64],
    spot: Option<f64>,
) -> SliceDiagnosticReport {
    let mut min_g = f64::INFINITY;
    let mut violations = Vec::new();

    for i in 0..k_grid.len() {
        let k = k_grid[i];
        let w = w_grid[i];
        let dw = dw_grid[i];
        let d2w = d2w_grid[i];

        let g = durrleman_g(k, w, dw, d2w);
        if g < min_g {
            min_g = g;
        }

        if g < -1e-7 || w <= 0.0 {
            let strike = spot.map(|s| s * k.exp());
            violations.push(ButterflyViolation {
                log_moneyness: k,
                g_value: g,
                total_variance: w,
                strike,
            });
        }
    }

    SliceDiagnosticReport {
        expiry,
        butterfly_arbitrage_passed: violations.is_empty(),
        min_g_value: if min_g.is_infinite() { 0.0 } else { min_g },
        violations,
    }
}

/// Check calendar arbitrage across two expiries T1 < T2 at identical log-moneyness grid points
pub fn check_calendar_arbitrage(
    t1: f64,
    t2: f64,
    k_grid: &[f64],
    w_grid_1: &[f64],
    w_grid_2: &[f64],
    spot: Option<f64>,
) -> Vec<CalendarViolation> {
    let mut violations = Vec::new();
    for i in 0..k_grid.len() {
        let k = k_grid[i];
        let w1 = w_grid_1[i];
        let w2 = w_grid_2[i];

        if w2 < w1 - 1e-7 {
            let strike = spot.map(|s| s * k.exp());
            violations.push(CalendarViolation {
                log_moneyness: k,
                expiry_1: t1,
                expiry_2: t2,
                total_var_1: w1,
                total_var_2: w2,
                strike,
            });
        }
    }
    violations
}
