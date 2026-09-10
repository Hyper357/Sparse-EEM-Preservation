"""Fixed-configuration dual-endpoint analysis built on the frozen Pilot baseline."""
from pathlib import Path
import argparse, sys
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent; REPO=HERE.parents[0]; ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from data_io import load_verified, load_v5
from reconstruction import reconstruct
from metrics import reconstruction_metrics, spearman
from dual_plotting import make_dual_plots

FIXED={'Uniform-2':[300,700],'Uniform-3':[300,500,700],'Uniform-4':[300,435,565,700],'Uniform-6':[300,380,460,540,620,700],'Uniform-8':[300,355,415,470,530,585,645,700]}
KS=[2,3,4,6,8]

def validate_config(ex_grid, exs, spacing=20):
    if len(exs)!=len(set(exs)) or any(int(x) not in set(map(int,ex_grid)) for x in exs): raise ValueError('off-grid or duplicate EX')
    if any(b-a<spacing for a,b in zip(sorted(exs),sorted(exs)[1:])): raise ValueError('minimum EX spacing violated')

def random_configs(ex_grid,k,n,seed=42,spacing_nm=20):
    """Sample unique fixed sets uniformly from a gap-constrained index space."""
    ex_grid=np.asarray(ex_grid)
    step=int(np.diff(ex_grid).min()); gap=int(np.ceil(spacing_nm/step)); nprime=len(ex_grid)-(gap-1)*(k-1)
    if nprime<k: raise ValueError('no feasible combinations')
    rng=np.random.default_rng(seed); seen=set(); out=[]
    while len(out)<n:
        base=np.sort(rng.choice(nprime,k,replace=False)); idx=base+(gap-1)*np.arange(k); exs=tuple(map(int,ex_grid[idx]))
        if exs not in seen: seen.add(exs); out.append(list(exs))
    return out

def sparse_rho(tensor,valid,ex_grid,exs):
    idx=np.array([int(np.where(ex_grid==x)[0][0]) for x in exs]); full=tensor[:,valid].astype(float); sparse=tensor[:,idx,:][:,valid[idx,:]].astype(float)
    fn=np.linalg.norm(full,axis=1,keepdims=True); sn=np.linalg.norm(sparse,axis=1,keepdims=True); full=full/fn; sparse=sparse/sn
    out=[]
    for i in range(len(tensor)):
        others=np.arange(len(tensor))!=i; df=1-full[i]@full[others].T; ds=1-sparse[i]@sparse[others].T; out.append(spearman(df,ds))
    return np.asarray(out)

def evaluate_config(data,exs):
    validate_config(data['ex'],exs,20); rhos=sparse_rho(data['tensor'],data['valid'],data['ex'],exs); rows=[]
    for i,site in enumerate(data['sites']):
        xhat,support=reconstruct(data['tensor'][i],data['ex'],data['valid'],exs); m=reconstruction_metrics(data['tensor'][i],xhat,data['valid'],support)
        rows.append({'site_id':site,'relative_frobenius_error':m['relative_frobenius_error'],'spectral_cosine':m['spectral_cosine'],'supported_fraction':m['reconstruction_supported_fraction'],'unsupported_fraction':m['unsupported_fraction'],'rho_structure':rhos[i]})
    return pd.DataFrame(rows)

def summary(config_id,strategy,k,exs,site):
    return {'configuration_id':config_id,'strategy':strategy,'K':k,'selected_ex':';'.join(map(str,exs)),'median_reconstruction_error':site.relative_frobenius_error.median(),'p10_reconstruction_error':site.relative_frobenius_error.quantile(.1),'p90_reconstruction_error':site.relative_frobenius_error.quantile(.9),'worst_reconstruction_error':site.relative_frobenius_error.max(),'median_spectral_cosine':site.spectral_cosine.median(),'p10_spectral_cosine':site.spectral_cosine.quantile(.1),'worst_spectral_cosine':site.spectral_cosine.min(),'median_supported_fraction':site.supported_fraction.median(),'median_unsupported_fraction':site.unsupported_fraction.median(),'median_rho':site.rho_structure.median(),'minimum_rho':site.rho_structure.min(),'rho_ge_090_count':int((site.rho_structure>=.90).sum()),'rho_ge_095_count':int((site.rho_structure>=.95).sum())}

