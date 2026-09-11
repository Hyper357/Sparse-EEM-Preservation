# V6 analysis freeze

## Scope

This handoff freezes the existing V5 measured analysis and completed reconstruction/dual-endpoint pilot. It covers 29 main sites (S01-S28 and S30); S29 is excluded. The input is `clean_masked_tensor` on the verified 29 x 81 EX x 111 EM grid, with 4,149 common-valid EX-EM positions. No synthetic repeats, new samples, or new scientific analysis are introduced here.

## Primary endpoint

The primary endpoint is full-EEM-derived inter-sample structural preservation, `rho_structure = Spearman(d_full, d_sparse)`. Full and sparse vectors are separately L2-normalized; cosine distance is calculated from each held-out site to the other 28 sites, and the two distance vectors are compared by Spearman correlation. The main NAIG analysis uses the 20 nm minimum-spacing results. The 10 nm and 30 nm spacing results are sensitivity analyses only.

## Complementary endpoint

The complementary endpoint is full-EEM spectral reconstruction fidelity. Reconstruction is fixed to piecewise-linear interpolation along EX with nearest-edge extension, followed by restoration of the physical mask as missing. Publication-facing metrics are relative Frobenius error over supported positions within the full common-valid EEM domain, spectral cosine, and supported/unsupported fractions. It is not an EEM information percentage. Fig.1 representative measured EEM requires access to the existing V5 figure source / measured tensor and is not contained as raster data in this freeze package.

## Main structural results (20 nm minimum spacing)

NAIG: K1 median 0.8785; K2 median 0.9431; K3 median 0.9540 (P10 0.8604, minimum 0.4094, 24/29 >= 0.90, 19/29 >= 0.95); K4 median 0.9562 (minimum 0.6568); K5 median 0.9507 (minimum 0.8763); K6 median 0.9540 (P10 0.9351, minimum 0.9239, 29/29 >= 0.90, 19/29 >= 0.95); K7 median 0.9661; K8 median 0.9710 (minimum 0.9195, 24/29 >= 0.95).

## Strategy comparison

Uniform K4: median rho 0.9589, minimum 0.9015, 29/29 >= 0.90. Uniform K8: median rho 0.9869, 28/29 >= 0.95. VIG K4: median rho 0.9677, minimum 0.5402. Random combination-level structural results: K2 median 0.8533 and P95 0.9562; K3 median 0.9075 and P95 0.9726.

## Reconstruction and dual endpoint

Uniform-4 (`300;435;565;700`): median RE_F 0.263724, median cosine 0.968078, supported fraction 0.998313, median rho 0.958949, minimum rho 0.901478, 29/29 >= 0.90. Uniform-6 (`300;380;460;540;620;700`): median RE_F 0.219820, median cosine 0.975957, median rho 0.971538, minimum rho 0.858238, 28/29 >= 0.90. Uniform reconstruction improves overall with K but is not strictly monotonic.

Uniform-4 percentile ranks (structural median, minimum rho, coverage, reconstruction-error performance, cosine): 64.8, 78.2, 100.0, 38.2, 34.0. Uniform-6: 55.8, 36.0, 54.2, 69.6, 57.8. Neither fixed Uniform configuration is on the current dual-objective Pareto front. Exploratory same-dataset selected candidate K4 `320;440;530;640`: median RE_F 0.2231, median rho 0.97975, minimum rho 0.95731, 29/29 >= 0.95; this is exploratory and not externally validated.

## Technical repeats and sensitivity

Technical repeats contain 7 sites / 8 scenarios. Full-repeat rho is 0.6190 (S06), 0.8303 (S07), and 0.1078 (S22); these values must not be assigned a chemical or instrument cause without records. Spacing K1-K4 medians are identical under 10/20/30 nm; fold-level results are identical only through K1-K3, with S10/K4 as the 30 nm exception. Finite-window results remain those in the existing V5 measured output and are sensitivity evidence.

## Environmental supplementary

Some field-environment differences are associated with full-EEM spectral geometry in the supplementary analysis; environment versus sparse loss has no stable cross-budget FDR association. These observations do not modify the frozen EEM workflow.
