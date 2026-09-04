# Publication-Quality Volatility Surface Gradient Visualization Script in R
# Uses ggplot2 and viridis color palette

library(ggplot2)
library(arrow)
library(viridis)

#' Generate Volatility Smile Gradient Plot
generate_smile_gradient_plot <- function(df_surface, output_png = "docs/images/volatility_smile_gradient_r.png") {
  p <- ggplot(df_surface, aes(x = log_moneyness, y = implied_volatility, color = ttm, group = factor(ttm))) +
    geom_line(linewidth = 1.2) +
    geom_point(size = 2, alpha = 0.8) +
    scale_color_viridis_c(option = "magma", name = "Maturity (Years)") +
    theme_minimal(base_size = 14) +
    labs(
      title = "Kuwala Arbitrage-Free Volatility Smiles",
      subtitle = "Gatheral-Jacquier (2014) SSVI Multi-Tenor Slices",
      x = "Log-Moneyness k = ln(K / F)",
      y = "Implied Volatility sigma(k, T)"
    ) +
    theme(
      plot.title = element_text(face = "bold", size = 16),
      legend.position = "right",
      panel.grid.minor = element_blank()
    )
  
  ggsave(output_png, plot = p, width = 9, height = 6, dpi = 300)
  message(paste("Saved plot to:", output_png))
}
