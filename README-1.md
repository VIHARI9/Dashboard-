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

**Default: point it at a folder.** Put your `.xlsx` files (the 4 production
reports + `plan.xlsx`) in the same folder as `app.py` — the sidebar's "Folder
containing your .xlsx files" box defaults to that folder automatically, so
usually you don't need to type anything. Each file can hold one sheet or
several; the app scans every `.xlsx` in the folder and reads every sheet in
each. You can also point the box at any other folder, or use the file
uploader instead if you'd rather not have the files sit next to the code.

The app auto-detects which sheet is which (by file name + sheet name) and
which column is which (by header keywords), then shows a **"🔧 Confirm sheet
& column mapping"** panel in the sidebar so you can double check or correct
any guess before the charts render. This makes the app robust to small
differences in your real headers (extra spaces, "A Grade" vs "Agrade", a
generic "Sheet1" tab name, etc.) without editing code.

Expected sheets/columns (matches what you described):

| Sheet role | Key columns |
|---|---|
| Day wise no. of cells produced | Date, Agrade, Bgrade, BEL, EB, Total, ER, FOR, ER(Q), Total, Raw Wafer, Blue, Al, Ag, Cell, Total |
| Month wise no. of cells produced | same as above, first column = Month |
| Daywise MW report | Date, A/B/BEL/EB saleable (Nos), A/B/BEL/EB saleable MW, Total production MW |
| Monthwise MW report | same as above, first column = Month |
| **plan.xlsx** (Plan / Target) | Month, A grade (MW), B grade (MW), BEL grade (MW), Total Target (MW) |

Tip: the repeated "Total" columns (production total / rejection total /
breakage total) are handled by position, so keep them in that left-to-right
order in your sheet. The app recognizes `plan.xlsx` by its file name (or any
sheet/file with "plan"/"target" in the name) so it's never confused with the
production sheets.

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

`plan.xlsx` (Month, A grade, B grade, BEL grade, Total Target — all MW) now
drives Plan Achievement, Required Rate, the Plan-vs-Actual chart, the
grade-wise plan achievement in the MTD Summary panel, and the Plan MW column
in the Monthly Performance table. If a given month isn't in `plan.xlsx`, or
the sheet isn't found/mapped, the sidebar falls back to a manual "Plan MW"
number you can type in.

## 5. Files

- `app.py` — the Streamlit app.
- `data_utils.py` — sheet-role guessing + column auto-mapping engine
  (production sheets + plan.xlsx).
- `generate_sample_data.py` — regenerates the demo data if you want to
  tweak/extend it.
- `sample_data.xlsx`, `plan.xlsx` — one combined workbook + a plan file, for
  a quick preview via "Use bundled sample data".
- `sample_folder/` — mirrors your real setup: 5 separate `.xlsx` files
  (4 production reports + plan.xlsx) with generic "Sheet1" tabs, to confirm
  the folder-path + auto-mapping flow works even without descriptive sheet
  names.
