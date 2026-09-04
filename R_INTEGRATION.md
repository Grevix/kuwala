# Kuwala R Analytics Integration (kuwalaR)

**Module Path:** `examples/r/`  
**Integration Paradigm:** Apache Arrow Zero-Copy Datasets & C-ABI  
**Target Visualizations:** `docs/images/volatility_smile_gradient.png`, `docs/images/volatility_surface_3d.png`  

---

## 1. Design & Scope

R is widely recognized in quantitative finance for its rich statistical, econometric, and visualization ecosystem (`ggplot2`, `viridis`, `data.table`). Rather than duplicating core numerical algorithms in R, Kuwala provides an **Arrow-native analytics interface**:

1. **Zero-Copy Arrow Persistence:**
   - Kuwala writes Hive-partitioned Parquet datasets (`partitioned/options/`).
   - R loads these files using `arrow::open_dataset()`, allowing instant querying of multi-gigabyte volatility slices without copying.
2. **Interactive Smile & Surface Plots:**
   - Publication-quality ggplot2 visualization scripts in `examples/r/generate_surface_gradients.R`.
3. **Signal & Econometric Analysis:**
   - Direct calculation of Volatility Risk Premium (VRP) and skew metrics in R.

---

## 2. Example Usage in R

```r
source("examples/r/kuwala_interface.R")

# Open Kuwala partitioned store via Arrow
ds <- load_kuwala_dataset("partitioned/options")

# Query specific expiration smile slice
smile_df <- extract_volatility_smile(ds, "2026-09-18")

# Generate publication-grade gradient plot
source("examples/r/generate_surface_gradients.R")
generate_smile_gradient_plot(smile_df, "docs/images/volatility_smile_gradient_r.png")
```
