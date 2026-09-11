from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "v6_analysis"

def test_v6_freeze_shape_and_scope():
    d = pd.read_csv(OUT / "tables" / "reconstruction_results.csv")
    assert len(d) == 10
    raw = pd.read_csv(ROOT / "outputs" / "tables" / "reconstruction_vs_structure.csv")
    assert len(raw) == 290
    assert "S29" not in set(raw.site_id)
    assert set(raw.site_id) == {f"S{i:02d}" for i in range(1,29)} | {"S30"}

def test_reconstruction_crosscheck_and_no_redundancy():
    raw = pd.read_csv(ROOT / "outputs" / "tables" / "reconstruction_vs_structure.csv")
    assert (raw.relative_frobenius_error_fullrange - raw.nrmse_energy_fullrange).abs().max() < 1e-12
    pub = pd.read_csv(OUT / "tables" / "reconstruction_results.csv")
    assert not any(c.startswith("nrmse") for c in pub.columns)

def test_required_figure_data_exist():
    names = ["fig1_eem_examples.csv", "fig3_structural_vs_K.csv", "fig3_strategy_comparison.csv", "fig4_reconstruction_vs_K.csv", "fig4_dual_endpoint_scatter.csv", "fig4_fixed_configuration_comparison.csv", "fig4_random_pareto_K4.csv", "fig4_random_pareto_K6.csv", "fig5_repeat_results.csv"]
    assert all((OUT / "figure_data" / n).exists() for n in names)

def test_handoff_boundaries_are_explicit():
    freeze = (OUT / "V6_ANALYSIS_FREEZE.md").read_text(encoding="utf-8")
    nums = (OUT / "V6_NUMBER_SHEET.md").read_text(encoding="utf-8")
    claims = (OUT / "V6_CLAIM_BOUNDARIES.md").read_text(encoding="utf-8")
    assert "20 nm minimum spacing" in freeze
    assert "10 nm and 30 nm spacing" in nums and "SENSITIVITY" in nums
    for term in ["reconstruction", "dual endpoint", "repeats", "environment"]:
        assert term.lower() in nums.lower()
    for forbidden in ["information percentage", "optimal algae channels", "LED", "CDOM"]:
        assert forbidden.lower() in claims.lower()
