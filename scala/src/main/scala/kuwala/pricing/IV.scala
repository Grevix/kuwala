package kuwala.pricing

import scala.math._

object IV {
  def solve(
    targetPrice: Double,
    spot: Double,
    strike: Double,
    t: Double,
    r: Double,
    q: Double,
    isCall: Boolean,
    tol: Double = 1e-8,
    maxIter: Int = 100
  ): Double = {
    if (t <= 1e-12 || spot <= 1e-12 || strike <= 1e-12) {
      Double.NaN
    } else {
      val dfR = exp(-r * t)
      val dfQ = exp(-q * t)
      val intrinsic = if (isCall) max(0.0, spot * dfQ - strike * dfR) else max(0.0, strike * dfR - spot * dfQ)

      if (targetPrice < intrinsic - 1e-7) {
        Double.NaN
      } else {
        // Initial estimate
        val fwd = spot * exp((r - q) * t)
        val cAdj = targetPrice - 0.5 * (fwd - strike) * dfR
        val rad = cAdj * cAdj - (fwd - strike) * (fwd - strike) * dfR * dfR / Pi
        var sigma = if (rad > 0.0) (sqrt(2.0 * Pi / t) / (fwd + strike)) * (cAdj + sqrt(rad)) else 0.25
        sigma = min(5.0, max(0.01, sigma))

        // Halley's method
        var iter = 0
        var converged = false
        while (iter < maxIter && !converged) {
          val p = BlackScholes.price(spot, strike, t, r, q, sigma, isCall)
          val diff = p - targetPrice
          if (abs(diff) <= tol) {
            converged = true
          } else {
            val gk = Greeks.calculate(spot, strike, t, r, q, sigma, isCall)
            val vega = gk.vega
            val volga = gk.volga
            if (vega > 1e-10) {
              val denom = vega - 0.5 * diff * (volga / vega)
              if (abs(denom) > 1e-10) {
                val nextSigma = sigma - diff / denom
                if (nextSigma > 1e-4 && nextSigma < 10.0) {
                  sigma = nextSigma
                } else {
                  converged = true // Break to bisection
                }
              } else converged = true
            } else converged = true
          }
          iter += 1
        }

        if (abs(BlackScholes.price(spot, strike, t, r, q, sigma, isCall) - targetPrice) <= tol) {
          sigma
        } else {
          // Bisection fallback
          var a = 1e-4
          var b = 8.0
          var i = 0
          while (i < 80 && (b - a) > tol) {
            val mid = 0.5 * (a + b)
            val fMid = BlackScholes.price(spot, strike, t, r, q, mid, isCall) - targetPrice
            if (fMid < 0.0) a = mid else b = mid
            i += 1
          }
          0.5 * (a + b)
        }
      }
    }
  }
}
