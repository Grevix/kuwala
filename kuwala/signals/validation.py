"""
Overfitting-Aware Time-Series Validation Harness & Purged K-Fold Cross Validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable, Any
import numpy as np
import pandas as pd


@dataclass
class ValidationFoldResult:
    fold_idx: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    in_sample_sharpe: float
    out_of_sample_sharpe: float
    sharpe_degradation: float
    out_of_sample_return: float
    max_drawdown: float


@dataclass
class ValidationReport:
    method: str
    n_folds: int
    mean_in_sample_sharpe: float
    mean_out_of_sample_sharpe: float
    degradation_ratio: float
    is_overfit_suspected: bool
    fold_results: List[ValidationFoldResult] = field(default_factory=list)

    def summary(self) -> str:
        status = "SUSPECTED (High Degradation / Leakage)" if self.is_overfit_suspected else "PASSED (Robust Generalization)"
        lines = [
            "===========================================================",
            f"  KUWALA SIGNAL VALIDATION REPORT: {self.method.upper()}",
            "===========================================================",
            f"• Number of Folds:             {self.n_folds}",
            f"• Mean In-Sample Sharpe:       {self.mean_in_sample_sharpe:.2f}",
            f"• Mean Out-of-Sample Sharpe:   {self.mean_out_of_sample_sharpe:.2f}",
            f"• Sharpe Degradation Ratio:    {self.degradation_ratio:.2%}",
            f"• Overfitting Risk:            {status}",
            "",
            "Fold Breakdown:",
        ]
        for f in self.fold_results:
            lines.append(
                f"  Fold {f.fold_idx}: Train[{f.train_start}..{f.train_end}] "
                f"Test[{f.test_start}..{f.test_end}] -> IS Sharpe: {f.in_sample_sharpe:.2f}, "
                f"OOS Sharpe: {f.out_of_sample_sharpe:.2f}"
            )
        lines.append("===========================================================")
        return "\n".join(lines)


def purged_kfold_split(
    df: pd.DataFrame,
    n_splits: int = 5,
    embargo_pct: float = 0.01,
) -> List[Tuple[np.ndarray, np.ndarray]]:
    """
    Purged K-Fold split for financial time series with an embargo period between train and test sets
    to eliminate information leakage across autocorrelated observations.
    """
    n_samples = len(df)
    indices = np.arange(n_samples)
    fold_size = n_samples // n_splits
    embargo_size = int(n_samples * embargo_pct)

    splits = []
    for i in range(n_splits):
        test_start = i * fold_size
        test_end = (i + 1) * fold_size if i != n_splits - 1 else n_samples
        test_idx = indices[test_start:test_end]

        # Purge & embargo training indices around test set
        train_left = indices[:max(0, test_start - embargo_size)]
        train_right = indices[min(n_samples, test_end + embargo_size):]
        train_idx = np.concatenate([train_left, train_right])

        splits.append((train_idx, test_idx))

    return splits


def validate_signal(
    signal_series: pd.Series,
    forward_returns: pd.Series,
    method: str = "walk_forward",
    n_folds: int = 5,
    embargo_pct: float = 0.01,
) -> ValidationReport:
    """
    Validate a quantitative signal against future returns with overfitting diagnostics.
    """
    df = pd.DataFrame({"signal": signal_series, "returns": forward_returns}).dropna()
    n_samples = len(df)
    if n_samples < 20:
        raise ValueError("Insufficient sample size for validation (minimum 20 observations required)")

    fold_results: List[ValidationFoldResult] = []

    if method == "walk_forward":
        # Expanding window walk-forward
        fold_size = n_samples // (n_folds + 1)
        for i in range(1, n_folds + 1):
            train_end_idx = i * fold_size
            test_end_idx = (i + 1) * fold_size if i != n_folds else n_samples

            train_df = df.iloc[:train_end_idx]
            test_df = df.iloc[train_end_idx:test_end_idx]

            # In-sample strategy returns
            is_strat = train_df["signal"] * train_df["returns"]
            oos_strat = test_df["signal"] * test_df["returns"]

            is_sharpe = float(is_strat.mean() / (is_strat.std() + 1e-8) * np.sqrt(252))
            oos_sharpe = float(oos_strat.mean() / (oos_strat.std() + 1e-8) * np.sqrt(252))
            deg = 1.0 - (oos_sharpe / max(1e-4, is_sharpe))

            cum_ret = (1.0 + oos_strat).cumprod()
            peak = cum_ret.cummax()
            mdd = float(((peak - cum_ret) / peak).max()) if not peak.empty else 0.0

            fold_results.append(
                ValidationFoldResult(
                    fold_idx=i,
                    train_start=str(train_df.index[0]),
                    train_end=str(train_df.index[-1]),
                    test_start=str(test_df.index[0]),
                    test_end=str(test_df.index[-1]),
                    in_sample_sharpe=is_sharpe,
                    out_of_sample_sharpe=oos_sharpe,
                    sharpe_degradation=deg,
                    out_of_sample_return=float(oos_strat.sum()),
                    max_drawdown=mdd,
                )
            )

    mean_is = np.mean([f.in_sample_sharpe for f in fold_results])
    mean_oos = np.mean([f.out_of_sample_sharpe for f in fold_results])
    overall_deg = 1.0 - (mean_oos / max(1e-4, mean_is)) if mean_is > 0 else 1.0
    is_overfit = bool(overall_deg > 0.50 or mean_oos < 0.0)

    return ValidationReport(
        method=method,
        n_folds=len(fold_results),
        mean_in_sample_sharpe=float(mean_is),
        mean_out_of_sample_sharpe=float(mean_oos),
        degradation_ratio=float(overall_deg),
        is_overfit_suspected=is_overfit,
        fold_results=fold_results,
    )
