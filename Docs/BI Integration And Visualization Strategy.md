# BI Integration And Visualization Strategy

## Purpose
This note explains the current RetailPulse visualization stack, how to improve it, whether MCP can help, and how Databricks can connect to Power BI or Tableau. It ends with one explicit recommendation so the project does not drift into tool-shopping.

## Current Visualization Stack

### Implemented in repo
- Canonical dashboard queries in `sql/retailpulse_dashboard_queries.sql`
- Dashboard build spec and operator guide in `Docs/databricks-dashboard-spec.md` and `Docs/databricks-dashboard-ui-guide.md`
- Evidence pack under `assets/screenshots/`
- Notebook fallback surface in `notebooks/12_report_pack.py`

### Verified in live Databricks workspace
- Published AI/BI dashboard: `RetailPulse Demo Dashboard`
- Dashboard id: `01f1305e8f1a115e8fb2b378bd4d8f99`
- Warehouse id: `2300565af9f2288c`
- Published revision: `2026-04-05T05:08:33.719Z`

### Recommended next step
- Treat the Databricks AI/BI dashboard as the system of record for live presentation
- Treat `12_report_pack.py` as the fallback evidence hub
- Treat screenshots as submission artifacts, not the primary analytics experience

### Not recommended right now
- Replacing the Databricks dashboard with a different BI tool before the current story is visually polished
- Introducing more dashboard surfaces than the team can maintain consistently

## What To Improve Inside Databricks First

### Visual structure
- Tighten page titles so they read like business sections, not notebook leftovers
- Standardize widget labels to business terms such as `Orders`, `Items`, `Rules`, `Segments`, and `Validation`
- Use one restrained color system across counters, bars, and lines instead of whatever Databricks defaults happen to pick
- Keep `Experimental Insights` visually separated from the release-safe sections

### Chart selection
- Reduce table-heavy panels and favor counters, horizontal bars, line charts, pivots, and conditional formatting
- Use sorted horizontal bars for department demand and segment comparisons
- Keep timing behavior in line charts or heatmap-style layouts rather than raw tables
- Reserve large tables for recommendation rules and stream validation detail only

### Interpretation layer
- Add one short line of interpretation under each non-obvious widget
- Explain what `lift`, `reorder rate`, and `basket size` mean in business terms
- Add a short note wherever a metric is exploratory rather than operational

### Interaction and polish
- Add page-level filters for department, daypart, segment, and metric view where the current dashboard supports them cleanly
- Replace any remaining rendered evidence with cleaner UI-native captures
- Keep one screenshot source of truth and replace files in place so docs do not drift

## Data Presentation Improvements

### Metric glossary
| Metric | Recommended business phrasing |
| --- | --- |
| `basket_size` | average number of products in an order |
| `reorder_rate` | share of products reordered from prior behavior |
| `order_count` | number of orders in the selected slice |
| `lift` | strength of co-purchase beyond random chance |

### Presentation rules
- Prefer friendly labels over raw field names
- Keep counts and percentages visually distinct
- Show recommendation strength with support, confidence, and lift together
- Keep `Experimental Insights` in a clearly separated section so executives do not read it as a release KPI block

## Can MCP Help

### Implemented in repo
- No repo-side MCP integration exists for Power BI or Tableau

### Verified in current environment
- The configured MCP environment in this Codex session exposes no Power BI or Tableau integration server
- The available MCP resources discovered here do not include a BI connector server for those tools

### Recommended next step
- Treat MCP as irrelevant for the current Databricks-to-BI path
- If a future Power BI or Tableau MCP server appears, treat it as a convenience layer only

### Not recommended right now
- Designing the BI rollout around MCP
- Assuming MCP is an official or stable production integration route for these tools

## Databricks To Power BI

### Supported path
- Databricks documents Power BI as a supported BI integration path through Partner Connect and Databricks SQL connectivity
- Power BI can connect to Databricks SQL warehouses through the official Databricks connector
- The practical boss-facing route is:
  1. keep Databricks AI/BI dashboard as the current live surface
  2. connect Power BI Desktop to the Databricks SQL warehouse
  3. build one polished executive report after the Databricks queries stabilize

