# Kuwala Julia Benchmark Harness
# Measures cold start / JIT compilation overhead vs steady-state warm throughput

include("../src/Kuwala.jl")
using .Kuwala
using Random

function run_julia_benchmarks()
    println("==========================================================")
    println("  Kuwala Julia Numerical Performance Benchmark           ")
    println("==========================================================")

    # 1. Cold Start / JIT Latency Measurement
    t_cold_start = time_ns()
    p_cold = Kuwala.black_scholes(100.0, 100.0, 1.0, 0.05, 0.0, 0.20; is_call=true)
    t_cold_end = time_ns()
    cold_latency_ms = (t_cold_end - t_cold_start) / 1e6
    println("Black-Scholes First Execution (Cold/JIT): $(round(cold_latency_ms, digits=4)) ms")

    # 2. Warm Steady-State Throughput
    Random.seed!(42)
    sizes = [10000, 100000, 1000000]

    for n in sizes
        spots = rand(Float64, n) .* 250.0 .+ 50.0
        strikes = rand(Float64, n) .* 250.0 .+ 50.0
        ttms = rand(Float64, n) .* 2.95 .+ 0.05
        rates = rand(Float64, n) .* 0.05 .+ 0.01
        divs = rand(Float64, n) .* 0.03
        vols = rand(Float64, n) .* 0.80 .+ 0.10
        prices = zeros(Float64, n)

        t0 = time_ns()
        for i in 1:n
            prices[i] = Kuwala.black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i]; is_call=true)
        end
        t1 = time_ns()
        elapsed_sec = (t1 - t0) / 1e9
        ops_sec = n / elapsed_sec

        println("  N = $(lpad(n, 7)) | Time: $(round(elapsed_sec, digits=4))s | Warm Throughput: $(round(Int, ops_sec)) ops/s")
    end
end

run_julia_benchmarks()
