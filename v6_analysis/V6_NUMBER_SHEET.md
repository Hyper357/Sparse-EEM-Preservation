# V6 number sheet — sole manuscript numeric entry point

All values below are transcribed from the existing frozen V5/pilot outputs. Status labels indicate intended manuscript use; no values were recomputed in this handoff. Do not use sensitivity or exploratory rows as main results.

## Abstract

- `0.9540`: NAIG K3 median structural-ranking preservation; MAIN, 20 nm spacing.
- `0.9540`: NAIG K6 median structural-ranking preservation; MAIN, 20 nm spacing.
- `0.219820`: Uniform-6 median supported-position RE_F; COMPLEMENTARY, fixed reconstruction pilot.

## Methods

- `29`: main sites S01-S28 + S30; MAIN.
- `4,149`: common-valid EX-EM positions; MAIN.
- `29-fold`: held-out-site evaluation, each held-out site compared with 28 others; MAIN.
- `5 nm`: adjacent-EX red-response summary spacing; SUPPLEMENTARY context, not full-EEM dimensionality.

## Results 3.1 — adjacent-EX correlations

- `0.8937` mean and `0.8973` median: cross-site Spearman correlation for 80 adjacent 5 nm red-response EX pairs; SUPPLEMENTARY/observational context.

## Results 3.2 — main NAIG K results

All values in this subsection are `median rho_structure` under 20 nm minimum spacing, status MAIN: K1 `0.8785`; K2 `0.9431`; K3 `0.9540` (P10 `0.8604`, minimum `0.4094`, 24/29 >=0.90, 19/29 >=0.95); K4 `0.9562` (minimum `0.6568`); K5 `0.9507` (minimum `0.8763`); K6 `0.9540` (P10 `0.9351`, minimum `0.9239`, 29/29 >=0.90, 19/29 >=0.95); K7 `0.9661`; K8 `0.9710` (minimum `0.9195`, 24/29 >=0.95).

## Results 3.3 — strategy results

- Uniform K4: median `0.9589`, minimum `0.9015`, 29/29 >=0.90; MAIN, 20 nm spacing.
- Uniform K8: median `0.9869`, 28/29 >=0.95; MAIN, 20 nm spacing.
- VIG K4: median `0.9677`, minimum `0.5402`; MAIN, 20 nm spacing.
- Random K2: combination-level median `0.8533`, P95 `0.9562`; EXPLORATORY.
- Random K3: combination-level median `0.9075`, P95 `0.9726`; EXPLORATORY.
- 10 nm and 30 nm spacing: SENSITIVITY only; do not substitute for the 20 nm main values.

## Results 3.4 — reconstruction

- Uniform-4 (`300;435;565;700`): RE_F median `0.263724`, cosine median `0.968078`, supported fraction median `0.998313`; COMPLEMENTARY.
- Uniform-6 (`300;380;460;540;620;700`): RE_F median `0.219820`, cosine median `0.975957`; COMPLEMENTARY.
- Uniform reconstruction has overall improvement with K but is not strictly monotonic; COMPLEMENTARY.

## Results 3.5 — complementarity and dual endpoint

- S21 NAIG K3: rho `~0.957`, RE_F `~0.685`, cosine `~0.771`; COMPLEMENTARY example.
- Uniform-4 percentile ranks: structural median `64.8`, minimum rho `78.2`, coverage `100.0`, reconstruction-error performance `38.2`, cosine `34.0`; EXPLORATORY comparison.
- Uniform-6 percentile ranks: `55.8`, `36.0`, `54.2`, `69.6`, `57.8`; EXPLORATORY comparison.
- Fixed Uniform-4 and Uniform-6 are not on the current dual-objective Pareto front; EXPLORATORY.
- K4 `320;440;530;640`: RE_F median `0.2231`, rho median `0.97975`, minimum rho `0.95731`, 29/29 >=0.95; EXPLORATORY, same-dataset selected, not externally validated.

## Results 3.6 — repeats and sensitivity

- Full-repeat rho: S06 `0.6190`, S07 `0.8303`, S22 `0.1078`; SUPPLEMENTARY technical QC, no causal attribution.
- Technical repeat scope: 7 sites / 8 scenarios; SUPPLEMENTARY.
- Spacing K1-K4 medians identical under 10/20/30 nm; fold-level identical only K1-K3; K4/S10 is the 30 nm exception; SENSITIVITY.
- Finite-window results: use `tables/sensitivity_results.csv`; SENSITIVITY.

## Supplementary

- Environment: some field-environment differences associate with full-EEM spectral geometry; environment vs sparse loss has no stable cross-budget FDR association; SUPPLEMENTARY observational background.
- Detailed spacing/window results: `tables/sensitivity_results.csv`; SENSITIVITY.
- Random/Pareto candidates: `figure_data/fig4_random_pareto_K4.csv` and `_K6.csv`; EXPLORATORY.

NRMSE is intentionally absent from this public number sheet: it is an internal algebraic cross-check of RE_F under the same normalization, not a second validation endpoint.
