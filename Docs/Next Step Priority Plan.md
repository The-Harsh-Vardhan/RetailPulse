# RetailPulse Next Step Priority Plan

## Purpose
This document answers the practical question: what should happen next, and what should not happen next.

The short answer is simple: do not spend the next cycle building more models. RetailPulse already has enough technical surface for a strong boss review and submission. The immediate bottleneck is release quality, visualization polish, and operational confidence.

## Current Judgment

### Implemented in repo
- End-to-end Databricks pipeline and bundle-based rebuild path
- Persisted report tables and release smoke checks
- Boss brief, production runbook, release checklist, handbook, and BI strategy docs
- Dashboard SQL, screenshot evidence pack, and notebook fallback

### Verified in live Databricks workspace
- Latest successful run id: `432431661287387`
- Job id: `61936309152043`
- Published dashboard: `RetailPulse Demo Dashboard`
- Warehouse id: `2300565af9f2288c`

### Recommended next step
- Freeze scope and finish a boss-ready internal pilot pass

### Not recommended right now
- More supervised-model training on the current leakage-prone setup
- New features, new marts, or a second modeling track

## Immediate Priority Order
1. Lock the release story.
2. Polish the dashboard and boss-facing evidence.
3. Enforce lightweight operational validation.
4. Decide later whether ML rigor is worth a dedicated redesign cycle.

## What To Do Now

### 1. Finish the release-quality pass
- Make sure the repo and live workspace say the same thing.
- Use `Docs/current-production-state.md` as the authoritative release record.
- Use `Docs/release-checklist.md` and `Docs/production-runbook.md` for every refresh.
- Intentionally commit the documentation state once it is internally consistent.
- Rehearse the boss walkthrough until it is stable at 6 to 8 minutes.

### 2. Improve visualization before adding more ML
- Tighten the current Databricks dashboard instead of adding new models.
- First-priority polish:
  - clearer business labels
  - fewer table-heavy panels
  - short interpretation text under charts
  - useful page-level filters where supported
  - stronger separation between release-safe KPIs and `Experimental Insights`
- If one extra BI surface is added, make it **Power BI Desktop**, not another modeling notebook.

### 3. Add minimal operational confidence
- Treat this as an internal pilot release, not a notebook exercise.
- Every candidate refresh should satisfy:
  - required report tables exist
  - required report tables are readable
  - `mart_association_rules` is non-empty
  - `report_stream_validation` still returns `mismatch_groups = 0`
  - dashboard metadata still resolves
  - latest rebuild finished `SUCCESS`

### 4. Defer supervised ML redesign unless it is explicitly worth it
- If evaluation is mostly about analytics engineering, business storytelling, and delivery quality, stop after release hardening and visualization polish.
- If evaluation strongly rewards ML rigor, the next ML task is not “train more.” It is:
  - redesign classifier features so `cluster_id` does not leak `total_orders`
  - redesign regression features so they use prior-only or temporally safe aggregates
  - retrain and re-evaluate only after the feature design is safe

## Recommended Milestone

### Current milestone
- **Boss-ready internal pilot freeze**

### Exit criteria
- Dashboard is polished enough for boss review
- Docs match the live workspace state
- Screenshot evidence matches the live story
- `Experimental Insights` remain clearly non-operational
- The full walkthrough works without improvisation

## Decision After The Freeze

### Business and production branch
Choose this if your priority is boss confidence, submission polish, and presentability.

Focus:
- cleaner dashboard
- stronger narrative consistency
- optional Power BI Desktop executive report
- continued manual release discipline

### ML rigor branch
Choose this only if the submission or boss will judge you heavily on predictive-methodology quality.

Focus:
- leakage-safe feature redesign
- fresh training, testing, and evaluation
- updated docs, screenshots, and dashboard wording after reruns

## Default Recommendation

### Now
- Release hardening
- Dashboard polish
- Boss-walkthrough rehearsal

### Next
- Optional Power BI Desktop executive layer

### Later
- Leakage-safe ML redesign only if it becomes a grading or boss priority
