#pragma once

#include "pricing.hpp"

namespace kuwala::cpp {

struct OptionGreeks {
    double delta{0.0};
    double gamma{0.0};
    double vega{0.0};
    double theta{0.0};
    double rho{0.0};
    double vanna{0.0};
    double volga{0.0};
    double charm{0.0};
};

/// Analytical 1st and 2nd Order Greeks for European Options
[[nodiscard]] inline OptionGreeks greeks(
    double spot,
    double strike,
    double t,
    double r,
    double q,
    double sigma,
    bool is_call = true
) noexcept {
    OptionGreeks g{};
    if (t <= 1e-12 || sigma <= 1e-12 || spot <= 1e-12 || strike <= 1e-12) {
        if (is_call) {
            g.delta = spot > strike ? 1.0 : (spot == strike ? 0.5 : 0.0);
        } else {
            g.delta = spot < strike ? -1.0 : (spot == strike ? -0.5 : 0.0);
        }
        return g;
    }

    double sqrt_t = std::sqrt(t);
    double df_r = std::exp(-r * t);
    double df_q = std::exp(-q * t);
    double d1 = (std::log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
    double d2 = d1 - sigma * sqrt_t;
    double n_prime_d1 = norm_pdf(d1);

    // Delta
    g.delta = is_call ? df_q * norm_cdf(d1) : df_q * (norm_cdf(d1) - 1.0);

    // Gamma
    g.gamma = df_q * n_prime_d1 / (spot * sigma * sqrt_t);

    // Vega (per 100% vol change)
    g.vega = spot * df_q * n_prime_d1 * sqrt_t;

    // Theta (annualized)
    double term1 = -(spot * df_q * n_prime_d1 * sigma) / (2.0 * sqrt_t);
    if (is_call) {
        g.theta = term1 - r * strike * df_r * norm_cdf(d2) + q * spot * df_q * norm_cdf(d1);
    } else {
        g.theta = term1 + r * strike * df_r * norm_cdf(-d2) - q * spot * df_q * norm_cdf(-d1);
    }

    // Rho
    g.rho = is_call ? strike * t * df_r * norm_cdf(d2) : -strike * t * df_r * norm_cdf(-d2);

    // Vanna: dVega/dSpot = dDelta/dVol
    g.vanna = -df_q * n_prime_d1 * d2 / sigma;

    // Volga / Vomma: dVega/dVol
    g.volga = g.vega * d1 * d2 / sigma;

    // Charm: dDelta/dt
    double charm_base = df_q * n_prime_d1 * (2.0 * (r - q) * t - d2 * sigma * sqrt_t) / (2.0 * t * sigma * sqrt_t);
    g.charm = is_call ? q * df_q * norm_cdf(d1) - charm_base : -q * df_q * norm_cdf(-d1) - charm_base;

    return g;
}

} // namespace kuwala::cpp
