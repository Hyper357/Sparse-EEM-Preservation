# Dual-endpoint fixed EX configuration report

## Scope

This analysis reuses the frozen 29-site V5 `clean_masked_tensor`, 4,149-position common mask, V5 rho definition, V5 Uniform sets, and the same piecewise-linear EX-axis reconstruction with nearest-edge extension. Fixed Uniform configurations are evaluated for all 29 sites. NAIG remains fold-specific; no frequency-derived NAIG fixed optimum is claimed. Random fixed K=4 and K=6 benchmarks contain 500 unique feasible configurations each, generated with seed 42 and minimum pairwise spacing 20 nm. Fixed Uniform rho values were checked against the corresponding V5 Uniform outputs.

## Direct answers

### Q1 — Do structural preservation and reconstruction favour the same EX configuration?

Not universally. They are complementary endpoints. Uniform-4 and Uniform-6 both show favourable performance on both dimensions, but the site/configuration relationship is not redundant and some high-rho cases have relatively poor pointwise reconstruction.

### Q2 — Uniform-4

Configuration: `300;435;565;700`

Median supported-position reconstruction error in the full common-valid domain: **0.263724**; P10/P90: **0.186357/0.465688**; worst: **0.639835**. Median spectral cosine: **0.968078**; worst: **0.770831**. Median supported fraction: **0.998313**. Median rho: **0.958949**; minimum rho: **0.901478**; rho ≥0.90: **29/29**; rho ≥0.95: **20/29**.

### Q3 — Uniform-6 versus Uniform-4

Uniform-6 error changes from 0.263724 to 0.219820; worst error from 0.639835 to 0.574238; cosine from 0.968078 to 0.975957; rho from 0.958949 to 0.971538. Median metrics improve, but minimum rho changes from 0.901478 to 0.858238 and rho ≥0.90 coverage changes from 29/29 to 28/29. Thus 6EX is not uniformly superior on lower-tail structure; the two added EX create a candidate-budget trade-off.

### Q4 — Random fixed-combination levels

Uniform-4 percentiles among Random K=4 are structural median **64.8**, minimum rho **78.2**, coverage **100.0**, reconstruction-error best-percentile **38.2**, cosine **34.0**. Uniform-6 values are **55.8**, **36.0**, **54.2**, **69.6**, and **57.8**, respectively.

### Q5/Q6 — Better random or Pareto-superior candidates

Uniform-4 is on the combined K=4 Pareto front: **no**; Uniform-6 is on the combined K=6 front: **no**. Random configurations that strictly dominate Uniform-4/6 on both median error and median rho number **155** and **100**, respectively. The front files contain non-dominated fixed candidates; examples should be treated as exploratory candidates, not optimal configurations.

### Q7 — Dual-objective candidates

The top-10%-on-both relative-rank screens contain **5** random K=4 and **10** random K=6 configurations; full rows are saved in `dual_endpoint_top10_random_K4.csv` and `dual_endpoint_top10_random_K6.csv`. Uniform-4 and Uniform-6 do not meet both top-10% ranks (see the percentile table).

### Q8 — Next-stage recommendation

**Retain 4EX + 6EX in parallel.** Uniform-4 is the lower-channel candidate with strong V5 structural preservation; Uniform-6 has lower median reconstruction error and higher median rho but a weaker structural lower tail. Both should proceed to EX–EM joint discretisation validation; neither is called an optimal algae-classification or final hardware configuration.

## Discordant cases and quadrants

`outputs/tables/discordant_cases.csv` records A/B/C/D quadrants using the median error and median rho across predefined fixed Uniform site/configuration rows, plus the prior fold-specific NAIG rows. A high-rho/high-error case means relationship ordering can remain stable while pointwise full-EEM recovery is poorer; a low-error/lower-rho case means the opposite endpoints diverge. No chemical attribution is made.

## Scope QA

29 main sites were used; S29 is absent; target positions remain 4,149; all fixed/random EX are on the 5-nm grid with spacing ≥20 nm; Uniform definitions are unchanged; no synthetic repeats or raw large EEM data were added.
