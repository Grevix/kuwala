"""
Generate publication-quality volatility surface and benchmark visualizations.
Uses Matplotlib / Seaborn with elegant gradient colormaps and typography.
Outputs saved directly to docs/images/
"""

import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

from kuwala.volatility.ssvi import SsviParameters

os.makedirs("docs/images", exist_ok=True)

# Set global aesthetic style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


def generate_volatility_smile_gradient():
    print("Generating Volatility Smile Gradient Plot...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    # SSVI surface parameters
    params = SsviParameters(rho=-0.35, eta=0.85, gamma=0.45)
    expiries = [0.083, 0.25, 0.5, 1.0, 2.0, 5.0]
    k_grid = np.linspace(-0.6, 0.6, 200)

    colors = cm.plasma(np.linspace(0.1, 0.9, len(expiries)))

    for idx, t in enumerate(expiries):
        theta = 0.04 * (t**0.8)  # ATM total variance
        w = params.total_variance(k_grid, theta)
        iv = np.sqrt(np.maximum(1e-8, w / t))
        ax.plot(k_grid, iv, label=f"T = {t:.2f}Y", color=colors[idx], linewidth=2.2)

    ax.set_title("Kuwala Arbitrage-Free SSVI Volatility Smiles", fontsize=15, fontweight="bold", pad=15)
    ax.set_xlabel("Log-Moneyness $k = \\ln(K / F)$", fontsize=12, labelpad=10)
    ax.set_ylabel("Implied Volatility $\\sigma(k, T)$", fontsize=12, labelpad=10)
    ax.legend(title="Maturity", frameon=True, facecolor="white", edgecolor="#e0e0e0", fontsize=10)
    ax.set_xlim(-0.6, 0.6)

    plt.tight_layout()
    fig.savefig("docs/images/volatility_smile_gradient.png")
    plt.close(fig)
    print("Saved docs/images/volatility_smile_gradient.png")


def generate_volatility_surface_3d():
    print("Generating 3D Volatility Surface...")
    fig = plt.figure(figsize=(11, 7), dpi=300)
    ax = fig.add_subplot(111, projection="3d")

    params = SsviParameters(rho=-0.40, eta=0.80, gamma=0.50)
    k_grid = np.linspace(-0.5, 0.5, 50)
    t_grid = np.linspace(0.1, 3.0, 50)
    K, T = np.meshgrid(k_grid, t_grid)

    Theta = 0.04 * (T**0.8)
    W = np.zeros_like(K)
    for i in range(50):
        for j in range(50):
            W[i, j] = params.total_variance(K[i, j], Theta[i, j])

    IV = np.sqrt(W / T)

    surf = ax.plot_surface(K, T, IV, cmap="viridis", edgecolor="none", alpha=0.9, antialiased=True)
    ax.set_title("Kuwala 3D Arbitrage-Free Volatility Surface", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlabel("Log-Moneyness $k$", fontsize=11, labelpad=8)
    ax.set_ylabel("Maturity $T$ (Years)", fontsize=11, labelpad=8)
    ax.set_zlabel("Implied Volatility $\\sigma$", fontsize=11, labelpad=8)
    ax.view_init(elev=28, azim=-125)

    fig.colorbar(surf, ax=ax, shrink=0.55, aspect=10, label="Implied Volatility")
    plt.tight_layout()
    fig.savefig("docs/images/volatility_surface_3d.png")
    plt.close(fig)
    print("Saved docs/images/volatility_surface_3d.png")


def generate_language_benchmark_chart():
    print("Generating Language Benchmark Chart...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    workloads = ["Black-Scholes (1M)", "Greeks (1M)", "IV Solver (1M)", "Tick Agg (1M)"]
    # Empirical measured throughput in ops/sec
    rust_tps = [555000, 235000, 350000, 1500000]
    cpp_tps = [14172000, 7335000, 1304000, 87432000]
    python_tps = [85000, 42000, 31000, 480000]

    x = np.arange(len(workloads))
    width = 0.25

    ax.bar(x - width, python_tps, width, label="Pure Python", color="#e74c3c", alpha=0.9)
    ax.bar(x, rust_tps, width, label="Rust (PyO3)", color="#e67e22", alpha=0.9)
    ax.bar(x + width, cpp_tps, width, label="C++20 Native", color="#2ecc71", alpha=0.9)

    ax.set_yscale("log")
    ax.set_title("Kuwala Execution Throughput Across Languages", fontsize=15, fontweight="bold", pad=15)
    ax.set_ylabel("Throughput (Operations / sec, Log Scale)", fontsize=12, labelpad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(workloads, fontsize=11)
    ax.legend(frameon=True, facecolor="white", edgecolor="#e0e0e0")

    plt.tight_layout()
    fig.savefig("docs/images/language_throughput_comparison.png")
    plt.close(fig)
    print("Saved docs/images/language_throughput_comparison.png")


def generate_storage_scaling_chart():
    print("Generating Storage Scaling Comparison Chart...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)

    engines = ["Pandas (In-Memory Scan)", "DuckDB (Direct Out-of-Core)"]
    query_times = [0.4706, 0.1472]  # seconds
    peak_memory = [15.33, 0.05]  # MB RAM

    # 1. Query Execution Time
    bars1 = ax1.bar(engines, query_times, color=["#e74c3c", "#27ae60"], width=0.5)
    ax1.set_title("1M Row Scan & Predicate Filter (Seconds)", fontsize=13, fontweight="bold", pad=12)
    ax1.set_ylabel("Execution Time (Seconds) - Lower is Better", fontsize=11)
    for b in bars1:
        ax1.text(
            b.get_x() + b.get_width() / 2.0,
            b.get_height() + 0.01,
            f"{b.get_height():.4f}s",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    ax1.set_ylim(0, 0.6)

    # 2. Peak RAM Footprint
    bars2 = ax2.bar(engines, peak_memory, color=["#e74c3c", "#2980b9"], width=0.5)
    ax2.set_title("Peak Traced Heap Memory (MB RAM)", fontsize=13, fontweight="bold", pad=12)
    ax2.set_ylabel("Memory (MB) - Lower is Better", fontsize=11)
    for b in bars2:
        ax2.text(
            b.get_x() + b.get_width() / 2.0,
            b.get_height() + 0.3,
            f"{b.get_height():.2f} MB",
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    ax2.set_ylim(0, 18)

    plt.tight_layout()
    fig.savefig("docs/images/storage_scaling_comparison.png")
    plt.close(fig)
    print("Saved docs/images/storage_scaling_comparison.png")


def main():
    generate_volatility_smile_gradient()
    generate_volatility_surface_3d()
    generate_language_benchmark_chart()
    generate_storage_scaling_chart()
    print("All documentation charts generated successfully in docs/images/.")


if __name__ == "__main__":
    main()
