"""Deterministic reconstruction pilot for the verified measured EEM tensor.

This is deliberately a small, auditable baseline: interpolation along EX,
nearest-edge extension, and no fitting on the held-out site.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "01_DATA" / "measured_verified" / "eem_measured.npz"
SETS = ROOT / "03_ANALYSIS" / "measured_verified" / "selected_excitation_sets_by_fold.csv"
RHO = ROOT / "03_ANALYSIS" / "measured_verified" / "site_structure_preservation.csv"
OUT = Path(__file__).resolve().parents[1] / "results"


def reconstruct(sample, ex_grid, valid_mask, selected_ex):
    """Interpolate each EM column, preserving invalid physical-mask cells."""
    selected_idx = np.array([int(np.where(ex_grid == x)[0][0]) for x in selected_ex])
    order = np.argsort(selected_idx)
    selected_idx = selected_idx[order]
    result = np.full_like(sample, np.nan, dtype=float)
    for j in range(sample.shape[1]):
        ok = valid_mask[selected_idx, j] & np.isfinite(sample[selected_idx, j])
        if not ok.any():
            continue
        y = sample[selected_idx, j][ok]
        x = ex_grid[selected_idx][ok]
        # Selected rows are within the common valid mask in this dataset.
        result[:, j] = np.interp(ex_grid, x, y)
    result[~valid_mask] = np.nan
    return result


def metrics(x, xhat, eval_mask):
    a, b = x[eval_mask], xhat[eval_mask]
    diff = b - a
    denom = np.linalg.norm(a)
    rmse = float(np.sqrt(np.mean(diff ** 2)))
    cos = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    return {
        "relative_frobenius_error": float(np.linalg.norm(diff) / denom),
        "nrmse_energy": float(rmse / np.sqrt(np.mean(a ** 2))),
        "spectral_cosine": cos,
    }


def spearman_without_scipy(a, b):
    """Spearman correlation using pandas ranks (keeps the pilot lightweight)."""
    return float(pd.Series(a).rank().corr(pd.Series(b).rank()))


def main():
    z = np.load(DATA, allow_pickle=True)
    x = z["clean_masked_tensor"]
    ex = z["ex_grid"]
    valid = z["mask_valid_stokes"].astype(bool)
    sites = z["site_ids"].astype(str)
    sets = pd.read_csv(SETS)
    rho = pd.read_csv(RHO).rename(columns={"spearman_rho_shape_l2": "rho_structure"})
    wanted = sets[sets.strategy.isin(["NAIG", "Uniform"]) & sets.N_EX.isin([2, 3, 4, 6, 8])].copy()
    rows = []
    for _, rec in wanted.iterrows():
        site = str(rec.held_out_station)
        i = int(np.where(sites == site)[0][0])
        selected = [int(v) for v in str(rec.selected_ex_nm).split(";")]
        xhat = reconstruct(x[i], ex, valid, selected)
        full_eval = valid & np.isfinite(xhat)
        full_m = metrics(x[i], xhat, full_eval)
        lo, hi = min(selected), max(selected)
        interp_mask = valid & (ex[:, None] >= lo) & (ex[:, None] <= hi)
        interp_eval = interp_mask & np.isfinite(xhat)
        interp_m = metrics(x[i], xhat, interp_eval)
        r = rho[(rho.outer_fold == rec.outer_fold) & (rho.strategy == rec.strategy) & (rho.N_EX == rec.N_EX)]
        rows.append({
            "site_id": site, "outer_fold": int(rec.outer_fold), "strategy": rec.strategy,
            "K": int(rec.N_EX), "selected_ex": ";".join(map(str, selected)),
            "relative_frobenius_error_fullrange": full_m["relative_frobenius_error"],
            "relative_frobenius_error_interpdomain": interp_m["relative_frobenius_error"],
            "nrmse_energy_fullrange": full_m["nrmse_energy"],
            "spectral_cosine_fullrange": full_m["spectral_cosine"],
            "spectral_cosine_interpdomain": interp_m["spectral_cosine"],
            "n_eval_fullrange": int(full_eval.sum()), "n_eval_interpdomain": int(interp_eval.sum()),
            "rho_structure": float(r.iloc[0].rho_structure),
        })
    per_site = pd.DataFrame(rows)
    summary_rows = []
    for (strategy, k), g in per_site.groupby(["strategy", "K"], sort=True):
        summary_rows.append({
            "strategy": strategy, "K": int(k), "n_sites": len(g),
            "median_reconstruction_error_fullrange": g.relative_frobenius_error_fullrange.median(),
            "p10_reconstruction_error_fullrange": g.relative_frobenius_error_fullrange.quantile(.10),
            "worst_reconstruction_error_fullrange": g.relative_frobenius_error_fullrange.max(),
            "median_reconstruction_error_interpdomain": g.relative_frobenius_error_interpdomain.median(),
            "median_spectral_cosine_fullrange": g.spectral_cosine_fullrange.median(),
            "p10_spectral_cosine_fullrange": g.spectral_cosine_fullrange.quantile(.10),
            "worst_spectral_cosine_fullrange": g.spectral_cosine_fullrange.min(),
            "median_rho_structure": g.rho_structure.median(),
            "spearman_error_vs_rho": spearman_without_scipy(g.relative_frobenius_error_fullrange, g.rho_structure),
        })
    summary = pd.DataFrame(summary_rows)
    OUT.mkdir(parents=True, exist_ok=True)
    per_site.to_csv(OUT / "pilot_per_site.csv", index=False)
    summary.to_csv(OUT / "pilot_summary.csv", index=False)
    manifest = {
        "input": str(DATA), "input_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "selection_source": str(SETS), "rho_source": str(RHO),
        "reconstruction": "piecewise linear along EX; nearest-edge extension; invalid mask restored missing",
        "strategies": ["NAIG", "Uniform"], "K": [2, 3, 4, 6, 8], "n_sites": int(len(sites)),
        "outputs": ["pilot_per_site.csv", "pilot_summary.csv"],
    }
    (OUT / "pilot_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(summary.to_string(index=False, float_format=lambda v: f"{v:.6f}"))


if __name__ == "__main__":
    main()
