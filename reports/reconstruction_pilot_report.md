# Sparse-EX to full-EEM reconstruction Pilot report

## Scope and decision

This isolated Pilot used only the verified V5 main scans (`S01–S28 + S30`, 29 sites), the V5 `clean_masked_tensor`, the common physical mask, and V5 fold-specific NAIG/Uniform selected-EX outputs. It evaluated exactly NAIG and Uniform at K = 2, 3, 4, 6, and 8. No synthetic repeat, learning model, V5/V6 manuscript edit, or post-hoc K change was used.

**Recommendation: Route 2.** Keep V5 structural rho as the primary endpoint and use reconstruction as a supplementary validation. The simple reconstruction endpoint is informative and complementary, but its full-range error trend is not stable for NAIG and differs materially from structural preservation.

## Definitions and accounting

For each held-out site and fold-specific selected EX set, reconstruction used only the selected measured slices. Each EM column was reconstructed along EX by piecewise-linear interpolation inside the selected span and nearest-edge extension outside it. A column with one supported selected response used a constant value; a column with no supported selected response remained missing. The physical mask remained missing.

The full-range target domain contains all 4,149 common-valid EX–EM positions. Numerical error/cosine values are computed on the subset of that target domain where the fixed reconstruction exists; the target count, supported count, and unsupported fraction are reported alongside every row. Unsupported positions were not silently deleted or relabelled as successful full-range recovery. Interpolation-domain metrics use valid targets between the minimum and maximum selected EX. Values shown as cosine similarity are spectral cosine similarities, not percentages of EEM information.

## Direct answers

### Q1 — Can a few EX recover the full EEM?

Partially, under this transparent baseline. At K=2 the median full-range relative Frobenius error was 0.245 for NAIG and 0.274 for Uniform; median full-range spectral cosine similarity was 0.970 and 0.964, respectively. These are useful spectral-shape similarities but not evidence that an equivalent percentage of EEM information was recovered. Worst-site errors remained high (0.778 NAIG; 0.662 Uniform at K=2).

### Q2 — What changes with K?

Uniform improves steadily in full-range error (median 0.274 → 0.192 from K=2 → 8) and cosine similarity (0.964 → 0.982). NAIG does not improve monotonically: median error is 0.245, 0.246, 0.246, 0.271, and 0.261 for K=2,3,4,6,8; median cosine is 0.970, 0.970, 0.972, 0.968, and 0.970. Thus increasing K is beneficial for Uniform in this baseline, but not a stable error improvement for NAIG.

### Q3 — Does 4–6 EX have candidate-budget meaning?

Uniform K=4–6 is a reasonable candidate budget for follow-up work: median error falls from 0.264 to 0.220 and median cosine rises from 0.968 to 0.976, while V5 rho is high (median 0.959 and 0.972). This is a candidate budget statement for this dataset and reconstruction rule only, not a universal optimum or hardware validation. NAIG K=4–6 does not show the same reconstruction gain.

### Q4 — NAIG versus Uniform

Uniform is more suitable for this reconstruction baseline, especially at K=6–8. NAIG is suitable for structural preservation at low K: its V5 rho medians are 0.943 (K=2) and 0.954 (K=3), and K=6 reaches rho ≥ 0.90 at all 29 sites. The endpoints do not select the same strategy uniformly: Uniform K=4 has V5 median rho 0.959 and minimum 0.901, while its reconstruction median error is 0.264.

### Q5 — Are reconstruction and rho redundant?

No. Across site/configuration rows, error–rho Spearman correlations range from 0.059 to 0.530 for Uniform and -0.214 to 0.212 for NAIG across K; cosine–rho correlations similarly range from -0.520 to -0.049 for Uniform and -0.097 to 0.245 for NAIG. The measures describe different objects: one is pixel-level spectral recovery and the other is distance-ranking preservation.

### Q6 — High structure but poorer EEM recovery?

Yes. A clear example is S21, NAIG K=3: rho = 0.957 while full-range relative Frobenius error = 0.685 and cosine similarity = 0.771. Other high-rho/poor-reconstruction examples include S06 NAIG K=8 (rho 0.969, error 0.652) and S21 Uniform K=4 (rho 0.979, error 0.640). Mathematically, a sparse representation can preserve pairwise distance ordering while missing substantial pointwise variation; no chemical attribution is made here.

### Q7 — Full-range versus interpolation domain and edge effects

Uniform selected sets include both 300 and 700 nm at every tested K, so its full-range and interpolation-domain values are identical by construction. NAIG median full-range versus interpolation-domain errors are: K=2, 0.245 vs 0.230; K=3, 0.246 vs 0.248; K=4, 0.246 vs 0.246; K=6, 0.271 vs 0.277; K=8, 0.261 vs 0.262. Edge extension is therefore not the sole explanation for the NAIG pattern. The edge diagnostic table records span and lower/upper gaps for every row. Unsupported positions arise from mask-induced lack of any valid selected EX response; their median full-range fraction is 3.18% for NAIG K=2/3/4, 1.06% at K=6, 0.89% at K=8, and 8.85%, 6.36%, 0.17%, 0.17%, 0.17% for Uniform K=2/3/4/6/8. They were not silently removed.

### Q8 — Route decision

**Route 2** follows the pre-specified protocol: structural rho remains primary because the reconstruction trend is strategy-dependent and non-monotonic for NAIG, while reconstruction adds independent information and should remain supplementary. This is not a claim that reconstruction is unimportant; the discordant cases are precisely why it should be retained as a separate validation layer.

## Summary statistics

The complete 29-site distributions, including median, P10, worst, IQR, mean, P90, support fractions, and rho comparisons, are in `outputs/tables/reconstruction_summary.csv`. The site/configuration joint table is `outputs/tables/reconstruction_vs_structure.csv`.

## Quality-control outcome

- 290 unique rows (29 sites × 2 strategies × 5 K); no duplicate or missing site/configuration rows.
- S29 absent; main sites exactly S01–S28 and S30.
- EX and EM grids and 4,149-position common mask validated from the NPZ arrays.
- Fold-specific selected EX values were checked against the 5-nm grid and joined one-to-one to V5 rho.
- Reconstruction code accesses only selected EX rows; mask cells remain missing.
- No synthetic repeat was used; only the 29 main scans entered the primary loop.
- Four unit tests pass; all figures are regenerated from the output CSVs by the same command.

## Files and reproduction

Run from the repository root:

```text
python src/reconstruction_pilot.py --config configs/pilot.yaml
pytest -q
```

Figures are available as 300-dpi PNG plus PDF and SVG in `outputs/figures/`: P1 error vs K, P2 cosine vs K, P3 reconstruction vs rho, P4 typical/lower-tail distributions, and P5 representative EEM diagnostics.
