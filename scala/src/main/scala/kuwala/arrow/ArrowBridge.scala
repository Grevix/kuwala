package kuwala.arrow

import kuwala.data._

object ArrowBridge {
  /** Map primitive arrays into Scala OptionQuote models for JVM pipeline processing. */
  def parseQuotes(
    underlying: String,
    strikes: Array[Double],
    expiriesEpochSec: Array[Long],
    bids: Array[Double],
    asks: Array[Double],
    isCalls: Array[Boolean]
  ): Array[OptionQuote] = {
    val n = strikes.length
    val quotes = new Array[OptionQuote](n)
    var i = 0
    while (i < n) {
      val optType = if (isCalls(i)) Call else Put
      val mid = 0.5 * (bids(i) + asks(i))
      quotes(i) = OptionQuote(
        underlying = underlying,
        strike = strikes(i),
        expiryEpochSeconds = expiriesEpochSec(i),
        optionType = optType,
        bid = bids(i),
        ask = asks(i),
        mid = mid
      )
      i += 1
    }
    quotes
  }
}
