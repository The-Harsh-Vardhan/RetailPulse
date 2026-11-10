# Audit 4th April, 2026

## Executive Verdict
RetailPulse is not a half-built mess. It is a mostly built Databricks capstone with real pipeline stages, real automation, real notebook outputs, and real presentation scaffolding. The problem is not "nothing is done." The problem is that the repo is currently stronger on implementation and narrative than on proof discipline. It is demoable today if you present it honestly. It is not fully submission-safe yet if you keep boasting the current ML metrics without disclosing leakage, and it is not fully packaged yet because some evidence is still described instead of stored.

## Audit Scope
This audit covers both:

- The committed repository state
- The current working tree state on April 4, 2026, including modified docs and notebooks not yet committed

That matters because the working tree already contains meaningful project progress that is not part of the last commit yet:

- Updated `README.md`
- Updated `notebooks/10_streaming_replay.py`
- Updated `notebooks/11_optimize.py`
- Updated `notebooks/12_report_pack.py`
- Updated generated notebook mirrors in `notebooks_ipynb/`
- New showcase docs: `Docs/showcase-summary.md` and `Docs/demo-script.md`

## What’s Actually Done

### Repo Progression So Far
From the Git history, the project moved through a sensible sequence instead of random notebook spam:

1. `first commit`
2. `docs: explain notebook formats and add future works inventory`
3. `tooling: add source-to-ipynb export workflow`
4. `build: add databricks asset bundle for full project run`
5. `ci: add github actions for validation and manual databricks runs`
6. `test: make utility imports stable in unittest runs`
7. `docs: add rebuild guide and github-ready polish`
8. `fix: make databricks serverless run succeed`

That is the shape of a real project, not a tutorial dump.

### Data Engineering Core
The main pipeline exists and is coherent:

- `notebooks/00_setup.py` creates schema and Unity Catalog volumes
- `notebooks/01_sample_and_upload.py` validates uploaded sampled CSV files
- `notebooks/02_bronze_ingest.py` ingests explicit-schema bronze Delta tables
- `notebooks/03_silver_transform.py` standardizes and enriches silver tables
- `notebooks/04_gold_model.py` builds dimensions, facts, and `mart_user_features`

This is the backbone of the repo, and it is already in place.

### Analytics And Mining
The analytics layer is not imaginary:

- `notebooks/05_olap.py` runs `CUBE` and `ROLLUP`
- `notebooks/06_association_rules.py` builds pairwise association rules and recommendation outputs
- `notebooks/07_clustering.py` runs KMeans over shopper features
- `notebooks/08_classifier.py` trains a decision tree for `power_user`
- `notebooks/09_regression.py` trains a regression model for basket size
- `notebooks/10_streaming_replay.py` runs an `AvailableNow` replay-style stream
- `notebooks/11_optimize.py` benchmarks `OPTIMIZE` and `ZORDER BY`
- `notebooks/12_report_pack.py` assembles final report-facing evidence views

That is already enough scope for a serious MVP demonstration.

### Automation And Reproducibility
The repo has more engineering discipline than most student submissions:

- `databricks.yml` plus `resources/retailpulse_job_resource.yml` define a sequential Databricks Asset Bundle job
- `.github/workflows/ci.yml` runs local validation on push and pull request
- `.github/workflows/run-databricks-bundle.yml` supports manual Databricks deploy-and-run from GitHub
- `scripts/sample_instacart.py` builds the deterministic local sample
- `scripts/export_databricks_source_to_ipynb.py` keeps `.ipynb` mirrors deterministic
- `scripts/split_stream_replay_batches.py` supports replay-batch preparation

This part is genuinely solid for an MVP.

### Tests And Local Validation
The local helper tooling is not untested:

- `tests/test_sample_instacart.py`
- `tests/test_split_stream_replay_batches.py`
- `tests/test_export_databricks_source_to_ipynb.py`

During this audit, these local checks passed:

- `python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb`
- `python -m py_compile scripts\sample_instacart.py scripts\split_stream_replay_batches.py scripts\export_databricks_source_to_ipynb.py`
- `python scripts/export_databricks_source_to_ipynb.py --check`

### Documentation And Demo Material
This is not just code anymore. The repo already has report and presentation scaffolding:

- `README.md`
- `Docs/Executive Summary.md`
- `Docs/Grocery Sales Analytics & Recommendation on Databricks_ 14-Day Plan.md`
- `Docs/rebuild-from-scratch.md`
- `Docs/showcase-summary.md`
- `Docs/demo-script.md`

That means the project is already past "implementation only" and into "presentation prep" territory.

## Roast / Findings

### 1. High: The ML metrics are not presentation-safe as written
This is the biggest honesty problem in the repo.

The clustering notebook trains on `total_orders` as part of the feature set in `notebooks/07_clustering.py:25-32`. Then the classifier reuses `cluster_id` as an input feature in `notebooks/08_classifier.py:25-33`, while the classifier label `power_user` is directly derived from `total_orders` in `notebooks/08_classifier.py:39-43`.

That means the classifier is not just learning behavior. It is partially learning from a cluster assignment that was itself influenced by the same target-defining variable.

