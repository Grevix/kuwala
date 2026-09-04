# Kuwala Julia Implied Volatility Solver Module

"""
    implied_volatility(target_price, spot, strike, t, r, q; is_call=true, tol=1e-8, max_iter=100) -> Float64
High-performance hybrid Halley's method with Brent-Dekker fallback for implied volatility inversion.
"""
function implied_volatility(
    target_price::Real,
    spot::Real,
    strike::Real,
    t::Real,
    r::Real,
    q::Real;
    is_call::Bool = true,
    tol::Float64 = 1e-8,
    max_iter::Int = 100
)::Float64
    p_target = Float64(target_price)
    s = Float64(spot)
    k = Float64(strike)
    ttm = Float64(t)
    rate = Float64(r)
    div = Float64(q)

    if ttm <= 1e-12 || s <= 1e-12 || k <= 1e-12
        return NaN
    end

    df_r = exp(-rate * ttm)
    df_q = exp(-div * ttm)
    intrinsic = is_call ? max(0.0, s * df_q - k * df_r) : max(0.0, k * df_r - s * df_q)

    if p_target < intrinsic - 1e-7
        return NaN
    end

    # Corrado-Miller initial guess
    fwd = s * exp((rate - div) * ttm)
    c_adj = p_target - 0.5 * (fwd - k) * df_r
    rad = c_adj * c_adj - (fwd - k) * (fwd - k) * df_r * df_r / π
    sigma = (rad > 0.0) ? (sqrt(2.0 * π / ttm) / (fwd + k)) * (c_adj + sqrt(rad)) : 0.25
    sigma = clamp(sigma, 0.01, 5.0)

    # 1. Halley's Method (Cubic convergence)
    for _ in 1:max_iter
        p = black_scholes(s, k, ttm, rate, div, sigma; is_call=is_call)
        diff = p - p_target
        if abs(diff) <= tol
            return sigma
        end

        gk = greeks(s, k, ttm, rate, div, sigma; is_call=is_call)
        vega = gk.vega
        volga = gk.volga

        if vega > 1e-10
            denom = vega - 0.5 * diff * (volga / vega)
            if abs(denom) > 1e-10
                step = -diff / denom
                next_sigma = sigma + step
                if next_sigma > 1e-4 && next_sigma < 10.0
                    sigma = next_sigma
                    continue
                end
            end
        end
        break # Fallback to bisection / Brent
    end

    # 2. Brent Fallback
    a, b = 1e-4, 8.0
    fa = black_scholes(s, k, ttm, rate, div, a; is_call=is_call) - p_target
    fb = black_scholes(s, k, ttm, rate, div, b; is_call=is_call) - p_target

    if fa * fb > 0.0
        return NaN
    end

    for _ in 1:100
        mid = 0.5 * (a + b)
        f_mid = black_scholes(s, k, ttm, rate, div, mid; is_call=is_call) - p_target
        if abs(f_mid) <= tol || (b - a) <= tol
            return mid
        end
        if fa * f_mid < 0.0
            b = mid
            fb = f_mid
        else
            a = mid
            fa = f_mid
        end
    end

    return 0.5 * (a + b)
end
