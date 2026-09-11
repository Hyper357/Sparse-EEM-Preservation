# V6 input readiness and unresolved data issues

Checked against origin/main commit ec033b02badc5334220ab1048e61da4291ac60fd after `git pull --rebase origin main` on 2026-09-11.

Status: manuscript rewriting and publication-figure production are paused pending the required analysis handoff. No core statistics were recomputed and no frozen values were changed. These are missing-input issues; a numerical contradiction has not been established.

## Required handoff document

`v6_analysis/V6_ANALYSIS_FREEZE.md` is absent from both the working tree and HEAD. `v6_analysis/README.md` exists, but substitution for the explicitly required document has not been authorized.

## Figure-ready data gaps

| Destination | Existing input | Missing input required under the no-recalculation rule |
|---|---|---|
| Fig.1 measured EEM panels | `figure_data/fig1_eem_examples.csv`: 12 site/configuration diagnostic rows | EX/EM coordinates and measured intensity grid, or explicitly approved reuse of existing figure assets; the CSV has no spectral intensity cells or site coordinates |
| Fig.3a/b | `fig3_structural_vs_K.csv`: 290 site rows, NAIG/Uniform, K=2,3,4,6,8 | Frozen plot-ready median/P10/minimum and coverage for the requested K=1–8 curve; no author-side aggregation will be performed |
| Fig.3c | `fig3_strategy_comparison.csv`: the same two strategies and five budgets | Frozen VIG/RDG/Random comparisons and their plotted summary statistics |
| Fig.4a/b | `fig4_reconstruction_vs_K.csv`: 290 site rows | Publication summary statistics exist in `tables/reconstruction_results.csv`, but the instruction requires plotting numbers from `figure_data/`; the analyst should include the approved summary there |
| Fig.4d | `fig4_fixed_configuration_comparison.csv`: five Uniform rows only | Frozen random K4/K6 configuration cloud, Pareto membership and selected exploratory examples; no analyst-side re-selection by the writer |

## V5 source availability

The complete V5 source exists locally outside the Git checkout at `../V5_FINAL/01_manuscript/manuscript_V5.md`, `.docx` and `.pdf`. V5 is not missing and will not be reconstructed from summaries. These source files remain untouched.

## Literature input

No filename matching the specified Han/Liu/Mao multiwavelength LIF paper was found in the repository during intake. Exact bibliographic details and primary-source verification remain necessary before writing its literature comparison.

## Resume condition

The analysis handoff owner supplies the required freeze document and completes the figure-ready exports above, or the author explicitly revises the input-source restrictions. Then read all handoff tables and the complete V5 source, build the manuscript/claim map and five figures, render the DOCX, review, commit and push. No manuscript-completion commit or push has been made at this stage.
