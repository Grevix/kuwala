"""
Generate canonical golden datasets for multi-language cross-validation.
Creates tests/golden/black_scholes.csv, tests/golden/greeks.csv, and tests/golden/implied_vol.csv.
"""

import os

import numpy as np
import pandas as pd

from kuwala.pricing import black_scholes, greeks

os.makedirs("tests/golden", exist_ok=True)
np.random.seed(42)


def generate_pricing_golden(n=10000):
    print(f"Generating {n} Black-Scholes golden records...")
    spots = np.random.uniform(10.0, 1000.0, n)
    strikes = spots * np.random.uniform(0.5, 2.0, n)
    ttms = np.random.uniform(0.01, 5.0, n)
    rates = np.random.uniform(-0.01, 0.10, n)
    divs = np.random.uniform(0.0, 0.05, n)
    vols = np.random.uniform(0.05, 1.50, n)
    is_calls = np.random.choice([True, False], n)

    prices = [black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], is_calls[i]) for i in range(n)]

    df = pd.DataFrame(
        {
            "spot": spots,
            "strike": strikes,
            "ttm": ttms,
            "rate": rates,
            "dividend": divs,
            "volatility": vols,
            "is_call": is_calls,
            "expected_price": prices,
        }
    )
    df.to_csv("tests/golden/black_scholes.csv", index=False)
    print("Saved tests/golden/black_scholes.csv")


def generate_greeks_golden(n=10000):
    print(f"Generating {n} Greeks golden records...")
    spots = np.random.uniform(20.0, 500.0, n)
    strikes = spots * np.random.uniform(0.6, 1.4, n)
    ttms = np.random.uniform(0.05, 3.0, n)
    rates = np.random.uniform(0.0, 0.08, n)
    divs = np.random.uniform(0.0, 0.04, n)
    vols = np.random.uniform(0.10, 1.0, n)
    is_calls = np.random.choice([True, False], n)

    deltas, gammas, vegas, thetas, rhos, vannas, volgas, charms = [], [], [], [], [], [], [], []
    for i in range(n):
        g = greeks(spots[i], strikes[i], ttms[i], rates[i], divs[i], vols[i], is_calls[i])
        deltas.append(g.delta)
        gammas.append(g.gamma)
        vegas.append(g.vega)
        thetas.append(g.theta)
        rhos.append(g.rho)
        vannas.append(g.vanna)
        volgas.append(g.volga)
        charms.append(g.charm)

    df = pd.DataFrame(
        {
            "spot": spots,
            "strike": strikes,
            "ttm": ttms,
            "rate": rates,
            "dividend": divs,
            "volatility": vols,
            "is_call": is_calls,
            "delta": deltas,
            "gamma": gammas,
            "vega": vegas,
            "theta": thetas,
            "rho": rhos,
            "vanna": vannas,
            "volga": volgas,
            "charm": charms,
        }
    )
    df.to_csv("tests/golden/greeks.csv", index=False)
    print("Saved tests/golden/greeks.csv")


def generate_iv_golden(n=5000):
    print(f"Generating {n} IV inversion golden records...")
    spots = np.random.uniform(50.0, 300.0, n)
    strikes = spots * np.random.uniform(0.8, 1.2, n)
    ttms = np.random.uniform(0.1, 2.0, n)
    rates = np.random.uniform(0.01, 0.06, n)
    divs = np.random.uniform(0.0, 0.03, n)
    true_vols = np.random.uniform(0.10, 0.80, n)
    is_calls = np.random.choice([True, False], n)

    target_prices = [
        black_scholes(spots[i], strikes[i], ttms[i], rates[i], divs[i], true_vols[i], is_calls[i]) for i in range(n)
    ]

    df = pd.DataFrame(
        {
            "target_price": target_prices,
            "spot": spots,
            "strike": strikes,
            "ttm": ttms,
            "rate": rates,
            "dividend": divs,
            "is_call": is_calls,
            "true_volatility": true_vols,
        }
    )
    df.to_csv("tests/golden/implied_vol.csv", index=False)
    print("Saved tests/golden/implied_vol.csv")


if __name__ == "__main__":
    generate_pricing_golden()
    generate_greeks_golden()
    generate_iv_golden()
    print("All golden test datasets generated successfully in tests/golden/.")
