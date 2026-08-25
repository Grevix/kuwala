use crate::greeks::calculate_greeks;
use crate::pricing::black_scholes_price;
use rayon::prelude::*;

const MIN_VOL: f64 = 1e-6;
const MAX_VOL: f64 = 20.0; // 2000% vol max bound

/// Solve Implied Volatility using a hybrid Halley's method (cubic convergence) with Brent-Dekker fallback
pub fn implied_volatility_single(
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
) -> Result<f64, String> {
    if price <= 0.0 || spot <= 0.0 || strike <= 0.0 || t <= 0.0 {
        return Err("Invalid inputs: price, spot, strike, and time must be positive".to_string());
    }

    let df_r = (-r * t).exp();
    let df_q = (-q * t).exp();

    // Arbitrage bounds check
    let (intrinsic, upper_bound) = if is_call {
        let intr = (spot * df_q - strike * df_r).max(0.0);
        let max_p = spot * df_q;
        (intr, max_p)
    } else {
        let intr = (strike * df_r - spot * df_q).max(0.0);
        let max_p = strike * df_r;
        (intr, max_p)
    };

    if price < intrinsic - 1e-7 || price > upper_bound + 1e-7 {
        return Err(format!(
            "Option price {} violates no-arbitrage bounds [{}, {}]",
            price, intrinsic, upper_bound
        ));
    }

    // Initial guess using Brenner-Subrahmanyam approximation if not provided
    let mut sigma = match initial_guess {
        Some(g) if g > MIN_VOL && g < MAX_VOL => g,
        _ => {
            let approx = (2.0 * std::f64::consts::PI / t).sqrt() * (price / spot);
            if approx > MIN_VOL && approx < 2.0 {
                approx
            } else {
                0.30 // 30% default starting point
            }
        }
    };

    // Phase 1: Try Halley's method (uses Vega and Volga for cubic step)
    for _ in 0..max_iter {
        let p_current = black_scholes_price(spot, strike, t, r, q, sigma, is_call);
        let diff = p_current - price;
        if diff.abs() < tol {
            return Ok(sigma);
        }

        let greeks = calculate_greeks(spot, strike, t, r, q, sigma, is_call);
        let vega = greeks.vega;
        let volga = greeks.volga;

        if vega.abs() < 1e-12 {
            // Near-zero vega: fallback to Brent-Dekker bracketing
            break;
        }

        // Halley step: delta_sigma = diff / (vega - 0.5 * diff * volga / vega)
        let denom = vega - 0.5 * diff * volga / vega;
        let step = if denom.abs() > 1e-12 {
            diff / denom
        } else {
            diff / vega // fallback to Newton step
        };

        let next_sigma = sigma - step;
        if next_sigma <= MIN_VOL || next_sigma >= MAX_VOL || step.is_nan() {
            // Out of bounds: fall back to Brent
            break;
        }

        if (next_sigma - sigma).abs() < tol {
            return Ok(next_sigma);
        }
        sigma = next_sigma;
    }

    // Phase 2: Brent-Dekker root finding on [MIN_VOL, MAX_VOL]
    brent_iv_solver(price, spot, strike, t, r, q, is_call, tol, max_iter * 2)
}

/// Robust Brent-Dekker 1D root finder for IV
fn brent_iv_solver(
    target_price: f64,
    spot: f64,
    strike: f64,
    t: f64,
    r: f64,
    q: f64,
    is_call: bool,
    tol: f64,
    max_iter: usize,
) -> Result<f64, String> {
    let f = |sigma: f64| black_scholes_price(spot, strike, t, r, q, sigma, is_call) - target_price;

    let mut a = MIN_VOL;
    let mut b = MAX_VOL;
    let mut fa = f(a);
    let mut fb = f(b);

    if fa * fb > 0.0 {
        return Err(format!(
            "Root not bracketed in [{}, {}]: f(a)={}, f(b)={}",
            MIN_VOL, MAX_VOL, fa, fb
        ));
    }

    if fa.abs() < fb.abs() {
        std::mem::swap(&mut a, &mut b);
        std::mem::swap(&mut fa, &mut fb);
    }

    let mut c = a;
    let mut fc = fa;
    let mut mflag = true;
    let mut d = 0.0;

    for _ in 0..max_iter {
        if fa.abs() < tol || fb.abs() < tol || (b - a).abs() < tol {
            return Ok(b);
        }

        let mut s = if (fa - fc).abs() > 1e-14 && (fb - fc).abs() > 1e-14 {
            // Inverse quadratic interpolation
            (a * fb * fc) / ((fa - fb) * (fa - fc))
                + (b * fa * fc) / ((fb - fa) * (fb - fc))
                + (c * fa * fb) / ((fc - fa) * (fc - fb))
        } else {
            // Secant method
            b - fb * (b - a) / (fb - fa)
        };

        // Conditions to check whether to accept interpolation or use bisection
        let cond1 = (s < (3.0 * a + b) / 4.0 && s > b) || (s > (3.0 * a + b) / 4.0 && s < b);
        let cond2 = mflag && (s - b).abs() >= (b - c).abs() / 2.0;
        let cond3 = !mflag && (s - b).abs() >= (c - d).abs() / 2.0;
        let cond4 = mflag && (b - c).abs() < tol;
        let cond5 = !mflag && (c - d).abs() < tol;

        if cond1 || cond2 || cond3 || cond4 || cond5 {
            s = (a + b) / 2.0;
            mflag = true;
        } else {
            mflag = false;
        }

        let fs = f(s);
        d = c;
        c = b;
        fc = fb;

        if fa * fs < 0.0 {
            b = s;
            fb = fs;
        } else {
            a = s;
            fa = fs;
        }

        if fa.abs() < fb.abs() {
            std::mem::swap(&mut a, &mut b);
            std::mem::swap(&mut fa, &mut fb);
        }
    }

    Ok(b)
}

/// Rayon-parallelized batch implied volatility calculation
pub fn implied_volatility_batch(
    prices: &[f64],
    spots: &[f64],
    strikes: &[f64],
    times: &[f64],
    rates: &[f64],
    divs: &[f64],
    is_calls: &[bool],
    initial_guesses: Option<&[f64]>,
    tol: f64,
    max_iter: usize,
) -> Vec<Option<f64>> {
    let n = prices.len();
    (0..n)
        .into_par_iter()
        .map(|i| {
            let guess = initial_guesses.and_then(|g| g.get(i).copied());
            implied_volatility_single(
                prices[i],
                spots[i],
                strikes[i],
                times[i],
                rates[i],
                divs[i],
                is_calls[i],
                guess,
                tol,
                max_iter,
            )
            .ok()
        })
        .collect()
}
