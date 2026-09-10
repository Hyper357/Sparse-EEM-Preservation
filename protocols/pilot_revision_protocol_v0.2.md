# Pilot Revision Protocol v0.2

## Purpose

This revision does **not** change the scientific route selected by the completed sparse-EX reconstruction Pilot. The goal is to correct three methodological/reporting issues before the reconstruction analysis is considered stable enough for V6 integration.

Current route remains:

- V5 structural preservation (`rho_structure`) = primary endpoint;
- full-EEM reconstruction = supplementary validation;
- V5/V6 manuscript text remains unchanged during this revision.

## Issue 1 — Correct the monotonicity claim for Uniform

The current report states that Uniform improves steadily with increasing K. This is not strictly supported by the output table.

Observed Uniform medians:

- K=2: relative Frobenius error = 0.2738578661; spectral cosine = 0.9642711187
- K=3: relative Frobenius error = 0.2572379139; spectral cosine = 0.9709158933
- K=4: relative Frobenius error = 0.2637237504; spectral cosine = 0.9680782170
- K=6: relative Frobenius error = 0.2198197509; spectral cosine = 0.9759571782
- K=8: relative Frobenius error = 0.1919923637; spectral cosine = 0.9817267041

Therefore K=3 -> K=4 shows a small reversal. Required wording:

> Uniform reconstruction shows an overall improvement as excitation budget increases, but the trend is not strictly monotonic.

Do not use `steadily improves`, `monotonically improves`, or equivalent language unless a formal monotonic statistic supports it.

## Issue 2 — Remove metric redundancy

The current implementation reports both:

`RE_F = ||X_hat - X||_F / ||X||_F`

and

`NRMSE_energy = sqrt(mean((X_hat-X)^2)) / sqrt(mean(X^2))`

When computed over the same supported positions, these are algebraically identical:

`NRMSE_energy = RE_F`.

Therefore they must not be presented as two independent validation metrics.

Required action:

- retain `relative_frobenius_error` as the primary numerical reconstruction-error metric;
- retain `spectral_cosine` as the complementary spectral-shape metric;
- retain `rho_structure` as the independent sample-relationship endpoint;
- either remove `nrmse_energy_*` from publication-facing summary tables/figures, or keep it only as a clearly labelled implementation cross-check with an explicit note that it is algebraically identical to `RE_F` under the present normalization;
- update tests to assert numerical equivalence if the NRMSE column is retained internally.

Do not describe RE_F and NRMSE_energy as independent evidence.

## Issue 3 — Clarify the meaning of full-range reconstruction error

The current code defines the numerical reconstruction metrics only on positions satisfying:

`target_mask & isfinite(X_hat)`.

Therefore positions inside the 4149-position common-valid target domain that have no reconstruction support do not enter the numerical error term. Their fraction is reported separately as `unsupported_fraction`.

This handling is acceptable for the Pilot, but the terminology must not imply that every target position contributed to the numerical error calculation.

Required action:

Use publication-facing wording such as:

> reconstruction error over supported positions within the full common-valid EEM domain

and report the support/unsupported fraction alongside it.

Do not describe this value alone as `full-EEM reconstruction error` without the support qualifier.

For every strategy x K summary, retain at least:

- `relative_frobenius_error_supported_full_domain`
- `spectral_cosine_supported_full_domain`
- `reconstruction_supported_fraction_full_domain`
- `unsupported_fraction_full_domain`
- interpolation-domain counterparts
- `rho_structure`

If existing column names are retained for backward compatibility, provide a publication-facing renamed table and document the mapping.

## Required QA

After revision:

1. Recompute all affected derived tables from the same frozen Pilot inputs.
2. Do not change selected EX sets, sites, masks, reconstruction rule, K values, or strategies.
3. Verify 290 rows remain: 29 sites x 2 strategies x 5 K.
4. Verify S29 remains absent.
5. Verify common-valid target count remains 4149.
6. Verify Uniform K=3 -> K=4 is described as a small reversal, not monotonic improvement.
7. If `nrmse_energy` is retained internally, assert `allclose(RE_F, NRMSE_energy)` over all non-missing rows.
8. Ensure all figures and publication-facing summary tables use only non-redundant metrics.
9. Do not alter the Route 2 decision unless the corrections themselves reveal an implementation error that materially changes the results.

## Expected outputs

At minimum update:

- `reports/reconstruction_pilot_report.md`
- `docs/reconstruction_metrics.md`
- `outputs/tables/reconstruction_summary.csv` or add a publication-facing cleaned summary table
- relevant plotting code if NRMSE was exposed as an independent metric
- tests
- `CHANGELOG.md`

Optionally add:

- `outputs/tables/reconstruction_summary_publication.csv`

with concise, non-redundant columns.

## Scientific interpretation to preserve

The main interpretation remains:

> Sparse-excitation preservation of full-EEM-derived sample relationship structure is not equivalent to pointwise full-EEM reconstruction fidelity. The two endpoints are complementary and can favour different excitation-selection strategies.

Do not convert spectral cosine or `1 - RE_F` into an "EEM information percentage".