### Desktop vs service
- Power BI Desktop is the simplest first step for a Windows-based internal pilot
- Power BI service becomes relevant after the report design stabilizes and you are ready to publish and refresh it

### Automation reality
- After the connection exists, Microsoft supports downstream automation through official Power BI PowerShell modules and the Power BI REST API
- That automation is for Power BI-side report and workspace operations, not for replacing Databricks bundle/deploy/run workflows

### Recommended next step
- Use Power BI Desktop as the first external BI target

### Not recommended right now
- Building a Power BI service publishing pipeline before the report content is stable
- Using Power BI as a substitute for fixing weak Databricks visual storytelling

## Databricks To Tableau

### Supported path
- Databricks documents Tableau as a supported BI integration through Partner Connect and the Tableau Databricks connector
- Tableau Desktop or Tableau Cloud can connect to Databricks SQL warehouses

### Automation reality
- Tableau supports downstream automation through official `tabcmd`
- That is useful after a Tableau report is already designed and published

### Recommended next step
- Consider Tableau only if the organization already uses Tableau Cloud or Tableau Server

### Not recommended right now
- Starting a second BI surface in Tableau if your actual stakeholders live in the Microsoft stack

## CLI Reality

### What Databricks CLI is good for
- Workspace authentication
- Bundle validate/deploy/run
- Dashboard metadata inspection
- Some Databricks-side partner and OAuth administration in supported environments

### What it is not
- The main end-to-end connection workflow for Power BI or Tableau
- A replacement for Power BI Desktop, Tableau Desktop, Power BI service, or Tableau Cloud publishing tools

### Important constraint
- Because RetailPulse is currently on Databricks Free Edition, account-level OAuth and partner-management flows may be unavailable or reduced. That is the safe inference from Databricks Free Edition limitations, so this project should assume Partner Connect and manual connector flows are the realistic path unless proven otherwise in the live workspace.

## Recommendation

### Official current surface
- Keep the published Databricks AI/BI dashboard as the official live analytics surface

### First external BI target
- Choose **Power BI Desktop** first

### Why
- Easiest boss-facing packaging on Windows
- Strong official Databricks support
- Strong Microsoft automation story after the report exists
- Lower friction than introducing Tableau unless the company already standardizes on Tableau

### Alternative
- Choose Tableau instead only when the surrounding organization, licensing, and review culture already centers on Tableau Cloud or Tableau Server

## Adoption Plan
1. Polish the Databricks dashboard first: labels, layout, filters, colors, and interpretation text.
2. Build one Power BI Desktop report against the Databricks SQL warehouse using the same release-safe metrics and the same `Experimental Insights` disclaimer.
3. Automate downstream BI publication only after the report design stabilizes and the team decides whether Power BI service or Tableau is actually worth maintaining.

## Official References
- Databricks Power BI docs: https://docs.databricks.com/en/partners/bi/power-bi.html
- Databricks Tableau docs: https://docs.databricks.com/gcp/en/partners/bi/tableau
- Databricks Partner Connect: https://docs.databricks.com/aws/en/partner-connect/
- Databricks OAuth app management: https://docs.databricks.com/gcp/en/integrations/enable-disable-oauth
- Databricks Free Edition limitations: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations
- Power BI Databricks connector: https://learn.microsoft.com/en-us/power-query/connectors/databricks
- Power BI PowerShell overview: https://learn.microsoft.com/en-us/powershell/power-bi/overview?view=powerbi-ps
- Power BI REST API: https://learn.microsoft.com/en-us/rest/api/power-bi/
- Tableau Databricks connector: https://help.tableau.com/current/pro/desktop/en-us/examples_databricks.htm
- Tableau `tabcmd`: https://help.tableau.com/current/online/en-us/tabcmd.htm
