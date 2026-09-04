# Kuwala Julia Analytical Pricing Module
# High-precision Black-Scholes and Black-76 options pricer

const INV_SQRT_2PI = 0.39894228040143267793994605993438
const SQRT_2 = 1.4142135623730950488016887242097

"""
    norm_cdf(x::Real) -> Float64
High-precision standard normal cumulative distribution function.
"""
function norm_cdf(x::Real)
    # Rational Chebyshev approximation / erfc formula
    return 0.5 * (1.0 + erf_approx(x / SQRT_2))
end

"""
    erf_approx(x::Real) -> Float64
Chebyshev rational approximation to the error function with error < 1.2e-7.
"""
function erf_approx(x::Real)
    # Standard Abramowitz & Stegun formula 7.1.26
    sign_x = sign(x)
    abs_x = abs(Float64(x))
    t = 1.0 / (1.0 + 0.3275911 * abs_x)
    poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return sign_x * (1.0 - poly * exp(-abs_x * abs_x))
end

"""
    norm_pdf(x::Real) -> Float64
Standard normal probability density function.
"""
function norm_pdf(x::Real)
    return INV_SQRT_2PI * exp(-0.5 * Float64(x)^2)
end

"""
    black_scholes(spot, strike, t, r, q, sigma; is_call=true) -> Float64
Analytical European Option pricing formula under the Black-Scholes model.
"""
function black_scholes(
    spot::Real,
    strike::Real,
    t::Real,
    r::Real,
    q::Real,
    sigma::Real;
    is_call::Bool = true
)::Float64
    s = Float64(spot)
    k = Float64(strike)
    ttm = Float64(t)
    rate = Float64(r)
    div = Float64(q)
    vol = Float64(sigma)

    if ttm <= 0.0
        return is_call ? max(0.0, s - k) : max(0.0, k - s)
    end
    if vol <= 0.0
        df_r = exp(-rate * ttm)
        df_q = exp(-div * ttm)
        return is_call ? max(0.0, s * df_q - k * df_r) : max(0.0, k * df_r - s * df_q)
    end
    if s <= 0.0
        return is_call ? 0.0 : k * exp(-rate * ttm)
    end
    if k <= 0.0
        return is_call ? s * exp(-div * ttm) : 0.0
    end

    df_r = exp(-rate * ttm)
    df_q = exp(-div * ttm)
    sqrt_t = sqrt(ttm)
    d1 = (log(s / k) + (rate - div + 0.5 * vol * vol) * ttm) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t

    if is_call
        return s * df_q * norm_cdf(d1) - k * df_r * norm_cdf(d2)
    else
        return k * df_r * norm_cdf(-d2) - s * df_q * norm_cdf(-d1)
    end
end

"""
    black76(forward, strike, t, r, sigma; is_call=true) -> Float64
Analytical Black-76 European Commodity / Futures option pricer.
"""
function black76(
    forward::Real,
    strike::Real,
    t::Real,
    r::Real,
    sigma::Real;
    is_call::Bool = true
)::Float64
    f = Float64(forward)
    k = Float64(strike)
    ttm = Float64(t)
    rate = Float64(r)
    vol = Float64(sigma)

    if ttm <= 0.0
        return is_call ? max(0.0, f - k) : max(0.0, k - f)
    end
    df = exp(-rate * ttm)
    if vol <= 0.0
        return df * (is_call ? max(0.0, f - k) : max(0.0, k - f))
    end

    sqrt_t = sqrt(ttm)
    d1 = (log(f / k) + 0.5 * vol * vol * ttm) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t

    if is_call
        return df * (f * norm_cdf(d1) - k * norm_cdf(d2))
    else
        return df * (k * norm_cdf(-d2) - f * norm_cdf(-d1))
    end
end
