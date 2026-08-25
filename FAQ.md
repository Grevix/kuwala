# Frequently Asked Questions (FAQ)

---

### What is Kuwala?
**Kuwala** is an open-source quantitative finance library for derivatives pricing, arbitrage-checked volatility surface calibration, local volatility modeling, market data workflows, and relative-value signal research.

---

### Who is Kuwala for?
Kuwala is designed for quantitative researchers, financial engineers, risk managers, students, and algorithmic traders who require an end-to-end, convention-consistent pipeline from raw market data to arbitrage-checked surfaces and backtesting connectors.

---

### Does Kuwala provide trading advice?
**No.** Kuwala is purely mathematical, scientific, and software infrastructure. It does not provide financial advice, trading signals for execution, or profit guarantees.

---

### Which markets and asset classes are supported?
Kuwala supports equity indices, single-stock equities, ETFs, FX, and macroeconomic series. Its core data structures are asset-class agnostic and handle any standardized option chain with spot, strike, expiry, and rate conventions.

---

### Where does market data come from?
Kuwala provides client-side adapters for Yahoo Finance, Federal Reserve Economic Data (FRED), SEC EDGAR, Dukascopy, and Nasdaq Data Link. Data is retrieved at runtime under the user's personal session.

---

### Does Kuwala include proprietary market data?
**No.** To respect upstream terms of service and license boundaries, Kuwala never vendors or redistributes proprietary market datasets in wheels or source releases.

---

### Does Kuwala require paid API keys?
**No.** Kuwala operates 100% on zero credentials for its core pipeline and flagship workflows. Optional external adapters (such as FRED or Nasdaq Data Link) require free or user-provided API keys configured via environment variables.

---

### How does the Rust core work?
Kuwala employs a dual-engine architecture: Python serves as the user-facing interface, while performance-critical routines (vectorized IV root finding, SSVI total variance, Durrleman $g(k)$ evaluations, discrete local variance) are implemented in a compiled Rust crate (`kuwala_core`) using PyO3 and Rayon parallelism.

---

### Does Kuwala guarantee arbitrage-free surfaces?
**No model can unconditionally guarantee absence of arbitrage on raw, noisy input data.** Instead, Kuwala provides **explicit, inspectable diagnostics** (`surface.diagnostics()`) that evaluate Durrleman's butterfly condition ($g(k) \ge 0$) and calendar spread monotonicity ($\partial_T w \ge 0$) slice-by-slice, reporting exact pass/fail coordinates rather than silently returning corrupted local variances.

---

### Can I use Kuwala for live trading?
Kuwala is focused on research, calibration, risk analysis, and backtesting signal generation. While its high-throughput Rust core is built for low-latency computation, execution routing and order management are outside its scope.

---

### How do I report a bug or contribute?
Please open an issue on GitHub or review [CONTRIBUTING.md](CONTRIBUTING.md) to submit a pull request.
