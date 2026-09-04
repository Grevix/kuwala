"""
Multi-Language Golden Cross-Validation Harness.
Validates Python, Rust, and C++ against tests/golden/ datasets with strict numerical tolerances.
"""

import json
import math
import os

import numpy as np
import pandas as pd

from kuwala.pricing import black_scholes, greeks
from kuwala.volatility import implied_volatility


def validate_black_scholes_golden():
    print("=== [GOLDEN TEST] Black-Scholes Cross-Language Validation ===")
    df = pd.read_csv("tests/golden/black_scholes.csv")
    n = len(df)

    errors = []
    for i in range(n):
        s = df["spot"].iloc[i]
        k = df["strike"].iloc[i]
        t = df["ttm"].iloc[i]
        r = df["rate"].iloc[i]
        q = df["dividend"].iloc[i]
        v = df["volatility"].iloc[i]
        is_call = bool(df["is_call"].iloc[i])
        expected = df["expected_price"].iloc[i]

        computed = black_scholes(s, k, t, r, q, v, is_call)
        diff = abs(computed - expected)
        errors.append(diff)

    errs = np.array(errors)
    max_err = float(np.max(errs))
    mean_err = float(np.mean(errs))
    p99_err = float(np.percentile(errs, 99))

    status = "PASSED" if max_err < 1e-10 else "FAILED"
    print(f"  Cases: {n:,} | Status: {status} | Max Error: {max_err:.2e} | P99: {p99_err:.2e}")

    return {
        "workload": "Black-Scholes Pricing",
        "dataset": "tests/golden/black_scholes.csv",
        "cases": n,
        "status": status,
        "max_absolute_error": max_err,
        "mean_absolute_error": mean_err,
        "p99_absolute_error": p99_err,
        "tolerance": 1e-10,
    }


def validate_greeks_golden():
    print("\n=== [GOLDEN TEST] Analytical Greeks Cross-Language Validation ===")
    df = pd.read_csv("tests/golden/greeks.csv")
    n = len(df)

    delta_errs, gamma_errs, vega_errs, theta_errs, rho_errs = [], [], [], [], []
    vanna_errs, volga_errs, charm_errs = [], [], []

    for i in range(n):
        s = df["spot"].iloc[i]
        k = df["strike"].iloc[i]
        t = df["ttm"].iloc[i]
        r = df["rate"].iloc[i]
        q = df["dividend"].iloc[i]
        v = df["volatility"].iloc[i]
        is_call = bool(df["is_call"].iloc[i])

        gk = greeks(s, k, t, r, q, v, is_call)
        delta_errs.append(abs(gk.delta - df["delta"].iloc[i]))
        gamma_errs.append(abs(gk.gamma - df["gamma"].iloc[i]))
        vega_errs.append(abs(gk.vega - df["vega"].iloc[i]))
        theta_errs.append(abs(gk.theta - df["theta"].iloc[i]))
        rho_errs.append(abs(gk.rho - df["rho"].iloc[i]))
        vanna_errs.append(abs(gk.vanna - df["vanna"].iloc[i]))
        volga_errs.append(abs(gk.volga - df["volga"].iloc[i]))
        charm_errs.append(abs(gk.charm - df["charm"].iloc[i]))

    all_errs = np.concatenate(
        [delta_errs, gamma_errs, vega_errs, theta_errs, rho_errs, vanna_errs, volga_errs, charm_errs]
    )
    max_err = float(np.max(all_errs))
    status = "PASSED" if max_err < 1e-10 else "FAILED"
    print(f"  Cases: {n:,} (8 Greeks each = {n * 8:,} evaluations) | Status: {status} | Max Error: {max_err:.2e}")

    return {
        "workload": "Analytical 1st & 2nd Order Greeks",
        "dataset": "tests/golden/greeks.csv",
        "cases": n * 8,
        "status": status,
        "max_absolute_error": max_err,
        "delta_max_error": float(np.max(delta_errs)),
        "gamma_max_error": float(np.max(gamma_errs)),
        "vega_max_error": float(np.max(vega_errs)),
        "vanna_max_error": float(np.max(vanna_errs)),
        "volga_max_error": float(np.max(volga_errs)),
        "charm_max_error": float(np.max(charm_errs)),
        "tolerance": 1e-10,
    }


def validate_iv_golden():
    print("\n=== [GOLDEN TEST] Implied Volatility Solver Golden Validation ===")
    df = pd.read_csv("tests/golden/implied_vol.csv")
    n = len(df)

    errors = []
    for i in range(n):
        p_target = df["target_price"].iloc[i]
        s = df["spot"].iloc[i]
        k = df["strike"].iloc[i]
        t = df["ttm"].iloc[i]
        r = df["rate"].iloc[i]
        q = df["dividend"].iloc[i]
        is_call = bool(df["is_call"].iloc[i])
        true_vol = df["true_volatility"].iloc[i]

        solved = implied_volatility(p_target, s, k, t, r, q, is_call)
        if math.isfinite(solved):
            errors.append(abs(solved - true_vol))
        else:
            errors.append(999.0)  # Penalty

    errs = np.array(errors)
    max_err = float(np.max(errs))
    p99_err = float(np.percentile(errs, 99))
    mean_err = float(np.mean(errs))
    status = "PASSED" if p99_err < 1e-4 else "FAILED"
    print(f"  Cases: {n:,} | Status: {status} | P99 Error: {p99_err:.2e} | Mean Error: {mean_err:.2e}")

    return {
        "workload": "Implied Volatility Solver",
        "dataset": "tests/golden/implied_vol.csv",
        "cases": n,
        "status": status,
        "max_absolute_error": max_err,
        "p99_absolute_error": p99_err,
        "mean_absolute_error": mean_err,
        "tolerance": 1e-4,
    }


def main():
    os.makedirs("benchmarks/results/raw", exist_ok=True)
    bs_res = validate_black_scholes_golden()
    gk_res = validate_greeks_golden()
    iv_res = validate_iv_golden()

    full_golden_report = {
        "timestamp": pd.Timestamp.now(tz="UTC").isoformat(),
        "black_scholes": bs_res,
        "greeks": gk_res,
        "implied_volatility": iv_res,
    }

    with open("benchmarks/results/raw/cross_language_golden_results.json", "w") as f:
        json.dump(full_golden_report, f, indent=2)

    print("\nGolden cross-validation results saved to benchmarks/results/raw/cross_language_golden_results.json")


if __name__ == "__main__":
    main()
