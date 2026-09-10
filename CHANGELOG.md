# Changelog

## 2026-09-10 — Reconstruction pilot executed

### Added

- deterministic NAIG and V5-defined Uniform full-EEM reconstruction pilot for K = 2, 3, 4, 6, and 8 across 29 verified main scans;
- common-mask-aware interpolation, nearest-edge extension, explicit single/unsupported support accounting, and edge diagnostics;
- per-site joint reconstruction/structure table, complete distribution summaries, five figure sets in 300-dpi PNG/PDF/SVG, tests, provenance, and decision report.

### Decision

Route 2: retain V5 structural rho as the primary endpoint and reconstruction as supplementary validation. V5/V6 manuscript text was not modified.

## 2026-09-10 — Methodology v0.1

Initial repository structure established for sparse-excitation EEM preservation analysis.

### Added

- clear separation between full-EEM reconstruction fidelity and inter-sample structural preservation;
- non-learning baseline reconstruction by piecewise linear interpolation along the EX axis;
- explicit common-mask and boundary-handling rules;
- reconstruction metrics: relative Frobenius error, NRMSE, spectral cosine similarity / spectral angle;
- relation to existing V5 cosine-distance + Spearman structure-ranking endpoint;
- reconstruction pilot protocol with pre-specified decision rules;
- implementation guardrails for future Python code.

### Scientific boundary

The project does not interpret any single metric as a universal percentage of "EEM information" and does not assume that EEM-preserving wavelengths are automatically optimal for algae classification or quantification.

### Next milestone

Run the isolated reconstruction pilot on the verified V5 dataset before changing the manuscript's primary endpoint.
