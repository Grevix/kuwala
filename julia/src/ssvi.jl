# Kuwala Julia SSVI & Arbitrage Diagnostics Module

struct SsviParameters
    rho::Float64
    eta::Float64
    gamma::Float64
    theta_map::Dict{Float64, Float64}
end

"""
    ssvi_total_variance(k, theta, rho, eta, gamma) -> Float64
Gatheral & Jacquier (2014) Surface SVI total implied variance w(k, theta).
"""
function ssvi_total_variance(k::Real, theta::Real, rho::Real, eta::Real, gamma::Real)::Float64
    phi = (theta <= 1e-8) ? eta : (eta / (theta^gamma))
    phi_k = phi * Float64(k)
    rad = sqrt(max(0.0, (phi_k + rho)^2 + (1.0 - rho^2)))
    return 0.5 * Float64(theta) * (1.0 + rho * phi_k + rad)
end

"""
    durrleman_g(k, w, dw_dk, d2w_dk2) -> Float64
Durrleman's second-derivative non-arbitrage condition g(k) >= 0.
"""
function durrleman_g(k::Real, w::Real, dw::Real, d2w::Real)::Float64
    if w <= 1e-12
        return 1.0
    end
    t1 = 1.0 - (Float64(k) * Float64(dw)) / (2.0 * Float64(w))
    t2 = (Float64(dw)^2 / 4.0) * (1.0 / Float64(w) + 0.25)
    t3 = 0.5 * Float64(d2w)
    return t1^2 - t2 + t3
end
