#pragma once

#include <cmath>
#include <numbers>
#include <algorithm>
#include <span>
#include <vector>

namespace kuwala::cpp {

constexpr double INV_SQRT_2PI = 0.39894228040143267793994605993438;
constexpr double SQRT_2 = 1.4142135623730950488016887242097;

/// High-precision Standard Normal CDF via std::erfc / std::erf
[[nodiscard]] inline double norm_cdf(double x) noexcept {
    return 0.5 * std::erfc(-x / SQRT_2);
}

/// Standard Normal Probability Density Function
[[nodiscard]] inline double norm_pdf(double x) noexcept {
    return INV_SQRT_2PI * std::exp(-0.5 * x * x);
}

/// Black-Scholes European Option Analytical Formula
[[nodiscard]] inline double black_scholes(
    double spot,
    double strike,
    double t,
    double r,
    double q,
    double sigma,
    bool is_call = true
) noexcept {
    if (t <= 0.0) {
        return is_call ? std::max(0.0, spot - strike) : std::max(0.0, strike - spot);
    }
    if (sigma <= 0.0) {
        double df_r = std::exp(-r * t);
        double df_q = std::exp(-q * t);
        return is_call ? std::max(0.0, spot * df_q - strike * df_r)
                       : std::max(0.0, strike * df_r - spot * df_q);
    }
    if (spot <= 0.0) {
        return is_call ? 0.0 : strike * std::exp(-r * t);
    }
    if (strike <= 0.0) {
        return is_call ? spot * std::exp(-q * t) : 0.0;
    }

    double df_r = std::exp(-r * t);
    double df_q = std::exp(-q * t);
    double sqrt_t = std::sqrt(t);
    double d1 = (std::log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrt_t);
    double d2 = d1 - sigma * sqrt_t;

    if (is_call) {
        return spot * df_q * norm_cdf(d1) - strike * df_r * norm_cdf(d2);
    } else {
        return strike * df_r * norm_cdf(-d2) - spot * df_q * norm_cdf(-d1);
    }
}

/// Black-76 Futures / Commodity Option Analytical Formula
[[nodiscard]] inline double black76(
    double forward,
    double strike,
    double t,
    double r,
    double sigma,
    bool is_call = true
) noexcept {
    if (t <= 0.0) {
        return is_call ? std::max(0.0, forward - strike) : std::max(0.0, strike - forward);
    }
    if (sigma <= 0.0) {
        double df = std::exp(-r * t);
        return is_call ? df * std::max(0.0, forward - strike) : df * std::max(0.0, strike - forward);
    }
    double df = std::exp(-r * t);
    double sqrt_t = std::sqrt(t);
    double d1 = (std::log(forward / strike) + 0.5 * sigma * sigma * t) / (sigma * sqrt_t);
    double d2 = d1 - sigma * sqrt_t;

    if (is_call) {
        return df * (forward * norm_cdf(d1) - strike * norm_cdf(d2));
    } else {
        return df * (strike * norm_cdf(-d2) - forward * norm_cdf(-d1));
    }
}

/// Vectorized Batch Black-Scholes (Contiguous memory, zero dynamic allocation)
inline void black_scholes_batch(
    std::span<const double> spots,
    std::span<const double> strikes,
    std::span<const double> ttms,
    std::span<const double> rates,
    std::span<const double> divs,
    std::span<const double> sigmas,
    std::span<const uint8_t> is_calls,
    std::span<double> out_prices
) noexcept {
    const size_t n = spots.size();
    for (size_t i = 0; i < n; ++i) {
        out_prices[i] = black_scholes(
            spots[i],
            strikes[i],
            ttms[i],
            rates[i],
            divs[i],
            sigmas[i],
            is_calls[i] != 0
        );
    }
}

} // namespace kuwala::cpp
