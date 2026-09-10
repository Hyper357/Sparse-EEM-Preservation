"""Make the four minimum pilot plots from the saved tables."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"

def main():
    d = pd.read_csv(OUT / "pilot_per_site.csv")
    s = pd.read_csv(OUT / "pilot_summary.csv")
    fig, ax = plt.subplots(2, 2, figsize=(11, 8), constrained_layout=True)
    colors = {"NAIG": "#356a9a", "Uniform": "#b46b42"}
    for strategy, g in s.groupby("strategy"):
        ax[0, 0].plot(g.K, g.median_reconstruction_error_fullrange, "o-", label=strategy, color=colors[strategy])
        ax[0, 1].plot(g.K, g.median_spectral_cosine_fullrange, "o-", label=strategy, color=colors[strategy])
        ax[1, 0].plot(g.K, g.p10_reconstruction_error_fullrange, "o--", label=f"{strategy} P10", color=colors[strategy])
        ax[1, 0].plot(g.K, g.worst_reconstruction_error_fullrange, "x:", label=f"{strategy} worst", color=colors[strategy])
    ax[0, 0].set(title="P1. Full-range reconstruction error", ylabel="Relative Frobenius error")
    ax[0, 1].set(title="P2. Full-range spectral cosine", ylabel="Cosine similarity")
    ax[1, 0].set(title="P4. Low-end reconstruction error", ylabel="Relative Frobenius error")
    for a in (ax[0, 0], ax[0, 1], ax[1, 0]):
        a.set_xlabel("K excitation slices"); a.set_xticks([2, 3, 4, 6, 8]); a.grid(alpha=.25)
        a.legend(frameon=False, fontsize=8)
    for strategy, g in d.groupby("strategy"):
        ax[1, 1].scatter(g.spectral_cosine_fullrange, g.rho_structure, s=18, alpha=.65, label=strategy, color=colors[strategy])
    ax[1, 1].set(title="P3. Reconstruction vs structural rho", xlabel="Full-range spectral cosine", ylabel="Structure-ranking rho")
    ax[1, 1].grid(alpha=.25); ax[1, 1].legend(frameon=False)
    fig.savefig(OUT / "pilot_figures.png", dpi=220)
    fig.savefig(OUT / "pilot_figures.pdf")
    print(OUT / "pilot_figures.png")

if __name__ == "__main__":
    main()
