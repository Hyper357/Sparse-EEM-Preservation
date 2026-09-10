from pathlib import Path
import hashlib
import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_verified(root: Path):
    path = root / '01_DATA' / 'measured_verified' / 'eem_measured.npz'
    z = np.load(path, allow_pickle=True)
    required = {'clean_masked_tensor', 'mask_valid_stokes', 'site_ids', 'ex_grid', 'em_grid'}
    missing = required - set(z.files)
    if missing:
        raise ValueError(f'missing required arrays: {sorted(missing)}')
    tensor = z['clean_masked_tensor'].astype(float)
    valid = z['mask_valid_stokes'].astype(bool)
    sites = z['site_ids'].astype(str)
    ex, em = z['ex_grid'].astype(int), z['em_grid'].astype(int)
    expected_sites = [f'S{i:02d}' for i in range(1, 29)] + ['S30']
    if list(sites) != expected_sites or 'S29' in sites:
        raise ValueError(f'unexpected main sites: {list(sites)}')
    if tensor.shape != (29, 81, 111) or valid.shape != (81, 111):
        raise ValueError(f'unexpected tensor/mask shape: {tensor.shape}, {valid.shape}')
    if not np.array_equal(ex, np.arange(300, 701, 5)) or not np.array_equal(em, np.arange(250, 801, 5)):
        raise ValueError('unexpected EX/EM grid')
    if int(valid.sum()) != 4149:
        raise ValueError(f'unexpected common valid positions: {valid.sum()}')
    return {'path': path, 'tensor': tensor, 'valid': valid, 'sites': sites, 'ex': ex, 'em': em,
            'sha256': sha256(path), 'npz_keys': z.files}


def load_v5(root: Path):
    base = root / '03_ANALYSIS' / 'measured_verified'
    sets = pd.read_csv(base / 'selected_excitation_sets_by_fold.csv')
    rho = pd.read_csv(base / 'site_structure_preservation.csv')
    rho = rho.rename(columns={'spearman_rho_shape_l2': 'rho_structure'})
    return sets, rho
