pub mod diagnostics;
pub mod dupire;
pub mod greeks;
pub mod iv;
pub mod pricing;
pub mod svi;

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

/// Black-Scholes European option pricing
#[pyfunction]
#[pyo3(signature = (spot, strike, t, r, q, sigma, is_call=true))]
fn py_black_scholes(
    spot: f64,
    strike: f64,
    t: f64,
    r: f64,
    q: f64,
    sigma: f64,
    is_call: bool,
) -> PyResult<f64> {
    Ok(pricing::black_scholes_price(
        spot, strike, t, r, q, sigma, is_call,
    ))
}

/// Black-76 European futures option pricing
#[pyfunction]
#[pyo3(signature = (forward, strike, t, r, sigma, is_call=true))]
fn py_black76(
    forward: f64,
    strike: f64,
    t: f64,
    r: f64,
    sigma: f64,
    is_call: bool,
) -> PyResult<f64> {
    Ok(pricing::black76_price(
        forward, strike, t, r, sigma, is_call,
    ))
}

/// Compute 1st and 2nd order Greeks
#[pyfunction]
#[pyo3(signature = (spot, strike, t, r, q, sigma, is_call=true))]
fn py_greeks<'py>(
    py: Python<'py>,
    spot: f64,
    strike: f64,
    t: f64,
    r: f64,
    q: f64,
    sigma: f64,
    is_call: bool,
) -> PyResult<Bound<'py, PyDict>> {
    let g = greeks::calculate_greeks(spot, strike, t, r, q, sigma, is_call);
    let dict = PyDict::new(py);
    dict.set_item("delta", g.delta)?;
    dict.set_item("gamma", g.gamma)?;
    dict.set_item("vega", g.vega)?;
    dict.set_item("theta", g.theta)?;
    dict.set_item("rho", g.rho)?;
    dict.set_item("vanna", g.vanna)?;
    dict.set_item("volga", g.volga)?;
    dict.set_item("charm", g.charm)?;
    Ok(dict)
}

/// Solve implied volatility for a single option
#[pyfunction]
#[pyo3(signature = (price, spot, strike, t, r, q, is_call=true, initial_guess=None, tol=1e-8, max_iter=100))]
fn py_implied_volatility(
    price: f64,
    spot: f64,
    strike: f64,
    t: f64,
    r: f64,
    q: f64,
    is_call: bool,
    initial_guess: Option<f64>,
    tol: f64,
    max_iter: usize,
) -> PyResult<f64> {
    iv::implied_volatility_single(
        price,
        spot,
        strike,
        t,
        r,
        q,
        is_call,
        initial_guess,
        tol,
        max_iter,
    )
    .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
}

/// Batch solve implied volatilities in parallel via Rayon
#[pyfunction]
#[pyo3(signature = (prices, spots, strikes, times, rates, divs, is_calls, initial_guesses=None, tol=1e-8, max_iter=100))]
fn py_implied_volatility_batch<'py>(
    py: Python<'py>,
    prices: Vec<f64>,
    spots: Vec<f64>,
    strikes: Vec<f64>,
    times: Vec<f64>,
    rates: Vec<f64>,
    divs: Vec<f64>,
    is_calls: Vec<bool>,
    initial_guesses: Option<Vec<f64>>,
    tol: f64,
    max_iter: usize,
) -> PyResult<Bound<'py, PyList>> {
    let guesses_slice = initial_guesses.as_deref();
    let results = iv::implied_volatility_batch(
        &prices,
        &spots,
        &strikes,
        &times,
        &rates,
        &divs,
        &is_calls,
        guesses_slice,
        tol,
        max_iter,
    );

    let py_list = PyList::empty(py);
    for res in results {
        match res {
            Some(v) => py_list.append(v)?,
            None => py_list.append(py.None())?,
        }
    }
    Ok(py_list)
}

/// Raw SVI total implied variance
#[pyfunction]
fn py_raw_svi_total_variance(k: f64, a: f64, b: f64, rho: f64, m: f64, sigma: f64) -> PyResult<f64> {
    Ok(svi::raw_svi_total_variance(k, a, b, rho, m, sigma))
}

/// SSVI total implied variance
#[pyfunction]
fn py_ssvi_total_variance(k: f64, theta: f64, rho: f64, eta: f64, gamma: f64) -> PyResult<f64> {
    Ok(svi::ssvi_total_variance(k, theta, rho, eta, gamma))
}

/// Durrleman g(k) value
#[pyfunction]
fn py_durrleman_g(k: f64, w: f64, dw: f64, d2w: f64) -> PyResult<f64> {
    Ok(diagnostics::durrleman_g(k, w, dw, d2w))
}

/// Dupire local volatility from total variance and partial derivatives
#[pyfunction]
fn py_dupire_local_volatility(k: f64, w: f64, dw_dk: f64, d2w_dk2: f64, dw_dt: f64) -> PyResult<f64> {
    dupire::dupire_local_volatility_from_total_variance(k, w, dw_dk, d2w_dk2, dw_dt)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e))
}

/// Kuwala Rust core module
#[pymodule]
fn kuwala_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_black_scholes, m)?)?;
    m.add_function(wrap_pyfunction!(py_black76, m)?)?;
    m.add_function(wrap_pyfunction!(py_greeks, m)?)?;
    m.add_function(wrap_pyfunction!(py_implied_volatility, m)?)?;
    m.add_function(wrap_pyfunction!(py_implied_volatility_batch, m)?)?;
    m.add_function(wrap_pyfunction!(py_raw_svi_total_variance, m)?)?;
    m.add_function(wrap_pyfunction!(py_ssvi_total_variance, m)?)?;
    m.add_function(wrap_pyfunction!(py_durrleman_g, m)?)?;
    m.add_function(wrap_pyfunction!(py_dupire_local_volatility, m)?)?;
    Ok(())
}