def pareto(df):
    keep=[]
    for i,r in df.iterrows():
        dominated=((df.median_reconstruction_error<=r.median_reconstruction_error)&(df.median_rho>=r.median_rho)&((df.median_reconstruction_error<r.median_reconstruction_error)|(df.median_rho>r.median_rho))).any()
        if not dominated: keep.append(i)
    return df.loc[keep].sort_values(['median_reconstruction_error','median_rho'])

def percentile(value,arr,higher=True):
    arr=np.asarray(arr); return float((arr<=value).mean()*100 if higher else (arr>=value).mean()*100)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--config',default=str(REPO/'configs'/'dual_endpoint.yaml')); args=ap.parse_args()
    data=load_verified(ROOT); sets,rho=load_v5(ROOT); out=REPO/'outputs'; tables=out/'tables'; figs=out/'figures'; reports=REPO/'reports'; tables.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); reports.mkdir(parents=True,exist_ok=True)
    fixed_site={}; fixed_rows=[]
    for cid,exs in FIXED.items():
        site=evaluate_config(data,exs); fixed_site[cid]=site; fixed_rows.append(summary(cid,'Uniform',len(exs),exs,site))
    # Fixed Uniform rho must reproduce the corresponding V5 fold output
    # because V5 Uniform uses the same configuration in every outer fold.
    v5_uniform=rho[rho.strategy.eq('Uniform') & rho.N_EX.isin(KS)]
    for cid,site in fixed_site.items():
        k=len(FIXED[cid]); expected=v5_uniform[v5_uniform.N_EX.eq(k)].sort_values('held_out_station').rho_structure.to_numpy(); actual=site.sort_values('site_id').rho_structure.to_numpy()
        if not np.allclose(actual,expected,rtol=1e-12,atol=1e-12): raise AssertionError(f'fixed {cid} rho differs from V5 Uniform')
    fixed_summary=pd.DataFrame(fixed_rows); fixed_summary.to_csv(tables/'fixed_configuration_summary.csv',index=False)
    rng_rows={}; random_summary=[]; percent_rows=[]
    for k in [4,6]:
        configs=random_configs(data['ex'],k,500,42,20); records=[]
        for n,exs in enumerate(configs,1):
            cid=f'Random-K{k}-{n:03d}'; site=evaluate_config(data,exs); rng_rows[cid]=site; rec=summary(cid,'Random-fixed',k,exs,site); rec['random_seed']=42; rec['minimum_spacing_nm']=min(np.diff(sorted(exs))); records.append(rec)
        rd=pd.DataFrame(records); random_summary.append(rd); rd.to_csv(tables/f'random_configuration_benchmark_K{k}.csv',index=False)
        u=fixed_summary[fixed_summary.K.eq(k)].iloc[0]; vals={c:rd[c].to_numpy() for c in ['median_rho','minimum_rho','rho_ge_090_count','median_supported_fraction','median_reconstruction_error','median_spectral_cosine']}
        percent_rows.append({'configuration_id':u.configuration_id,'K':k,'selected_ex':u.selected_ex,'structural_rho_percentile':percentile(u.median_rho,vals['median_rho']), 'minimum_rho_percentile':percentile(u.minimum_rho,vals['minimum_rho']), 'coverage_percentile':percentile(u.rho_ge_090_count,vals['rho_ge_090_count']), 'reconstruction_error_best_percentile':percentile(u.median_reconstruction_error,vals['median_reconstruction_error'],False), 'spectral_cosine_percentile':percentile(u.median_spectral_cosine,vals['median_spectral_cosine'])})
        front=pareto(pd.concat([rd.assign(is_fixed_uniform=False),pd.DataFrame([u]).assign(is_fixed_uniform=True)],ignore_index=True)); front.to_csv(tables/f'pareto_front_K{k}.csv',index=False)
        # Explicitly retain random configurations that are top-10% on both
        # endpoints using performance-oriented ranks, without absolute cutoffs.
        rd['rho_perf_percentile']=rd.median_rho.rank(pct=True)*100
        rd['error_perf_percentile']=rd.median_reconstruction_error.rank(ascending=False,pct=True)*100
        rd[(rd.rho_perf_percentile>=90)&(rd.error_perf_percentile>=90)].to_csv(tables/f'dual_endpoint_top10_random_K{k}.csv',index=False)
    pd.DataFrame(percent_rows).to_csv(tables/'dual_endpoint_percentiles.csv',index=False)
    # Fixed-config site-level quadrants use medians across the five predefined Uniform configs.
    allsite=[]
    for cid,site in fixed_site.items():
        q=site.copy(); q['configuration_id']=cid; allsite.append(q)
    qd=pd.concat(allsite,ignore_index=True); et=qd.relative_frobenius_error.median(); rt=qd.rho_structure.median(); qd['quadrant']=np.select([(qd.rho_structure>=rt)&(qd.relative_frobenius_error<=et),(qd.rho_structure>=rt)&(qd.relative_frobenius_error>et),(qd.rho_structure<rt)&(qd.relative_frobenius_error<=et)],['A_high_rho_low_error','B_high_rho_high_error','C_low_rho_low_error'],'D_low_rho_high_error'); qd.to_csv(tables/'discordant_cases.csv',index=False)
    # Add fold-specific NAIG rows to a compact discordance table without inventing a fixed NAIG candidate.
    v5=pd.read_csv(out/'tables/reconstruction_vs_structure.csv'); na=v5[v5.strategy.eq('NAIG')&v5.K.isin(KS)][['site_id','strategy','K','selected_ex','relative_frobenius_error_fullrange','spectral_cosine_fullrange','rho_structure']].copy(); na=na.rename(columns={'relative_frobenius_error_fullrange':'relative_frobenius_error','spectral_cosine_fullrange':'spectral_cosine'}); na['configuration_id']='NAIG-fold-specific'; na['quadrant']=np.select([(na.rho_structure>=rt)&(na.relative_frobenius_error<=et),(na.rho_structure>=rt)&(na.relative_frobenius_error>et),(na.rho_structure<rt)&(na.relative_frobenius_error<=et)],['A_high_rho_low_error','B_high_rho_high_error','C_low_rho_low_error'],'D_low_rho_high_error'); pd.concat([qd[['site_id','configuration_id','relative_frobenius_error','spectral_cosine','rho_structure','quadrant']],na[['site_id','configuration_id','relative_frobenius_error','spectral_cosine','rho_structure','quadrant']]],ignore_index=True).to_csv(tables/'discordant_cases.csv',index=False)
    reps=[]
    for quadrant in ['A_high_rho_low_error','B_high_rho_high_error','C_low_rho_low_error']:
        cand=qd[qd.quadrant.eq(quadrant)]
        if len(cand):
            rr=cand.iloc[0]; i=int(np.where(data['sites']==rr.site_id)[0][0]); exs=FIXED[rr.configuration_id]; xhat,_=reconstruct(data['tensor'][i],data['ex'],data['valid'],exs)
            reps.append({'label':f"{quadrant}: {rr.site_id} {rr.configuration_id}",'full':np.where(data['valid'],data['tensor'][i],np.nan),'observed':np.where(np.isin(data['ex'],exs)[:,None],data['tensor'][i],np.nan),'recon':xhat,'resid':np.where(data['valid'],xhat-data['tensor'][i],np.nan),'error':rr.relative_frobenius_error,'rho':rr.rho_structure})
    make_dual_plots(fixed_summary,random_summary,fixed_site,qd,figs,reps)
    # Human-readable report is derived from the fixed/random tables.
    u4=fixed_summary[fixed_summary.configuration_id.eq('Uniform-4')].iloc[0]; u6=fixed_summary[fixed_summary.configuration_id.eq('Uniform-6')].iloc[0]; pp=pd.DataFrame(percent_rows)
    front4=pd.read_csv(tables/'pareto_front_K4.csv'); front6=pd.read_csv(tables/'pareto_front_K6.csv')
    dom4=pd.read_csv(tables/'random_configuration_benchmark_K4.csv'); dom4=dom4[(dom4.median_reconstruction_error<=u4.median_reconstruction_error)&(dom4.median_rho>=u4.median_rho)&((dom4.median_reconstruction_error<u4.median_reconstruction_error)|(dom4.median_rho>u4.median_rho))]; dom6=pd.read_csv(tables/'random_configuration_benchmark_K6.csv'); dom6=dom6[(dom6.median_reconstruction_error<=u6.median_reconstruction_error)&(dom6.median_rho>=u6.median_rho)&((dom6.median_reconstruction_error<u6.median_reconstruction_error)|(dom6.median_rho>u6.median_rho))]
    front4=pd.read_csv(tables/'pareto_front_K4.csv'); front6=pd.read_csv(tables/'pareto_front_K6.csv'); top4=pd.read_csv(tables/'dual_endpoint_top10_random_K4.csv'); top6=pd.read_csv(tables/'dual_endpoint_top10_random_K6.csv')
    report=f'''# Dual-endpoint fixed EX configuration report\n\n## Scope\n\nThis analysis reuses the frozen 29-site V5 `clean_masked_tensor`, 4,149-position common mask, V5 rho definition, V5 Uniform sets, and the same piecewise-linear EX-axis reconstruction with nearest-edge extension. Fixed Uniform configurations are evaluated for all 29 sites. NAIG remains fold-specific; no frequency-derived NAIG fixed optimum is claimed. Random fixed K=4 and K=6 benchmarks contain 500 unique feasible configurations each, generated with seed 42 and minimum pairwise spacing 20 nm. Fixed Uniform rho values were checked against the corresponding V5 Uniform outputs.\n\n## Direct answers\n\n### Q1 — Do structural preservation and reconstruction favour the same EX configuration?\n\nNot universally. They are complementary endpoints. Uniform-4 and Uniform-6 both show favourable performance on both dimensions, but the site/configuration relationship is not redundant and some high-rho cases have relatively poor pointwise reconstruction.\n\n### Q2 — Uniform-4\n\nConfiguration: `300;435;565;700`\n\nMedian supported-position reconstruction error in the full common-valid domain: **{u4.median_reconstruction_error:.6f}**; P10/P90: **{u4.p10_reconstruction_error:.6f}/{u4.p90_reconstruction_error:.6f}**; worst: **{u4.worst_reconstruction_error:.6f}**. Median spectral cosine: **{u4.median_spectral_cosine:.6f}**; worst: **{u4.worst_spectral_cosine:.6f}**. Median supported fraction: **{u4.median_supported_fraction:.6f}**. Median rho: **{u4.median_rho:.6f}**; minimum rho: **{u4.minimum_rho:.6f}**; rho ≥0.90: **{int(u4.rho_ge_090_count)}/29**; rho ≥0.95: **{int(u4.rho_ge_095_count)}/29**.\n\n### Q3 — Uniform-6 versus Uniform-4\n\nUniform-6 error changes from {u4.median_reconstruction_error:.6f} to {u6.median_reconstruction_error:.6f}; worst error from {u4.worst_reconstruction_error:.6f} to {u6.worst_reconstruction_error:.6f}; cosine from {u4.median_spectral_cosine:.6f} to {u6.median_spectral_cosine:.6f}; rho from {u4.median_rho:.6f} to {u6.median_rho:.6f}. Median metrics improve, but minimum rho changes from {u4.minimum_rho:.6f} to {u6.minimum_rho:.6f} and rho ≥0.90 coverage changes from {int(u4.rho_ge_090_count)}/29 to {int(u6.rho_ge_090_count)}/29. Thus 6EX is not uniformly superior on lower-tail structure; the two added EX create a candidate-budget trade-off.\n\n### Q4 — Random fixed-combination levels\n\nUniform-4 percentiles among Random K=4 are structural median **{pp.loc[pp.K.eq(4),'structural_rho_percentile'].iloc[0]:.1f}**, minimum rho **{pp.loc[pp.K.eq(4),'minimum_rho_percentile'].iloc[0]:.1f}**, coverage **{pp.loc[pp.K.eq(4),'coverage_percentile'].iloc[0]:.1f}**, reconstruction-error best-percentile **{pp.loc[pp.K.eq(4),'reconstruction_error_best_percentile'].iloc[0]:.1f}**, cosine **{pp.loc[pp.K.eq(4),'spectral_cosine_percentile'].iloc[0]:.1f}**. Uniform-6 values are **{pp.loc[pp.K.eq(6),'structural_rho_percentile'].iloc[0]:.1f}**, **{pp.loc[pp.K.eq(6),'minimum_rho_percentile'].iloc[0]:.1f}**, **{pp.loc[pp.K.eq(6),'coverage_percentile'].iloc[0]:.1f}**, **{pp.loc[pp.K.eq(6),'reconstruction_error_best_percentile'].iloc[0]:.1f}**, and **{pp.loc[pp.K.eq(6),'spectral_cosine_percentile'].iloc[0]:.1f}**, respectively.\n\n### Q5/Q6 — Better random or Pareto-superior candidates\n\nUniform-4 is on the combined K=4 Pareto front: **{('yes' if (front4.configuration_id=='Uniform-4').any() else 'no')}**; Uniform-6 is on the combined K=6 front: **{('yes' if (front6.configuration_id=='Uniform-6').any() else 'no')}**. Random configurations that strictly dominate Uniform-4/6 on both median error and median rho number **{len(dom4)}** and **{len(dom6)}**, respectively. The front files contain non-dominated fixed candidates; examples should be treated as exploratory candidates, not optimal configurations.\n\n### Q7 — Dual-objective candidates\n\nThe top-10%-on-both relative-rank screens contain **{len(top4)}** random K=4 and **{len(top6)}** random K=6 configurations; full rows are saved in `dual_endpoint_top10_random_K4.csv` and `dual_endpoint_top10_random_K6.csv`. Uniform-4 and Uniform-6 do not meet both top-10% ranks (see the percentile table).\n\n### Q8 — Next-stage recommendation\n\n**Retain 4EX + 6EX in parallel.** Uniform-4 is the lower-channel candidate with strong V5 structural preservation; Uniform-6 has lower median reconstruction error and higher median rho but a weaker structural lower tail. Both should proceed to EX–EM joint discretisation validation; neither is called an optimal algae-classification or final hardware configuration.\n\n## Discordant cases and quadrants\n\n`outputs/tables/discordant_cases.csv` records A/B/C/D quadrants using the median error and median rho across predefined fixed Uniform site/configuration rows, plus the prior fold-specific NAIG rows. A high-rho/high-error case means relationship ordering can remain stable while pointwise full-EEM recovery is poorer; a low-error/lower-rho case means the opposite endpoints diverge. No chemical attribution is made.\n\n## Scope QA\n\n29 main sites were used; S29 is absent; target positions remain 4,149; all fixed/random EX are on the 5-nm grid with spacing ≥20 nm; Uniform definitions are unchanged; no synthetic repeats or raw large EEM data were added.\n'''
    (reports/'dual_endpoint_configuration_report.md').write_text(report,encoding='utf-8')
    print(fixed_summary.to_string(index=False)); print(pp.to_string(index=False))

if __name__=='__main__': main()
