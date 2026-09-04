package kuwala

import org.scalatest.funsuite.AnyFunSuite
import org.scalatest.matchers.should.Matchers
import kuwala.pricing._

class KuwalaSuite extends AnyFunSuite with Matchers {
  test("Black-Scholes analytical pricer and Put-Call parity") {
    val spot = 100.0
    val strike = 100.0
    val t = 1.0
    val r = 0.05
    val q = 0.0
    val vol = 0.20

    val call = BlackScholes.price(spot, strike, t, r, q, vol, isCall = true)
    val put = BlackScholes.price(spot, strike, t, r, q, vol, isCall = false)

    call shouldBe (10.45058 +- 1e-4)
    val rhs = spot - strike * math.exp(-r * t)
    (call - put) shouldBe (rhs +- 1e-6)
  }

  test("Greeks analytical formula consistency") {
    val g = Greeks.calculate(100.0, 100.0, 1.0, 0.05, 0.0, 0.20, isCall = true)
    g.delta should (be > 0.5 and be < 0.7)
    g.gamma should be > 0.0
    g.vega should be > 0.0
  }

  test("IV solver round-trip") {
    val target = BlackScholes.price(100.0, 100.0, 1.0, 0.05, 0.0, 0.20, isCall = true)
    val solved = IV.solve(target, 100.0, 100.0, 1.0, 0.05, 0.0, isCall = true)
    solved shouldBe (0.20 +- 1e-5)
  }
}
