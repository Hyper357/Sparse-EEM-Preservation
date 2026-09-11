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
    (OUT / "V6_NUMBER_SHEET.md").write_text("# V6 number sheet\n\n- Scope: 29 sites (S01-S28, S30); S29 excluded; common-valid target domain: 4,149 EX-EM positions.\n- Structural endpoint: V5 `spearman_rho_shape_l2`, interpreted as inter-sample distance-ranking preservation.\n- Reconstruction: supported-position relative Frobenius error and spectral cosine; unsupported fraction is reported separately.\n- Uniform K=3 to K=4 is a small reversal, so the trend is overall improvement but not strictly monotonic.\n\n## Structural summary\n\n```csv\n" + selected.to_csv(index=False) + "```\n", encoding="utf-8")
    (OUT / "V6_CLAIM_BOUNDARIES.md").write_text("# V6 claim boundaries\n\n- Primary endpoint remains V5 structural ranking preservation (`rho_structure`).\n- Full-EEM reconstruction is supplementary validation, not an information-retention percentage.\n- Report reconstruction error only as error over supported positions within the full common-valid EEM domain; pair it with support/unsupported fractions.\n- NAIG and Uniform reconstruction trends are strategy-dependent; do not claim a universal optimal EX count or hardware performance.\n- Environmental associations are supplementary observational background and do not causally correct the EEM workflow.\n- Repeat outputs are contextual QC and are not additional independent main-scan samples.\n", encoding="utf-8")
    manifest = {"sites": SITES, "n_sites": 29, "target_positions": 4149, "rows_reconstruction_vs_structure": len(recon), "source": "V5 verified outputs + completed reconstruction/dual-endpoint pilot", "nrmse_policy": "internal cross-check only; not publication-facing"}
    (OUT / "V6_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
