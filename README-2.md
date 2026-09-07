# Solar Cell Manufacturing Dashboard

Modular Streamlit dashboard for PERC cell production data (Streamlit + Plotly
+ Pandas + NumPy), dark MES-style theme, financial-year (Apr → Mar) aware.

## 1. Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. On first run it also writes
`.streamlit/config.toml` next to `app.py` (only if that file doesn't already
exist) so Streamlit's own chrome matches the dark theme from the first paint.

## 2. Project layout

| File | Responsibility |
|---|---|
| `app.py` | Page layout only — sidebar nav, header, and the 3 tab renderers (Overview / Production / Analytics). |
| `data_utils.py` | Reading `.xlsx` files, guessing which sheet/column is which, cleaning into canonical DataFrames, financial-year math, formatting helpers. |
| `charts.py` | One function per chart type (donuts, combo trend, SPC-style rejection trend, pareto, heatmap, gauge...). Pure functions — data in, `go.Figure` out. |
| `styles.py` | Dark-theme CSS injected into the app, and the `.streamlit/config.toml` bootstrap. |
| `generate_sample_data.py` | Regenerates the bundled demo data. |

## 3. Feeding it your data

Put your `.xlsx` files (the 4 production reports + `plan.xlsx`) in the same
folder as `app.py` — the sidebar's "Folder with your .xlsx files" box
defaults there automatically. Each file can hold one sheet or several; every
`.xlsx` in the folder is scanned. You can also point the box elsewhere, or
use the file uploader instead.

The app auto-detects sheet roles (by file + sheet name) and column mapping
(by header keywords), then shows **"🔧 Confirm sheet & column mapping"** in
the sidebar so you can review or correct any guess before charts render —
robust to header differences like extra spaces, "A Grade" vs "Agrade", or a
generic "Sheet1" tab name.

Expected sheets/columns:

| Sheet role | Key columns |
|---|---|
| Day wise no. of cells produced | Date, Agrade, Bgrade, BEL, EB, Total, ER, FOR, ER(Q), Total, Raw Wafer, Blue, Al, Ag, Cell, Total |
| Month wise no. of cells produced | same, first column = Month |
| Daywise MW report | Date, A/B/BEL/EB saleable (Nos), A/B/BEL/EB saleable MW, Total production MW |
| Monthwise MW report | same, first column = Month |
| plan.xlsx | Month, A grade, B grade, BEL grade, Total Target (all MW) |
| *(optional)* SAP Efficiency / Tester Efficiency (Halm) columns | can live in either "day wise" sheet — mapped in the same panel if present |

If SAP/Tester efficiency columns aren't found, the Daily Efficiency Trend
chart (Production tab) still renders using a computed proxy (based on
breakage/rejection ratios) — the app tells you this via a caption whenever
it happens.

## 4. What's on each tab

**Overview** — *not* date-range driven; always shows the latest available
production date ("AS OF: 15-May-2025"). 8 KPI cards (Today's/MTD/YTD
Production, Yield %, Reject %, Run Rate, Required Rate, Plan Achievement as
a radial gauge), each with the exact comparison format requested (e.g.
"▲ 8.15% Previous MTD (+9.48 MW)"). Grade-wise donuts (Nos & MW), a Breakage
Split donut (MW + cell count in the legend), Run Rate vs Required Rate,
MTD Summary, a Rejection Trend (FOR % / ER % / Breakage %, SPC-style with
data labels), and the Monthly Performance Summary table (months shown as
"Jan 2025", not timestamps).

**Production** — From/To range picker + Daily/Weekly/Monthly view selector.
Charts: **Daily Production Trend** (combo: Good Cells (Nos.) bars + Overall
MW & A Grade MW lines, dual axis, value labels), **Daily Efficiency Trend**
(SAP Efficiency vs Tester Efficiency), Yield Trend, Rejection Trend, and
Plan vs Actual — all respond to the range and view selector.

**Analytics** — its own range + view selector. Breakage Pareto (horizontal
bars, MW & % sorted descending) and the Rejection Heatmap (Mon–Sun ×
ISO week, green/amber/red). Both are captioned to clarify they're computed
over the selected date range; the heatmap is always daily-grain by design
(day-of-week only makes sense that way).

All figures are formatted to 2 decimal places throughout.

## 5. Financial year

FY runs **April → March**. The sidebar's FY selector lists every FY that
overlaps your data, defaulting to the FY containing the latest production
date. YTD figures, and the default start date on Production/Analytics range
pickers, follow the selected FY.

## 6. Notes on estimated figures

Two things in your 4 sheets + plan.xlsx don't map to a source column
one-to-one, so they're computed with a clearly-labeled estimate:

- **Breakage MW** (Breakage Split donut, Breakage Pareto, Rejection Heatmap)
  — your sheets record breakage by *cell count*, not MW per type. The app
  estimates MW using the period's average watt/cell (`Total production MW`
  ÷ total saleable cells) × broken cell count. Captioned wherever it's used.
- **SAP/Tester Efficiency** — see §3 above.

If you have real source columns for either, map them in the sidebar's
mapping panel and the estimate is skipped automatically.
