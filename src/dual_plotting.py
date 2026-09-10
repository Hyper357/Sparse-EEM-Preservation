from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

COLORS={'Uniform':'#B46A3C','Random-fixed':'#9AA3AD'}
def save(fig,p):
    fig.savefig(p.with_suffix('.png'),dpi=300,bbox_inches='tight'); fig.savefig(p.with_suffix('.svg'),bbox_inches='tight'); fig.savefig(p.with_suffix('.pdf'),bbox_inches='tight'); plt.close(fig)
def style(ax): ax.grid(alpha=.25); ax.spines[['top','right']].set_visible(False)
def make_dual_plots(fixed,randoms,fixed_site,quadrants,out,representatives):
    # P6: compact dual endpoint comparison.
    fig,ax=plt.subplots(1,2,figsize=(10,4.2));
    for st,g in fixed.groupby('strategy'):
        ax[0].plot(g.K,g.median_reconstruction_error,'o-',label=st,color=COLORS[st]); ax[1].plot(g.K,g.median_rho,'o-',label=st,color=COLORS[st])
    for a,y in [(ax[0],'Median supported-position reconstruction error'),(ax[1],'Median rho_structure')]: a.set_xlabel('K'); a.set_ylabel(y); a.set_xticks([2,3,4,6,8]); a.legend(frameon=False); style(a)
    fig.suptitle('P6. Fixed Uniform configurations: dual endpoint comparison'); save(fig,out/'P6_uniform_dual_endpoint')
    # P7/P8 Pareto clouds.
    for k,rd in zip([4,6],randoms):
        u=fixed[fixed.K.eq(k)].iloc[0]; fig,ax=plt.subplots(figsize=(6.6,4.8)); ax.scatter(rd.median_reconstruction_error,rd.median_rho,s=12,c='#B7BEC7',alpha=.55,label=f'Random fixed K={k} (n={len(rd)})'); ax.scatter([u.median_reconstruction_error],[u.median_rho],s=90,c='#B46A3C',marker='*',label=f'Uniform-{k}'); ax.set(xlabel='Median supported-position reconstruction error',ylabel='Median rho_structure',title=f'P{7 if k==4 else 8}. Random fixed K={k} Pareto space'); ax.legend(frameon=False); style(ax); save(fig,out/f'P{7 if k==4 else 8}_random_K{k}_pareto')
    # P9: site-level fixed configurations.
    fig,ax=plt.subplots(figsize=(7,5));
    for cid,g in quadrants.groupby('configuration_id'):
        ax.scatter(g.relative_frobenius_error,g.rho_structure,s=18,alpha=.55,label=cid)
    ax.set(xlabel='Supported-position reconstruction error',ylabel='rho_structure',title='P9. Site-level reconstruction versus structure'); ax.legend(frameon=False,fontsize=7,ncol=2); style(ax); save(fig,out/'P9_site_reconstruction_vs_rho')
    # P10 representative heatmaps.
    chosen=representatives[:3] if representatives else []
    if chosen:
        fig,axs=plt.subplots(len(chosen),4,figsize=(12,3.2*len(chosen)),squeeze=False)
        gvmin=min(np.nanpercentile(z['full'],2) for z in chosen); gvmax=max(np.nanpercentile(z['full'],98) for z in chosen); gr=max(max(abs(np.nanpercentile(z['resid'],2)),abs(np.nanpercentile(z['resid'],98))) for z in chosen)
        for r,z in enumerate(chosen):
            for c,(arr,title) in enumerate([(z['full'],'Measured full EEM'),(z['observed'],'Sparse observed EX'),(z['recon'],'Reconstructed EEM'),(z['resid'],'Residual')]):
                im=axs[r,c].imshow(arr,aspect='auto',origin='lower',cmap='viridis' if c<3 else 'coolwarm',vmin=gvmin if c<3 else -gr,vmax=gvmax if c<3 else gr); axs[r,c].set_title(title,fontsize=10); axs[r,c].set_xlabel('EM index'); axs[r,c].set_ylabel('EX index'); fig.colorbar(im,ax=axs[r,c],fraction=.046,pad=.02)
            axs[r,0].text(-.40,.5,z['label'],transform=axs[r,0].transAxes,rotation=90,ha='center',va='center',fontsize=8)
        fig.suptitle('P10. Representative discordant cases'); fig.tight_layout(rect=[.04,0,.99,.97]); save(fig,out/'P10_representative_discordant_cases')
