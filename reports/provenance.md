# Provenance

- Input file: `01_DATA/measured_verified/eem_measured.npz` (outside this repository; not uploaded).
- Input SHA256: recorded in `outputs/pilot_manifest.json`.
- Arrays used: `clean_masked_tensor`, `mask_valid_stokes`, `site_ids`, `ex_grid`, `em_grid`.
- Main sites: S01–S28 and S30 (29); S29 excluded because it has no valid main EEM.
- Grid: EX 300–700 nm in 5 nm steps (81); EM 250–800 nm in 5 nm steps (111).
- Common valid physical positions: 4,149.
- V5 selection source: `03_ANALYSIS/measured_verified/selected_excitation_sets_by_fold.csv`.
- V5 structure source: `03_ANALYSIS/measured_verified/site_structure_preservation.csv`.
- Selection: fold-specific V5 NAIG and V5-defined Uniform; held-out site excluded from NAIG selection by source protocol.
- Reconstruction: piecewise linear interpolation along EX, nearest-edge extension, one-support constant, zero-support missing; no random process and no seed required.
- Python environment used: Python 3.10; NumPy 2.2.6; pandas 2.3.3; Matplotlib 3.10.9; pytest 8.x.
- Runtime: 2026-09-10 Asia/Shanghai; exact generated timestamp in `outputs/pilot_manifest.json`.
- Git commit before push: `a4651c528192c3a73c3a7851d7a687241bd786af` (the final amended SHA is reported by Git after this provenance update).
