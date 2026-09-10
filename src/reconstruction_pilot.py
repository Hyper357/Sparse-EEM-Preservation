from pathlib import Path
import argparse, json, sys
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from data_io import load_verified, load_v5
from reconstruction import reconstruct, domain_masks
from metrics import reconstruction_metrics, spearman
from plotting import make_all

ROOT = HERE.parents[1]
REPO = HERE.parents[0]
KS = [2, 3, 4, 6, 8]
STRATEGIES = ['NAIG', 'Uniform']


def selected(rec): return [int(v) for v in str(rec.selected_ex_nm).split(';')]


def main():
    p = argparse.ArgumentParser(); p.add_argument('--config', default=str(REPO/'configs'/'pilot.yaml')); args=p.parse_args()
    data = load_verified(ROOT); sets, rho = load_v5(ROOT)
    sel = sets[sets.strategy.isin(STRATEGIES) & sets.N_EX.isin(KS)].copy()
    if len(sel) != 29*len(STRATEGIES)*len(KS): raise ValueError(f'expected 290 fold selections, got {len(sel)}')
    rows=[]; rep=[]
    for _, rec in sel.iterrows():
        site=str(rec.held_out_station); i=int(np.where(data['sites']==site)[0][0]); exs=selected(rec)
        if len(exs) != int(rec.N_EX): raise ValueError('selected EX count mismatch')
        xhat, support = reconstruct(data['tensor'][i], data['ex'], data['valid'], exs)
        full, interp = domain_masks(data['ex'], data['valid'], exs)
        edge_mask = full & ~interp
        fm=reconstruction_metrics(data['tensor'][i],xhat,full,support); im=reconstruction_metrics(data['tensor'][i],xhat,interp,support)
        rr=rho[(rho.outer_fold==rec.outer_fold)&(rho.strategy==rec.strategy)&(rho.N_EX==rec.N_EX)&(rho.held_out_station==rec.held_out_station)]
        if len(rr)!=1: raise ValueError('rho join is not one-to-one')
        row={'site_id':site,'outer_fold':int(rec.outer_fold),'strategy':rec.strategy,'K':int(rec.N_EX),'selected_ex':';'.join(map(str,exs)),
             'selected_ex_span_nm':max(exs)-min(exs),'lower_edge_gap_nm':min(exs)-300,'upper_edge_gap_nm':700-max(exs),'rho_structure':float(rr.iloc[0].rho_structure)}
        emetrics=reconstruction_metrics(data['tensor'][i],xhat,edge_mask,support)
        for prefix,m in [('fullrange',fm),('interpdomain',im),('edgeonly',emetrics)]:
            for k in ['relative_frobenius_error','nrmse_energy','spectral_cosine','reconstruction_supported_fraction','single_support_fraction','unsupported_fraction','target_positions','supported_positions','single_support_positions','unsupported_positions']:
                row[f'{k}_{prefix}']=m[k]
        rows.append(row)
    d=pd.DataFrame(rows)
    d['relative_frobenius_error_fullrange']=d.relative_frobenius_error_fullrange.astype(float)
    # Canonical un-suffixed support fields in the requested joint table refer
    # to the full-range denominator; the suffixed fields remain explicit too.
    d['reconstruction_supported_fraction']=d.reconstruction_supported_fraction_fullrange
    d['single_support_fraction']=d.single_support_fraction_fullrange
    d['unsupported_fraction']=d.unsupported_fraction_fullrange
    # Required v0.2 invariant: the two retained error columns are identical
    # under the present normalization and identical support masks.
    err_cols=['relative_frobenius_error_fullrange','nrmse_energy_fullrange','relative_frobenius_error_interpdomain','nrmse_energy_interpdomain','relative_frobenius_error_edgeonly','nrmse_energy_edgeonly']
    for a,b in [(err_cols[0],err_cols[1]),(err_cols[2],err_cols[3]),(err_cols[4],err_cols[5])]:
        if not np.allclose(d[a].to_numpy(), d[b].to_numpy(), equal_nan=True, rtol=1e-12, atol=1e-12):
            raise AssertionError(f'RE_F/NRMSE equivalence failed: {a} vs {b}')
    summary=[]
    for (st,k),g in d.groupby(['strategy','K'],sort=True):
        q=lambda col,prob: float(g[col].quantile(prob))
        summary.append({'strategy':st,'K':int(k),'n_sites':len(g),
          'relative_frobenius_error_fullrange_median':q('relative_frobenius_error_fullrange',.5),'relative_frobenius_error_fullrange_p10':q('relative_frobenius_error_fullrange',.1),'relative_frobenius_error_fullrange_p90':q('relative_frobenius_error_fullrange',.9),'relative_frobenius_error_fullrange_worst':float(g.relative_frobenius_error_fullrange.max()),'relative_frobenius_error_fullrange_iqr':q('relative_frobenius_error_fullrange',.75)-q('relative_frobenius_error_fullrange',.25),
          'relative_frobenius_error_interpdomain_median':q('relative_frobenius_error_interpdomain',.5),'nrmse_energy_fullrange_median':q('nrmse_energy_fullrange',.5),'spectral_cosine_fullrange_median':q('spectral_cosine_fullrange',.5),'spectral_cosine_fullrange_p10':q('spectral_cosine_fullrange',.1),'spectral_cosine_fullrange_worst':float(g.spectral_cosine_fullrange.min()),'spectral_cosine_fullrange_iqr':q('spectral_cosine_fullrange',.75)-q('spectral_cosine_fullrange',.25),'spectral_cosine_interpdomain_median':q('spectral_cosine_interpdomain',.5),
          'supported_fraction_median':q('reconstruction_supported_fraction_fullrange',.5),'single_support_fraction_median':q('single_support_fraction_fullrange',.5),'unsupported_fraction_median':q('unsupported_fraction_fullrange',.5),'interp_supported_fraction_median':q('reconstruction_supported_fraction_interpdomain',.5),'interp_unsupported_fraction_median':q('unsupported_fraction_interpdomain',.5),'rho_structure_median':q('rho_structure',.5),'rho_structure_min':float(g.rho_structure.min()),'rho_ge_0.90':int((g.rho_structure>=.9).sum()),'spearman_error_vs_rho':spearman(g.relative_frobenius_error_fullrange,g.rho_structure),'spearman_cosine_vs_rho':spearman(g.spectral_cosine_fullrange,g.rho_structure),
          'spectral_cosine_fullrange_p90':q('spectral_cosine_fullrange',.9)})
    s=pd.DataFrame(summary)
    # Complete distribution summary for every requested numerical metric.
    metric_cols=['relative_frobenius_error_fullrange','relative_frobenius_error_interpdomain','nrmse_energy_fullrange','spectral_cosine_fullrange','spectral_cosine_interpdomain']
    for col in metric_cols:
        stats=d.groupby(['strategy','K'])[col].agg(median='median',p10=lambda x:x.quantile(.1),worst='min' if 'cosine' in col else 'max',iqr=lambda x:x.quantile(.75)-x.quantile(.25),mean='mean').reset_index()
        stats=stats.rename(columns={k:f'{col}_{k}' for k in ['median','p10','worst','iqr','mean']})
        s=s.drop(columns=[c for c in stats.columns if c in s.columns and c not in ['strategy','K']],errors='ignore').merge(stats,on=['strategy','K'],how='left')
    out=REPO/'outputs'; tables=out/'tables'; figs=out/'figures'; reports=REPO/'reports'; tables.mkdir(parents=True,exist_ok=True); figs.mkdir(parents=True,exist_ok=True); reports.mkdir(parents=True,exist_ok=True)
    d.to_csv(tables/'reconstruction_vs_structure.csv',index=False); s.to_csv(tables/'reconstruction_summary.csv',index=False)
    pub_cols=['strategy','K','n_sites',
      'relative_frobenius_error_fullrange_median','relative_frobenius_error_fullrange_p10','relative_frobenius_error_fullrange_worst','relative_frobenius_error_fullrange_iqr','relative_frobenius_error_fullrange_mean',
      'spectral_cosine_fullrange_median','spectral_cosine_fullrange_p10','spectral_cosine_fullrange_worst','spectral_cosine_fullrange_iqr','spectral_cosine_fullrange_mean',
      'relative_frobenius_error_interpdomain_median','relative_frobenius_error_interpdomain_p10','relative_frobenius_error_interpdomain_worst','relative_frobenius_error_interpdomain_iqr','relative_frobenius_error_interpdomain_mean',
      'spectral_cosine_interpdomain_median','spectral_cosine_interpdomain_p10','spectral_cosine_interpdomain_worst','spectral_cosine_interpdomain_iqr','spectral_cosine_interpdomain_mean',
      'supported_fraction_median','single_support_fraction_median','unsupported_fraction_median','interp_supported_fraction_median','interp_unsupported_fraction_median','rho_structure_median','rho_structure_min','rho_ge_0.90']
    pub=s[pub_cols].rename(columns={
      'relative_frobenius_error_fullrange_median':'relative_frobenius_error_supported_full_domain_median','relative_frobenius_error_fullrange_p10':'relative_frobenius_error_supported_full_domain_p10','relative_frobenius_error_fullrange_worst':'relative_frobenius_error_supported_full_domain_worst','relative_frobenius_error_fullrange_iqr':'relative_frobenius_error_supported_full_domain_iqr','relative_frobenius_error_fullrange_mean':'relative_frobenius_error_supported_full_domain_mean',
      'spectral_cosine_fullrange_median':'spectral_cosine_supported_full_domain_median','spectral_cosine_fullrange_p10':'spectral_cosine_supported_full_domain_p10','spectral_cosine_fullrange_worst':'spectral_cosine_supported_full_domain_worst','spectral_cosine_fullrange_iqr':'spectral_cosine_supported_full_domain_iqr','spectral_cosine_fullrange_mean':'spectral_cosine_supported_full_domain_mean',
      'relative_frobenius_error_interpdomain_median':'relative_frobenius_error_supported_interpolation_domain_median','relative_frobenius_error_interpdomain_p10':'relative_frobenius_error_supported_interpolation_domain_p10','relative_frobenius_error_interpdomain_worst':'relative_frobenius_error_supported_interpolation_domain_worst','relative_frobenius_error_interpdomain_iqr':'relative_frobenius_error_supported_interpolation_domain_iqr','relative_frobenius_error_interpdomain_mean':'relative_frobenius_error_supported_interpolation_domain_mean',
      'spectral_cosine_interpdomain_median':'spectral_cosine_supported_interpolation_domain_median','spectral_cosine_interpdomain_p10':'spectral_cosine_supported_interpolation_domain_p10','spectral_cosine_interpdomain_worst':'spectral_cosine_supported_interpolation_domain_worst','spectral_cosine_interpdomain_iqr':'spectral_cosine_supported_interpolation_domain_iqr','spectral_cosine_interpdomain_mean':'spectral_cosine_supported_interpolation_domain_mean','supported_fraction_median':'reconstruction_supported_fraction_full_domain_median','single_support_fraction_median':'single_support_fraction_full_domain_median','unsupported_fraction_median':'unsupported_fraction_full_domain_median','interp_supported_fraction_median':'reconstruction_supported_fraction_interpolation_domain_median','interp_unsupported_fraction_median':'unsupported_fraction_interpolation_domain_median'})
    pub.to_csv(tables/'reconstruction_summary_publication.csv',index=False)
    # Add edge diagnostic at the same site/configuration grain.
    edge=d[['site_id','strategy','K','selected_ex','selected_ex_span_nm','lower_edge_gap_nm','upper_edge_gap_nm','relative_frobenius_error_fullrange','relative_frobenius_error_interpdomain','spectral_cosine_fullrange','reconstruction_supported_fraction_fullrange','unsupported_fraction_fullrange']]
    edge.to_csv(tables/'edge_extrapolation_diagnostic.csv',index=False)
    # Select representatives from the completed table: typical, worst, and
    # high-rho/poor-reconstruction when that discordant case exists.
    rep_rows=[]
    med=d.relative_frobenius_error_fullrange.median()
    rep_rows.append(('typical', d.iloc[(d.relative_frobenius_error_fullrange-med).abs().argmin()]))
    rep_rows.append(('poor_reconstruction', d.iloc[d.relative_frobenius_error_fullrange.argmax()]))
    discord=d[d.rho_structure.ge(.95)]
    if len(discord): rep_rows.append(('high_rho_poor_reconstruction', discord.iloc[discord.relative_frobenius_error_fullrange.argmax()]))
    rep2=[]
    for label, row in rep_rows:
        i=int(np.where(data['sites']==row.site_id)[0][0]); exs=[int(v) for v in row.selected_ex.split(';')]
        xhat,support=reconstruct(data['tensor'][i],data['ex'],data['valid'],exs)
        resid=np.where(data['valid'],xhat-data['tensor'][i],np.nan)
        z={'label':f"{label}: {row.site_id} {row.strategy} K={row.K}", 'full':np.where(data['valid'],data['tensor'][i],np.nan),'observed':np.where(np.isin(data['ex'],exs)[:,None],data['tensor'][i],np.nan),'recon':xhat,'resid':resid}
        z={**z,'vmin':np.nanpercentile(z['full'],2),'vmax':np.nanpercentile(z['full'],98),'rvmin':np.nanpercentile(z['resid'],2),'rvmax':np.nanpercentile(z['resid'],98)}; rep2.append(z)
    make_all(d,s,figs,rep2)
    manifest={'input_file':str(data['path']),'input_sha256':data['sha256'],'sites':list(data['sites']),'n_sites':29,'excluded_sites':['S29'],'ex_grid_nm':[300,700,5],'em_grid_nm':[250,800,5],'common_valid_positions':int(data['valid'].sum()),'tensor_array':'clean_masked_tensor','forbidden_array':'clean_interpolated_tensor','strategies':STRATEGIES,'K':KS,'selection_source':'03_ANALYSIS/measured_verified/selected_excitation_sets_by_fold.csv','rho_source':'03_ANALYSIS/measured_verified/site_structure_preservation.csv','reconstruction':'piecewise linear along EX with nearest-edge extension; one-support constant; zero-support missing; no random process; seed not applicable','generated_utc':pd.Timestamp.utcnow().isoformat()}
    (out/'pilot_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(s.to_string(index=False)); return d,s

if __name__=='__main__': main()
