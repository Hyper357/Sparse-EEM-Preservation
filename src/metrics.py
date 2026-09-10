import numpy as np
import pandas as pd


def reconstruction_metrics(x, xhat, target_mask, support):
    """Return metrics on supported targets plus explicit domain coverage.

    ``nrmse_energy`` is retained as a backward-compatible implementation
    cross-check. With the same supported positions and energy normalization,
    it is algebraically identical to relative Frobenius error.
    """
    target = target_mask.astype(bool)
    supported = target & np.isfinite(xhat)
    n = int(target.sum())
    ns = int(supported.sum())
    single = int((supported & (support == 1)).sum())
    unsupported = target & ~np.isfinite(xhat)
    out = {'target_positions': n, 'supported_positions': ns,
           'single_support_positions': single, 'unsupported_positions': int(unsupported.sum()),
           'reconstruction_supported_fraction': ns / n if n else np.nan,
           'single_support_fraction': single / n if n else np.nan,
           'unsupported_fraction': int(unsupported.sum()) / n if n else np.nan}
    if ns == 0:
        return {**out, 'relative_frobenius_error': np.nan, 'nrmse_energy': np.nan, 'spectral_cosine': np.nan}
    a, b = x[supported], xhat[supported]
    diff = b - a
    denom = np.linalg.norm(a)
    out.update(relative_frobenius_error=float(np.linalg.norm(diff) / denom) if denom else np.nan,
               nrmse_energy=float(np.sqrt(np.mean(diff ** 2)) / np.sqrt(np.mean(a ** 2))) if np.mean(a ** 2) else np.nan,
               spectral_cosine=float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))) if np.linalg.norm(b) else np.nan)
    return out


def spearman(a, b):
    return float(pd.Series(a).rank(method='average').corr(pd.Series(b).rank(method='average')))
