"""
Surface Principal Component Analysis (PCA) & Residual Monitoring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Sequence, Union

import numpy as np


@dataclass
class SurfacePcaResult:
    mean_surface: np.ndarray
    explained_variance_ratio: np.ndarray
    components: np.ndarray
    scores: np.ndarray

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


def surface_pca(
    surface_matrices: Union[np.ndarray, Sequence[np.ndarray], List[np.ndarray]],
    n_components: int = 3,
) -> SurfacePcaResult:
    """
    Perform PCA decomposition on a timeseries or cross-section of implied volatility surfaces.

    Decomposes surface dynamics into Level, Slope (Skew), and Curvature (Twist).

    Parameters
    ----------
    surface_matrices : np.ndarray or list of 2D surface arrays
        3D array of shape (N_timesteps, N_expiries, N_strikes).
    n_components : int, default 3
        Number of principal components to extract.

    Returns
    -------
    SurfacePcaResult
        Explained variance ratios, principal components (eigenvectors), and component scores.
    """
    surfs = np.asarray(surface_matrices, dtype=np.float64)
    if surfs.ndim == 2:
        surfs = surfs[np.newaxis, ...]

    n_samples, n_exp, n_k = surfs.shape
    flattened = surfs.reshape(n_samples, n_exp * n_k)

    # Center the surfaces
    mean_surface = np.mean(flattened, axis=0)
    centered = flattened - mean_surface

    if n_samples <= 1:
        return SurfacePcaResult(
            mean_surface=mean_surface.reshape(n_exp, n_k),
            explained_variance_ratio=np.array([1.0, 0.0, 0.0][:n_components]),
            components=np.zeros((min(n_components, n_samples), n_exp, n_k)),
            scores=np.zeros((n_samples, min(n_components, n_samples))),
        )

    # SVD
    u, s, vt = np.linalg.svd(centered, full_matrices=False)
    explained_variance = (s**2) / (n_samples - 1)
    total_var = np.sum(explained_variance)
    if total_var > 0:
        explained_ratio = explained_variance[:n_components] / total_var
    else:
        explained_ratio = np.ones(min(n_components, len(s))) / min(n_components, len(s))

    comp_count = min(n_components, vt.shape[0])
    components = vt[:comp_count, :].reshape(comp_count, n_exp, n_k)
    scores = centered @ vt[:comp_count, :].T

    return SurfacePcaResult(
        mean_surface=mean_surface.reshape(n_exp, n_k),
        explained_variance_ratio=explained_ratio,
        components=components,
        scores=scores,
    )
