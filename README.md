# Solar Cell Manufacturing Dashboard


A Streamlit dashboard that replicates the reference UI: KPI cards, grade-wise
donuts, daily/monthly trends, run-rate tracking, breakage pareto, a rejection
heatmap, and a monthly performance table — built from your 4 Excel sheets.

## 1. Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## 2. Feeding it your data

In the sidebar, upload your Excel file(s):
- One workbook containing all 4 sheets, **or**
- Several files, each with one sheet — the app merges them.

The app auto-detects which sheet is which (by sheet name) and which column is
which (by header keywords), then shows a **"🔧 Confirm sheet & column
mapping"** panel in the sidebar so you can double check or correct any guess
before the charts render. This makes the app robust to small differences in
your real headers (extra spaces, "A Grade" vs "Agrade", etc.) without editing
code.

Expected sheets/columns (matches what you described):

| Sheet role | Key columns |
|---|---|
| Day wise no. of cells produced | Date, Agrade, Bgrade, BEL, EB, Total, ER, FOR, ER(Q), Total, Raw Wafer, Blue, Al, Ag, Cell, Total |
| Month wise no. of cells produced | same as above, first column = Month |
| Daywise MW report | Date, A/B/BEL/EB saleable (Nos), A/B/BEL/EB saleable MW, Total production MW |
| Monthwise MW report | same as above, first column = Month |

Tip: the repeated "Total" columns (production total / rejection total /
breakage total) are handled by position, so keep them in that left-to-right
order in your sheet.

## 3. What's on the dashboard

- **KPI row**: Today's Production, MTD, YTD, Yield %, Reject %, Run Rate,
  Required Rate, Plan Achievement — all computed live from the MW and Nos.
  sheets, with vs-yesterday / vs-last-month / vs-last-year deltas.
- **Grade-wise donuts** (Nos. and MW) for the selected period.
- **Daily production trend** line chart.
- **Plan vs Actual (Monthly)** bar chart — plan target is a sidebar input
  since your sheets don't include a "Planning" table; set it (or wire up a
  5th Planning sheet later, the mapping panel is built to extend).
- **Run Rate vs Required Rate** trend.
- **MTD Summary** panel.
- **Yield Trend, Rejection Trend, Breakage Pareto, Rejection Heatmap.**
- **Monthly Performance Summary** table (Plan, Actual, Achv %, A Grade %,
  Yield %, Reject %, Breakage %, Run Rate, Required Rate).

## 4. Notes on the "Plan" numbers

Your 4 sheets don't include a monthly plan/target table (the image's
"Planning" nav item implies a 5th sheet you haven't described yet). Until you
add that sheet, Plan MW is a sidebar input (`Monthly Target (Plan)`) applied
across the visible months. Swap this for a real `Planning` sheet whenever
you're ready — add a `plan_mw` role to `data_utils.py` the same way the other
4 roles are defined, and update the two spots in `app.py` that currently read
`monthly_plan_mw`.

## 5. Files

- `app.py` — the Streamlit app.
- `data_utils.py` — sheet-role guessing + column auto-mapping engine.
- `generate_sample_data.py` — regenerates `sample_data.xlsx` (demo data) if
  you want to tweak/extend the sample.
- `sample_data.xlsx` — bundled demo data so you can preview the dashboard
  immediately (tick "Use bundled sample data" in the sidebar).
