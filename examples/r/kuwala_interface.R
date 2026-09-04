# Kuwala R Analytics Interface (kuwalaR Prototype)
# Interoperability via Apache Arrow and reticulate / C-ABI

library(arrow)

#' Load Kuwala Partitioned Volatility Surface / Quotes
#' @param parquet_dir Path to Hive-partitioned parquet directory
#' @return Arrow Dataset
load_kuwala_dataset <- function(parquet_dir) {
  if (!dir.exists(parquet_dir)) {
    stop(paste("Directory does not exist:", parquet_dir))
  }
  ds <- open_dataset(parquet_dir)
  return(ds)
}

#' Extract Volatility Smile Slice
#' @param ds Arrow Dataset
#' @param target_expiry Target expiration date (ISO-8601 string)
#' @return data.frame with strike, log_moneyness, and implied_volatility
extract_volatility_smile <- function(ds, target_expiry) {
  df <- ds |>
    filter(expiry == target_expiry) |>
    select(strike, moneyness, implied_volatility, bid, ask) |>
    collect()
  
  df$log_moneyness <- log(df$moneyness)
  return(df)
}

#' Compute Volatility Risk Premium in R
#' @param atm_iv Implied volatility at-the-money
#' @param realized_vol Realized volatility over trailing window
#' @return VRP spread
calculate_vrp_r <- function(atm_iv, realized_vol) {
  return(atm_iv - realized_vol)
}
