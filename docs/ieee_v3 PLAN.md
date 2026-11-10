# IEEE Paper v3: richer release-safe visuals with a stronger methods formulation

## Summary
Create a new manuscript at [IEEE_Paper_v3.tex](c:/D Drive/Projects/6th Sem/RetailPulse/Docs/Submission/IEEE_Paper_v3.tex) by refactoring [IEEE_Paper_v2.tex](c:/D Drive/Projects/6th Sem/RetailPulse/Docs/Submission/IEEE_Paper_v2.tex), not overwriting it. Keep the current IEEE journal structure and all validated April 5, 2026 facts, but rebalance the paper toward four release-safe evidence lanes: OLAP behavior, product-demand visuals, recommendation/segmentation proof, and validation proof. Add a heavier but still disciplined math treatment in methodology, and keep exploratory ML present only as a short caveated subsection without new figures.

## Key Changes
### Manuscript structure
- Keep title, authors, abstract, core claims, and bibliography base from v2.
- Tighten Introduction, Related Work, and Limitations by removing repeated prose so the extra space is spent on figures and equations instead of narrative duplication.
- Insert a short `Analytical Formulation` subsection in Methodology after the report-table discussion and before the analytics subsections.
- Keep the current Results flow, but explicitly map each added figure to a persisted report table or dashboard widget so the paper reads as evidence-backed, not screenshot-driven.

### Figures and dashboard evidence
- Reuse existing validated visuals only; do not add exploratory ML screenshots and do not fabricate new charts.
- Copy the selected screenshot assets into [Docs/Submission/Figures](c:/D Drive/Projects/6th Sem/RetailPulse/Docs/Submission/Figures) so the submission remains self-contained under the existing `\graphicspath`.
- Keep the existing TikZ end-to-end workflow figure.
- Add `03_olap_outputs.png` as a full-width figure for department demand and hourly timing behavior.
- Keep `10_orders_by_day.png` as the day-of-week order and basket-size evidence figure.
- Add `11_top_products.png` as a product-concentration figure in the order-behavior subsection.
- Keep `13_cluster_k_scores.png` as the clustering model-selection figure.
- Add `08_stream_validation.png` as the primary validation dashboard figure.
- Do not embed `05_cluster_profiles.png`, `12_seed_recommendations.png`, or `15_olap_validation.png` as screenshots because the existing LaTeX tables already communicate those results more cleanly.
- Use IEEE-compatible float handling: add `subfig` only if needed, prefer `figure*` for wide dashboard visuals, and avoid `float`/`[H]` patterns from the older report draft.

### Mathematics
- Formalize deterministic sampling with the retained-user set definition \(S=\{u \mid u \bmod 10 = 0\}\).
- Add the association-rule metric equations for support, confidence, and lift.
- Add feature standardization notation for the clustering feature vector.
- Add the KMeans objective and the average-silhouette selection rule for \(k \in \{3,4,5\}\).
- Add a streaming-validation mismatch formulation that defines exact agreement at group level and the release criterion of zero mismatches.
- Add one silhouette-method reference to the bibliography if the formal equation is introduced and no such citation already exists.

### Tables and prose balance
- Retain the existing validated count, top-rule, seed-recommendation, cluster-profile, stream-validation, OLAP-validation, optimize-summary, and exploratory-metrics tables.
- Shorten the exploratory predictive subsection to one compact paragraph plus the existing small metrics table, with the current disclaimer text unchanged.
- Update captions so each figure/table states the backing report table or dashboard query surface where relevant.

## Interfaces / Artifacts
- New deliverable: [IEEE_Paper_v3.tex](c:/D Drive/Projects/6th Sem/RetailPulse/Docs/Submission/IEEE_Paper_v3.tex).
- No runtime or code API changes.
- Submission asset set expands from the current two local figures to the selected release-safe screenshot set needed by v3.

## Test Plan
- LaTeX build succeeds for v3 with bibliography and no missing asset errors.
- All references, citations, figure labels, and table labels resolve cleanly.
- Wide figures remain readable in the IEEE two-column layout without clipped captions, unreadable axis labels, or overfull equation/table blocks.
- Every newly added visual corresponds to a validated repo-backed artifact already present in `assets/screenshots`.
- Exploratory ML remains visibly demoted: no new exploratory figures, disclaimer text unchanged, and no release-safe claims derived from that section.

## Assumptions
- `IEEE_Paper_v2.tex` remains untouched and v3 is created as a sibling file.
- The paper should favor release-safe dashboard evidence over full five-page dashboard coverage.
- Existing validated numbers and dates remain authoritative; v3 is a packaging upgrade, not a new experiment run.
- Power-of-10 guidance does not map directly to this manuscript-editing task, so it will not be forced into the document plan.
