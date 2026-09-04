# Kuwala Julia Analytical Greeks Module

struct OptionGreeks
    delta::Float64
    gamma::Float64
    vega::Float64
    theta::Float64
    rho::Float64
    vanna::Float64
    volga::Float64
    charm::Float64
end

"""
    greeks(spot, strike, t, r, q, sigma; is_call=true) -> OptionGreeks
Analytical 1st and 2nd order Greeks: Delta, Gamma, Vega, Theta, Rho, Vanna, Volga, Charm.
"""
function greeks(
    spot::Real,
    strike::Real,
    t::Real,
    r::Real,
    q::Real,
    sigma::Real;
    is_call::Bool = true
)::OptionGreeks
    s = Float64(spot)
    k = Float64(strike)
    ttm = Float64(t)
    rate = Float64(r)
    div = Float64(q)
    vol = Float64(sigma)

    if ttm <= 1e-12 || vol <= 1e-12 || s <= 1e-12 || k <= 1e-12
        d = is_call ? (s > k ? 1.0 : (s == k ? 0.5 : 0.0)) : (s < k ? -1.0 : (s == k ? -0.5 : 0.0))
        return OptionGreeks(d, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    end

    sqrt_t = sqrt(ttm)
    df_r = exp(-rate * ttm)
    df_q = exp(-div * ttm)
    d1 = (log(s / k) + (rate - div + 0.5 * vol * vol) * ttm) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t
    n_prime_d1 = norm_pdf(d1)

    # 1st Order Greeks
    delta = is_call ? df_q * norm_cdf(d1) : df_q * (norm_cdf(d1) - 1.0)
    gamma = df_q * n_prime_d1 / (s * vol * sqrt_t)
    vega = s * df_q * n_prime_d1 * sqrt_t

    term1 = -(s * df_q * n_prime_d1 * vol) / (2.0 * sqrt_t)
    theta = is_call ? (term1 - rate * k * df_r * norm_cdf(d2) + div * s * df_q * norm_cdf(d1)) :
                      (term1 + rate * k * df_r * norm_cdf(-d2) - div * s * df_q * norm_cdf(-d1))

    rho = is_call ? k * ttm * df_r * norm_cdf(d2) : -k * ttm * df_r * norm_cdf(-d2)

    # 2nd Order Greeks
    vanna = -df_q * n_prime_d1 * d2 / vol
    volga = vega * d1 * d2 / vol
    charm_base = df_q * n_prime_d1 * (2.0 * (rate - div) * ttm - d2 * vol * sqrt_t) / (2.0 * ttm * vol * sqrt_t)
    charm = is_call ? (div * df_q * norm_cdf(d1) - charm_base) : (-div * df_q * norm_cdf(-d1) - charm_base)

    return OptionGreeks(delta, gamma, vega, theta, rho, vanna, volga, charm)
end
