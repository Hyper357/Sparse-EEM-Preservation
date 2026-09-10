import numpy as np


def selected_indices(ex_grid, selected_ex):
    pos = {int(v): i for i, v in enumerate(ex_grid)}
    if len(selected_ex) != len(set(selected_ex)) or any(int(v) not in pos for v in selected_ex):
        raise ValueError('selected EX contains duplicate or off-grid wavelength')
    return np.array([pos[int(v)] for v in selected_ex], dtype=int)


def reconstruct(sample, ex_grid, valid_mask, selected_ex):
    """Reconstruct only from selected measured EX responses; invalid cells remain NaN."""
    idx = selected_indices(ex_grid, selected_ex)
    out = np.full(sample.shape, np.nan, dtype=float)
    support = np.zeros(sample.shape, dtype=np.int8)
    for j in range(sample.shape[1]):
        ok = valid_mask[idx, j] & np.isfinite(sample[idx, j])
        if not ok.any():
            continue
        x = ex_grid[idx][ok]
        y = sample[idx, j][ok]
        support[:, j] = len(x)
        if len(x) == 1:
            out[:, j] = y[0]
        else:
            # np.interp is linear inside support and nearest-edge outside support.
            out[:, j] = np.interp(ex_grid, x, y)
    out[~valid_mask] = np.nan
    support[~valid_mask] = 0
    return out, support


def domain_masks(ex_grid, valid_mask, selected_ex):
    lo, hi = min(selected_ex), max(selected_ex)
    full = valid_mask.copy()
    interp = full & (ex_grid[:, None] >= lo) & (ex_grid[:, None] <= hi)
    return full, interp
