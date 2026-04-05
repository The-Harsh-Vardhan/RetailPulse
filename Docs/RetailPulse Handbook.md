# RetailPulse Handbook

## Purpose
RetailPulse is a controlled internal analytics pilot built on Databricks Free Edition. It uses a deterministic 10% sample of the Instacart dataset to demonstrate a full warehouse-style pipeline, an analytics layer, recommendation logic, segmentation, exploratory modeling, a replay-style streaming check, and a boss-facing dashboard surface.

This handbook is the single detailed explanation of what the project is, what it actually does today, how to run it, how to demo it, and where the important assets live.

## Current State At A Glance

### Implemented in repo
- Databricks source notebooks in `notebooks/` with generated `.ipynb` mirrors in `notebooks_ipynb/`
- Databricks Asset Bundle configuration for a sequential full rebuild job
- Persisted report tables for OLAP, clustering, cluster-k selection, streaming validation, optimize evidence, and exploratory model metrics
- SQL query pack for the published AI/BI dashboard
- Boss-facing and release-facing docs under `Docs/`
- Screenshot evidence pack under `assets/screenshots/`

### Verified in live Databricks workspace
- Workspace host: `https://dbc-27b50dca-30e0.cloud.databricks.com/`
- Job id: `61936309152043`
- Latest successful run id: `631388168060027`
- Latest successful run date: April 5, 2026
- Published dashboard: `RetailPulse Demo Dashboard`
- Dashboard id: `01f1305e8f1a115e8fb2b378bd4d8f99`
- Warehouse id: `2300565af9f2288c`

### Recommended next step
- Keep the published Databricks AI/BI dashboard as the official live surface
- Keep the richer five-page Dashboard V2 layout as the live review surface
- Use the report pack notebook and screenshot set as fallback evidence
- Keep classifier and regression outputs labeled as `Experimental Insights`

### Not recommended right now
- Treating the classifier or regression outputs as production-grade decision engines
- Expanding scope with new features before the release story is fully stable
- Replacing the dashboard stack with an external BI tool before the Databricks story is polished

## What RetailPulse Is
- An internal Databricks Free Edition pilot, not a customer-scale SLA product
- A deterministic 10% Instacart sample project designed for reproducibility and reviewability
- A grocery-order analytics and recommendation system centered on counts, baskets, reorder behavior, and timing
- Not true sales analytics, because Instacart does not include raw prices, revenue, or absolute calendar dates

## What It Actually Builds
- A bronze, silver, and gold Delta pipeline over grocery-order data
- A star schema centered on `fact_order_items` and `fact_orders`
- Persisted OLAP report tables using `CUBE` and `ROLLUP`
- Pairwise association rules for recommendation examples
- KMeans customer segmentation
- An `Experimental Insights` classifier for power-user prediction
- An `Experimental Insights` regression model for basket-size prediction
- A replay-style streaming validation flow using `Trigger.AvailableNow`
- `OPTIMIZE` and `ZORDER BY` benchmark evidence
- A published AI/BI dashboard plus `12_report_pack.py` as the notebook fallback, both organized into a five-section Dashboard V2 story

## How The System Flows
```text
Instacart raw CSVs
-> deterministic local 10% sample
-> sampled CSV upload to Databricks volume
-> bronze Delta tables
-> silver cleansed/enriched tables
-> gold facts, dimensions, marts, and report tables
-> dashboard queries + report pack + screenshot evidence
```

### Detailed flow
1. Build a deterministic 10% sample locally from the full Instacart CSV set.
2. Upload the sampled CSV files into the raw Unity Catalog volume expected by the Databricks notebooks.
3. Authenticate the Databricks CLI.
4. Validate and deploy the Databricks Asset Bundle.
5. Run the `retailpulse_full_rebuild` job.
6. Inspect the resulting facts, marts, and report tables.
7. Review outputs through the published AI/BI dashboard first and the report-pack notebook second.

## How To Use The Project

### 1. Prepare local prerequisites
- Install Python
- Install Databricks CLI
- Download the raw Instacart CSV files

Expected raw files:
- `orders.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `products.csv`
- `aisles.csv`
- `departments.csv`

### 2. Build the deterministic sample
```powershell
python scripts/sample_instacart.py `
  --input-dir C:\path\to\instacart_raw `
  --output-dir C:\path\to\retailpulse_sample
