from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

COLORS = {'NAIG': '#245A8D', 'Uniform': '#B46A3C'}
KVALS = [2, 3, 4, 6, 8]


def _save(fig, path):
    fig.savefig(path.with_suffix('.png'), dpi=300, bbox_inches='tight')
    fig.savefig(path.with_suffix('.pdf'), bbox_inches='tight')
    fig.savefig(path.with_suffix('.svg'), bbox_inches='tight')
    plt.close(fig)


def _style(ax):
    ax.grid(axis='y', color='#D9DEE5', lw=.7, alpha=.8)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right']].set_visible(False)


def make_all(per_site, summary, figures_dir, representative=None):
    figures_dir.mkdir(parents=True, exist_ok=True)
    # P1: distribution-aware error curves.
    fig, ax = plt.subplots(figsize=(6.5, 4.3))
    for st, g in summary.groupby('strategy'):
        c = COLORS[st]; ax.plot(g.K, g.relative_frobenius_error_fullrange_median, 'o-', color=c, label=st)
        ax.fill_between(g.K, g.relative_frobenius_error_fullrange_p10, g.relative_frobenius_error_fullrange_p90, color=c, alpha=.14)
    ax.set(title='P1. Full-range reconstruction error', xlabel='Number of selected EX slices (K)', ylabel='Relative Frobenius error')
    ax.legend(frameon=False, loc='upper right'); ax.set_xticks(KVALS); _style(ax); _save(fig, figures_dir/'P1_error_vs_K')
    # P2.
    fig, ax = plt.subplots(figsize=(6.5, 4.3))
    for st, g in summary.groupby('strategy'):
        c = COLORS[st]; ax.plot(g.K, g.spectral_cosine_fullrange_median, 'o-', color=c, label=st)
        ax.fill_between(g.K, g.spectral_cosine_fullrange_p10, g.spectral_cosine_fullrange_p90, color=c, alpha=.14)
    ax.set(title='P2. Full-range spectral cosine similarity', xlabel='Number of selected EX slices (K)', ylabel='Spectral cosine similarity')
    ax.set_ylim(0, 1.02); ax.legend(frameon=False, loc='lower right'); ax.set_xticks(KVALS); _style(ax); _save(fig, figures_dir/'P2_cosine_vs_K')
    # P3.
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    for st, g in per_site.groupby('strategy'):
        for k, gg in g.groupby('K'):
            ax.scatter(gg.spectral_cosine_fullrange, gg.rho_structure, s=24, alpha=.68, color=COLORS[st], marker={2:'o',3:'s',4:'^',6:'D',8:'P'}[k], label=f'{st} K={k}')
    handles, labels = ax.get_legend_handles_labels(); seen = dict(zip(labels, handles))
    ax.legend(seen.values(), seen.keys(), frameon=False, fontsize=7, ncol=2)
    ax.set(title='P3. Reconstruction fidelity and structural preservation', xlabel='Full-range spectral cosine similarity', ylabel='V5 structure-ranking Spearman rho'); _style(ax); _save(fig, figures_dir/'P3_reconstruction_vs_rho')
    # P4.
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.1), sharex=True)
    for st, g in summary.groupby('strategy'):
        c=COLORS[st]
        axes[0].plot(g.K, g.relative_frobenius_error_fullrange_median, 'o-', color=c, label=f'{st} median')
        axes[0].plot(g.K, g.relative_frobenius_error_fullrange_p10, 'o--', color=c, alpha=.75, label=f'{st} P10')
        axes[0].plot(g.K, g.relative_frobenius_error_fullrange_worst, 'x:', color=c, alpha=.85, label=f'{st} worst')
        axes[1].plot(g.K, g.spectral_cosine_fullrange_median, 'o-', color=c, label=f'{st} median')
        axes[1].plot(g.K, g.spectral_cosine_fullrange_p10, 'o--', color=c, alpha=.75, label=f'{st} P10')
        axes[1].plot(g.K, g.spectral_cosine_fullrange_worst, 'x:', color=c, alpha=.85, label=f'{st} worst')
    axes[0].set_ylabel('Relative Frobenius error'); axes[1].set_ylabel('Spectral cosine similarity')
    for a in axes: a.set_xlabel('K'); a.set_xticks(KVALS); _style(a); a.legend(frameon=False, fontsize=7)
    fig.suptitle('P4. Typical and lower-tail performance by K'); _save(fig, figures_dir/'P4_distribution_by_K')
    # P5: representative measured/observed/reconstructed/residual heatmaps.
    if representative:
        fig, axes = plt.subplots(len(representative), 4, figsize=(13, 3.1*len(representative)), squeeze=False)
        gvmin=min(z['vmin'] for z in representative); gvmax=max(z['vmax'] for z in representative)
        gr=max(abs(z['rvmin']) for z in representative); gr=max(gr, max(abs(z['rvmax']) for z in representative))
        for r, item in enumerate(representative):
            for c, (arr, title) in enumerate([(item['full'], 'Measured full EEM'), (item['observed'], 'Sparse observed EX'), (item['recon'], 'Reconstructed EEM'), (item['resid'], 'Residual')]):
                im=axes[r,c].imshow(arr, aspect='auto', origin='lower', cmap='viridis' if c<3 else 'coolwarm', vmin=gvmin if c<3 else -gr, vmax=gvmax if c<3 else gr)
                axes[r,c].set_title(title, fontsize=10); axes[r,c].set_xlabel('EM index'); axes[r,c].set_ylabel('EX index')
                fig.colorbar(im, ax=axes[r,c], fraction=.046, pad=.02)
            axes[r,0].text(-.42, .5, item['label'], transform=axes[r,0].transAxes, rotation=90, va='center', ha='center', fontsize=9)
        fig.suptitle('P5. Representative full-EEM reconstruction diagnostics', y=.995); fig.tight_layout(rect=[.04,0,.99,.97]); _save(fig, figures_dir/'P5_representative_EEM')
