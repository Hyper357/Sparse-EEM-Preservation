# Sparse-EEM-Preservation

A research workspace for evaluating how much of a full excitation-emission matrix (EEM) is preserved when only a small number of excitation wavelengths (EX) are retained.

## Scientific question

A full EEM contains dense fluorescence responses across excitation and emission dimensions. A future compact fluorescence sensor may only be able to measure a small number of excitation wavelengths. This repository studies a staged question:

> If only K excitation slices are measured, how well can the full EEM itself be reconstructed, and how well are the inter-sample relationships defined by the full EEM preserved?

The project deliberately separates two endpoints that should not be conflated:

1. **Full-EEM reconstruction fidelity** — preservation of the spectral object itself.
2. **Inter-sample structural preservation** — preservation of sample-to-sample relationships induced by the full EEM.

Neither endpoint is interpreted as "percentage of all EEM information" or as a direct measure of algae-classification information.

## Proposed V6 pilot

The first pilot should keep the existing V5 wavelength-selection framework unchanged and add a transparent reconstruction endpoint.

### A. Reconstruction endpoint

For a selected set of K excitation wavelengths:

1. retain all physically valid emission responses for each selected EX;
2. reconstruct missing EX slices along the excitation axis using a fixed, non-learning baseline;
3. compare the reconstructed EEM with the measured full EEM on the common valid mask.

Initial baseline:

- piecewise linear interpolation along the EX axis;
- no neural network or learned reconstruction model;
- one identical reconstruction rule for all wavelength-selection strategies;
- no interpolation into physically excluded Rayleigh/Raman mask positions;
- explicit handling of wavelengths outside the selected EX range.

Primary candidate reconstruction metrics:

- relative Frobenius error;
- NRMSE;
- full-vs-reconstructed spectral cosine similarity or spectral angle.

### B. Structural-preservation endpoint

Retain the V5 endpoint:

- L2-normalize full and sparse EEM representations;
- compute cosine distances between samples;
- for each held-out site, compare its full-EEM distance ranking to its sparse-EX distance ranking using Spearman correlation.

This endpoint measures preservation of **full-EEM-derived inter-sample relational structure**, not full spectral reconstruction.

## Interpretation

The most informative outcome may be a difference between the two endpoints. For example, a small K may preserve sample relationships well while still reconstructing the full EEM imperfectly. Such a result would imply that the excitation budget required for downstream representation may be smaller than the budget required for faithful recovery of the original high-resolution EEM.

Conversely, if reconstruction and structural preservation improve together, this would strengthen the case that a compact EX set captures broadly useful spectral variation.

## Guardrails

This project does **not** assume that:

- EEM information is equivalent to algae information;
- a wavelength set that is optimal for EEM reconstruction is optimal for algae classification;
- reconstruction fidelity alone validates a specific hardware design;
- a 4–6 EX budget is a universal optimum;
- simulated finite EX windows validate a real LED spectral power distribution.

Task-specific algae classification or quantification requires separate labeled validation.

## Repository structure

- `docs/scientific_question.md` — precise problem definition and scope.
- `docs/methodology_v1.md` — proposed dual-endpoint methodology.
- `docs/reconstruction_metrics.md` — definitions and interpretation of reconstruction metrics.
- `docs/relation_to_V5.md` — how this pilot extends rather than replaces V5.
- `protocols/reconstruction_pilot_protocol.md` — executable analysis protocol for the next coding stage.
- `src/README.md` — implementation rules before code is added.
- `CHANGELOG.md` — methodology history.

## Status

The isolated reconstruction pilot has been executed for NAIG and V5-defined Uniform at K = 2, 3, 4, 6, and 8 using 29 verified main scans. Reproducible code is in `src/`, tables and 300-dpi/vector figures are in `outputs/`, and the interpretation is documented in `reports/reconstruction_pilot_report.md`. The pilot recommends retaining V5 structural rho as primary and reconstruction as supplementary; no V5/V6 manuscript text was changed.
