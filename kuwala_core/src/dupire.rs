use crate::diagnostics::durrleman_g;

/// Compute Dupire local volatility at log-moneyness k and expiry T from total variance and its partial derivatives
/// sigma_loc^2(k, T) = (dw/dT) / g(k, T)
/// where g(k, T) is Durrleman's condition
pub fn dupire_local_variance_from_total_variance(
    k: f64,
    w: f64,
    dw_dk: f64,
    d2w_dk2: f64,
    dw_dt: f64,
) -> Result<f64, String> {
    if w <= 1e-12 {
        return Err("Total variance must be strictly positive".to_string());
    }
    if dw_dt < -1e-7 {
        return Err(format!(
            "Calendar arbitrage violation at k={:.4}: dw/dT = {:.6e} < 0",
            k, dw_dt
        ));
    }

    let g = durrleman_g(k, w, dw_dk, d2w_dk2);
    if g <= 1e-7 {
        return Err(format!(
            "Butterfly arbitrage violation at k={:.4}: Durrleman g = {:.6e} <= 0",
            k, g
        ));
    }

    let local_var = dw_dt / g;
    if local_var < 0.0 {
        return Err(format!("Computed negative local variance: {}", local_var));
    }

    Ok(local_var)
}

/// Compute Dupire local volatility sigma_loc(k, T) = sqrt(local_var)
pub fn dupire_local_volatility_from_total_variance(
    k: f64,
    w: f64,
    dw_dk: f64,
    d2w_dk2: f64,
    dw_dt: f64,
) -> Result<f64, String> {
    let loc_var = dupire_local_variance_from_total_variance(k, w, dw_dk, d2w_dk2, dw_dt)?;
    Ok(loc_var.sqrt())
}
