package kuwala.pricing

import scala.math._

final case class OptionGreeks(
  delta: Double,
  gamma: Double,
  vega: Double,
  theta: Double,
  rho: Double,
  vanna: Double,
  volga: Double,
  charm: Double
)

object Greeks {
  def calculate(
    spot: Double,
    strike: Double,
    t: Double,
    r: Double,
    q: Double,
    sigma: Double,
    isCall: Boolean
  ): OptionGreeks = {
    if (t <= 1e-12 || sigma <= 1e-12 || spot <= 1e-12 || strike <= 1e-12) {
      val d = if (isCall) (if (spot > strike) 1.0 else if (spot == strike) 0.5 else 0.0)
              else (if (spot < strike) -1.0 else if (spot == strike) -0.5 else 0.0)
      OptionGreeks(d, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    } else {
      val dfR = exp(-r * t)
      val dfQ = exp(-q * t)
      val sqrtT = sqrt(t)
      val d1 = (log(spot / strike) + (r - q + 0.5 * sigma * sigma) * t) / (sigma * sqrtT)
      val d2 = d1 - sigma * sqrtT
      val nPrimeD1 = BlackScholes.normPdf(d1)

      val delta = if (isCall) dfQ * BlackScholes.normCdf(d1) else dfQ * (BlackScholes.normCdf(d1) - 1.0)
      val gamma = dfQ * nPrimeD1 / (spot * sigma * sqrtT)
      val vega = spot * dfQ * nPrimeD1 * sqrtT

      val term1 = -(spot * dfQ * nPrimeD1 * sigma) / (2.0 * sqrtT)
      val theta = if (isCall) {
        term1 - r * strike * dfR * BlackScholes.normCdf(d2) + q * spot * dfQ * BlackScholes.normCdf(d1)
      } else {
        term1 + r * strike * dfR * BlackScholes.normCdf(-d2) - q * spot * dfQ * BlackScholes.normCdf(-d1)
      }

      val rho = if (isCall) strike * t * dfR * BlackScholes.normCdf(d2) else -strike * t * dfR * BlackScholes.normCdf(-d2)
      val vanna = -dfQ * nPrimeD1 * d2 / sigma
      val volga = vega * d1 * d2 / sigma
      val charmBase = dfQ * nPrimeD1 * (2.0 * (r - q) * t - d2 * sigma * sqrtT) / (2.0 * t * sigma * sqrtT)
      val charm = if (isCall) q * dfQ * BlackScholes.normCdf(d1) - charmBase else -q * dfQ * BlackScholes.normCdf(-d1) - charmBase

      OptionGreeks(delta, gamma, vega, theta, rho, vanna, volga, charm)
    }
  }
}
