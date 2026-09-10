# Changelog

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