```

### 3. Regenerate notebook mirrors when notebook source changes
```powershell
python scripts/export_databricks_source_to_ipynb.py
```

### 4. Authenticate Databricks CLI
Preferred:
```powershell
databricks auth login --host https://<your-workspace-host>
```

Fallback:
```powershell
databricks configure --host https://<your-workspace-host>
```

### 5. Validate and deploy the bundle
```powershell
databricks bundle validate -t dev
databricks bundle deploy -t dev
```

### 6. Run the full workflow
```powershell
databricks bundle run retailpulse_full_rebuild -t dev
```

### 7. Run local validation before release work
```powershell
python -m unittest -q tests.test_sample_instacart tests.test_split_stream_replay_batches tests.test_export_databricks_source_to_ipynb
$files = @((Get-ChildItem notebooks -Filter *.py).FullName) + @((Get-ChildItem scripts -Filter *.py).FullName) + @((Get-ChildItem tests -Filter *.py).FullName)
python -m py_compile $files
python scripts/export_databricks_source_to_ipynb.py --check
databricks bundle validate -t dev
```

## Where To Inspect Results

### Dashboard-first path
- Open `RetailPulse Demo Dashboard`
- Use `Executive Overview` for the headline result and core table counts
- Use `Order Behavior` for daypart, hourly, and product-level behavior
- Use `Recommendations And Segments` for rules, seed recommendations, and cluster interpretation
- Use `Execution And Data Quality` for validation and release-signoff evidence
- Use `Experimental Insights And Performance` only for exploratory metrics and optimize evidence

### Notebook fallback path
- Open `notebooks/12_report_pack.py`
- Use it when the dashboard is unavailable or when a drill-down is easier in notebook form
- The notebook mirrors the same five sections as Dashboard V2 so the story stays consistent

### Release evidence
- Screenshot evidence: `assets/screenshots/`
- Dashboard query source: `sql/retailpulse_dashboard_queries.sql`
- Dashboard build instructions: `Docs/databricks-dashboard-ui-guide.md`
- Production posture and release IDs: `Docs/current-production-state.md`

## How To Demo It
1. Start with the published AI/BI dashboard, not raw notebooks.
2. Walk the five-section story in order: Executive Overview, Order Behavior, Recommendations And Segments, Execution And Data Quality, then Experimental Insights And Performance.
3. Use `12_report_pack.py` only if a widget fails or a specific panel needs drill-down.
4. Keep the core explanation disciplined:
   - recommendation and segmentation are valid deliverables
   - streaming validation is a correctness story
   - optimize benchmark is documented honestly
   - classifier and regression are exploratory, not operational

## Known Constraints

### Implemented in repo
- Manual release path
- Free Edition-compatible notebook/job structure
- Dashboard fallback path
- Screenshot evidence pack

### Verified in live Databricks workspace
- Published dashboard and successful April 5 run
- Working SQL warehouse for the dashboard
- Bundle-driven full rebuild path

### Recommended next step
- Keep the release posture as a controlled internal pilot
- Use the release checklist and runbook for every boss-facing refresh

### Not recommended right now
- Auto-running full rebuilds on every push
- Claiming sales, revenue, or date-based business outcomes that the dataset cannot support
- Using `Experimental Insights` outputs as release gates

## Where Everything Lives
- Canonical notebooks: `notebooks/`
- Convenience notebook mirrors: `notebooks_ipynb/`
- Helper scripts: `scripts/`
- Dashboard SQL: `sql/`
- Tests: `tests/`
- Bundle resources: `resources/`
- Release and showcase docs: `Docs/`
- Screenshot evidence: `assets/screenshots/`

## FAQ

### Why does this project not show real sales or revenue?
Instacart does not include product prices or revenue. RetailPulse therefore focuses on item counts, basket size, reorder behavior, day-of-week, hour-of-day, and days-since-prior-order.

### Why are there no absolute calendar dates?
The source dataset does not contain them. The project uses relative ordering features such as `order_dow`, `order_hour_of_day`, and `days_since_prior_order`.

### Why does the recommendation notebook use pairwise rules instead of FP-growth?
The final Free Edition-safe implementation uses pairwise association rules because that path was more reliable in the serverless environment while still producing reviewable recommendation outputs.

### Why can `OPTIMIZE` look slower instead of faster?
Because this sample is small. The benchmark was still worth running because it proves the project measured the effect honestly instead of assuming improvement.

### Why are the classifier and regression outputs not operational?
Their current feature construction is still best treated as exploratory. They stay in the project for boss discussion and future modeling work, but they are not release KPIs or operational decision drivers.

### What should I open first as a reviewer?
Open the published dashboard first. If anything is unclear, then use `Docs/demo-script.md`, `Docs/showcase-summary.md`, and `notebooks/12_report_pack.py`.

## Related Docs
- [Showcase Summary](showcase-summary.md)
- [Demo Script](demo-script.md)
- [Current Production State](current-production-state.md)
- [Production Runbook](production-runbook.md)
- [Release Checklist](release-checklist.md)
- [Dashboard Metadata](dashboard-metadata.md)
- [BI Integration And Visualization Strategy](BI%20Integration%20And%20Visualization%20Strategy.md)
