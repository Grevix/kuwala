package kuwala.data

import java.time.Instant

sealed trait OptionType
case object Call extends OptionType
case object Put extends OptionType

final case class OptionQuote(
  underlying: String,
  strike: Double,
  expiryEpochSeconds: Long,
  optionType: OptionType,
  bid: Double,
  ask: Double,
  mid: Double,
  last: Option[Double] = None,
  volume: Option[Long] = None,
  openInterest: Option[Long] = None,
  timestamp: Instant = Instant.now()
) {
  def isCall: Boolean = optionType == Call
}

final case class TickRecord(
  timestampNs: Long,
  symbol: String,
  price: Double,
  volume: Double,
  bid: Double,
  ask: Double
)