The regression story is also weak. `notebooks/04_gold_model.py:96-149` creates user aggregates from all orders, and `notebooks/09_regression.py:25-48` feeds those user-level aggregates back into per-order basket-size prediction. That is not a clean temporal or held-out feature design. It is closer to "predicting a row with knowledge aggregated from the whole user history including the row’s own era."

Blunt version: the metrics may be numerically real, but the evaluation design is not strong enough to brag about them as if they were clean predictive results.

What this means for the demo:

- You can still show the ML notebooks
- You should not oversell the accuracy and RMSE as if they are robust production-grade predictive evidence
- If asked, the honest framing is "exploratory modeling built on derived user features, with methodology that still needs tightening"

### 2. Medium: The repo claims stronger evidence packaging than it actually stores
The OLAP notebook displays outputs, but it does not persist them as report tables.

- `notebooks/05_olap.py:63-84` displays `cube_df`, `rollup_df`, `basket_df`, and a comparison frame
- `notebooks/12_report_pack.py:57-62` pulls persisted report tables for classifier, regression, clustering, streaming, optimization, and rules, but not OLAP outputs
- `Docs/showcase-summary.md:107-111` claims every major deliverable is backed by a persisted output table

That last claim is too strong. The project has persisted evidence for several major areas, but not for everything it says.

Blunt version: this is a documentation confidence problem, not a pipeline failure.

### 3. Medium: CI checks the repo shape, not the real analytical behavior
The CI workflow in `.github/workflows/ci.yml:25-32` runs:

- unit tests
- Python compile checks
- notebook mirror drift check

That is useful, but it does not:

- run Databricks notebooks
- validate gold-model row contracts end-to-end
- verify report tables exist
- verify the bundle job outputs still match the docs

Blunt version: CI proves the repo is tidy. It does not prove the actual analytics product still works.

### 4. Medium: Submission assets are still described instead of packaged
The README literally says screenshots can be added later in `README.md:288-300`. The `assets/` folder currently contains Mermaid source files, not a finished evidence pack. That is fine for development, but weak for final submission.

Right now the project has:

- diagram source files
- report docs
- demo script
- validated run notes

What it does not yet have in repo form is a clear submission artifact bundle such as:

- screenshot folder
- exported result images/tables
- one clean "show this to evaluator" artifact location

Blunt version: the repo is ready to talk about the demo, not fully ready to hand over the demo evidence.

### 5. Low: The project is actually far along
This needs to be said clearly so the roast does not become fake drama.

What is already good:

- Real medallion pipeline
- Real Databricks bundle orchestration
- Real CI
- Real helper scripts
- Real unit tests for local tooling
- Real rebuild documentation
- Real demo script
- Real validated run notes
- Honest documentation about dataset limitations and optimize results

This is not a weak repo. It is a strong repo with a few credibility gaps in the final stretch.

## What’s Left For MVP Demo And Submission

### Must Do Before Demo
- Rewrite the classifier and regression claims so they explicitly disclose leakage risk or stop boasting those metrics as hard evidence.
- Capture and store the actual demo screenshots or exported result tables for OLAP, recommendations, clustering, classifier, regression, streaming validation, and optimize summary.
- Commit the current working-tree changes so the repo state matches the story you are telling.
- Rehearse the 6 to 8 minute demo flow against the validated run and the current docs, not against memory.

### Should Do Before Submission
- Persist OLAP outputs as report tables or soften the docs so they do not claim stronger evidence packaging than the notebooks provide.
- Create one submission-facing artifact location such as `assets/screenshots/` or `Docs/artifacts/` and put the actual evidence there.
- Tighten the README so "implemented now" and "future work later" are separated with zero ambiguity.
- Make sure the new showcase docs, notebook changes, and README changes are committed together as one coherent submission state.

### Nice To Have If Time Remains
- Add notebook-level validation beyond helper-script tests.
- Add a simple dashboard or rendered diagrams for easier evaluation.
- Redesign the model methodology to remove leakage and use cleaner train/test feature construction.
- Add stronger evidence automation so docs and reported metrics cannot drift away from generated outputs.

## Verification Snapshot
Local audit checks run successfully:

- `python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb`
- `python -m py_compile scripts\sample_instacart.py scripts\split_stream_replay_batches.py scripts\export_databricks_source_to_ipynb.py`
- `python scripts/export_databricks_source_to_ipynb.py --check`

Repository facts confirmed during the audit:

- The Databricks bundle config exists
- The sequential job resource exists
- CI exists
- Manual Databricks GitHub workflow exists
- The target audit file did not previously exist and was added as a report-only change

## MVP Status
For a project demonstration, you are close.

For a final submission, the repo needs one more honesty-and-packaging pass.

If I had to score the current state:

- Engineering implementation: strong
- Demo readiness: good, with rehearsal and artifact capture still needed
- Submission readiness: decent, but blocked by overstated ML confidence and incomplete evidence packaging

## Bottom Line
RetailPulse is implemented enough for a live MVP demo right now. It is not yet honest-enough for a final submission if you keep presenting the current ML metrics as clean predictive proof and keep the evidence pack half in notebooks and half in promises. Fix the claim discipline, package the artifacts, commit the real repo state, and this becomes a strong submission instead of a strong almost-submission.
