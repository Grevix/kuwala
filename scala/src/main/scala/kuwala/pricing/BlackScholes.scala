package kuwala.pricing

import scala.math._

object BlackScholes {
  private final val InvSqrt2Pi: Double = 0.39894228040143267793994605993438
  private final val Sqrt2: Double = 1.4142135623730950488016887242097

  @inline def normCdf(x: Double): Double = {
    0.5 * (1.0 + erfApprox(x / Sqrt2))
  }

  @inline def normPdf(x: Double): Double = {
    InvSqrt2Pi * exp(-0.5 * x * x)
  }

  @inline def erfApprox(x: Double): Double = {
    val signX = if (x < 0) -1.0 else 1.0
    val absX = abs(x)
    val t = 1.0 / (1.0 + 0.3275911 * absX)
    val poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    signX * (1.0 - poly * exp(-absX * absX))
  }

  /** Analytical Black-Scholes European Option pricer on primitives (Zero JVM Heap Allocation). */
  def price(
    spot: Double,
    strike: Double,
    t: Double,
    r: Double,
    q: Double,
    sigma: Double,
    isCall: Boolean
  ): Double = {
    if (t <= 0.0) {
      if (isCall) max(0.0, spot - strike) else max(0.0, strike - spot)
    } else if (sigma <= 0.0) {
      val dfR = exp(-r * t)
      val dfQ = exp(-q * t)
      if (isCall) max(0.0, spot * dfQ - strike * dfR) else max(0.0, strike * dfR - spot * dfQ)
    } else if (spot <= 0.0) {
      if (isCall) 0.0 else strike * exp(-r * t)
    } else if (strike <= 0.0) {
      if (isCall) spot * exp(-q * t) else 0.0
    } else {
      val dfR = exp(-r * t)
      val dfQ = exp(-q * t)
      val sqrtT = sqrt(t)
      val d1 = (log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrtT)
      val d2 = d1 - sigma * sqrtT

      if (isCall) {
        spot * dfQ * normCdf(d1) - strike * dfR * normCdf(d2)
      } else {
        strike * dfR * normCdf(-d2) - spot * dfQ * normCdf(-d1)
      }
    }
  }

  /** Batch pricing over primitive contiguous arrays (Zero JVM Object Boxing). */
  def priceBatch(
    spots: Array[Double],
    strikes: Array[Double],
    ttms: Array[Double],
    rates: Array[Double],
    divs: Array[Double],
    sigmas: Array[Double],
    isCalls: Array[Boolean],
    outPrices: Array[Double]
  ): Unit = {
    var i = 0
    val n = spots.length
    while (i < n) {
      outPrices(i) = price(spots(i), strikes(i), ttms(i), rates(i), divs(i), sigmas(i), isCalls(i))
      i += 1
    }
  }
}
