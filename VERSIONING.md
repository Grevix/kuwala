# Kuwala Versioning Model & Release Gates

## 1. Versioning Hierarchy

Kuwala adheres to Semantic Versioning (SemVer 2.0.0):
- **MAJOR**: Incompatible API breaking changes.
- **MINOR**: Backward-compatible quantitative models, data adapters, or new analytical modules.
- **PATCH**: Bug fixes, numerical stability improvements, performance optimizations.

Under the Umbrella 0.1.0 milestone, stages were executed sequentially:
`0.1.0 -> 0.2.0 -> 0.3.0 -> 0.4.0 -> 0.5.0`

---

## 2. Release Gates & Definition of Done

A milestone is considered complete **only** when all of the following criteria are satisfied:
1. **Mathematical Correctness**: All formulas validated against published reference vectors and finite-difference ground truths.
2. **Arbitrage Guard Rails**: No surface is marked valid without passing butterfly and calendar arbitrage checks.
3. **Reproducible Benchmarks**: Speeds and memory footprints verified with committed benchmark scripts.
4. **Test Suite**: 100% passing unit, integration, and property tests in CI.
5. **Legibility & DX**: 2-minute quickstart workflow executes out-of-the-box without manual configuration.
6. **Data Compliance**: Strictly client-side runtime fetching with no proprietary data bundled in wheels or repositories.
