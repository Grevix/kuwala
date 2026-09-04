package kuwala

import kuwala.pricing._
import kuwala.data._
import kuwala.arrow._
import scala.util.Random

object Main {
  def main(args: Array[String]): Unit = {
    println("==========================================================")
    println("  Kuwala Scala / JVM Engine Verification & Benchmark      ")
    println("==========================================================")

    // 1. Black-Scholes & Put-Call Parity Test
    val spot = 100.0
    val strike = 100.0
    val t = 1.0
    val r = 0.05
    val q = 0.0
    val vol = 0.20

    val call = BlackScholes.price(spot, strike, t, r, q, vol, isCall = true)
    val put = BlackScholes.price(spot, strike, t, r, q, vol, isCall = false)
    val rhs = spot - strike * math.exp(-r * t)
    val parityDiff = math.abs((call - put) - rhs)

    println(f"1. Black-Scholes ATM Call: $call%.6f (Expected: 10.45058)")
    println(f"   Put-Call Parity Error: $parityDiff%.2e")
    assert(math.abs(call - 10.45058) < 1e-4, "BS call mismatch")
    assert(parityDiff < 1e-6, "Parity mismatch")

    // 2. Greeks Analytical Test
    val g = Greeks.calculate(100.0, 100.0, 1.0, 0.05, 0.0, 0.20, isCall = true)
    println(f"2. Greeks: Delta=${g.delta}%.4f, Gamma=${g.gamma}%.4f, Vega=${g.vega}%.4f, Theta=${g.theta}%.4f, Rho=${g.rho}%.4f")
    assert(g.delta > 0.5 && g.delta < 0.7, "Delta out of range")
    assert(g.gamma > 0.0, "Gamma <= 0")
    assert(g.vega > 0.0, "Vega <= 0")

    // 3. IV Inversion Test
    val solvedIv = IV.solve(call, 100.0, 100.0, 1.0, 0.05, 0.0, isCall = true)
    println(f"3. IV Solver Round-Trip: Solved=$solvedIv%.6f, True=$vol%.6f, Error=${math.abs(solvedIv - vol)}%.2e")
    assert(math.abs(solvedIv - vol) < 1e-5, "IV round-trip failed")

    // 4. Arrow Bridge Model Mapping Test
    val quotes = ArrowBridge.parseQuotes(
      "SPY",
      Array(90.0, 100.0, 110.0),
      Array(1700000000L, 1700000000L, 1700000000L),
      Array(12.0, 4.5, 1.2),
      Array(12.2, 4.7, 1.3),
      Array(true, true, true)
    )
    println(s"4. Arrow Bridge Quotes Created: ${quotes.length} quotes")
    assert(quotes.length == 3 && quotes(1).mid == 4.6, "Arrow bridge mismatch")

    // 5. Throughput Benchmarks (Cold vs Warm)
    println("\n--- 5. JVM Black-Scholes Batch Pricing Benchmark ---")
    val rng = new Random(42)
    val sizes = Seq(10000, 100000, 1000000)

    for (n <- sizes) {
      val spots = Array.fill(n)(rng.nextDouble() * 250.0 + 50.0)
      val strikes = Array.fill(n)(rng.nextDouble() * 250.0 + 50.0)
      val ttms = Array.fill(n)(rng.nextDouble() * 2.95 + 0.05)
      val rates = Array.fill(n)(rng.nextDouble() * 0.05 + 0.01)
      val divs = Array.fill(n)(rng.nextDouble() * 0.03)
      val vols = Array.fill(n)(rng.nextDouble() * 0.80 + 0.10)
      val isCalls = Array.fill(n)(true)
      val outPrices = new Array[Double](n)

      // Measure
      val t0 = System.nanoTime()
      BlackScholes.priceBatch(spots, strikes, ttms, rates, divs, vols, isCalls, outPrices)
      val t1 = System.nanoTime()
      val elapsedSec = (t1 - t0) / 1e9
      val throughput = n / elapsedSec

      println(f"  N = $n%7d | Time: $elapsedSec%.4fs | Throughput: ${throughput.toInt}%,d ops/s")
    }

    println("\n[VERIFIED] All Scala / JVM numerical tests and benchmarks passed successfully.")
  }
}
