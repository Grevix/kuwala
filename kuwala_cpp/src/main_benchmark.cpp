#include <iostream>
#include <vector>
#include <chrono>
#include <random>
#include <numeric>
#include <iomanip>
#include <fstream>
#include "../include/kuwala_cpp/pricing.hpp"
#include "../include/kuwala_cpp/greeks.hpp"
#include "../include/kuwala_cpp/iv.hpp"
#include "../include/kuwala_cpp/microstructure.hpp"

using namespace kuwala::cpp;

struct LatencyStats {
    double min_ns;
    double p50_ns;
    double p95_ns;
    double p99_ns;
    double max_ns;
    double mean_ns;
    double total_seconds;
    double throughput_ops_sec;
};

template <typename Func>
LatencyStats measure_workload(size_t count, Func&& f) {
    std::vector<double> latencies;
    latencies.reserve(count);

    auto start_total = std::chrono::high_resolution_clock::now();

    for (size_t i = 0; i < count; ++i) {
        auto t0 = std::chrono::high_resolution_clock::now();
        f(i);
        auto t1 = std::chrono::high_resolution_clock::now();
        double ns = std::chrono::duration<double, std::nano>(t1 - t0).count();
        latencies.push_back(ns);
    }

    auto end_total = std::chrono::high_resolution_clock::now();
    double total_sec = std::chrono::duration<double>(end_total - start_total).count();

    std::sort(latencies.begin(), latencies.end());

    double sum = std::accumulate(latencies.begin(), latencies.end(), 0.0);
    double mean = sum / static_cast<double>(count);
    double p50 = latencies[static_cast<size_t>(count * 0.50)];
    double p95 = latencies[static_cast<size_t>(count * 0.95)];
    double p99 = latencies[static_cast<size_t>(count * 0.99)];

    return LatencyStats{
        .min_ns = latencies.front(),
        .p50_ns = p50,
        .p95_ns = p95,
        .p99_ns = p99,
        .max_ns = latencies.back(),
        .mean_ns = mean,
        .total_seconds = total_sec,
        .throughput_ops_sec = static_cast<double>(count) / total_sec
    };
}

