import pytest
import numpy as np
import pandas as pd
import kuwala
from kuwala.signals.validation import validate_signal, purged_kfold_split

def test_purged_kfold_splits():
    df = pd.DataFrame({"val": range(100)})
    splits = purged_kfold_split(df, n_splits=5, embargo_pct=0.02)
    assert len(splits) == 5
    for train_idx, test_idx in splits:
        assert len(test_idx) == 20
        # Verify no intersection between train and test
        assert len(set(train_idx).intersection(set(test_idx))) == 0

def test_walk_forward_validation_harness():
    np.random.seed(42)
    n = 100
    dates = pd.date_range("2026-01-01", periods=n, freq="B")
    
    # Pure noise signal against random returns
    signal = pd.Series(np.random.choice([-1.0, 1.0], size=n), index=dates)
    returns = pd.Series(np.random.normal(0, 0.01, size=n), index=dates)

    report = validate_signal(signal, returns, method="walk_forward", n_folds=4)

    assert report.n_folds == 4
    assert hasattr(report, "mean_out_of_sample_sharpe")
    assert hasattr(report, "is_overfit_suspected")
    summary = report.summary()
    assert "KUWALA SIGNAL VALIDATION REPORT" in summary
