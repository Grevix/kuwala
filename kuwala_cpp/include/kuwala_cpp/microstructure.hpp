#pragma once

#include <cstdint>
#include <vector>
#include <span>
#include <cmath>
#include <algorithm>

namespace kuwala::cpp {

struct RawTick {
    int64_t timestamp_ns;
    double price;
    double volume;
    double bid;
    double ask;
};

struct Bar {
    int64_t start_time_ns;
    int64_t end_time_ns;
    double open;
    double high;
    double low;
    double close;
    double volume;
    double vwap;
    double buy_volume;
    double sell_volume;
    double effective_spread;
    uint32_t trade_count;
};

/// High-Performance Microstructure Aggregator (Lee-Ready Tick Rule + VWAP)
inline std::vector<Bar> aggregate_ticks(
    std::span<const RawTick> ticks,
    int64_t bar_interval_ns
) noexcept {
    std::vector<Bar> bars;
    if (ticks.empty() || bar_interval_ns <= 0) {
        return bars;
    }

    int64_t current_bar_start = (ticks[0].timestamp_ns / bar_interval_ns) * bar_interval_ns;
    int64_t current_bar_end = current_bar_start + bar_interval_ns;

    Bar current_bar{
        .start_time_ns = current_bar_start,
        .end_time_ns = current_bar_end,
        .open = ticks[0].price,
        .high = ticks[0].price,
        .low = ticks[0].price,
        .close = ticks[0].price,
        .volume = 0.0,
        .vwap = 0.0,
        .buy_volume = 0.0,
        .sell_volume = 0.0,
        .effective_spread = 0.0,
        .trade_count = 0
    };

    double cumulative_pv = 0.0;
    double cumulative_spread_v = 0.0;
    double prev_price = ticks[0].price;
    int last_side = 1; // 1: buy, -1: sell

    for (const auto& tick : ticks) {
        if (tick.timestamp_ns >= current_bar_end) {
            // Close current bar
            if (current_bar.volume > 0.0) {
                current_bar.vwap = cumulative_pv / current_bar.volume;
                current_bar.effective_spread = cumulative_spread_v / current_bar.volume;
            } else {
                current_bar.vwap = current_bar.close;
            }
            bars.push_back(current_bar);

            // Advance to next bar interval
            current_bar_start = (tick.timestamp_ns / bar_interval_ns) * bar_interval_ns;
            current_bar_end = current_bar_start + bar_interval_ns;

            current_bar = Bar{
                .start_time_ns = current_bar_start,
                .end_time_ns = current_bar_end,
                .open = tick.price,
                .high = tick.price,
                .low = tick.price,
                .close = tick.price,
                .volume = 0.0,
                .vwap = 0.0,
                .buy_volume = 0.0,
                .sell_volume = 0.0,
                .effective_spread = 0.0,
                .trade_count = 0
            };
            cumulative_pv = 0.0;
            cumulative_spread_v = 0.0;
        }

        // Update OHLC
        current_bar.high = std::max(current_bar.high, tick.price);
        current_bar.low = std::min(current_bar.low, tick.price);
        current_bar.close = tick.price;
        current_bar.volume += tick.volume;
        current_bar.trade_count++;

        cumulative_pv += tick.price * tick.volume;

        // Lee-Ready Tick Rule
        int side = 0;
        if (tick.bid > 0.0 && tick.ask > 0.0 && tick.ask > tick.bid) {
            double midpoint = 0.5 * (tick.bid + tick.ask);
            double eff_spread = 2.0 * std::abs(tick.price - midpoint);
            cumulative_spread_v += eff_spread * tick.volume;

            if (tick.price > midpoint) {
                side = 1;
            } else if (tick.price < midpoint) {
                side = -1;
            }
        }
        if (side == 0) {
            // Price tick test
            if (tick.price > prev_price) {
                side = 1;
            } else if (tick.price < prev_price) {
                side = -1;
            } else {
                side = last_side;
            }
        }

        last_side = side;
        prev_price = tick.price;

        if (side == 1) {
            current_bar.buy_volume += tick.volume;
        } else {
            current_bar.sell_volume += tick.volume;
        }
    }

    // Flush last bar
    if (current_bar.trade_count > 0) {
        if (current_bar.volume > 0.0) {
            current_bar.vwap = cumulative_pv / current_bar.volume;
            current_bar.effective_spread = cumulative_spread_v / current_bar.volume;
        } else {
            current_bar.vwap = current_bar.close;
        }
        bars.push_back(current_bar);
    }

    return bars;
}

} // namespace kuwala::cpp