int main(int argc, char* argv[]) {
    std::cout << "========================================================\n";
    std::cout << "  Kuwala C++20 Low-Latency Engine Standalone Benchmark   \n";
    std::cout << "========================================================\n\n";

    std::mt19937_64 rng(42);
    std::uniform_real_distribution<double> dist_s(50.0, 300.0);
    std::uniform_real_distribution<double> dist_k(50.0, 300.0);
    std::uniform_real_distribution<double> dist_t(0.05, 3.0);
    std::uniform_real_distribution<double> dist_r(0.01, 0.06);
    std::uniform_real_distribution<double> dist_q(0.0, 0.03);
    std::uniform_real_distribution<double> dist_v(0.10, 0.90);

    const std::vector<size_t> bs_sizes = {10000, 100000, 1000000, 10000000};
    const std::vector<size_t> iv_sizes = {10000, 100000, 1000000};
    const std::vector<size_t> gk_sizes = {10000, 100000, 1000000};
    const std::vector<size_t> tick_sizes = {1000000, 10000000};

    std::ofstream json_out("benchmarks/results/raw/cpp_benchmark_results.json");
    json_out << "{\n  \"benchmarks\": {\n";

    // 1. Black-Scholes Benchmarks
    std::cout << "--- 1. Black-Scholes Pricing (C++) ---\n";
    for (size_t idx = 0; idx < bs_sizes.size(); ++idx) {
        size_t n = bs_sizes[idx];
        std::vector<double> spots(n), strikes(n), ttms(n), rates(n), divs(n), vols(n), prices(n);
        for (size_t i = 0; i < n; ++i) {
            spots[i] = dist_s(rng);
            strikes[i] = dist_k(rng);
            ttms[i] = dist_t(rng);
            rates[i] = dist_r(rng);
            divs[i] = dist_q(rng);
            vols[i] = dist_v(rng);
        }

        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < n; ++i) {
            prices[i] = black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], true);
        }
        auto end = std::chrono::high_resolution_clock::now();
        double sec = std::chrono::duration<double>(end - start).count();
        double ops = static_cast<double>(n) / sec;

        std::cout << "  N = " << std::setw(10) << n 
                  << " | Time: " << std::setw(8) << std::fixed << std::setprecision(4) << sec << "s"
                  << " | Throughput: " << std::setw(12) << std::fixed << std::setprecision(0) << ops << " ops/s\n";
    }

    // 2. Greeks Benchmarks
    std::cout << "\n--- 2. Greeks Analytical (C++) ---\n";
    for (size_t idx = 0; idx < gk_sizes.size(); ++idx) {
        size_t n = gk_sizes[idx];
        std::vector<double> spots(n), strikes(n), ttms(n), rates(n), divs(n), vols(n);
        for (size_t i = 0; i < n; ++i) {
            spots[i] = dist_s(rng);
            strikes[i] = dist_k(rng);
            ttms[i] = dist_t(rng);
            rates[i] = dist_r(rng);
            divs[i] = dist_q(rng);
            vols[i] = dist_v(rng);
        }

        auto start = std::chrono::high_resolution_clock::now();
        volatile double dummy = 0.0;
        for (size_t i = 0; i < n; ++i) {
            OptionGreeks g = greeks(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], true);
            dummy = dummy + g.delta + g.gamma + g.vega + g.vanna + g.volga + g.charm;
        }
        auto end = std::chrono::high_resolution_clock::now();
        double sec = std::chrono::duration<double>(end - start).count();
        double ops = static_cast<double>(n) / sec;

        std::cout << "  N = " << std::setw(10) << n 
                  << " | Time: " << std::setw(8) << std::fixed << std::setprecision(4) << sec << "s"
                  << " | Throughput: " << std::setw(12) << std::fixed << std::setprecision(0) << ops << " ops/s\n";
    }

    // 3. Implied Volatility Solver Benchmarks
    std::cout << "\n--- 3. Implied Volatility Solver (C++) ---\n";
    for (size_t idx = 0; idx < iv_sizes.size(); ++idx) {
        size_t n = iv_sizes[idx];
        std::vector<double> spots(n), strikes(n), ttms(n), rates(n), divs(n), vols(n), targets(n);
        for (size_t i = 0; i < n; ++i) {
            spots[i] = dist_s(rng);
            strikes[i] = dist_k(rng);
            ttms[i] = dist_t(rng);
            rates[i] = dist_r(rng);
            divs[i] = dist_q(rng);
            vols[i] = dist_v(rng);
            targets[i] = black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], true);
        }

        auto start = std::chrono::high_resolution_clock::now();
        volatile double solved_sum = 0.0;
        for (size_t i = 0; i < n; ++i) {
            double solved = implied_volatility(targets[i], spots[i], strikes[i], ttms[i], rates[i], divs[i], true);
            solved_sum = solved_sum + solved;
        }
        auto end = std::chrono::high_resolution_clock::now();
        double sec = std::chrono::duration<double>(end - start).count();
        double ops = static_cast<double>(n) / sec;

        std::cout << "  N = " << std::setw(10) << n 
                  << " | Time: " << std::setw(8) << std::fixed << std::setprecision(4) << sec << "s"
                  << " | Throughput: " << std::setw(12) << std::fixed << std::setprecision(0) << ops << " ops/s\n";
    }

    // 4. Tick-to-Bar Microstructure Aggregator Benchmarks
    std::cout << "\n--- 4. Microstructure Tick Aggregator (C++) ---\n";
    for (size_t idx = 0; idx < tick_sizes.size(); ++idx) {
        size_t n = tick_sizes[idx];
        std::vector<RawTick> ticks(n);
        int64_t t0 = 1700000000000000000LL;
        double p = 150.0;
        for (size_t i = 0; i < n; ++i) {
            t0 += static_cast<int64_t>(dist_t(rng) * 1000000.0);
            p += (dist_v(rng) - 0.5) * 0.1;
            ticks[i] = RawTick{
                .timestamp_ns = t0,
                .price = p,
                .volume = 100.0,
                .bid = p - 0.01,
                .ask = p + 0.01
            };
        }

        auto start = std::chrono::high_resolution_clock::now();
        std::vector<Bar> bars = aggregate_ticks(ticks, 60000000000LL); // 1-minute bars
        auto end = std::chrono::high_resolution_clock::now();
        double sec = std::chrono::duration<double>(end - start).count();
        double ops = static_cast<double>(n) / sec;

        std::cout << "  Ticks = " << std::setw(10) << n 
                  << " | Bars Created: " << std::setw(6) << bars.size()
                  << " | Time: " << std::setw(8) << std::fixed << std::setprecision(4) << sec << "s"
                  << " | Ingestion: " << std::setw(12) << std::fixed << std::setprecision(0) << ops << " ticks/s\n";
    }

    std::cout << "\n========================================================\n";
    std::cout << "  Benchmark Run Completed Successfully.                  \n";
    std::cout << "========================================================\n";

    return 0;
}
