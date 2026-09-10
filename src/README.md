# src

This directory contains the implementation for the completed reconstruction pilot. Run `python src/reconstruction_pilot.py --config configs/pilot.yaml` from the repository root to regenerate all derived tables and figures. The loader reads verified V5 inputs one directory above this repository and stores no raw EEM data here.

## Implementation rules

The first code version should be deliberately simple and auditable.

Required properties:

- Python implementation;
- deterministic outputs;
- reuse the verified V5 site list and common physical mask;
- preserve missing values in excluded Rayleigh/Raman regions;
- no learned reconstruction model in the baseline;
- one shared reconstruction function for all EX-selection strategies;
- explicit handling of EX boundaries;
- per-site and per-configuration machine-readable outputs;
- figures generated from saved result tables, not from hidden in-memory states.

Suggested modules:

```text
src/
├── reconstruct.py
├── metrics.py
├── run_pilot.py
└── plotting.py
```

## Baseline reconstruction API

Suggested interface:

```python
reconstruct_eem(
    full_eem,
    ex_grid,
    em_grid,
    valid_mask,
    selected_ex,
    boundary_mode="nearest",
)
```

The function should return both:

- reconstructed full-grid EEM;
- a reconstruction-evaluation mask.

## Reproducibility

Every pilot run should record:

- input file manifest;
- selected EX set;
- strategy name;
- K;
- reconstruction rule;
- boundary rule;
- metric definitions;
- random seed where applicable;
- output table checksum or commit SHA.

Do not add optimized or neural reconstruction until the transparent baseline has been evaluated and archived.
