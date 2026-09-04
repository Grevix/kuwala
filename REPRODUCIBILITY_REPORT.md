# Kuwala v0.2.0 Master Reproducibility Guide

**Audit Date:** September 2026  
**Auditor:** Quantitative Systems Architect & QA Lead  
**Subject:** End-to-End Reproducibility of All Verification Results  
**Status:** FULLY REPRODUCIBLE  

---

## 1. System Requirements & Toolchain Manifest

To reproduce all benchmarks, numerical invariants, and cross-language tests, configure the following toolchains:

| Toolchain | Minimum Required Version | System Path / Verification Command |
| :--- | :--- | :--- |
| **Python** | 3.10+ (Tested on 3.14.3) | `.\.venv\Scripts\python --version` |
| **Rust / Cargo** | 1.80+ (Tested on 1.85+) | `cargo --version` |
| **C++ Compiler** | C++20 compliant (MSVC 2022 v14.44 or GCC 12+) | `cl.exe` |
| **Julia** | 1.10+ (Tested on 1.12.7) | `julia --version` |
| **Java JDK** | JDK 17+ (Tested on Eclipse Temurin 17.0.20.1) | `java -version` |
| **Scala** | Scala 3.3+ (Tested on 3.9.0 via Coursier) | `scala-cli --version` |
| **R** | R 4.3+ (Tested on R 4.6.0) | `Rscript --version` |

---

## 2. Step-by-Step Reproduction Commands

### Step A: Core Pytest Suite (58 Unit & Integration Tests)
```powershell
.\.venv\Scripts\pytest tests/ -v
```
*Expected Result:* 58 passed in ~60-65 seconds (100% pass rate).

### Step B: Hostile Red-Team Suite (16 Adversarial Tests)
```powershell
.\.venv\Scripts\pytest tests/red_team/ -v
```
*Expected Result:* 16 passed in ~2.0 seconds (100% pass rate).

### Step C: Master Audit Campaign & Live Data Inversion (107,445 Cases)
```powershell
.\.venv\Scripts\python scripts/run_master_audit_campaign.py
```
*Expected Result:* 
- Execution time: ~25-30 seconds.
- Ingestion of real options for SPY, QQQ, AAPL, MSFT.
- Production of `REAL_IV_VALIDATION.csv` (4,013 contracts, 3,355 converged, nanodollar repricing error $2.88 \times 10^{-9}$).
- Bootstrapping of 11 real FRED Treasury pillars across 16,154 observations.
- Execution of 100,000 Put-Call Parity invariant checks (Max Err $1.14 \times 10^{-13}$).
- 107,425 / 107,445 tests passed (99.98%).
- Artifact written: `research/master_validation_results.json`.

### Step D: Julia Numerical Parity & Benchmark
```powershell
julia --project=julia julia/test/runtests.jl
julia --project=julia julia/benchmark/benchmark.jl
```
*Expected Result:* 6/6 tests pass in 0.3s; warm benchmark throughput $\sim 12.37\text{M ops/s}$.

### Step E: C++20 Low-Latency Benchmark
```powershell
cd kuwala_cpp
cl /EHsc /std:c++20 /O2 /fp:fast /I include src/main_benchmark.cpp /Fe:build/main_benchmark.exe
.\build\main_benchmark.exe
cd ..
```
*Expected Result:* 10M options priced in ~0.836s (11.96M ops/s); 10M ticks aggregated in ~0.156s (63.98M ticks/s).

### Step F: Scala / JVM Parity & Benchmark
```powershell
python scala/run_scala.py
```
*Expected Result:* Parity error $7.11 \times 10^{-15}$; IV error $4.56 \times 10^{-12}$; throughput $\sim 13.33\text{M ops/s}$ at $N=1,000,000$.

### Step G: R Script Interface Smoke Test
```powershell
Rscript examples/r/kuwala_interface.R
```
*Expected Result:* Successful execution with zero syntax or linkage errors.
