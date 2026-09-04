#pragma once

#include "pricing.hpp"
#include "greeks.hpp"
#include <limits>
#include <stdexcept>

namespace kuwala::cpp {

/// High-Performance Implied Volatility Solver (Halley's Method + Brent Fallback)
[[nodiscard]] inline double implied_volatility(
    double target_price,
    double spot,
    double strike,
    double t,
    double r,
    double q,
    bool is_call = true,
    double tol = 1e-8,
    int max_iter = 100
) noexcept {
    if (t <= 1e-12 || spot <= 1e-12 || strike <= 1e-12) {
        return std::numeric_limits<double>::quiet_NaN();
    }

    double df_r = std::exp(-r * t);
    double df_q = std::exp(-q * t);
    double intrinsic = is_call ? std::max(0.0, spot * df_q - strike * df_r)
                               : std::max(0.0, strike * df_r - spot * df_q);

    if (target_price < intrinsic - 1e-7) {
        return std::numeric_limits<double>::quiet_NaN();
    }

    // Initial Volatility Guess: Corrado-Miller (1996) approximation
    double fwd = spot * std::exp((r - q) * t);
    double money = std::abs(fwd - strike);
    double c_adj = target_price - 0.5 * (fwd - strike) * df_r;
    double rad = c_adj * c_adj - (fwd - strike) * (fwd - strike) * df_r * df_r / std::numbers::pi;
    double sigma = (rad > 0.0) ? (std::sqrt(2.0 * std::numbers::pi / t) / (fwd + strike)) * (c_adj + std::sqrt(rad)) : 0.25;

    sigma = std::clamp(sigma, 0.01, 5.0);

    // 1. Halley's Method (Cubic convergence using Vega and Volga)
    for (int i = 0; i < max_iter; ++i) {
        double p = black_scholes(spot, strike, t, r, q, sigma, is_call);
        double diff = p - target_price;
        if (std::abs(diff) <= tol) {
            return sigma;
        }

        OptionGreeks gk = greeks(spot, strike, t, r, q, sigma, is_call);
        double vega = gk.vega;
        double volga = gk.volga;

        if (vega > 1e-10) {
            // Halley update: delta_sigma = - diff / (vega - 0.5 * diff * (volga / vega))
            double denom = vega - 0.5 * diff * (volga / vega);
            if (std::abs(denom) > 1e-10) {
                double step = -diff / denom;
                double next_sigma = sigma + step;
                if (next_sigma > 1e-4 && next_sigma < 10.0) {
                    sigma = next_sigma;
                    continue;
                }
            }
        }
        break; // Fallback to Brent
    }

    // 2. Brent-Dekker Root Finding Fallback
    double a = 1e-4;
    double b = 8.0;
    double fa = black_scholes(spot, strike, t, r, q, a, is_call) - target_price;
    double fb = black_scholes(spot, strike, t, r, q, b, is_call) - target_price;

    if (fa * fb > 0.0) {
        return std::numeric_limits<double>::quiet_NaN();
    }

    double c = a, fc = fa;
    bool mflag = true;
    double d = 0.0;

    for (int iter = 0; iter < 100; ++iter) {
        if (std::abs(fb) <= tol || std::abs(b - a) <= tol) {
            return b;
        }

        double s_val;
        if (std::abs(fa - fc) > 1e-14 && std::abs(fb - fc) > 1e-14) {
            // Inverse quadratic interpolation
            s_val = (a * fb * fc) / ((fa - fb) * (fa - fc)) +
                    (b * fa * fc) / ((fb - fa) * (fb - fc)) +
                    (c * fa * fb) / ((fc - fa) * (fc - fb));
        } else {
            // Secant method
            s_val = b - fb * (b - a) / (fb - fa);
        }

        double cond1 = (s_val < (3.0 * a + b) / 4.0 && s_val > b) || (s_val > (3.0 * a + b) / 4.0 && s_val < b);
        double cond2 = mflag && (std::abs(s_val - b) >= std::abs(b - c) / 2.0);
        double cond3 = !mflag && (std::abs(s_val - b) >= std::abs(c - d) / 2.0);
        double cond4 = mflag && (std::abs(b - c) < tol);
        double cond5 = !mflag && (std::abs(c - d) < tol);

        if (cond1 || cond2 || cond3 || cond4 || cond5) {
            s_val = 0.5 * (a + b);
            mflag = true;
        } else {
            mflag = false;
        }

        double fs = black_scholes(spot, strike, t, r, q, s_val, is_call) - target_price;
        d = c;
        c = b;
        fc = fb;

        if (fa * fs < 0.0) {
            b = s_val;
            fb = fs;
        } else {
            a = s_val;
            fa = fs;
        }

        if (std::abs(fa) < std::abs(fb)) {
            std::swap(a, b);
            std::swap(fa, fb);
        }
    }

    return b;
}

} // namespace kuwala::cpp
