"""Build the reviewable V6 analysis freeze from immutable V5/pilot outputs."""
from pathlib import Path
import json
import shutil
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
V5 = PARENT / "03_ANALYSIS" / "measured_verified"
PILOT = ROOT / "outputs" / "tables"
ENV = PARENT / "environmental_background_outputs"
OUT = ROOT / "v6_analysis"

SITES = [f"S{i:02d}" for i in range(1, 29)] + ["S30"]

def cp(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)

def write(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")

def main():
    (OUT / "tables").mkdir(parents=True, exist_ok=True)
    (OUT / "figure_data").mkdir(parents=True, exist_ok=True)
    structural = pd.read_csv(V5 / "site_structure_preservation.csv")
    recon = pd.read_csv(PILOT / "reconstruction_vs_structure.csv")
    assert len(recon) == 290 and set(recon.site_id) == set(SITES)
    assert "S29" not in set(recon.site_id)

    # Publication-facing outputs use non-redundant metrics only.
    write(pd.read_csv(V5 / "spacing_summary.csv"), OUT / "tables" / "main_structural_results.csv")
    write(pd.read_csv(PILOT / "reconstruction_summary_publication.csv"), OUT / "tables" / "reconstruction_results.csv")
    fixed = pd.read_csv(PILOT / "fixed_configuration_summary.csv")
    pct = pd.read_csv(PILOT / "dual_endpoint_percentiles.csv")
    write(fixed.merge(pct, on=["configuration_id", "K", "selected_ex"], how="left", suffixes=("", "_percentile")), OUT / "tables" / "dual_endpoint_results.csv")
    targets = pd.read_csv(V5 / "actual_repeat_targets.csv").assign(result_type="repeat_target")
    substitution = pd.read_csv(V5 / "actual_repeat_substitution.csv").assign(result_type="repeat_substitution")
    repeats = pd.concat([targets, substitution], ignore_index=True, sort=False)
    write(repeats, OUT / "tables" / "repeat_results.csv")
    sens = pd.concat([pd.read_csv(V5 / "finite_window_summary.csv"), pd.read_csv(V5 / "spacing_summary.csv")], ignore_index=True, sort=False)
    write(sens, OUT / "tables" / "sensitivity_results.csv")
    envs = []
    for f in ["environment_vs_sparse_loss.csv", "environment_vs_eem_proxy_statistics.csv", "turbidity_rho_statistics.csv", "mrm_chlorophyll_turbidity_results.csv"]:
        d = pd.read_csv(ENV / f); d.insert(0, "source_file", f); envs.append(d)
    write(pd.concat(envs, ignore_index=True, sort=False), OUT / "tables" / "environment_supplement.csv")

    # Figure-ready data; selected EX remain strings to preserve fold-specific order.
    write(recon[["site_id", "strategy", "K", "selected_ex", "rho_structure", "relative_frobenius_error_fullrange", "spectral_cosine_fullrange", "reconstruction_supported_fraction_fullrange", "unsupported_fraction_fullrange"]], OUT / "figure_data" / "fig3_structural_vs_K.csv")
    write(recon[["site_id", "strategy", "K", "selected_ex", "relative_frobenius_error_fullrange", "relative_frobenius_error_interpdomain", "spectral_cosine_fullrange", "spectral_cosine_interpdomain", "reconstruction_supported_fraction_fullrange", "unsupported_fraction_fullrange"]], OUT / "figure_data" / "fig4_reconstruction_vs_K.csv")
    write(recon[["site_id", "strategy", "K", "selected_ex", "rho_structure", "relative_frobenius_error_fullrange", "spectral_cosine_fullrange"]], OUT / "figure_data" / "fig4_dual_endpoint_scatter.csv")
    write(fixed, OUT / "figure_data" / "fig4_fixed_configuration_comparison.csv")
    write(pd.read_csv(PILOT / "pareto_front_K4.csv"), OUT / "figure_data" / "fig4_random_pareto_K4.csv")
    write(pd.read_csv(PILOT / "pareto_front_K6.csv"), OUT / "figure_data" / "fig4_random_pareto_K6.csv")
    write(repeats, OUT / "figure_data" / "fig5_repeat_results.csv")
    # Representative EEM panel metadata and measured selected-slice coordinates.
    examples = recon[recon.site_id.isin(["S01", "S15", "S30"]) & recon.K.isin([4, 6])].copy()
    examples.insert(0, "panel_role", "representative_main_scan")
    write(examples, OUT / "figure_data" / "fig1_eem_examples.csv")
    write(recon[["strategy", "K", "selected_ex", "relative_frobenius_error_fullrange", "spectral_cosine_fullrange", "rho_structure"]], OUT / "figure_data" / "fig3_strategy_comparison.csv")
    (OUT / "figure_data" / "README.md").write_text("All CSVs are derived from frozen V5/pilot outputs. No synthetic repeats or new EX selections were generated. Reconstruction metrics are supported-position metrics; rho is structure-ranking preservation.\n", encoding="utf-8")

    # Machine-readable number sheet and claim boundary.
    num = pd.read_csv(V5 / "spacing_summary.csv")
    selected = num[num.N_EX.isin([1,2,3,4,6,8])].copy()
    (OUT / "V6_NUMBER_SHEET.md").write_text(NUMBER_SHEET, encoding="utf-8")
    (OUT / "V6_ANALYSIS_FREEZE.md").write_text(FREEZE, encoding="utf-8")
    (OUT / "V6_CLAIM_BOUNDARIES.md").write_text(CLAIMS, encoding="utf-8")
    manifest = {"sites": SITES, "n_sites": 29, "target_positions": 4149, "rows_reconstruction_vs_structure": len(recon), "source": "V5 verified outputs + completed reconstruction/dual-endpoint pilot", "nrmse_policy": "internal cross-check only; not publication-facing"}
    (OUT / "V6_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

FREEZE = """# V6 analysis freeze

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
"""

NUMBER_SHEET = """# V6 number sheet — sole manuscript numeric entry point

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
"""

CLAIMS = """# V6 claim boundaries

## Allowed

- full-EEM-derived inter-sample structural preservation;
- supported-position reconstruction fidelity;
- complementary structural and reconstruction endpoints;
- candidate EX budget for this dataset and fixed evaluation rule;
- exploratory fixed candidate configuration, explicitly labelled and not externally validated.

## Prohibited

- rho as EEM information percentage;
- cosine or `1 - RE_F` as information-recovery percentage;
- optimal algae channels or validated hardware wavelengths;
- claim that 6 x 4 is already validated;
- LED or hardware validation;
- CDOM concentration claims;
- causal environmental correction of the EEM workflow;
- universal optimal EX count or generalization beyond this measured dataset;
- treating technical repeats as independent main samples;
- treating NRMSE as independent evidence from RE_F.
"""

if __name__ == "__main__":
    main()
