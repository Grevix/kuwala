# Kuwala Julia Test Suite

using Test
include("../src/Kuwala.jl")
using .Kuwala

@testset "Kuwala Analytical Pricing & Numerical Invariants" begin
    # 1. ATM Standard Option
    price_call = Kuwala.black_scholes(100.0, 100.0, 1.0, 0.05, 0.0, 0.20; is_call=true)
    @test isapprox(price_call, 10.450583572185565, atol=1e-4)

    price_put = Kuwala.black_scholes(100.0, 100.0, 1.0, 0.05, 0.0, 0.20; is_call=false)
    # Put-Call parity check: C - P = S - K*exp(-rT)
    rhs = 100.0 - 100.0 * exp(-0.05 * 1.0)
    @test isapprox(price_call - price_put, rhs, atol=1e-6)

    # 2. Greeks
    g = Kuwala.greeks(100.0, 100.0, 1.0, 0.05, 0.0, 0.20; is_call=true)
    @test g.delta > 0.5 && g.delta < 0.7
    @test g.gamma > 0.0
    @test g.vega > 0.0

    # 3. IV Solver Round-Trip
    solved_iv = Kuwala.implied_volatility(price_call, 100.0, 100.0, 1.0, 0.05, 0.0; is_call=true)
    @test isapprox(solved_iv, 0.20, atol=1e-5)
end
