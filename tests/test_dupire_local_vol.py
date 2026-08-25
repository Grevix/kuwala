import numpy as np

import kuwala


def test_dupire_flat_surface_consistency():
    # If implied volatility is constant sigma=0.20 across all expiries and strikes,
    # then Dupire local volatility should identically equal 0.20.
    expiries = [0.25, 0.50, 0.75, 1.0]
    k_grid = np.linspace(-0.2, 0.2, 30)
    w_mat = np.zeros((len(expiries), len(k_grid)))
    for i, t in enumerate(expiries):
        w_mat[i, :] = (0.20**2) * t

    surf = kuwala.volatility.VolatilitySurface("TEST", 100.0, expiries, k_grid, w_mat)
    loc_vol = surf.local_vol()

    # Middle rows/cols should be close to 0.20
    mid_vals = loc_vol[1:3, 10:20]
    np.testing.assert_allclose(mid_vals, 0.20, rtol=1e-3)
